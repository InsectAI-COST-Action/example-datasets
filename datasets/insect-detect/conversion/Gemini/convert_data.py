import pandas as pd
import os

def convert_media_data(source_csv_path, output_csv_path, base_image_path):
    # Read the source metadata CSV
    source_df = pd.read_csv(source_csv_path)

    # Prepare a list to hold the new media records
    media_records = []

    # Iterate through each row in the source dataframe to create media records
    for index, row in source_df.iterrows():
        media_id = f"{row['device_id']}_{row['session_id']}_{row['timestamp']}".replace(":", "_").replace(".", "_")
        deployment_id = f"{row['device_id']}_{row['session_id']}"
        file_path = os.path.join(base_image_path, row["filename"])

        media_record = {
            "mediaID": media_id,
            "deploymentID": deployment_id,
            "captureMethod": "activityDetection",
            "timestamp": row["timestamp"],
            "filePath": file_path,
            "filePublic": "FALSE",
            "fileName": row["filename"],
            "fileMediatype": "image/jpeg",
            "exifData": "",
            "favorite": "",
            "mediaComments": "",
            "observationTags": "",
            "observationComments": ""
        }
        media_records.append(media_record)

    # Create a new DataFrame from the processed records
    media_df = pd.DataFrame(media_records)

    # Define the columns in the exact order as per media_template.csv for output
    # Assuming the template columns are: mediaID,deploymentID,captureMethod,timestamp,filePath,filePublic,fileName,fileMediatype,exifData,favorite,mediaComments,observationTags,observationComments
    output_columns = [
        "mediaID", "deploymentID", "captureMethod", "timestamp",
        "filePath", "filePublic", "fileName", "fileMediatype",
        "exifData", "favorite", "mediaComments", "observationTags",
        "observationComments"
    ]
    media_df = media_df[output_columns]

    # Write the new DataFrame to a CSV file
    media_df.to_csv(output_csv_path, index=False, quotechar='"', quoting=1)

    print(f"Converted media data written to {output_csv_path}")

if __name__ == "__main__":
    source_csv_file = "datasets/insect-detect/raw/data/2026-04-16/2026-04-16_18-38-26/2026-04-16_18-38-26_metadata.csv"
    output_csv_file = "datasets/insect-detect/conversion/Gemini/media.csv"
    base_image_directory = "2026-04-16/2026-04-16_18-38-26/"

    convert_media_data(source_csv_file, output_csv_file, base_image_directory)
