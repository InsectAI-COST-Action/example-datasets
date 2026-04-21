#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[3]
SOURCE_DIR = ROOT / "Cerro_Hoya_Expedition"
DATASET_DIR = ROOT / "datasets" / "Mothbox"
MEDIA_DIR = DATASET_DIR / "media"
RAW_DIR = DATASET_DIR / "raw-data"
CODE_DIR = DATASET_DIR / "code"

DEPLOYMENTS_TEMPLATE = ROOT / "deployments_template.csv"
MEDIA_TEMPLATE = ROOT / "media_template.csv"
OBSERVATIONS_TEMPLATE = ROOT / "observations_template.csv"

TZ_OFFSET = "-05:00"  # America/Panama


@dataclass
class MetadataRecord:
    deployment_name: str
    deployment_folder: str
    site: str
    latitude: str
    longitude: str
    deployment_date: str
    collect_date: str
    device: str
    values: Dict[str, str]


def read_template_columns(path: Path) -> List[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle))
    return header


def ensure_clean_dirs() -> None:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CODE_DIR.mkdir(parents=True, exist_ok=True)


def copy_partitioned_files() -> Tuple[List[Path], List[Path]]:
    copied_media: List[Path] = []
    copied_json: List[Path] = []

    for jpg in SOURCE_DIR.rglob("*.jpg"):
        rel = jpg.relative_to(SOURCE_DIR)
        if "patches" not in rel.parts:
            continue
        dst = MEDIA_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(jpg, dst)
        copied_media.append(dst)

    for jsn in SOURCE_DIR.rglob("*.json"):
        rel = jsn.relative_to(SOURCE_DIR)
        dst = RAW_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(jsn, dst)
        copied_json.append(dst)

    src_exports = SOURCE_DIR / "exports"
    dst_exports = RAW_DIR / "exports"
    if dst_exports.exists():
        shutil.rmtree(dst_exports)
    shutil.copytree(src_exports, dst_exports)

    src_meta = SOURCE_DIR / "metadata_old_format.csv"
    shutil.copy2(src_meta, RAW_DIR / "metadata_old_format.csv")
    return copied_media, copied_json


def parse_date_ddmmyy(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    return datetime.strptime(value, "%d-%m-%y").strftime("%Y-%m-%d")


def iso_from_date(date_str: str, end_of_day: bool = False) -> str:
    if not date_str:
        return ""
    time_part = "23:59:59" if end_of_day else "00:00:00"
    return f"{date_str}T{time_part}{TZ_OFFSET}"


def try_float(text: str) -> Optional[float]:
    try:
        return float(text)
    except Exception:
        return None


def detect_lat_lon(row: List[str], header: List[str], site_value: str) -> Tuple[str, str]:
    site_idx = header.index("site") if "site" in header else 0
    for i in range(site_idx + 1, len(row) - 1):
        lat = try_float(row[i])
        lon = try_float(row[i + 1])
        if lat is None or lon is None:
            continue
        if -90 <= lat <= 90 and -180 <= lon <= 180:
            return str(lat), str(lon)
    return "", ""


def parse_metadata() -> Dict[str, MetadataRecord]:
    path = SOURCE_DIR / "metadata_old_format.csv"
    records: Dict[str, MetadataRecord] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        for row in reader:
            if not row or not any(v.strip() for v in row):
                continue
            values = {header[i]: (row[i].strip() if i < len(row) else "") for i in range(len(header))}
            dep_name = values.get("deployment_name", "")
            site = values.get("site", "")
            device = values.get("device", "")
            dep_date = parse_date_ddmmyy(values.get("deployment_date", ""))
            coll_date = parse_date_ddmmyy(values.get("collect_date", ""))
            latitude, longitude = detect_lat_lon(row, header, site)
            dep_folder = "_".join(dep_name.split("_")[-4:]) if dep_name else ""
            if dep_name:
                records[dep_name] = MetadataRecord(
                    deployment_name=dep_name,
                    deployment_folder=dep_folder,
                    site=site,
                    latitude=latitude,
                    longitude=longitude,
                    deployment_date=dep_date,
                    collect_date=coll_date,
                    device=device,
                    values=values,
                )
    return records


def fallback_id(prefix: str, *parts: str) -> str:
    joined = "|".join(parts)
    return f"{prefix}_{hashlib.sha1(joined.encode('utf-8')).hexdigest()[:16]}"


def parse_patch_timestamp(patch_name: str) -> str:
    stem = Path(patch_name).stem
    mtch = re.search(r"_(\d{4})_(\d{2})_(\d{2})__(\d{2})_(\d{2})_(\d{2})_", stem)
    if mtch:
        yyyy, mm, dd, hh, mi, ss = mtch.groups()
        return f"{yyyy}-{mm}-{dd}T{hh}:{mi}:{ss}{TZ_OFFSET}"
    mtch = re.search(r"_(\d{4})_(\d{2})_(\d{2})__(\d{2})_(\d{2})_(\d{2})$", stem)
    if mtch:
        yyyy, mm, dd, hh, mi, ss = mtch.groups()
        return f"{yyyy}-{mm}-{dd}T{hh}:{mi}:{ss}{TZ_OFFSET}"
    return ""


def load_bbox_index() -> Dict[str, Dict[str, str]]:
    bbox: Dict[str, Dict[str, str]] = {}
    for jsn in RAW_DIR.rglob("*.json"):
        if jsn.name == "night_summary.json":
            continue
        try:
            data = json.loads(jsn.read_text(encoding="utf-8"))
        except Exception:
            continue
        for shp in data.get("shapes", []):
            patch_path = (shp.get("patch_path") or "").replace("\\", "/")
            patch_name = Path(patch_path).name
            points = shp.get("points") or []
            if not patch_name or not points:
                continue
            xs = [p[0] for p in points if isinstance(p, list) and len(p) == 2]
            ys = [p[1] for p in points if isinstance(p, list) and len(p) == 2]
            if not xs or not ys:
                continue
            min_x = min(xs)
            min_y = min(ys)
            width = max(xs) - min_x
            height = max(ys) - min_y
            bbox[patch_name] = {
                "bboxX": f"{min_x:.3f}",
                "bboxY": f"{min_y:.3f}",
                "bboxWidth": f"{width:.3f}",
                "bboxHeight": f"{height:.3f}",
            }
    return bbox


def choose_metadata_for_export_deployment(
    export_deployment: str, metadata_records: Dict[str, MetadataRecord]
) -> Optional[MetadataRecord]:
    folder_candidate = export_deployment.split("Cerro_Hoya_Expedition_")[-1]
    matches = [m for m in metadata_records.values() if m.deployment_folder == folder_candidate]
    if matches:
        return matches[0]
    for m in metadata_records.values():
        if m.deployment_name.endswith(folder_candidate):
            return m
    return None


def write_csv(path: Path, columns: List[str], rows: Iterable[Dict[str, str]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, "") for col in columns})
            count += 1
    return count


def create_readme() -> None:
    readme = DATASET_DIR / "README.md"
    readme.write_text(
        "\n".join(
            [
                "# Mothbox Cerro Hoya",
                "",
                "This dataset was generated from `Cerro_Hoya_Expedition` using a Python conversion script.",
                "",
                "- `media/`: patch JPG files only (original source images intentionally excluded).",
                "- `raw-data/`: source JSON files, exports, and metadata_old_format.csv.",
                "- Camtrap-style outputs: `deployments.csv`, `media.csv`, `observations.csv`, `unaccountedfor.csv`, `datapackage.json`.",
            ]
        ),
        encoding="utf-8",
    )


def create_datapackage(row_counts: Dict[str, int]) -> None:
    datapackage = {
        "profile": "camtrap-dp",
        "name": "mothbox-cerro-hoya",
        "created": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "licenses": [
            {"scope": "data", "name": "unknown", "path": "", "title": "Unknown"}
        ],
        "resources": [
            {
                "name": "deployments",
                "path": "deployments.csv",
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0/deployments-table-schema.json",
                "dialect": {"csv": {"header": True}},
                "count": row_counts.get("deployments", 0),
            },
            {
                "name": "media",
                "path": "media.csv",
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0/media-table-schema.json",
                "dialect": {"csv": {"header": True}},
                "count": row_counts.get("media", 0),
            },
            {
                "name": "observations",
                "path": "observations.csv",
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0/observations-table-schema.json",
                "dialect": {"csv": {"header": True}},
                "count": row_counts.get("observations", 0),
            },
        ],
    }
    (DATASET_DIR / "datapackage.json").write_text(json.dumps(datapackage, indent=2), encoding="utf-8")


def main() -> None:
    deployments_columns = read_template_columns(DEPLOYMENTS_TEMPLATE)
    media_columns = read_template_columns(MEDIA_TEMPLATE)
    observations_columns = read_template_columns(OBSERVATIONS_TEMPLATE)

    ensure_clean_dirs()
    copy_partitioned_files()

    metadata_records = parse_metadata()
    bbox_index = load_bbox_index()
    export_files = sorted((RAW_DIR / "exports").glob("*.csv"))

    deployments_rows: Dict[str, Dict[str, str]] = {}
    media_rows: Dict[str, Dict[str, str]] = {}
    observations_rows: List[Dict[str, str]] = []
    unaccounted_rows: List[Dict[str, str]] = []

    used_export_fields = {
        "deployment",
        "occurrenceID",
        "eventID",
        "scientificName",
        "eventDate",
        "eventTime",
        "filepath",
        "identifiedBy",
        "image_id",
    }

    for export_file in export_files:
        with export_file.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for idx, row in enumerate(reader, start=2):
                export_deployment = (row.get("deployment") or "").strip()
                md = choose_metadata_for_export_deployment(export_deployment, metadata_records)

                deployment_id = md.deployment_name if md else fallback_id("deployment", export_deployment)
                if deployment_id not in deployments_rows:
                    deployments_rows[deployment_id] = {
                        "deploymentID": deployment_id,
                        "locationID": (md.site if md else ""),
                        "locationName": (md.site if md else ""),
                        "latitude": (md.latitude if md else ""),
                        "longitude": (md.longitude if md else ""),
                        "coordinateUncertainty": "",
                        "deploymentStart": (iso_from_date(md.deployment_date) if md else ""),
                        "deploymentEnd": (iso_from_date(md.collect_date, end_of_day=True) if md else ""),
                        "setupBy": "",
                        "cameraID": (md.device if md else ""),
                        "cameraModel": "",
                        "cameraDelay": "",
                        "cameraHeight": "",
                        "cameraDepth": "",
                        "cameraTilt": "",
                        "cameraHeading": "",
                        "detectionDistance": "",
                        "timestampIssues": "",
                        "baitUse": "",
                        "featureType": "",
                        "habitat": "",
                        "deploymentGroups": "",
                        "deploymentTags": "",
                        "deploymentComments": "",
                    }
                    if md:
                        mapped_metadata = {"deployment_name", "site", "device", "deployment_date", "collect_date", "latitude", "longitude"}
                        for field, value in md.values.items():
                            if field in mapped_metadata or not (value or "").strip():
                                continue
                            unaccounted_rows.append(
                                {
                                    "source_file": "metadata_old_format.csv",
                                    "source_row": deployment_id,
                                    "source_field": field,
                                    "source_value": value,
                                    "mapped_table": "deployments",
                                    "mapped_id": deployment_id,
                                }
                            )

                patch_name = (row.get("occurrenceID") or "").strip()
                media_id = Path(patch_name).stem if patch_name else fallback_id(
                    "media", row.get("filepath", ""), row.get("eventDate", ""), row.get("eventTime", "")
                )
                raw_filepath = (row.get("filepath") or "").replace("\\", "/")
                rel_media_path = raw_filepath.split("Cerro_Hoya_Expedition/", 1)[-1]
                media_rows[media_id] = {
                    "mediaID": media_id,
                    "deploymentID": deployment_id,
                    "captureMethod": "",
                    "timestamp": parse_patch_timestamp(patch_name),
                    "filePath": rel_media_path,
                    "filePublic": "",
                    "fileName": Path(rel_media_path).name,
                    "fileMediatype": "image/jpeg",
                    "exifData": "",
                    "favorite": "",
                    "mediaComments": "",
                }

                identified_by = (row.get("identifiedBy") or "").strip()
                method = "machine" if identified_by.lower() == "mothbot" else "human"
                bbox = bbox_index.get(Path(patch_name).name, {})
                obs_id = (row.get("occurrenceID") or "").strip() or fallback_id(
                    "obs", media_id, row.get("scientificName", ""), row.get("eventID", "")
                )
                observations_rows.append(
                    {
                        "observationID": obs_id,
                        "deploymentID": deployment_id,
                        "mediaID": media_id,
                        "eventID": (row.get("eventID") or "").strip(),
                        "eventStart": (iso_from_date(md.deployment_date) if md else ""),
                        "eventEnd": (iso_from_date(md.collect_date, end_of_day=True) if md else ""),
                        "observationLevel": "media",
                        "observationType": "machine_observation",
                        "cameraSetupType": "",
                        "scientificName": (row.get("scientificName") or "").strip(),
                        "count": "",
                        "lifeStage": "",
                        "sex": "",
                        "behavior": "",
                        "individualID": "",
                        "individualPositionRadius": "",
                        "individualPositionAngle": "",
                        "individualSpeed": "",
                        "bboxX": bbox.get("bboxX", ""),
                        "bboxY": bbox.get("bboxY", ""),
                        "bboxWidth": bbox.get("bboxWidth", ""),
                        "bboxHeight": bbox.get("bboxHeight", ""),
                        "classificationMethod": method,
                        "classifiedBy": identified_by,
                        "classificationTimestamp": (row.get("classificationTimestamp") or "").strip(),
                        "classificationProbability": "",
                        "observationTags": "",
                        "observationComments": "",
                    }
                )

                for field, value in row.items():
                    if field in used_export_fields or not (value or "").strip():
                        continue
                    unaccounted_rows.append(
                        {
                            "source_file": export_file.name,
                            "source_row": str(idx),
                            "source_field": field,
                            "source_value": value,
                            "mapped_table": "observations",
                            "mapped_id": obs_id,
                        }
                    )

    deployments_count = write_csv(DATASET_DIR / "deployments.csv", deployments_columns, deployments_rows.values())
    media_count = write_csv(DATASET_DIR / "media.csv", media_columns, media_rows.values())
    observations_count = write_csv(DATASET_DIR / "observations.csv", observations_columns, observations_rows)
    write_csv(
        DATASET_DIR / "unaccountedfor.csv",
        ["source_file", "source_row", "source_field", "source_value", "mapped_table", "mapped_id"],
        unaccounted_rows,
    )
    create_datapackage({"deployments": deployments_count, "media": media_count, "observations": observations_count})
    create_readme()
    print(f"Wrote {deployments_count} deployments, {media_count} media, {observations_count} observations.")


if __name__ == "__main__":
    main()
