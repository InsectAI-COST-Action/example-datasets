<!-- Image: media/Lepmon#SN010030_TH_J_2025-07-03_T_0308.jpg -->
# Sample dataset fromt the lepmon project

<img src="media/Lepmon#SN010030_TH_J_2025-07-02_T_2330.jpg" alt="RangeX example image" width="300"/>

## Media folder contents
The folder `media` contains the raw data as they are uploaded from the camera: one run from one nights moth observation. Here: July 2nd 2025 between 9:04 pm till 5:34 am next day.

### Files:
 - *.jpg: raw images from the camera device
 - Lepmon#SN010030_TH_J_2025-07-02_T_2102.csv: metadata about each image, including abiotic sensoric and trechnical measurements
 - Lepmon#SN010030_TH_J_2025-07-02_T_2102.log: lofgile of the run
 - Lepmon#SN010030_TH_J_2025-07-02_T_2102_Kameraeinstellungen: Camera settings


- There are three images available in full resolution
	- Lepmon#SN010030_TH_J_2025-07-03_T_0322.jpg
	- Lepmon#SN010030_TH_J_2025-07-02_T_2306.jpg
	- Lepmon#SN010030_TH_J_2025-07-03_T_0116.jpg


## Data folder contents

Alle files for the different tables in json and csv format:
- meatadata
- deployment
- media
- detections
- model

## Open questions

- Link to bbox url if present missing?
- What about measurement values taken with each image, e.g. temperature, light conditions, etc.? 
- Methods for capturing, processing?


## Camtrap DP suggestions
- scientific name - determination only to family/genus level?
- individual ID might be only unique within input dataset - how to make it unique globally

- training data (manually anotated) should include information on the species catalogue used by experts for detemination. Some species, escpecially hard to determine ones, allways have these physical labels in the physical collections. This makes it easy to keep track, when species are lumbed together (synonyms) or split later one


## lepmon webpage
[https://lepmon.de/en/lepmon-en/](https://lepmon.de/en/lepmon-en/)