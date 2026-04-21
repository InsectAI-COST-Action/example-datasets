"""
Proposed Camtrap DP conversion for flower_visitors minidataset.

This script was run locally from: .../example-datasets/datasets/flower_visitors/code/
A Python enviornment with the packages listed in requirements.txt is required to run it end-to-end.

Outputs (in the parent dataset folder .../example-datasets/datasets/flower_visitors/) are:
    - deployments.csv
    - media.csv
    - observations.csv
    - datapackage.json

Author: Valentin Ștefan, vibe coded with Claude and GitHub Copilot
"""
from __future__ import annotations

import json
import mimetypes
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS

# --------------------------------------------------------------------------
# 0. Paths (all relative to flower_visitors/code/)
# --------------------------------------------------------------------------
DATASET_ROOT = Path("..")       # .../flower_visitors/
REPO_ROOT = Path("../../..")    # .../example-datasets/
ANNOTATIONS_TSV = DATASET_ROOT / "raw_data" / "annotations_subset.tsv"
MEDIA_RAW = DATASET_ROOT / "media" / "raw"
MEDIA_BG = DATASET_ROOT / "media" / "backgrounds"
# media/cropped/ is intentionally NOT ingested as media — it is a derived ROI
# cropped from media/raw/, and is referenced only through observationTags.

DEPLOYMENTS_TEMPLATE = REPO_ROOT / "deployments_template.csv"
MEDIA_TEMPLATE = REPO_ROOT / "media_template.csv"
OBSERVATIONS_TEMPLATE = REPO_ROOT / "observations_template.csv"

OUT_DEPLOYMENTS = DATASET_ROOT / "deployments.csv"
OUT_MEDIA = DATASET_ROOT / "media.csv"
OUT_OBSERVATIONS = DATASET_ROOT / "observations.csv"
OUT_DATAPACKAGE = DATASET_ROOT / "datapackage.json"

# --------------------------------------------------------------------------
# 1. Load source TSV
# --------------------------------------------------------------------------
df = pd.read_csv(ANNOTATIONS_TSV, sep="\t")
df["deploymentID"] = df["date"].astype(str) + "_" + df["plant_folder"].astype(str)
print(f"Loaded {len(df)} annotation rows; {df['deploymentID'].nunique()} deployments")

# --------------------------------------------------------------------------
# 2. Helpers
# --------------------------------------------------------------------------
# Order matters: from coarsest to finest. `deepest_rank` in the TSV selects
# which one is authoritative per row.
RANK_COLUMNS = [
    "order", "suborder", "infraorder", "superfamily", "family",
    "clustergenera", "genus", "morphospecies", "species",
]
# Ranks that are valid GBIF/Camtrap DP terms for `taxonRank`. Others
# (morphospecies, clustergenera) go into observationTags instead.
STANDARD_RANKS = {"order", "suborder", "infraorder", "superfamily",
                  "family", "genus", "species"}

# Who classified what — Hymenoptera were IDed by Aspen Workman; all other
# orders (Diptera, Araneae, etc.) by Jared Cobain.
HYMENOPTERA_CLASSIFIER = "Aspen Workman"
OTHER_CLASSIFIER = "Jared C. Cobain"


def classifier_for_row(row: pd.Series) -> str | float:
    order = row.get("order")
    if isinstance(order, str) and order.strip().lower() == "hymenoptera":
        return HYMENOPTERA_CLASSIFIER
    if isinstance(order, str) and order.strip():
        return OTHER_CLASSIFIER
    return np.nan


# Filename timestamp fallback. Raw full-frame files look like
#     2021-07-20_Trifolium-sp-01-EC_IMG_20210720_112107.jpg
# Backgrounds use a double-underscore separator that we normalise to single.
_FILENAME_TS_RE = re.compile(r"_IMG_(\d{8})_(\d{6})")


def timestamp_from_filename(filename: str) -> str | None:
    """Parse `..._IMG_YYYYMMDD_HHMMSS.jpg` → ISO 8601 UTC, or None."""
    m = _FILENAME_TS_RE.search(filename.replace("__", "_"))
    if not m:
        return None
    try:
        dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        return dt.replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def build_scientific_name(row: pd.Series) -> tuple[str | float, str | float]:
    """
    Returns (scientificName, taxonRank) using the deepest populated rank.

    - Genus + species → "Genus species"
    - Morphospecies / clustergenera → fall back to the coarsest valid rank
      (typically family), and encode the informal name in observationTags.
    """
    deepest = row.get("deepest_rank")
    if pd.isna(deepest):
        return (np.nan, np.nan)

    genus = row.get("genus")
    species = row.get("species")

    if deepest == "species" and pd.notna(genus) and pd.notna(species):
        return (f"{str(genus).capitalize()} {species}", "species")

    if deepest in STANDARD_RANKS:
        val = row.get(deepest)
        if pd.notna(val):
            return (str(val).capitalize(), deepest)

    # Informal ranks (morphospecies, clustergenera): walk up to the finest
    # standard rank with a value.
    for rank in reversed(RANK_COLUMNS):
        if rank in STANDARD_RANKS and pd.notna(row.get(rank)):
            return (str(row[rank]).capitalize(), rank)

    # Shouldn't happen for this dataset (everything at least has `order`).
    return (np.nan, np.nan)


def build_observation_tags(
    row: pd.Series,
    img_wh: tuple[int, int] | None = None,
) -> str | float:
    """
    Pipe-separated key:value list carrying everything that doesn't fit a
    standard Camtrap DP observation column.

    Bbox provenance is encoded explicitly so the original pixel values + the
    full-frame dimensions are recoverable from the normalized bboxX/Y/W/H:
        bboxFormat:normXYWH_fullFrame
        bboxPx:<x>,<y>,<w>,<h>
        imgSizePx:<W>,<H>
    The target-flower ROI crop region (which the cropped JPEG was taken from)
    travels alongside as roiPx + croppedFile.
    """
    tags: list[str] = []

    # --- bbox format + pixel provenance --------------------------------
    # Camtrap DP 1.0 spec: bboxX/Y/Width/Height are normalized [0,1] on the
    # full-frame image, top-left anchor, xywh.
    tags.append("bboxFormat:normXYWH_fullFrame")
    if all(pd.notna(row.get(c)) for c in ("x", "y", "width", "height")):
        tags.append(
            f"bboxPx:{int(row['x'])},{int(row['y'])},"
            f"{int(row['width'])},{int(row['height'])}"
        )
    if img_wh is not None:
        tags.append(f"imgSizePx:{img_wh[0]},{img_wh[1]}")

    # --- target-flower ROI crop region on the full-frame ----------------
    x_roi, y_roi = row.get("x_roi"), row.get("y_roi")
    w_roi, h_roi = row.get("width_roi"), row.get("height_roi")
    if all(pd.notna(v) for v in (x_roi, y_roi, w_roi, h_roi)):
        tags.append(
            f"roiPx:{int(x_roi)},{int(y_roi)},"
            f"{int(w_roi)},{int(h_roi)}"
        )
    crop = row.get("new_filename")
    if pd.notna(crop) and crop != "":
        tags.append(f"croppedFile:media/cropped/{crop}")

    # --- taxonomic provenance ------------------------------------------
    deepest = row.get("deepest_rank")
    if pd.notna(deepest):
        tags.append(f"deepestRank:{deepest}")
    for rank in RANK_COLUMNS + ["species_sex"]:
        conf = row.get(f"conf_{rank}")
        if pd.notna(conf) and conf != "":
            tags.append(f"conf_{rank}:{conf}")
    for rank in ("morphospecies", "clustergenera"):
        val = row.get(rank)
        if pd.notna(val) and val != "":
            tags.append(f"{rank}:{val}")

    # --- plant host + multi-box context --------------------------------
    for col in ("plant_genus", "plant_epithet", "plant_folder"):
        val = row.get(col)
        if pd.notna(val) and val != "":
            tags.append(f"{col}:{val}")
    n_boxes = row.get("n_boxes")
    if pd.notna(n_boxes):
        tags.append(f"nBoxesInFrame:{int(n_boxes)}")

    return "|".join(tags) if tags else np.nan


def mediaid_from_filename(filename: str) -> str:
    """Stable mediaID: filename stem."""
    return Path(filename).stem


def deploymentid_from_filename(filename: str) -> str:
    """`2021-07-20_Trifolium-sp-01-EC_IMG_20210720_112107.jpg`
       → `2021-07-20_Trifolium-sp-01-EC`"""
    date, plant_folder, *_ = filename.split("_", 2)
    return f"{date}_{plant_folder}"


def extract_exif(path: Path) -> tuple[dict, str | None]:
    """Return (exif_dict, ISO-8601 UTC timestamp | None)."""
    metadata: dict = {}
    timestamp_iso: str | None = None
    try:
        with Image.open(path) as img:
            exif = img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(value, (bytes, bytearray)):
                        continue
                    if isinstance(value, float) and np.isnan(value):
                        value = None
                    if tag == "DateTimeOriginal":
                        try:
                            dt = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                            timestamp_iso = dt.replace(
                                tzinfo=timezone.utc
                            ).isoformat()
                        except (ValueError, TypeError):
                            pass
                    metadata[tag] = value
    except Exception as err:
        print(f"  ! EXIF read failed for {path.name}: {err}")
    return metadata, timestamp_iso


# --------------------------------------------------------------------------
# 3. deployments.csv
# --------------------------------------------------------------------------
df_deployments = pd.read_csv(DEPLOYMENTS_TEMPLATE)

deployment_ids = sorted(df["deploymentID"].unique())

# Per-deployment plant taxonomy from the TSV (one target flower per deployment by design)
plant_by_dep = (
    df.groupby("deploymentID")[["plant_genus", "plant_epithet"]]
    .first()
    .to_dict("index")
)

dep_rows = []
for dep_id in deployment_ids:
    date_str, plant_folder = dep_id.split("_", 1)
    plant = plant_by_dep.get(dep_id, {})
    plant_genus = (plant.get("plant_genus") or "").strip()
    plant_epithet = (plant.get("plant_epithet") or "").strip()
    plant_sci = (
        f"{plant_genus.capitalize()} {plant_epithet}".strip()
        if plant_genus or plant_epithet else ""
    )

    tag_items = [f"plant_folder:{plant_folder}"]
    if plant_genus:
        tag_items.append(f"targetPlantGenus:{plant_genus}")
    if plant_epithet:
        tag_items.append(f"targetPlantEpithet:{plant_epithet}")
    if plant_sci:
        tag_items.append(f"targetPlantScientificName:{plant_sci}")

    dep_rows.append({
        "deploymentID": dep_id,
        "locationID": "LEI_A-701-1",
        "locationName": "Leipzig Botanical Garden",
        "latitude": 51.381921,
        "longitude": 12.272399,
        "coordinateUncertainty": np.nan,   # unknown
        # Placeholder; overwritten below with per-deployment min/max EXIF.
        "deploymentStart": datetime.strptime(
            date_str, "%Y-%m-%d"
        ).replace(tzinfo=timezone.utc).isoformat(),
        "deploymentEnd": datetime.strptime(
            date_str, "%Y-%m-%d"
        ).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc).isoformat(),
        "setupBy": np.nan,                 # unknown / not attributed
        "cameraID": np.nan,                # no hardware cameraID recorded
        "cameraModel": "smartphone",       # refine with make/model if known
        "timestampIssues": False,
        "baitUse": False,
        # featureType is a Camtrap DP 1.0 enum (roadPaved, burrow, nestSite,
        # waterSource, fruitingTree, …) — "flower" is not a valid value and
        # the frictionless validator rejects it. Left blank; the target-flower
        # context is captured in `deploymentTags` and `habitat` instead.
        "featureType": np.nan,
        "habitat": "urban botanical garden meadow; target plant in flower",
        # deploymentGroups is reserved for grouping deployments together (e.g.
        # "treatment", "2021_season") — not for the target plant identity,
        # which lives in deploymentTags below.
        "deploymentGroups": np.nan,
        "deploymentTags": "|".join(tag_items),
    })
df_deployments = pd.concat(
    [df_deployments, pd.DataFrame(dep_rows).reindex(columns=df_deployments.columns)],
    ignore_index=True,
)

# --------------------------------------------------------------------------
# 4. media.csv (full-frames from media/raw/ + media/backgrounds/)
# --------------------------------------------------------------------------
df_media = pd.read_csv(MEDIA_TEMPLATE)
# Columns dropped from template that we don't touch are fine — reindex fills NaN.

media_rows = []
background_media: list[dict] = []          # subset of media_rows flagged blank
img_dims: dict[str, tuple[int, int]] = {}  # mediaID → (w, h) for bbox normalisation

for folder, is_background in [(MEDIA_RAW, False), (MEDIA_BG, True)]:
    if not folder.exists():
        print(f"Skipping missing folder: {folder}")
        continue
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in (".jpg", ".jpeg"):
            continue
        # backgrounds use double-underscore separator; normalise
        original_name = path.name.replace("__", "_")
        media_id = mediaid_from_filename(original_name)
        deployment_id = deploymentid_from_filename(original_name)

        exif, ts = extract_exif(path)
        if ts is None:
            ts = timestamp_from_filename(path.name)
            if ts is not None:
                print(f"  . {path.name}: used filename timestamp (EXIF missing)")
        mtype, _ = mimetypes.guess_type(path)
        mtype = mtype or "image/jpeg"

        with Image.open(path) as img:
            img_dims[media_id] = img.size  # (w, h)

        rel_path = path.relative_to(DATASET_ROOT).as_posix()  # media/raw/foo.jpg

        media_rows.append({
            "mediaID": media_id,
            "deploymentID": deployment_id,
            "captureMethod": "timeLapse",
            "timestamp": ts,
            "filePath": rel_path,
            "filePublic": True,
            "fileName": path.name,
            "fileMediatype": mtype,
            "exifData": json.dumps({"EXIF": exif}, default=str) if exif else np.nan,
            "mediaComments": "background (no flower visitor)" if is_background else np.nan,
        })
        if is_background:
            background_media.append(
                {"mediaID": media_id, "deploymentID": deployment_id, "timestamp": ts}
            )

df_media = pd.concat(
    [df_media, pd.DataFrame(media_rows).reindex(columns=df_media.columns)],
    ignore_index=True,
)
print(f"media.csv rows: {len(df_media)}")

# --------------------------------------------------------------------------
# 4b. Per-deployment min/max EXIF timestamps → deploymentStart/End
# --------------------------------------------------------------------------
ts_series = pd.to_datetime(df_media["timestamp"], utc=True, errors="coerce")
by_dep = (
    df_media.assign(_ts=ts_series)
    .dropna(subset=["_ts"])
    .groupby("deploymentID")["_ts"]
    .agg(["min", "max"])
)
for dep_id, (tmin, tmax) in by_dep.iterrows():
    df_deployments.loc[
        df_deployments["deploymentID"] == dep_id, "deploymentStart"
    ] = tmin.isoformat()
    df_deployments.loc[
        df_deployments["deploymentID"] == dep_id, "deploymentEnd"
    ] = tmax.isoformat()

# --------------------------------------------------------------------------
# 5. observations.csv
# --------------------------------------------------------------------------
# Three kinds of rows, in order:
#   (a) one media-level row per bbox in the TSV (observationLevel="media",
#       observationType="animal"), eventStart/End = the media's own timestamp,
#       eventID = seq_id (the individual-insect track);
#   (b) one event-level row per unique seq_id (observationLevel="event",
#       observationType="animal"), carrying the shared scientificName /
#       classifiedBy across the frames of the sequence;
#   (c) one blank media-level row per background image (observationLevel=
#       "media", observationType="blank").
# individualID is left empty across the board per current Camtrap DP guidance
# — the individual-vs-event-vs-individualID semantics are still being
# worked out; seq_id lives in eventID instead.
df_observations = pd.read_csv(OBSERVATIONS_TEMPLATE)
media_ts = dict(zip(df_media["mediaID"], df_media["timestamp"]))
df["_mediaID"] = df["filename_full_frame"].map(mediaid_from_filename)
df["_timestamp"] = df["_mediaID"].map(media_ts)

obs_rows: list[dict] = []

# --- (a) media-level bbox rows ---------------------------------------------
for _, row in df.iterrows():
    media_id = row["_mediaID"]
    img_wh = img_dims.get(media_id)
    if img_wh is None:
        print(f"  ! No image dims for {media_id}; skipping bbox normalisation")
        bx = by = bw = bh = np.nan
    else:
        img_w, img_h = img_wh
        bx = float(np.clip(row["x"] / img_w, 0, 1))
        by = float(np.clip(row["y"] / img_h, 0, 1))
        bw = float(np.clip(row["width"] / img_w, 0, 1))
        bh = float(np.clip(row["height"] / img_h, 0, 1))

    sci_name, _taxon_rank = build_scientific_name(row)
    seq = row.get("seq_id")
    media_time = row["_timestamp"]

    sex_raw = row.get("species_sex")
    sex = sex_raw if sex_raw in ("male", "female", "worker", "queen") else np.nan

    obs_rows.append({
        # observationID combines the media filename stem (which already
        # encodes date + plant_folder + frame timestamp and is itself
        # unique per full-frame image) with `id_box` to disambiguate
        # multiple bboxes in the same frame.
        "observationID": f"{media_id}_box{int(row['id_box'])}",
        "deploymentID": row["deploymentID"],
        "mediaID": media_id,
        "eventID": f"seq_{int(seq)}" if pd.notna(seq) else np.nan,
        "eventStart": media_time,
        "eventEnd": media_time,
        "observationLevel": "media",
        "observationType": "animal",
        "scientificName": sci_name,
        "count": 1,
        "lifeStage": "adult",
        "sex": sex,
        # individualID intentionally blank — see header comment above.
        "individualID": np.nan,
        "bboxX": bx,
        "bboxY": by,
        "bboxWidth": bw,
        "bboxHeight": bh,
        "classificationMethod": "human",
        "classifiedBy": classifier_for_row(row),
        # classificationProbability intentionally left empty — annotator
        # confidence in this dataset is a subjective ordinal (high/medium/low),
        # not a calibrated probability.
        "classificationProbability": np.nan,
        "observationTags": build_observation_tags(row, img_wh=img_wh),
    })

# --- (b) event-level rows (one per seq_id) --------------------------------
# eventStart / eventEnd span the frames that captured the individual across
# the sequence — min and max of the per-frame timestamps in the group.
seq_groups = df.dropna(subset=["seq_id"]).groupby("seq_id", sort=True)
for seq_id, grp in seq_groups:
    first = grp.iloc[0]
    sci_name, _ = build_scientific_name(first)
    seq_ts = pd.to_datetime(grp["_timestamp"], utc=True, errors="coerce").dropna()
    ev_start = seq_ts.min().isoformat() if not seq_ts.empty else np.nan
    ev_end = seq_ts.max().isoformat() if not seq_ts.empty else np.nan
    obs_rows.append({
        # observationID anchors on the deploymentID (unique by date +
        # plant_folder) and the seq track number, so no collision with the
        # media-level `<mediaID>_box<n>` rows.
        "observationID": f"{first['deploymentID']}_event_seq{int(seq_id)}",
        "deploymentID": first["deploymentID"],
        "mediaID": np.nan,
        "eventID": f"seq_{int(seq_id)}",
        "eventStart": ev_start,
        "eventEnd": ev_end,
        "observationLevel": "event",
        "observationType": "animal",
        "scientificName": sci_name,
        "count": 1,
        "lifeStage": "adult",
        "individualID": np.nan,
        "bboxX": np.nan,
        "bboxY": np.nan,
        "bboxWidth": np.nan,
        "bboxHeight": np.nan,
        "classificationMethod": "human",
        "classifiedBy": classifier_for_row(first),
        "classificationTimestamp": np.nan,
        "classificationProbability": np.nan,
        "observationTags": np.nan,
    })

# --- (c) blank observations for background media --------------------------
for bg in background_media:
    obs_rows.append({
        # mediaID already encodes date + plant_folder + frame timestamp and
        # is unique; `_blank` suffix keeps it distinct from the animal rows.
        "observationID": f"{bg['mediaID']}_blank",
        "deploymentID": bg["deploymentID"],
        "mediaID": bg["mediaID"],
        "eventID": np.nan,
        # eventStart/End required by the schema — use the background's own
        # timestamp so validation passes.
        "eventStart": bg["timestamp"],
        "eventEnd": bg["timestamp"],
        "observationLevel": "media",
        "observationType": "blank",
        "scientificName": np.nan,
        # count left blank: the Camtrap DP 1.0 schema requires count >= 1
        # when present, which rules out count=0 for blanks. Leaving it empty
        # is the spec-compliant way to say "no animal present".
        "count": np.nan,
        "individualID": np.nan,
        "bboxX": np.nan,
        "bboxY": np.nan,
        "bboxWidth": np.nan,
        "bboxHeight": np.nan,
        "classificationMethod": "human",
        "classifiedBy": np.nan,
        "classificationTimestamp": np.nan,
        "classificationProbability": np.nan,
        "observationTags": np.nan,
    })

df_observations = pd.concat(
    [df_observations, pd.DataFrame(obs_rows).reindex(columns=df_observations.columns)],
    ignore_index=True,
)
print(f"observations.csv rows: {len(df_observations)}")

# --------------------------------------------------------------------------
# 6. Cross-table integrity checks
# --------------------------------------------------------------------------
def _check(name: str, missing_set: set):
    if missing_set:
        print(f"  ! {name}: {sorted(missing_set)[:5]}"
              f"{' ...' if len(missing_set) > 5 else ''}")

_check(
    "deploymentIDs in media missing from deployments",
    set(df_media["deploymentID"].dropna()) - set(df_deployments["deploymentID"].dropna()),
)
_check(
    "mediaIDs in observations missing from media",
    set(df_observations["mediaID"].dropna()) - set(df_media["mediaID"].dropna()),
)
for req in ("deploymentID", "deploymentStart", "deploymentEnd",
            "latitude", "longitude"):
    miss = df_deployments[req].isna().sum()
    if miss:
        print(f"  ! deployments.{req}: {miss} missing")
for req in ("mediaID", "deploymentID", "timestamp", "filePath",
            "filePublic", "fileMediatype"):
    miss = df_media[req].isna().sum()
    if miss:
        print(f"  ! media.{req}: {miss} missing")
for req in ("observationID", "deploymentID", "eventStart", "eventEnd",
            "observationLevel", "observationType"):
    miss = df_observations[req].isna().sum()
    if miss:
        print(f"  ! observations.{req}: {miss} missing")

# --------------------------------------------------------------------------
# 7. datapackage.json
# --------------------------------------------------------------------------
taxonomic = []
seen = set()
for _, obs in df_observations.iterrows():
    sci = obs["scientificName"]
    if pd.isna(sci) or sci in seen:
        continue
    seen.add(sci)
    # Find the rank from a lookup over TSV rows with matching sci name
    sample = df.apply(lambda r: build_scientific_name(r)[0] == sci, axis=1)
    ranks = df.loc[sample].apply(lambda r: build_scientific_name(r)[1], axis=1)
    ranks = [r for r in ranks if pd.notna(r)]
    taxonomic.append({
        "scientificName": sci,
        "taxonRank": ranks[0] if ranks else "family",
    })

datapackage = {
    "resources": [
        {
            "name": "deployments",
            "path": "deployments.csv",
            "profile": "tabular-data-resource",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0/deployments-table-schema.json",
        },
        {
            "name": "media",
            "path": "media.csv",
            "profile": "tabular-data-resource",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0/media-table-schema.json",
        },
        {
            "name": "observations",
            "path": "observations.csv",
            "profile": "tabular-data-resource",
            "format": "csv",
            "mediatype": "text/csv",
            "encoding": "utf-8",
            "schema": "https://raw.githubusercontent.com/tdwg/camtrap-dp/1.0/observations-table-schema.json",
        },
    ],
    "name": "flower-visitors-insectai-datathon",
    "created": datetime.now(timezone.utc).isoformat(),
    "contributors": [
        {
            "title": "Valentin Ștefan",
            "role": "author",
            "email": "valentin.stefan@idiv.de",
        },
        {"title": "Aspen Workman", "role": "contributor"},
        {"title": "Jared C. Cobain", "role": "contributor"},
        {"title": "Demetra Rakosy", "role": "contributor"},
        {"title": "Boryana Wild Stoykova", "role": "contributor"},
        {"title": "Elena Cyranka", "role": "contributor"},
        {"title": "Raquel Urrego Álvarez", "role": "contributor"},
        {"title": "Tiffany Knight", "role": "principalInvestigator"},
    ],
    "licenses": [
        {
            "scope": "media",
            "name": "CC-BY-NC-SA-4.0",
            "path": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "title": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
        },
        {
            "scope": "data",
            "name": "CC-BY-NC-SA-4.0",
            "path": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "title": "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
        },
    ],
    "project": {
        "title": "Flower visitors (smartphone time-lapse subset)",
        "description": (
            "Subset of arthropod flower-visit images collected via smartphone "
            "time-lapse photography in and around Leipzig/Halle, Germany. "
            "Full dataset: https://doi.org/10.5281/zenodo.15096610. "
            "Bounding boxes in observations.csv follow Camtrap DP 1.0 "
            "convention: normalized [0,1] coordinates (bboxX/Y/Width/Height) "
            "relative to the full-frame image, top-left anchor, xywh "
            "(x = left, y = top, width & height in the same normalized units). "
            "The original pixel bbox, the full-frame image dimensions, and "
            "the target-flower ROI crop region are preserved per-row in "
            "observationTags as bboxPx, imgSizePx, and roiPx. "
            "Insect identification credits: Hymenoptera by Aspen Workman; "
            "all other orders (Diptera, Araneae, etc.) by Jared C. Cobain."
        ),
        "samplingDesign": "targeted",
        "captureMethod": "timeLapse",
        "individualAnimals": True,
        "observationLevel": "media",
    },
    "spatial": {
        "type": "Point",
        "coordinates": [12.272399, 51.381921],   # GeoJSON order: [lon, lat]
    },
    "temporal": {"start": "2021-07-20", "end": "2021-08-14"},
    "taxonomic": taxonomic,
    "bibliographicCitation": (
        "Ștefan, V., Workman, A., Cobain, J. C., Rakosy, D., Wild Stoykova, B., "
        "Cyranka, E., Urrego Álvarez, R., & Knight, T. (2025). "
        "Dataset of arthropod flower visits captured via smartphone time-lapse "
        "photography [Data set]. Zenodo. "
        "https://doi.org/10.5281/zenodo.15096610"
    ),
}

# --------------------------------------------------------------------------
# 8. Write outputs
# --------------------------------------------------------------------------
df_deployments.to_csv(OUT_DEPLOYMENTS, index=False)
df_media.to_csv(OUT_MEDIA, index=False)
# Camtrap DP typed `count` as integer; pandas auto-promotes the column to
# float when blank rows (the event-level + blank observations) introduce
# NaN. Cast to nullable Int64 so the CSV serialises as `1` instead of `1.0`.
df_observations["count"] = df_observations["count"].astype("Int64")
df_observations.to_csv(OUT_OBSERVATIONS, index=False)
with open(OUT_DATAPACKAGE, "w") as f:
    json.dump(datapackage, f, indent=4, ensure_ascii=False)

print("\nWrote:")
for p in (OUT_DEPLOYMENTS, OUT_MEDIA, OUT_OBSERVATIONS, OUT_DATAPACKAGE):
    print(f"  {p}")

print("\nNext: frictionless validate ../datapackage.json")
