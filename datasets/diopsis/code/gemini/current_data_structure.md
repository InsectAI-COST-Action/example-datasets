erDiagram
    DATA_INFILTRATIE ||--o{ MEDIA : has
    MEDIA ||--o{ DETECTION : has
    DETECTION ||--o{ INDIVIDUAL : has

    DATA_INFILTRATIE {
        string sensor_name PK
        string deployment_name
        datetime capture_on
        string media_id FK
        string resolution
        string name
        float probability
        float body_length_mm
        float biomass_mg
        float x1
        float x2
        float y1
        float y2
        string individual_id FK
        string individual_taxon_name
        float individual_taxon_probability
    }

    IMAGE_ID_TO_FILE_MAPPING {
        string image_id PK, FK
        string image_file
    }

    MEDIA {
        string media_id PK
        string image_file
        datetime capture_on
        string resolution
    }

    DETECTION {
        string media_id FK
        string name
        float probability
        float body_length_mm
        float biomass_mg
        float x1
        float x2
        float y1
        float y2
        string individual_id FK
    }

    INDIVIDUAL {
        string individual_id PK
        string individual_taxon_name
        float individual_taxon_probability
    }