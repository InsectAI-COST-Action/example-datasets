# Current Insect-Detect Data Model

This document outlines the relational data model for the current `insect-detect` dataset based on the raw CSV and JSON files.

## Tables and Their Schemas

### Device (Conceptual)
This entity represents the camera device. Its primary identifier, `device_id`, is used as a foreign key in other tables.
- `device_id`: STRING (Primary Key)

### SessionInfo
This table contains information about each recording session.
- `device_id`: STRING (Primary Key, Foreign Key to Device)
- `session_id`: STRING (Primary Key, Unique identifier for a session within a device)
- `session_start`: DATETIME (Timestamp when the session started)
- `session_end`: DATETIME (Timestamp when the session ended)
- `duration_min`: FLOAT (Duration of the session in minutes)
- `unique_track_ids`: INTEGER (Number of unique insect tracks identified in the session)
- `disk_free_gb`: FLOAT (Free disk space on the device at the end of the session)
- `chargelevel_start`: STRING (Battery charge level at the start of the session)
- `chargelevel_end`: STRING (Battery charge level at the end of the session)

### Detection
This table stores details about each individual insect detection event. Each row corresponds to a detection within an image.
- `filename`: STRING (Primary Key, Name of the image file where the detection occurred)
- `device_id`: STRING (Foreign Key to SessionInfo)
- `session_id`: STRING (Foreign Key to SessionInfo)
- `timestamp`: DATETIME (Timestamp of the image capture)
- `label`: STRING (Detected object label, e.g., "insect")
- `confidence`: FLOAT (Confidence score of the detection)
- `track_id`: INTEGER (Unique ID for a tracked object within a session and image)
- `track_status`: STRING (Status of the tracked object, e.g., "TRACKED")
- `x_min`: FLOAT (Normalized minimum X-coordinate of the bounding box)
- `y_min`: FLOAT (Normalized minimum Y-coordinate of the bounding box)
- `x_max`: FLOAT (Normalized maximum X-coordinate of the bounding box)
- `y_max`: FLOAT (Normalized maximum Y-coordinate of the bounding box)
- `lens_position`: INTEGER (Camera lens position at the time of capture)
- `iso_sensitivity`: INTEGER (ISO sensitivity setting)
- `exposure_time`: FLOAT (Exposure time in milliseconds)

### SystemLog
This table records system-level metrics and status during a session.
- `device_id`: STRING (Foreign Key to SessionInfo)
- `session_id`: STRING (Foreign Key to SessionInfo)
- `timestamp`: DATETIME (Primary Key, Timestamp of the log entry)
- `rpi_cpu_temp`: FLOAT (Raspberry Pi CPU temperature)
- `rpi_cpu_usage_avg`: FLOAT (Raspberry Pi CPU average usage)
- `rpi_cpu_usage_sum`: FLOAT (Raspberry Pi CPU total usage)
- `rpi_ram_usage`: FLOAT (Raspberry Pi RAM usage)
- `rpi_ram_available`: FLOAT (Raspberry Pi RAM available)
- `oak_chip_temp`: FLOAT (OAK chip temperature)
- `oak_cpu_usage_css`: FLOAT (OAK CPU usage CSS)
- `oak_cpu_usage_mss`: FLOAT (OAK CPU usage MSS)
- `oak_ram_usage_ddr`: FLOAT (OAK RAM usage DDR)
- `oak_ram_available_ddr`: FLOAT (OAK RAM available DDR)
- `oak_ram_usage_css`: FLOAT (OAK RAM usage CSS)
- `oak_ram_available_css`: FLOAT (OAK RAM available CSS)
- `oak_ram_usage_mss`: FLOAT (OAK RAM usage MSS)
- `oak_ram_available_mss`: FLOAT (OAK RAM available CMX)
- `oak_ram_usage_cmx`: FLOAT (OAK RAM usage CMX)
- `oak_ram_available_cmx`: FLOAT (OAK RAM available CMX)
- `power_input`: STRING (Source of power input)
- `charge_level`: INTEGER (Battery charge level)
- `voltage_in_V`: FLOAT (Input voltage)
- `voltage_out_V`: FLOAT (Output voltage)
- `current_out_A`: FLOAT (Output current)
- `temp_wittypi`: FLOAT (Wittypi temperature)

### Configuration
This table represents the camera and deployment configuration for a specific session.
- `config_id`: STRING (Primary Key, Derived from `session_id` in the raw data filename)
- `session_id`: STRING (Foreign Key to SessionInfo)
- `deployment`: JSON OBJECT (Deployment settings, including location, notes, etc.)
- `camera`: JSON OBJECT (Camera settings like fps, resolution, focus, isp)
- `detection`: JSON OBJECT (Detection model and thresholds)
- `recording`: JSON OBJECT (Recording duration and interval settings)
- `processing`: JSON OBJECT (Image processing settings like cropping)
- `webapp`: JSON OBJECT (Web application streaming settings)
- `network`: JSON OBJECT (Network connectivity settings)
- `powermanager`: JSON OBJECT (Power management parameters)
- `oak`: JSON OBJECT (OAK specific hardware settings)
- `led`: JSON OBJECT (LED light control settings)
- `metrics`: JSON OBJECT (Metrics collection configuration)
- `storage`: JSON OBJECT (Storage management and archiving)
- `startup`: JSON OBJECT (Device startup behaviors)

## Relationships

- **Device to SessionInfo:**
    - One `Device` has many `SessionInfo` records.
    - Relationship: `Device.device_id` (PK) -> `SessionInfo.device_id` (FK)

- **SessionInfo to Detection:**
    - One `SessionInfo` record can have many `Detection` records.
    - Relationship: `SessionInfo.device_id`, `SessionInfo.session_id` (PKs) -> `Detection.device_id`, `Detection.session_id` (FKs)

- **SessionInfo to SystemLog:**
    - One `SessionInfo` record can have many `SystemLog` entries.
    - Relationship: `SessionInfo.device_id`, `SessionInfo.session_id` (PKs) -> `SystemLog.device_id`, `SystemLog.session_id` (FKs)

- **SessionInfo to Configuration:**
    - One `SessionInfo` record uses one `Configuration` (assuming config is per session).
    - Relationship: `SessionInfo.session_id` (PK) -> `Configuration.session_id` (FK)
