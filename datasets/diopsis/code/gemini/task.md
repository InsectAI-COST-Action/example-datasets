I am working on the dataset in datasets/diopsis. I need to convert the raw dataset in subfolder raw-data/*.csv (2 files) to a CamtrapDP dataset in subfolder camtrap-data (3 files). The target format is described in detail on these pages:
- deployments.csv: https://camtrap-dp.tdwg.org/data/#deployments 
- media.csv: https://camtrap-dp.tdwg.org/data/#media 
- observations.csv: https://camtrap-dp.tdwg.org/data/#observations 
Read these before you start the conversion. 

We need to fill in all the required fields of the 3 target files: deployments.csv, media.csv and observations.csv

You can use this folder to store your results: datasets/diopsis/gemini

First let's make subtasks: 
1. make a mermaid diagram of the data structure for the current situation
2. make a mermaid diagram of the data structure for the target situation. Main entities are: media_id, detection_id and observation_id. Session_id is probably needed to combine time-consecutive media items into a temporal session
3. Make a proposal to map the data fields from the current to the target structure and store the mapping in subfolder gemini/mapping.md. 

Add remarks to the mapping when
1. there are target fields that are required according to the info on the website, but cannot be filled
2. there is information in the raw data that you cannot place in the target data
3. there are groupings or conversions needed. Mention how you will do the modification. Highlight issues that you are not 95% sure about.

After that, let me review the mapping and answer the questions that you have.

==============================
I have completed the initial tasks:

1.  **Current Data Structure Diagram**: I've created a Mermaid diagram illustrating the current data structure based on the raw CSV files. You can find it at [`datasets/diopsis/gemini/current_data_structure.md`](datasets/diopsis/gemini/current_data_structure.md).
2.  **Target Data Structure Diagram**: I've created a Mermaid diagram for the target CamtrapDP data structure (deployments, media, observations) based on the provided documentation. This is available at [`datasets/diopsis/gemini/target_data_structure.md`](datasets/diopsis/gemini/target_data_structure.md).
3.  **Data Field Mapping Proposal**: I've prepared a detailed mapping proposal from the raw data fields to the CamtrapDP fields, including remarks for missing fields, unplaceable information, and necessary groupings/conversions. This document is located at [`datasets/diopsis/gemini/mapping.md`](datasets/diopsis/gemini/mapping.md).

Please review these documents, especially the mapping proposal in [`datasets/diopsis/gemini/mapping.md`](datasets/diopsis/gemini/mapping.md), and provide your feedback and answers to the questions raised in the remarks.
==============================
You need to revise the mapping in mapping.md. You added fields to the list, but the only fields required in the camtrap csv's are the ones in the  headers of the target files (see folder camptrap-data: deployments.csv, media.csv and observations.csv). Remove the fields that are not in these headers
==============================
I have revised the mapping proposal in [`datasets/diopsis/gemini/mapping.md`](datasets/diopsis/gemini/mapping.md) to include only the fields present in the headers of your target CamtrapDP files. I also incorporated your feedback regarding `locationID`.

Please review the updated mapping and provide your feedback on the remaining questions highlighted as remarks, particularly regarding `sequence_id`, the handling of "No detections found" rows in `observations.csv`, and the suitability of `individual_id` as a persistent `individualID`.
==============================
THese are my answers. Can you update the mapping.md ? 

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
==============================
I have updated the mapping proposal in [`datasets/diopsis/gemini/mapping.md`](datasets/diopsis/gemini/mapping.md) with all your feedback and clarifications. All specific instructions for fields like `captureMethod`, `fileMediatype`, `eventEnd` logic, `observationType` criteria, `scientificName` filtering, `individualID` usage, `classificationMethod`, `classifiedBy`, `classificationTimestamp`, `classificationProbability`, and `observationComments` have been incorporated. The handling of "No detections found" rows has also been updated.

This revised mapping document is now ready for your final review before proceeding with the data conversion.
==============================
Now continue with the data conversion. Write a python script to do the conversion. I want to reveiw the script before it is executed. Keep asking questions until you are >95% sure what to do. 
One remark about the image filenames: the original filenames contained colons, but these were replaces with hyphens. The lookup table (raw-data/image_id_to_file_mapping.csv) still contains filenames without the modification. The names with the hyphens are leading.
==============================

I have developed the Python script `datasets/diopsis/gemini/convert_diopsis.py` to convert the raw Diopsis dataset to CamtrapDP format, incorporating all the mapping rules and feedback discussed. The script handles data loading, preprocessing (including filename normalization), and the generation of `deployments.csv`, `media.csv`, and `observations.csv`.

Please review the script at [`datasets/diopsis/gemini/convert_diopsis.py`](datasets/diopsis/gemini/convert_diopsis.py) and let me know if you have any questions or require further modifications before execution.