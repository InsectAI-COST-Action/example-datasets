<!-- Image: raw/data/2026-04-16/2026-04-16_18-38-26/insdet-cam01_2026-04-16_18-38-41-142032.jpg -->
# Insect Detect dataset

This is an example dataset, captured with the [Insect Detect](https://maxsitt.github.io/insect-detect-docs/)
camera trap.

The `raw` directory contains full-frame images at 4K resolution (3840x2160)
together with associated metadata and cropped detections, a config file snapshot and log files.
Data was captured with the
[`capture.py`](https://github.com/maxsitt/insect-detect/blob/main/src/insectdetect/capture.py)
script under artificial lab conditions with a 1 minute recording session duration.

The `post-processed` directory contains the classified and post-processed metadata.
The `*_top1_final.csv` file contains the metadata that could be used for further
downstream analyses where each row corresponds to a tracked individual.

## Folder Conversion:

Mapping tables for the Camtrap-DP templates

Two approaches: 

1) mapped every single field in the standard to the data
2) used Gemini to do an automatic mapping (mapping_plan.md)

## Suggestions

Limiting attractantType to lure, light, and sound feels restrictive. Insect Detect uses a coloured platform to 
attract pollinators, which doesn't seem to fit in these three categories. Similar attactants, such as artifical
flowers, would likely also have the same problem. We haven't settled on a word that would encompass these
attractants, but even something like an "other" category could allow this term to be more inclusive while still
providing standardized names for the most common attractant types.

