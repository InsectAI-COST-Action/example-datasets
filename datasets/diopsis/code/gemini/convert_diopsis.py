#!/usr/bin/env python3

import pandas as pd
import uuid
from datetime import datetime
import os

# --- Configuration --- 
RAW_DATA_DIR = "./datasets/diopsis/raw-data"
OUTPUT_DIR = "./datasets/diopsis/code/gemini/camtrap-data"

DATA_INFILTRATIE_PATH = os.path.join(RAW_DATA_DIR, "data_infiltratie_c231_2025.csv")
IMAGE_MAPPING_PATH = os.path.join(RAW_DATA_DIR, "image_id_to_file_mapping.csv")

DEPLOYMENTS_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "deployments.csv")
MEDIA_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "media.csv")
OBSERVATIONS_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "observations.csv")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_raw_data():
    """Loads the raw data files."""
    df_data = pd.read_csv(DATA_INFILTRATIE_PATH)
    df_image_map = pd.read_csv(IMAGE_MAPPING_PATH)
    return df_data, df_image_map

def preprocess_data(df_data, df_image_map):
    """Performs initial data cleaning and pre-processing."""
    # Handle filename discrepancy (colons to hyphens)
    # The image_id_to_file_mapping.csv contains original filenames with colons
    # The actual filenames have hyphens.
    # We need to standardize the 'image_file' in df_image_map to have hyphens.
    df_image_map['image_file_cleaned'] = df_image_map['image_file'].str.replace(':', '-')

    # Merge the dataframes to get image file paths
    df_merged = pd.merge(df_data, df_image_map, left_on='media_id', right_on='image_id', how='left')

    # Convert capture_on to datetime objects
    df_merged['capture_on'] = pd.to_datetime(df_merged['capture_on'])

    return df_merged

def generate_deployments(df_merged):
    """Generates the deployments.csv content."""
    deployments = []
    # Group by sensor_name and deployment_name to get unique deployments
    for (sensor_name, deployment_name), group in df_merged.groupby(['sensor_name', 'deployment_name']):
        deployment_id = f"{sensor_name}_{deployment_name.replace(' ', '_')}"
        deployment_start = group['capture_on'].min().isoformat()
        deployment_end = group['capture_on'].max().isoformat()

        deployments.append({
            'deploymentID': deployment_id,
            'locationID': deployment_name, # Confirmed unique by user
            'locationName': deployment_name,
            'latitude': None, # To be determined by user
            'longitude': None, # To be determined by user
            'deploymentStart': deployment_start,
            'deploymentEnd': deployment_end,
            'cameraID': sensor_name,
            'cameraModel': None,
            'baitUse': None,
            'featureType': None,
            'habitat': None,
            'deploymentComments': None
        })
    return pd.DataFrame(deployments)

def generate_media(df_merged):
    """Generates the media.csv content."""
    media_items = []
    # Each unique media_id is a media item
    # Filter for unique media_id entries to avoid duplicates
    df_unique_media = df_merged[['media_id', 'sensor_name', 'deployment_name', 'capture_on', 'resolution', 'image_file_cleaned']].drop_duplicates(subset=['media_id'])

    for index, row in df_unique_media.iterrows():
        deployment_id = f"{row['sensor_name']}_{row['deployment_name'].replace(' ', '_')}"
        file_name = row['image_file_cleaned']
        file_extension = os.path.splitext(file_name)[1].lstrip('.') # Remove leading dot
        
        width, height = None, None
        if pd.notna(row['resolution']) and 'x' in row['resolution']:
            try:
                res_parts = row['resolution'].split('x')
                width = int(res_parts[0])
                height = int(res_parts[1])
            except ValueError: # Handle cases where resolution might not be perfectly parsable
                pass

        media_items.append({
            'mediaID': row['media_id'],
            'deploymentID': deployment_id,
            'captureMethod': 'activityDetection',
            'timestamp': row['capture_on'].isoformat(),
            'filePath': f"camtrap-data/images/{file_name}", # Relative path
            'fileName': file_name,
            'fileMediatype': 'image/jpeg',
            'mediaComments': None
        })
    return pd.DataFrame(media_items)

def generate_observations(df_merged):
    """Generates the observations.csv content."""
    observations = []

    # Filter out rows with "No detections found" or "Too small to detect" for scientificName
    df_detections = df_merged[
        (df_merged['name'] != 'No detections found for this media item') & 
        (df_merged['name'] != 'Too small to detect')
    ].copy() # Use .copy() to avoid SettingWithCopyWarning

    for index, row in df_detections.iterrows():
        # Generate observationID
        observation_id = str(uuid.uuid4())
        deployment_id = f"{row['sensor_name']}_{row['deployment_name'].replace(' ', '_')}"

        # Determine scientificName
        scientific_name = row['individual_taxon_name'] if pd.notna(row['individual_taxon_name']) else row['name']

        # Determine observationType
        observation_type = 'unknown'
        if pd.notna(row['probability']) and row['probability'] >= 0.5 and row['name'] != 'Too small for identification':
            observation_type = 'animal'

        # Determine eventEnd logic
        # User wants eventEnd to be captureOn of the last media item if grouped by individual_id
        # Since we are iterating row by row (each row is essentially a detection/observation)
        # and not explicitly grouping media items into sequences within this function,
        # for now, eventStart and eventEnd will be the same capture_on.
        # A more complex grouping logic for eventEnd would be implemented if 'sequence_id' was defined.
        # For now, default to capture_on for both.
        event_start = row['capture_on'].isoformat()
        event_end = row['capture_on'].isoformat() # Default, will be updated if individual_id grouping is implemented

        # Prepare observationComments
        observation_comments = []
        if pd.notna(row['body_length_mm']):
            observation_comments.append(f"{{body_length_mm: {row['body_length_mm']}}}")
        if pd.notna(row['biomass_mg']):
            observation_comments.append(f"{{biomass_mg: {row['biomass_mg']}}}")
        
        # Bounding box coordinates
        bbox_x, bbox_y, bbox_width, bbox_height = None, None, None, None
        if pd.notna(row['x1']) and pd.notna(row['x2']) and pd.notna(row['y1']) and pd.notna(row['y2']):
            bbox_x = row['x1']
            bbox_y = row['y1']
            bbox_width = row['x2'] - row['x1']
            bbox_height = row['y2'] - row['y1']

        observations.append({
            'observationID': observation_id,
            'deploymentID': deployment_id,
            'mediaID': row['media_id'],
            'eventID': None, # No clear mapping, left empty
            'eventStart': event_start,
            'eventEnd': event_end, # See remark above
            'observationLevel': 'detection', # Default, could be 'individual' if individual_id is truly persistent
            'observationType': observation_type,
            'scientificName': scientific_name,
            'count': 1, # Each detection is a count of 1
            'lifeStage': None,
            'sex': None,
            'behavior': None,
            'individualID': row['individual_id'] if pd.notna(row['individual_id']) else None, # User confirmed using this
            'bboxX': bbox_x,
            'bboxY': bbox_y,
            'bboxWidth': bbox_width,
            'bboxHeight': bbox_height,
            'classificationMethod': 'machine',
            'classifiedBy': 'Diopsis 2025',
            'classificationTimestamp': None, # User requested to leave empty
            'classificationProbability': row['probability'] if pd.notna(row['probability']) else None,
            'observationComments': ', '.join(observation_comments) if observation_comments else None
        })
    return pd.DataFrame(observations)

def main():
    print("Loading raw data...")
    df_data, df_image_map = load_raw_data()

    print("Preprocessing data...")
    df_merged = preprocess_data(df_data, df_image_map)

    print("Generating deployments.csv...")
    df_deployments = generate_deployments(df_merged)
    df_deployments.to_csv(DEPLOYMENTS_OUTPUT_PATH, index=False)
    print(f"deployments.csv saved to {DEPLOYMENTS_OUTPUT_PATH}")

    print("Generating media.csv...")
    df_media = generate_media(df_merged)
    df_media.to_csv(MEDIA_OUTPUT_PATH, index=False)
    print(f"media.csv saved to {MEDIA_OUTPUT_PATH}")

    print("Generating observations.csv...")
    df_observations = generate_observations(df_merged)
    df_observations.to_csv(OBSERVATIONS_OUTPUT_PATH, index=False)
    print(f"observations.csv saved to {OBSERVATIONS_OUTPUT_PATH}")

    print("Conversion complete!")

if __name__ == "__main__":
    main()
