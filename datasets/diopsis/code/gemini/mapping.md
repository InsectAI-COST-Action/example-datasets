### Mapping Proposal: Current to CamtrapDP

This section outlines the proposed mapping of fields from the raw dataset (`data_infiltratie_c231_2025.csv` and `image_id_to_file_mapping.csv`) to the CamtrapDP format (`deployments.csv`, `media.csv`, `observations.csv`).

#### `deployments.csv` Mapping

| CamtrapDP Field (`deployments.csv`) | Raw Data Field (`data_infiltratie_c231_2025.csv`) | Grouping/Conversion/Remarks |
| :-------------------------------- | :------------------------------------------------ | :-------------------------- |
| `deploymentID` (Required)         | `sensor_name` + `deployment_name`                  | Grouping: Concatenate `sensor_name` and `deployment_name` to create a unique deployment ID. Example: `DIOPSIS-231_Boer5 - Controle 1`. |
| `locationID` (Required)           | `deployment_name`                                  | Use `deployment_name`. Confirmed by user as unique. |
| `locationName`                    | `deployment_name`                                  | Use `deployment_name`. |
| `latitude`                        | (To be determined)                                 | **Remark 1.1**: User needs to find the polygon of Alblasserwaard. Will be left empty for now. |
| `longitude`                       | (To be determined)                                 | **Remark 1.2**: User needs to find the polygon of Alblasserwaard. Will be left empty for now. |
| `deploymentStart` (Required)      | Min(`capture_on`) per `deploymentID`              | Conversion: Find the earliest `capture_on` timestamp for each unique `deploymentID`. |
| `deploymentEnd` (Required)        | Max(`capture_on`) per `deploymentID`              | Conversion: Find the latest `capture_on` timestamp for each unique `deploymentID`. |
| `cameraID` (Required)             | `sensor_name`                                      | Use `sensor_name` as `cameraID`. |
| `cameraModel`                     | (Cannot be filled)                                 | **Remark 1.3**: No corresponding field in raw data. Will be left empty. |
| `baitUse`                         | (Cannot be filled)                                 | **Remark 1.4**: No corresponding field in raw data. Will be left empty. |
| `featureType`                     | (Cannot be filled)                                 | **Remark 1.5**: No corresponding field in raw data. Will be left empty. |
| `habitat`                         | (Cannot be filled)                                 | **Remark 1.6**: No corresponding field in raw data. Will be left empty. |
| `deploymentComments`              | (Cannot be filled)                                 | **Remark 1.7**: No corresponding field in raw data. Will be left empty. |

#### `media.csv` Mapping

| CamtrapDP Field (`media.csv`)     | Raw Data Field (`data_infiltratie_c231_2025.csv` / `image_id_to_file_mapping.csv`) | Grouping/Conversion/Remarks |
| :-------------------------------- | :--------------------------------------------------------------------------------- | :-------------------------- |
| `mediaID` (Required)              | `media_id` / `image_id`                                                            | Use the existing `media_id` (from `data_infiltratie_c231_2025.csv`) or `image_id` (from `image_id_to_file_mapping.csv`). They appear to be the same UUID. |
| `deploymentID` (Required)         | `sensor_name` + `deployment_name`                                                  | Grouping: Concatenate `sensor_name` and `deployment_name` as used for `deployments.csv`. |
| `captureMethod`                   | "activityDetection"                                                              | **Remark 1.8**: Set to 'activityDetection' as per user instruction. |
| `timestamp` (Required)            | `capture_on`                                                                       | Use `capture_on`. Ensure format is ISO 8601. |
| `filePath`                        | Derived from `file_name`                                                           | Conversion: Construct the relative path to the image file. This would likely be `camtrap-data/images/<file_name>`. **Remark 3.1**: This assumes all images will be placed in a single `images` subfolder within `camtrap-data`. Confirmed by user. |
| `fileName` (Required)             | `image_file`                                                                       | Use `image_file` from `image_id_to_file_mapping.csv`. This needs to be joined using `media_id = image_id`. |
| `fileMediatype` (Required)        | "image/jpeg"                                                                     | Conversion: Set to 'image/jpeg' as per user instruction. |
| `mediaComments`                   | (Cannot be filled)                                                                 | **Remark 1.9**: No corresponding field. Will be left empty. |

#### `observations.csv` Mapping

| CamtrapDP Field (`observations.csv`) | Raw Data Field (`data_infiltratie_c231_2025.csv`) | Grouping/Conversion/Remarks |
| :---------------------------------- | :------------------------------------------------ | :-------------------------- |
| `observationID` (Required)          | Generated (UUID)                                  | Conversion: Generate a unique UUID for each observation. Each row in `data_infiltratie_c231_2025.csv` that is *not* "No detections found for this media item" and meets other criteria represents an observation. If `individual_id` is present, it can be used to link multiple detections of the same individual within an image, but `observationID` must be globally unique per observation. |
| `deploymentID` (Required)           | `sensor_name` + `deployment_name`                  | Grouping: Concatenate `sensor_name` and `deployment_name` as used for `deployments.csv`. |
| `mediaID` (Required)                | `media_id`                                         | Use the existing `media_id`. |
| `eventID`                           | (Cannot be filled)                                 | **Remark 1.10**: No clear corresponding field. Will be left empty. |
| `eventStart`                        | `capture_on`                                       | Use `capture_on`. |
| `eventEnd`                          | `capture_on` (or Max `capture_on` per `individual_id`) | Conversion: If multiple media items can be grouped by `individual_id`, use the `capture_on` of the last media item as `eventEnd`. Otherwise, use `capture_on`. No `sequence_id` will be defined. |
| `observationLevel`                  | "individual" or "detection" or "event"             | Conversion: Set as "individual" if `individual_id` is present, otherwise "detection" if there's a bbox, otherwise "event" if it's a general observation without specific individual/detection. |
| `observationType`                   | Conditional                                       | Conversion: Set to 'animal' for all detections with `probability` >= 0.5. Otherwise, set to 'unknown'. Exception: also set to 'unknown' when `name` is 'Too small for identification'. **Remark 3.3**: Rows with "No detections found" will not be added to observations. |
| `scientificName` (Required)         | `name` (or `individual_taxon_name`)                | Use `name` if not "No detections found" and not "Too small to detect". If `individual_taxon_name` is present, it might be a more refined identification for the individual. Prioritize `individual_taxon_name` if available, otherwise use `name`. |
| `count`                             | `1` (for each distinct `individual_id` or detection) | Conversion: Each detection (row) typically represents a count of 1. If `individual_id` groups multiple detections of the same individual, `count` should be 1 for that individual. If no `individual_id`, each detection is count 1. |
| `lifeStage`                         | (Cannot be filled)                                 | **Remark 1.11**: No corresponding field. Will be left empty. |
| `sex`                               | (Cannot be filled)                                 | **Remark 1.12**: No corresponding field. Will be left empty. |
| `behavior`                          | (Cannot be filled)                                 | **Remark 1.13**: No corresponding field. Will be left empty. |
| `individualID`                      | `individual_id`                                    | Use `individual_id` from the raw data. This links multiple bounding boxes to the same individual within a media item. Confirmed by user as suitable for persistent `individualID`. |
| `bboxX`                             | `x1`                                               | Use `x1`. These are normalized coordinates (0-1). |
| `bboxY`                             | `y1`                                               | Use `y1`. These are normalized coordinates (0-1). |
| `bboxWidth`                         | `x2` - `x1`                                        | Conversion: Calculate width from `x2` - `x1`. |
| `bboxHeight`                        | `y2` - `y1`                                        | Conversion: Calculate height from `y2` - `y1`. |
| `classificationMethod`              | "machine"                                         | **Remark 3.5**: Set to 'machine' as per user instruction. |
| `classifiedBy`                      | "Diopsis 2025"                                    | **Remark 1.14**: Set to 'Diopsis 2025' as per user instruction. |
| `classificationTimestamp`           | (Cannot be filled)                                 | **Remark 3.6**: User requested to leave empty. |
| `classificationProbability`         | `probability` (of detection)                       | Use `probability`. Can also include `individual_taxon_probability` here. |
| `observationComments`               | `body_length_mm`, `biomass_mg`                     | Conversion: Add a string with `{body_length_mm: xx, biomass_mg: xxx}`. `resolution` will be left out. |

---

**Additional Remarks and Issues (Revised):**

*   **Session ID/Sequence ID**: No `sequence_id` will be defined. If multiple media items can be grouped by `individual_id`, then `eventEnd` in `observations.csv` can use the `capture_on` of the last media item in that group. Otherwise, `capture_on` will be used for both `eventStart` and `eventEnd`. This removes the need for `session_id` to combine time-consecutive media items into a temporal session for `media.csv`.
*   **Missing Metadata**: A significant amount of metadata required by CamtrapDP (e.g., `coordinateUncertainty`, `cameraDelay`, `cameraHeight`, `cameraDepth`, `cameraTilt`, `cameraHeading`, `detectionDistance`, `timestampIssues`, `filePublic`, `exifData`, `favorite`, `observationTags`) is not present in the raw data. This will result in many empty fields in the target CSVs.
*   **Data Types**: The raw data contains floats for probabilities and measurements, and strings for names and IDs. These will need to be correctly parsed and formatted for CamtrapDP. Dates/times will need ISO 8601 formatting.
*   **Primary Keys**: `mediaID`, `deploymentID`, and `observationID` will need to be consistently generated or used across the output files to maintain referential integrity.
*   **"No detections found" rows**: Rows where `name` is "No detections found for this media item" will *not* be added to `observations.csv` as per user instruction. For `deployments.csv` and `media.csv`, these rows still contribute to deployment timelines and represent valid media items, respectively.
*   **UUID Generation**: `observationID` will need to be a newly generated UUID to ensure global uniqueness. `media_id` is already a UUID in the raw data. The concept of `detection_id` from the target diagram is subsumed within `observationID` and bounding box fields in the actual `observations.csv` header. The user did not provide `detection_id` in the `observations.csv` header. This is no longer an issue as `detection_id` is not a target field. 