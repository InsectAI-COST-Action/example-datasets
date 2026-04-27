<!-- Image: https://object-arbutus.cloud.computecanada.ca/ami-trapdata/newfoundland/Unit-1/2024%20Snapshots/2024%20Ami%20Images-%20Unit%201%20Pasadena/01-20240709024649-snapshot.jpg -->

# Antenna dataset

This is a small subset of data from the project "NRCAN Moth Surveillance Solutions" on [Antenna](https://www.insectai.org/). This project is monitoring forest species in Canada, for example Choristoneura fumiferana, which is considered one of the most destructive forest pests in North America.

![Example capture](https://object-arbutus.cloud.computecanada.ca/ami-trapdata/newfoundland/Unit-1/2024%20Snapshots/2024%20Ami%20Images-%20Unit%201%20Pasadena/01-20240709024649-snapshot.jpg)

The dataset includes 476 occurrences\* from 12 captures. Multiple sites, stations and years are represented in the dataset. The occurrence labels are derived from a combination of machine predictions and human identifications. For the machine predictions, the pipeline "Québec & Vermont moths" was used for processing. This pipeline uses multiple algorithms (one for object detection, one for binary classification and one for fine-grained classification).

_\* On Antenna, an occurrence refers to when an individual is detected in a sequence of one or more captures with no time interruption._

## Raw data

The folder [`raw-data`](./raw-data) includes 2 files:

- [`occurrences.csv`](./raw-data/occurrences.csv) (298 KB) is a minimal dataset export from Antenna including selected fields for occurrences
- [`occurrences.json`](./raw-data/occurrences.json) (6.4 MB) is a full dataset export from Antenna including all raw data nested for occurrences
- [`occurrences_preprocessed.csv`](./raw-data/occurrences_preprocessed.csv) (372 KB) is the minimal export extended and preprocessed to better fit Camtrap DP

Related media is hosted and can be accessed from URLs included in exports.

## Workshop process

### Step 1: Define mapping

During the workshop, we started by creating a mapping table. For each field in [`raw-data/occurrences.csv`](./raw-data/occurrences.csv), we tried to map it to a Camtrap DP file and field. We also made notes about any preprocessing needed. After this, we had a look at the required fields in Camtrap DP, to see where the Antenna export might need extensions. This resulted in [`code/mapping.csv`](./code/mapping.csv).

### Step 2: Extend and preprocess data

As the next step, we extended the Antenna export with the missing required fields. Good news was that the missing required data was stored and available, just not exposed in the minimal export. We also did some preprocessing of the data (timestamp conversions, etc.). This resulted in [`raw-data/occurrences_preprocessed.csv`](./raw-data/occurrences_preprocessed.csv). For this step, we used Claude.

### Step 3: Generate files for Camtrap DP

Time to generate files for Camtrap DP! Based on the preprocessed data, we first defined an updated mapping. This resulted in [`code/mapping_preprocessed.csv`](./code/mapping_preprocessed.csv). From this, we could now generate files `deployments.csv`, `media.csv` and `observations.csv`. We also generated `datapackage.json` from a template. For this step, we used Claude.

### Step 4: Validate

We used [Frictionless](https://frictionlessdata.io/) for validation. This was very helpful and we could quickly identify gaps. From the repo root, we run:

```
uvx frictionless validate datasets/antenna/datapackage.json
```

## Reflections

For the mapping, the trickiest part was to figure out how to deal with events and tracks. We went a bit back and forth here. On Antenna, we define an event as "a fixed period of time of monitoring for one station", however for Camtrap DP, the event definition is more narrow. It was suggested to use events to represent a track, which first surprised us. In the suggested mapping table we can therefore see that `first_appearance_timestamp` and `last_appearance_timestamp` are mapped to `eventStart` and `eventEnd`.

We also discussed how to define a deployment. It was suggested that a deployment could be defined as "a fixed period of time of monitoring for one station" (what we call an event on Antenna, typically one night of monitoring). To represent "a location where a device is deployed" (what we call a deployment on Antenna), we could use Camtrap DP `deploymentGroups`. However, to keep the structure simple and to avoid repeating device information in the deployments table, we ended up ignoring the Antenna events.

### Take aways

- Antenna tracks = Camtrap DP events!
- Media-based observations should be used for observations that are directly associated with one media file
- For datasets where we only want to include the best detection for each occurrence, we should use media-based observations
- For datasets where we want to include all detections for each occurrence, we should use media-based observations for the detections combined with event-based observations for the occurrences
- To link media-based and event-based observations, we should use the field `eventID`

### Camtrap DP suggestions

The main gap we noticed during the mapping is that we are currently missing a way to include information about machine predictions and human identifications (see [`code/mapping.csv`](./code/mapping.csv)). To summarize, we would like to include the following information:

- Details about algorithms involved
- The output from the algorithms involved
- Details about humans involved
- The output from humans involved

The goal would be to capture the full identification history for each observation to make it possible to tell what lead up to the final determination. We would like it to be possible for each observation to have multiple machine predictions and human identifications associated. For the single observation, it would be nice if we could include more details about the final determination, for example if verified by a human or not, without having to derive this from other tables.

## Next steps

On the Antenna side, we should extend the minimal export to include all the required information for Camtrap DP. It would simplify the process not having to go fetch missing information from different API endpoints.

To generate files for Camtrap DP, we would also like to try use Frictionless instead of Claude, to ensure a consistent output.

Lastly, once Camtrap DP has more complete support for automated insect monitoring, we would like to add this as an export option on Antenna. For this workshop, we focused on the required Camtrap DP fields, but we also have more information that could be included. Later on, we would also like to support importing data that follows this standard.
