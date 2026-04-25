# CamtrapDP Data Model

This document outlines the relational data model for the CamtrapDP standard, based on the provided documentation.

## Tables and Their Schemas

### datapackage.json (Dataset Metadata - Conceptual)
This is a single JSON file containing overall metadata for the dataset. It is not a relational table in the traditional sense, but it's a core component.
- `name`: STRING (Dataset name)
- `description`: STRING (Dataset description)
- `version`: STRING (Dataset version)
- `source`: STRING (Dataset source)
- `contributors`: ARRAY of OBJECTS (List of contributors with their details)
- `keywords`: ARRAY of STRINGS (Keywords describing the dataset)
- `licences`: ARRAY of OBJECTS (Licensing information)
- `resources`: ARRAY of OBJECTS (List of all associated resources and used schemas)
- `study_methodology`: OBJECT (Information on sampling design, capture method, and individual recognition)
- `scope`: OBJECT (Taxonomic, temporal, and geographic scope of the dataset)

### Deployments
This table contains details about each camera trap deployment.
- `deploymentID`: STRING (Primary Key, Unique identifier for each deployment)
- `locationID`: STRING (Identifier for the location)
- `locality`: STRING (General location name)
- `latitude`: FLOAT (Latitude of the deployment)
- `longitude`: FLOAT (Longitude of the deployment)
- `country`: STRING (Country of deployment)
- `altitude`: FLOAT (Altitude of the deployment)
- `habitat`: STRING (Habitat type at the deployment site)
- `start_datetime`: DATETIME (Start date and time of the deployment)
- `end_datetime`: DATETIME (End date and time of the deployment)
- `camera_model`: STRING (Make and model of the camera trap)
- `camera_height`: FLOAT (Height of the camera above ground)
- `camera_depth`: FLOAT (Depth of the camera from a reference point)
- `camera_tilt`: FLOAT (Tilt angle of the camera)
- `camera_heading`: FLOAT (Compass heading of the camera)
- `bait_use`: STRING (Information on whether bait was used)
- `sampling_design`: STRING (Description of the sampling design)
- `capture_method`: STRING (Method used for capturing data)
- `individual_recognition`: BOOLEAN (Indicates if individuals are recognized)

### Media
This table contains information about each media asset (image or video).
- `mediaID`: STRING (Primary Key, Unique identifier for each media record)
- `deploymentID`: STRING (Foreign Key to Deployments)
- `file_path`: STRING (Relative path to the media file)
- `file_name`: STRING (Name of the media file, derived from `file_path`)
- `public_flag`: BOOLEAN (Indicates if the media file is publicly accessible)
- `media_type`: STRING (IANA media type, e.g., "image/jpeg")
- `exif_data`: JSON STRING (EXIF metadata of the media file, stored as a JSON string)

### Observations
This table contains details about each observation (detection) in the media.
- `observationID`: STRING (Primary Key, Unique identifier for each observation)
- `mediaID`: STRING (Foreign Key to Media)
- `eventID`: STRING (Identifier for an event, used for event-based observations)
- `start_datetime`: DATETIME (Start date and time of the observation)
- `end_datetime`: DATETIME (End date and time of the observation)
- `observationLevel`: STRING (Level of observation, e.g., "media" or "event")
- `observationType`: STRING (Type of observation, e.g., "animal", "human", "vehicle", "blank")
- `taxon_name`: STRING (Scientific name of the observed taxon)
- `count`: INTEGER (Number of individuals observed)
- `sex`: STRING (Sex of the observed individual)
- `behaviour`: STRING (Behavior of the observed individual)
- `individualID`: STRING (Identifier for an individual animal)
- `bbox_x_min`: FLOAT (Minimum X coordinate of the bounding box, normalized)
- `bbox_y_min`: FLOAT (Minimum Y coordinate of the bounding box, normalized)
- `bbox_width`: FLOAT (Width of the bounding box, normalized)
- `bbox_height`: FLOAT (Height of the bounding box, normalized)
- `classifier_who`: STRING (Who performed the classification)
- `classifier_how`: STRING (Method of classification)
- `classifier_when`: DATETIME (When the classification was performed)

## Relationships

- **Deployments to Media:**
    - One `Deployment` can be associated with many `Media` records.
    - Relationship: `Deployments.deploymentID` (PK) -> `Media.deploymentID` (FK)

- **Media to Observations:**
    - One `Media` record can contain many `Observation` records.
    - Relationship: `Media.mediaID` (PK) -> `Observations.mediaID` (FK)
