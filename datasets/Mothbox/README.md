<!-- Image: media/Hoya_408m_calmoBarbo_2025-01-26/2025-01-26/patches/calmoBarbo_2025_01_27__04_53_06_HDR0_3_Mothbot_yolo11m_4500_imgsz1600_b1_2024-01-18.pt.jpg -->
# 🐞 Mothbox dataset (Camtrap DP)

<img src="media/Hoya_408m_calmoBarbo_2025-01-26/2025-01-26/patches/calmoBarbo_2025_01_27__04_53_06_HDR0_3_Mothbot_yolo11m_4500_imgsz1600_b1_2024-01-18.pt.jpg" alt="Mothbox example patch image" width="300"/>

This dataset was generated from `Cerro_Hoya_Expedition` using a Python conversion script.

- `media/`: patch JPG files only (original source images intentionally excluded).
- `raw-data/`: source JSON files, exports, and mothbot_metadata.csv.
- Camtrap-style outputs: `deployments.csv`, `media.csv`, `observations.csv`, `unaccountedfor.csv`, `datapackage.json`.

## Technical Requirements

The conversion script `code/convert_mothbox_to_camtrapdp.py` currently uses only Python standard-library modules:

- `csv`
- `hashlib`
- `json`
- `re`
- `shutil`
- `dataclasses`
- `datetime`
- `pathlib`
- `typing`

No third-party Python packages are required.