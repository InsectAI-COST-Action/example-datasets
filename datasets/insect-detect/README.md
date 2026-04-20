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
