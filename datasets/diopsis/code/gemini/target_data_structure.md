erDiagram
    DEPLOYMENTS ||--o{ MEDIA : has
    DEPLOYMENTS ||--o{ OBSERVATIONS : has
    MEDIA ||--o{ OBSERVATIONS : has_many

    DEPLOYMENTS {
        string deployment_id PK
        string location_id
        string latitude
        string longitude
        string deployment_start_date
        string deployment_end_date
        string camera_id
        string camera_model
        string camera_setup_notes
        string bait_type
        string bait_description
        string feature_type
        string feature_type_method
        string habitat
        string operational_status
        string event_geographic_locality
        string event_id
        string recorder
        string sensor_method
        string data_license
        string rights_holder
        string bibliographic_citation
        string dataset_id
    }

    MEDIA {
        string media_id PK
        string deployment_id FK
        string sequence_id
        string capture_method
        string timestamp
        string file_name
        string file_size
        string file_extension
        string mime_type
        string width
        string height
        string relative_path
        string focal_length
        string individual_id
        string video_start_timestamp
        string video_end_timestamp
        string video_url
        string gps_coordinates
        string camera_angle
        string animal_maturity
        string sex
        string life_stage
        string behavior
        string individual_position
        string object_position_x
        string object_position_y
        string object_width
        string object_height
    }

    OBSERVATIONS {
        string observation_id PK
        string deployment_id FK
        string media_id FK
        string event_id
        string event_type
        string event_start
        string event_end
        string individual_id
        string individual_count
        string age
        string sex
        string life_stage
        string behavior
        string organism_id
        string scientific_name
        string vernacular_name
        string taxon_id
        string class
        string order
        string family
        string genus
        string specific_epithet
        string infraspecific_epithet
        string identification_references
        string identification_remarks
        string identified_by
        string detection_id
        string bbox_x
        string bbox_y
        string bbox_width
        string bbox_height
        string observation_type
        string remarks
    }