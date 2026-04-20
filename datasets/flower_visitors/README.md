# Flower visitors minidataset

Subset of dataset from https://doi.org/10.5281/zenodo.15096610

See more details in that readme file on the Zenodo repository about data and metadata.

## File layout

- `raw/`                       full-frame smartphone images
- `cropped/`                   ROI-cropped images around the target flower (ROI: target flower / part of inflorescence)
- `backgrounds/`               frames without flower visitors (negative images)
- `annotations_subset.tsv`     subset of annotations_full_frames.txt

## Scope

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
