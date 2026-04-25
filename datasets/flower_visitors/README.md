<!-- Image: media/raw/2021-08-11_Achillea-millefolium-bs-01_IMG_20210811_114248.jpg -->

# "flower_visitors" mini-dataset

<img src="media/raw/2021-08-11_Achillea-millefolium-bs-01_IMG_20210811_114248.jpg" alt="flower_visitors example image" width="300"/>

This is a small subset of original dataset from https://doi.org/10.5281/zenodo.15096610

This folder contains the code to convert the "flower_visitors" mini-dataset from its original data format to the [Camtrap DP standard](https://camtrap-dp.tdwg.org/).

## Folders & files layout

Sampled images & annotation files:
  - `media/raw/`                       full-frame smartphone images
  - `media/cropped/`                   ROI-cropped images around the target flower (ROI = Region of Interest: target flower / part of inflorescence)
  - `media/backgrounds/`               frames without flower visitors (negative images)
  - `raw-data/annotations_subset.tsv`  subset of annotations_full_frames.txt

Code:
  - `code/data_conversion.py`          Python code used for data conversion
  - `code/requirements.txt`            list of Python libraries needed in the Python environment for `code/data_conversion.py`

Generated files with the code:
  - `observations.csv`
  - `media.csv`
  - `deployments.csv`

## mini-dataset scope

- Sampled plants:
  - Trifolium pratense
  - Daucus carota
  - Achillea millefolium
- Full-frame images: 25
- Cropped ROI images: 25
- Background images (negatives without flower visitors): 5
- Bounding boxes (detections): 25
- Individual insect sequences: 9

## Taxonomic order counts

```
order
hymenoptera    12
diptera        10
araneae         3
```

## Deepest populated taxonomic rank per instance (bounding box)

```
deepest_rank
order            3
family           6
clustergenera    3
genus            4
morphospecies    3
species          6
```

## What this subset is designed to stress-test

- Mixed taxonomic rank. Bees (Hymenoptera) and flies (Diptera) are identified to the finest rank possible; other orders to order only.
- Sequence structure. `seq_id` groups multiple frames of the same individual, so the "what counts as an event" question from CameraDP standards needs to be doubled check on how it applies here. A bounding box within an image is an "isntance" of that individual insect.
- Confidence levels. Columns `conf_order`, `conf_family`, `conf_species`, etc. record human annotator confidence.
- Multi-insect frames. At least one frame has `n_boxes >= 2` (2 arthopod instances)
- Multiple deployments. 3 `plant_folders` on different plant species.

## Original dataset

Ştefan, V., Workman, A., Cobain, J. C., Rakosy, D., Wild Stoykova, B., Cyranka, E., Urrego Álvarez, R., & Knight, T. (2025). Dataset of arthropod flower visits captured via smartphone time-lapse photography [Data set]. Zenodo. https://doi.org/10.5281/zenodo.15096610

Licence: CC BY-NC-SA 4.0, with commercial AI training use reserved by the copyright holder (see the Zenodo record for full terms).

## InsectAI Camtrap DP suggestions

### 1. Add `flower` to the `featureType` enum (or introduce `targetSpecies`)

[featureType](https://camtrap-dp.tdwg.org/data/#deployments.featureType) currently lists only mammal-focused feature classes. Plant-pollinator and flower-visitor datasets are a real and growing use case (time-lapse smartphones on target flowers, inflorescences or flowering patches). I suggest adding `flower`, `inflorescence`, or `bloomingPlant`.

A cleaner alternative is a new optional field `targetSpecies` (scientificName of what the camera was *aimed at*, distinct from what was *captured*). For this dataset that would be e.g. `targetSpecies = "Trifolium pratense"` per deployment.

Also, for plant-pollinator datasets the target plant's taxonomy is first-class deployment metadata, not just habitat.Perhaps adding structured optional deployment fields can add clarity: `targetPlantScientificName`, `targetPlantGenus`, `targetPlantEpithet`, `targetPlantFamily`.

### 2. Per-rank taxonomic uncertainty

The hierarchical taxonomy (human identifications) in this dataset carries a confidence *per rank* (`conf_order: high`, `conf_family: medium`, `conf_genus: low`), reflecting how ID confidence drops as you go finer. Camtrap DP has a single `classificationProbability` for the whole classification.

Proposed: a repeatable `taxonomicAssertion` structure (or a `taxonomicUncertainty` JSON column) with `rank`, `name`, `confidence` per entry. For example, ordinal labels (`high`/`medium`/`low`) could be valid alongside numeric probabilities, with the schema stating which convention is used. This can be useful for trust-weighted ecology analyses and also for training ML pipelines.

### 3. Formalise informal ranks (`morphospecies`, `clustergenera`)

Custom level taxonomic ranks could be considered as well (e.g. morphospecies, cluster-genera) when the specimen cannot be identified to a Linnean rank. Camtrap DP currently forces these into free-text or tags. A schema addition example:

- `morphospeciesName`: a dataset-local label (e.g. `red_yellow`).
- `clusterGeneraNames`: list of candidate genera (e.g. `[Syritta, Tropidia]`).

and they can sit *beside* `scientificName` (which should stay at the finest resolvable Linnean rank for GBIF compatibility). This would let both pipelines (GBIF-matching and full-resolution ecology) consume the same data file without losing information.

### 4. `individualID` vs `eventID`

The spec does not clearly state the relationship when a dataset tracks an individual *within* a deployment but cannot re-identify it. Many insect individuals will not be able to be re-identified, unless specifically marked.

### 5. Blank observations (for "negative" images - images without insects): `count = 0` should be valid

`count ≥ 1` for blanks forces the unintuitive "leave `count` empty" convention. Allowing `count = 0` (explicitly) on `observationType = "blank"` rows would be much less surprising, and distinguishes "we checked, nothing was there" from "we did not record".

### 6. CV-training extras

For computer-vision consumers, two optional properties / ideas:

- `mediaChecksum` (sha256 of the image bytes) at the media level lets downstream training sets detect duplicates and silently-modified files.
- `annotationPass` or some info on label quality at the observation level so training pipelines can filter on label quality without extra text parsing.
