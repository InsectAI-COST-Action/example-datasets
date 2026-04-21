<!-- Image: media/5mp_300521_10_18_30_696493.jpg -->

# Plant-pollinator interactions — Balearic Islands

<img src="media/5mp_300521_10_18_30_696493.jpg" alt="Plant-pollinator interactions example image" width="300"/>

Dataset of pollinators visiting flowers, Mediterranean field sites.

Work in progress — InsectAI WG3 Datathon, Niš 2026.

This dataset contains images of pollinators visiting flowers, collected as part of a citizen science project in the Balearic Islands (Mediterranean ecosystem, Spain). Images were captured using personal cameras (smartphones and compact cameras) during active pollination events in natural field conditions.

The dataset includes:
- Images annotated in Pascal VOC XML format
- Pollinators identified to species level where possible, otherwise to genus or functional group
- Multiple Mediterranean plant species as background
- Natural heterogeneous field conditions

Taxonomic resolution is mixed: some individuals are identified to species (e.g. Apis mellifera, Vanessa cardui), others to genus (e.g. Eucera, Osmia), and others only to functional group (e.g. Bee, Fly, Beetle, Butterfly).

For a full class distribution and image size breakdown, see dataset_summary.csv


Dataset prepared for the InsectAI WG3 Datathon, Nis 2026.

Data controller: Pau Enric Serra Marin (pau.enric.serra@gmail.com)

Data wranglers: Wouter Koch, Fez Hasan


## Camtrap DP suggestions
- Dealing with non-standardized scientific names: we consider resolving/mapping, but is ideally left to the dataset owner
- Should crop and classification always be separate steps? (Linked through sourceDetectionId)