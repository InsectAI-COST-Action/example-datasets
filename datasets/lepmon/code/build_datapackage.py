#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


RESOURCE_FILES = (
    "deployments.csv",
    "media.csv",
    "model.csv",
    "detections.csv",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate datapackage.json from raw-data/metadata.json "
            "and copy the tabular data files beside it."
        )
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Dataset directory containing raw-data/, media/, and datapackage.json.",
    )
    return parser.parse_args()


def load_metadata(metadata_path: Path) -> dict:
    with metadata_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, list) or not payload or not isinstance(payload[0], dict):
        raise ValueError(f"Expected a non-empty JSON array in {metadata_path}")

    return payload[0]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "lepmon"


def split_values(value: str, pattern: str) -> list[str]:
    return [item.strip() for item in re.split(pattern, value) if item.strip()]


def normalize_description(value: str | None) -> str | None:
    if not value:
        return None

    parts = split_values(value, r"\|")
    if not parts:
        return None
    return " | ".join(parts)


def normalize_datetime(value: str | None) -> str | None:
    if not value:
        return None

    candidate = value.strip().replace(" ", "T")
    try:
        parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
    except ValueError:
        return value

    if parsed.tzinfo is None:
        return parsed.isoformat(timespec="milliseconds")
    return parsed.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def build_spatial(metadata: dict) -> dict | None:
    keys = ("min_lon", "min_lat", "max_lon", "max_lat")
    if any(metadata.get(key) is None for key in keys):
        return None

    min_lon = float(metadata["min_lon"])
    min_lat = float(metadata["min_lat"])
    max_lon = float(metadata["max_lon"])
    max_lat = float(metadata["max_lat"])

    if min_lon == max_lon and min_lat == max_lat:
        return {
            "type": "Point",
            "coordinates": [min_lon, min_lat],
        }

    return {
        "type": "Polygon",
        "coordinates": [[
            [min_lon, min_lat],
            [max_lon, min_lat],
            [max_lon, max_lat],
            [min_lon, max_lat],
            [min_lon, min_lat],
        ]],
    }


def build_contributors(metadata: dict) -> list[dict]:
    raw_value = metadata.get("project_contributor", "")
    return [{"title": name, "role": "author"} for name in split_values(raw_value, r";")]


def build_taxonomic(metadata: dict) -> list[dict]:
    raw_value = metadata.get("project_taxa", "")
    taxa = split_values(raw_value, r"[;|,]")
    return [{"scientificName": taxon} for taxon in taxa]


def read_header_fields(csv_path: Path) -> list[dict]:
    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        headers = next(reader)
    return [{"name": header.strip().strip('"')} for header in headers if header.strip()]


def build_resources(dataset_dir: Path) -> list[dict]:
    resources = []
    raw_data_dir = dataset_dir / "raw-data"

    for filename in RESOURCE_FILES:
        source_path = raw_data_dir / filename
        resources.append(
            {
                "name": source_path.stem,
                "path": filename,
                "profile": "tabular-data-resource",
                "format": "csv",
                "mediatype": "text/csv",
                "encoding": "utf-8",
                "dialect": {
                    "delimiter": "\t",
                },
                "schema": {
                    "fields": read_header_fields(source_path),
                },
            }
        )

    return resources


def build_datapackage(metadata: dict, dataset_dir: Path) -> dict:
    identifier = str(metadata.get("project_identifier") or dataset_dir.name)
    title = metadata.get("project_title")
    description = normalize_description(metadata.get("project_description"))

    datapackage = {
        "profile": "data-package",
        "name": slugify(identifier),
        "title": title,
        "description": description,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "contributors": build_contributors(metadata),
        "resources": build_resources(dataset_dir),
        "project": {
            "identifier": identifier,
            "title": title,
        },
        "temporal": {
            "start": normalize_datetime(metadata.get("min_time")),
            "end": normalize_datetime(metadata.get("max_time")),
        },
        "taxonomic": build_taxonomic(metadata),
    }

    spatial = build_spatial(metadata)
    if spatial is not None:
        datapackage["spatial"] = spatial

    if description:
        datapackage["project"]["description"] = description

    return prune_empty_values(datapackage)


def prune_empty_values(value):
    if isinstance(value, dict):
        pruned = {
            key: prune_empty_values(item)
            for key, item in value.items()
            if item is not None
        }
        return {key: item for key, item in pruned.items() if item not in ("", [], {})}

    if isinstance(value, list):
        pruned = [prune_empty_values(item) for item in value]
        return [item for item in pruned if item not in ("", [], {})]

    return value


def copy_resource_files(dataset_dir: Path) -> None:
    raw_data_dir = dataset_dir / "raw-data"
    missing = [filename for filename in RESOURCE_FILES if not (raw_data_dir / filename).is_file()]
    if missing:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(f"Missing expected raw-data files: {missing_list}")

    for filename in RESOURCE_FILES:
        shutil.copy2(raw_data_dir / filename, dataset_dir / filename)


def main() -> None:
    args = parse_args()
    dataset_dir = args.dataset_dir.resolve()
    metadata_path = dataset_dir / "raw-data" / "metadata.json"

    metadata = load_metadata(metadata_path)
    datapackage = build_datapackage(metadata, dataset_dir)

    copy_resource_files(dataset_dir)

    datapackage_path = dataset_dir / "datapackage.json"
    with datapackage_path.open("w", encoding="utf-8") as handle:
        json.dump(datapackage, handle, indent=2)
        handle.write("\n")

    print(f"Wrote {datapackage_path}")
    for filename in RESOURCE_FILES:
        print(f"Copied {dataset_dir / filename}")


if __name__ == "__main__":
    main()
