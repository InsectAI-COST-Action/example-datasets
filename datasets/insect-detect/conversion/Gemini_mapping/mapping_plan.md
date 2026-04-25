# Insect-Detect to CamtrapDP Data Model Mapping Plan

This document outlines the proposed mapping from the current `insect-detect` data model to the CamtrapDP standard data model. The goal is to identify how data fields from the raw `insect-detect` dataset can be transformed and aligned with the CamtrapDP structure.

## Current Insect-Detect Data Model to CamtrapDP Mapping

### 1. Device (Current Model) -> Deployments (CamtrapDP)

The `Device` information from the current model will primarily map to the `Deployments` table in CamtrapDP. Each `device_id` essentially represents a deployment.

| Current Model (Device) Field | CamtrapDP (Deployments) Field | Notes/Transformation |
|:-----------------------------|:------------------------------|:---------------------|
| `device_id`                  | `deploymentID`                | Direct mapping. |
| (Implicit device info)       | `locationID`                  | To be derived or set to a default/placeholder if not available in current data. |
| (Implicit device info)       | `locality`                    | To be derived or set to a default/placeholder if not available. |
| (Implicit device info)       | `latitude`                    | From `Configuration.deployment.location.latitude`. |
| (Implicit device info)       | `longitude`                   | From `Configuration.deployment.location.longitude`. |
| (Implicit device info)       | `country`                     | To be derived or set to a default/placeholder. |
| (Implicit device info)       | `altitude`                    | To be derived or set to a default/placeholder. |
| (Implicit device info)       | `habitat`                     | To be derived or set to a default/placeholder. |
| (Implicit device info)       | `camera_model`                | To be derived from device metadata or set to a default. |
| (Implicit device info)       | `camera_height`               | To be derived or set to a default. |
| (Implicit device info)       | `camera_depth`                | To be derived or set to a default. |
| (Implicit device info)       | `camera_tilt`                 | To be derived or set to a default. |
| (Implicit device info)       | `camera_heading`              | To be derived or set to a default. |
| (Implicit device info)       | `bait_use`                    | To be derived or set to a default. |
| (Implicit device info)       | `sampling_design`             | To be derived or set to a default. |
| (Implicit device info)       | `capture_method`              | To be derived or set to a default. |
| (Implicit device info)       | `individual_recognition`      | To be derived or set to a default. |

### 2. SessionInfo (Current Model) -> Deployments (CamtrapDP)

The `SessionInfo` table provides critical temporal information for deployments.

| Current Model (SessionInfo) Field | CamtrapDP (Deployments) Field | Notes/Transformation |
|:----------------------------------|:------------------------------|:---------------------|
| `session_start`                   | `start_datetime`              | Direct mapping. |
| `session_end`                     | `end_datetime`                | Direct mapping. |
| `device_id`                       | (Used for joining)            | Joins to `Deployments.deploymentID`. |
| `session_id`                      | (Not directly mapped as a primary field) | Can be used as a secondary identifier or in notes. |
| `duration_min`                    | (No direct mapping)           | Can be calculated from `start_datetime` and `end_datetime`. |
| `disk_free_gb`                    | (No direct mapping)           | Can be added to `exif_data` or `notes` if necessary. |
| `chargelevel_start`               | (No direct mapping)           | Can be added to `exif_data` or `notes` if necessary. |
| `chargelevel_end`                 | (No direct mapping)           | Can be added to `exif_data` or `notes` if necessary. |

### 3. Detection (Current Model) -> Media & Observations (CamtrapDP)

Each row in the `Detection` table represents a specific observation within an image, requiring mapping to both `Media` and `Observations` in CamtrapDP.

#### 3.1 Detection (Current Model) -> Media (CamtrapDP)

| Current Model (Detection) Field | CamtrapDP (Media) Field | Notes/Transformation |
|:--------------------------------|:------------------------|:---------------------|
| `filename`                      | `file_name`             | Direct mapping. |
| `filename`                      | `file_path`             | Construct relative path using `file_name` and assumed base directory. |
| `device_id` + `session_id` + `timestamp` + `filename` | `mediaID`               | Concatenate to create a unique media ID. |
| `device_id`                     | `deploymentID`          | Foreign key to `Deployments.deploymentID`. |
| (No direct mapping)             | `public_flag`           | Set to default (e.g., `false`) or derive from dataset policy. |
| (No direct mapping)             | `media_type`            | Set to "image/jpeg" for JPGs. |
| `lens_position`                 | `exif_data`             | Include in JSON string. |
| `iso_sensitivity`               | `exif_data`             | Include in JSON string. |
| `exposure_time`                 | `exif_data`             | Include in JSON string. |

#### 3.2 Detection (Current Model) -> Observations (CamtrapDP)

| Current Model (Detection) Field | CamtrapDP (Observations) Field | Notes/Transformation |
|:--------------------------------|:-------------------------------|:---------------------|
| `device_id` + `session_id` + `timestamp` + `track_id` | `observationID`                | Concatenate to create a unique observation ID. |
| `device_id` + `session_id` + `timestamp` + `filename` | `mediaID`                      | Foreign key to `Media.mediaID` (same as derived above). |
| `timestamp`                     | `start_datetime`               | Direct mapping. |
| `timestamp`                     | `end_datetime`                 | Direct mapping (assuming instantaneous observation). |
| `label`                         | `observationType`              | Map "insect" to "animal" or more specific if possible. |
| `confidence`                    | (No direct mapping)            | Can be included in `classifier_how` or `notes`. |
| `track_id`                      | `individualID`                 | Can map track_id to individualID, if track_id represents individual insects. |
| `x_min`, `y_min`, `x_max`, `y_max` | `bbox_x_min`, `bbox_y_min`, `bbox_width`, `bbox_height` | Calculate width (`x_max - x_min`) and height (`y_max - y_min`). |
| (No direct mapping)             | `eventID`                      | To be derived or set to a default. |
| (No direct mapping)             | `observationLevel`             | Set to "media". |
| (No direct mapping)             | `taxon_name`                   | To be derived from `label` or further classification. |
| (No direct mapping)             | `count`                        | Default to 1 for individual detections. |
| (No direct mapping)             | `sex`                          | To be derived or set to `unknown`. |
| (No direct mapping)             | `behaviour`                    | To be derived or set to `unknown`. |
| (No direct mapping)             | `classifier_who`               | Set to "machine" or specific model name. |
| `detection.model` (from Config) | `classifier_how`               | Reference the detection model used. |
| (Timestamp of detection)        | `classifier_when`              | Use `timestamp` from `Detection` or `SessionInfo.session_start`. |

### 4. SystemLog (Current Model) -> Deployments (Metadata/Notes) (CamtrapDP)

`SystemLog` data contains technical details about the device's operation. Many of these might not have direct counterparts in CamtrapDP core tables but can be stored as metadata or notes.

| Current Model (SystemLog) Field | CamtrapDP Field (Suggestion) | Notes/Transformation |
|:--------------------------------|:-----------------------------|:---------------------|
| `timestamp`                     | `exif_data` or `notes`       | Can be included in `exif_data` for a media record if the timestamps align, or in general deployment notes. |
| `rpi_cpu_temp`                  | `exif_data` or `notes`       | Store as part of deployment metadata. |
| `rpi_cpu_usage_avg`             | `exif_data` or `notes`       | Store as part of deployment metadata. |
| `rpi_ram_usage`                 | `exif_data` or `notes`       | Store as part of deployment metadata. |
| `oak_chip_temp`                 | `exif_data` or `notes`       | Store as part of deployment metadata. |
| `power_input`                   | `exif_data` or `notes`       | Store as part of deployment metadata. |
| `charge_level`                  | `exif_data` or `notes`       | Store as part of deployment metadata. |
| `voltage_in_V`                  | `exif_data` or `notes`       | Store as part of deployment metadata. |
| `current_out_A`                 | `exif_data` or `notes`       | Store as part of deployment metadata. |
| `temp_wittypi`                  | `exif_data` or `notes`       | Store as part of deployment metadata. |

### 5. Configuration (Current Model) -> Deployments (Metadata/Notes) & datapackage.json (CamtrapDP)

The `Configuration` data will be crucial for populating several fields in `Deployments` and the overall `datapackage.json` metadata.

| Current Model (Configuration) Section | CamtrapDP Field (Suggestion) | Notes/Transformation |
|:--------------------------------------|:-----------------------------|:---------------------|
| `deployment.start`                    | `deployments.start_datetime` | Direct mapping (if available). |
| `deployment.location.latitude`        | `deployments.latitude`       | Direct mapping. |
| `deployment.location.longitude`       | `deployments.longitude`      | Direct mapping. |
| `deployment.notes`                    | `deployments.notes`          | Direct mapping. |
| `camera.fps`                          | `deployments.camera_settings` (JSON) | Include in a JSON string within `deployments.camera_settings` or `exif_data`. |
| `camera.image.resolution`             | `deployments.camera_settings` (JSON) | Include in a JSON string. |
| `camera.focus.lens_pos`               | `exif_data` (Media)          | Can be extracted and mapped to media EXIF. |
| `detection.model`                     | `observations.classifier_how` | Direct mapping. |
| `detection.conf_threshold`            | `observations.classifier_how` (notes) | Can be added as a note in `classifier_how`. |
| (All other config fields)             | `datapackage.json` (study_methodology or notes) / `deployments.notes` / `exif_data` (Media) | These can be included in the dataset metadata (`datapackage.json`), specific deployment notes, or as part of the `exif_data` for media where appropriate. This requires careful consideration during the conversion process to determine the most logical placement. |
