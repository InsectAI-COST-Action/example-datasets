# Antenna dataset

This is a small subset of data from the project "NRCAN Moth Surveillance Solutions" on [Antenna](https://www.insectai.org/). This project is monitoring forest species in Canada, for example Choristoneura fumiferana, which is considered one of the most destructive forest pests in North America.

![Example capture](https://object-arbutus.cloud.computecanada.ca/ami-trapdata/newfoundland/Unit-1/2024%20Snapshots/2024%20Ami%20Images-%20Unit%201%20Pasadena/01-20240709024649-snapshot.jpg)

The dataset includes 476 occurrences\* from 12 captures. Multiple sites, stations and years are represented in the dataset. The occurrence labels are derived from a combination of machine predictions and human identifications. For the machine predictions, the pipeline "Québec & Vermont moths" was used for processing. This pipeline uses multiple algorithms (one for object detection, one for binary classification and one for fine grained classification).

_\* On Antenna, an occurrence refers to when an individual is detected in a sequence of one or more captures with no time interruption._

## Raw data

The folder [`raw-data`](./raw-data) includes 2 files:

- [`occurrences.csv`](./raw-data/occurrences.csv) (298 KB) is a compact format including selected fields for occurrences
- [`occurrences.json`](./raw-data/occurrences.json) (6,4 MB) includes all raw data nested for occurrences

Related media is hosted and can be accessed from URLs included in exports.
