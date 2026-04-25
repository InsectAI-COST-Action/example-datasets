### Mapping Proposal: Current to CamtrapDP

This section outlines the proposed mapping of fields from the raw dataset (`data_infiltratie_c231_2025.csv` and `image_id_to_file_mapping.csv`) to the CamtrapDP format (`deployments.csv`, `media.csv`, `observations.csv`).

#### `deployments.csv` Mapping

| CamtrapDP Field (`deployments.csv`) | Raw Data Field (`data_infiltratie_c231_2025.csv`) | Grouping/Conversion/Remarks |
| :-------------------------------- | :------------------------------------------------ | :-------------------------- |
| `deploymentID` (Required)         | `sensor_name` + `deployment_name`                  | Grouping: Concatenate `sensor_name` and `deployment_name` to create a unique deployment ID. Example: `DIOPSIS-231_Boer5 - Controle 1`. |
| `locationID` (Required)           | `deployment_name`                                  | Use `deployment_name`. Confirmed by user as unique. |
| `locationName`                    | `deployment_name`                                  | Use `deployment_name`. |
| `latitude`                        | (Cannot be filled)                                 | **Remark 1.1**: No corresponding field in raw data. Will be left empty. |
| `longitude`                       | (Cannot be filled)                                 | **Remark 1.2**: No corresponding field in raw data. Will be left empty. |
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
| `captureMethod`                   | (Cannot be filled)                                                                 | **Remark 1.8**: No corresponding field. Will be left empty. |
| `timestamp` (Required)            | `capture_on`                                                                       | Use `capture_on`. Ensure format is ISO 8601. |
| `filePath`                        | Derived from `file_name`                                                           | Conversion: Construct the relative path to the image file. This would likely be `camtrap-data/images/<file_name>`. **Remark 3.1**: This assumes all images will be placed in a single `images` subfolder within `camtrap-data`. |
| `fileName` (Required)             | `image_file`                                                                       | Use `image_file` from `image_id_to_file_mapping.csv`. This needs to be joined using `media_id = image_id`. |
| `fileMediatype` (Required)        | Derived from `image_file` extension                                                | Conversion: Infer MIME type (e.g., 'image/jpeg') from file extension of `image_file`. |
| `mediaComments`                   | (Cannot be filled)                                                                 | **Remark 1.9**: No corresponding field. Will be left empty. |

#### `observations.csv` Mapping

| CamtrapDP Field (`observations.csv`) | Raw Data Field (`data_infiltratie_c231_2025.csv`) | Grouping/Conversion/Remarks |
| :---------------------------------- | :------------------------------------------------ | :-------------------------- |
| `observationID` (Required)          | Generated (UUID)                                  | Conversion: Generate a unique UUID for each observation. Each row in `data_infiltratie_c231_2025.csv` that is *not* "No detections found for this media item" represents an observation. If `individual_id` is present, it can be used to link multiple detections of the same individual within an image, but `observationID` must be globally unique per observation. |
| `deploymentID` (Required)           | `sensor_name` + `deployment_name`                  | Grouping: Concatenate `sensor_name` and `deployment_name` as used for `deployments.csv`. |
| `mediaID` (Required)                | `media_id`                                         | Use the existing `media_id`. |
| `eventID`                           | (Cannot be filled)                                 | **Remark 1.10**: No clear corresponding field. Will be left empty. Could potentially be derived from `deploymentID` and `capture_on` or `session_id`. |
| `eventStart`                        | `capture_on`                                       | Use `capture_on`. |
| `eventEnd`                          | `capture_on`                                       | Use `capture_on`. Assuming instantaneous observation for now. If a `sequence_id` or `session_id` are derived (for `media.csv`), `eventEnd` could be `max(capture_on)` for that sequence/session. |
| `observationLevel`                  | "individual" or "detection" or "event"             | Conversion: Set as "individual" if `individual_id` is present, otherwise "detection" if there's a bbox, otherwise "event" if it's a general observation without specific individual/detection. **Remark 3.2**: Needs clarification on appropriate level. If a row has "No detections found", this might not lead to an observation. This is not 95% sure how "No detections found" rows should affect `observationLevel` if they are included. |
| `observationType`                   | `name` == "No detections found for this media item" ? "empty" : "detection" | Conversion: If `name` is "No detections found...", then "empty", otherwise "detection". This assumes we only create observations for actual detections. **Remark 3.3**: If a row is "No detections found", should it still generate an `observations.csv` entry with `observationType = "empty"`? The CamtrapDP documentation implies observations are about actual observed organisms. If not, these rows should be filtered out from `observations.csv`. This is not 95% sure. |
| `scientificName` (Required)         | `name` (or `individual_taxon_name`)                | Use `name` if not "No detections found". If `individual_taxon_name` is present, it might be a more refined identification for the individual. Prioritize `individual_taxon_name` if available, otherwise use `name`. |
| `count`                             | `1` (for each distinct `individual_id` or detection) | Conversion: Each detection (row) typically represents a count of 1. If `individual_id` groups multiple detections of the same individual, `count` should be 1 for that individual. If no `individual_id`, each detection is count 1. |
| `lifeStage`                         | (Cannot be filled)                                 | **Remark 1.11**: No corresponding field. Will be left empty. |
| `sex`                               | (Cannot be filled)                                 | **Remark 1.12**: No corresponding field. Will be left empty. |
| `behavior`                          | (Cannot be filled)                                 | **Remark 1.13**: No corresponding field. Will be left empty. |
| `individualID`                      | `individual_id`                                    | Use `individual_id` from the raw data. This links multiple bounding boxes to the same individual within a media item. **Remark 3.4**: `individualID` in CamtrapDP refers to a persistent identifier for an individual organism across multiple observations, potentially even across deployments. `individual_id` in the raw data seems to be per-image detection. This is not 95% sure if `individual_id` from the raw data is truly suitable as a persistent `individualID`. |
| `bboxX`                             | `x1`                                               | Use `x1`. These are normalized coordinates (0-1). |
| `bboxY`                             | `y1`                                               | Use `y1`. These are normalized coordinates (0-1). |
| `bboxWidth`                         | `x2` - `x1`                                        | Conversion: Calculate width from `x2` - `x1`. |
| `bboxHeight`                        | `y2` - `y1`                                        | Conversion: Calculate height from `y2` - `y1`. |
| `classificationMethod`              | (Implicitly "Automated Detection/Classification") | Conversion: Can be set to a default value like "Automated Detection/Classification". **Remark 3.5**: Raw data does not specify the method explicitly. This is not 95% sure. |
| `classifiedBy`                      | (Cannot be filled)                                 | **Remark 1.14**: No corresponding field. Will be left empty. |
| `classificationTimestamp`           | `capture_on`                                       | Use `capture_on` as a proxy for classification timestamp if no other timestamp is available. **Remark 3.6**: This assumes classification happens at capture, which might not be true for post-processed data. This is not 95% sure. |
| `classificationProbability`         | `probability` (of detection)                       | Use `probability`. Can also include `individual_taxon_probability` here. |
| `observationComments`               | `body_length_mm`, `biomass_mg`, `resolution`      | Concatenate these fields into a comment string. **Remark 3.7**: Grouping disparate data into a single `observationComments` field may reduce its usability for structured queries. This is not 95% sure about the best way to handle these fields. |

---

**Additional Remarks and Issues (Revised):**

*   **Session ID/Sequence ID**: The user mentioned "Session_id is probably needed to combine time-consecutive media items into a temporal session". This is a crucial aspect for `media.csv` where `sequence_id` (though not in the provided header, but a common CamtrapDP field) or implicit grouping can be used. For `observations.csv`, `eventID`, `eventStart`, and `eventEnd` could be linked to these sessions. The raw data only provides `capture_on`. A method would need to be defined to group these. For example, consecutive images from the same `deploymentID` within a certain time window (e.g., 5 minutes) could be grouped.
*   **Missing Metadata**: A significant amount of metadata required by CamtrapDP (e.g., `coordinateUncertainty`, `cameraDelay`, `cameraHeight`, `cameraDepth`, `cameraTilt`, `cameraHeading`, `detectionDistance`, `timestampIssues`, `filePublic`, `exifData`, `favorite`, `observationTags`) is not present in the raw data. This will result in many empty fields in the target CSVs.
*   **Data Types**: The raw data contains floats for probabilities and measurements, and strings for names and IDs. These will need to be correctly parsed and formatted for CamtrapDP. Dates/times will need ISO 8601 formatting.
*   **Primary Keys**: `mediaID`, `deploymentID`, and `observationID` will need to be consistently generated or used across the output files to maintain referential integrity.
*   **"No detections found" rows**: How to handle rows where `name` is "No detections found for this media item"?
    *   For `deployments.csv`: These rows still contribute to `deploymentStart` and `deploymentEnd` if they are part of a deployment's timeline.
    *   For `media.csv`: These rows represent a valid media item, so an entry should be created for them.
    *   For `observations.csv`: An `observations.csv` entry should probably *not* be created for these. The CamtrapDP schema implies `observations.csv` is for *observations* of organisms. If such a row were to be included, `scientificName` would be empty, `count` would be 0, and `observationType` could be "empty" as discussed in remark 3.3.
*   **UUID Generation**: `observationID` will need to be a newly generated UUID to ensure global uniqueness. `media_id` is already a UUID in the raw data. The concept of `detection_id` from the target diagram is subsumed within `observationID` and bounding box fields in the actual `observations.csv` header. The user did not provide `detection_id` in the `observations.csv` header.



Answers (Elsbeth): 
1.1 and 1.2: I need to find the polygon of Alblasserwaard (a region in Holland)
1.3 tm 1.7: ok leaving empty
1.8: set to 'activityDetection' 
3.1: correct
- fileMediatype: set to 'image/jpeg'
1.9: ok to leave empty
1.10: ok to leave empty
- eventEnd: no sequence_id will be defined. If you can group multiple media items by individual_id, then you can use the captureOn of the last as eventEnd time. For all other cases: use captureOn.
3.2: If a row has "No detections found", don't add it to the observations.
3.3: set to 'animal' for all detections with probability >= 0.5, else 'unknown'. Exception: also set to 'unknown' when name is 'Too small for identification'
- scientificName : Also don't use when name is 'Too small to detect'
1.11, 1.12, 1.13: ok to leave empty
3.4: ok to use individual_id from the raw data
3.5: classificationMethod: set to 'machine'
1.14: classifiedBy: set to 'Diopsis 2025'
3.6: leave empty
- classificationProbability: use probability
3.7: leave out resolution, but add a string with {body_length_mm: xx, biomass_mg: xxx}