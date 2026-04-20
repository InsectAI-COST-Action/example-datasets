<!-- Image: raw-data/20250613022959-snapshot.jpg -->
# Invasive Alien Species (IAS) dataset 
TODO

## Setup
The [code](./code) folder contains two scripts:

1. **[prepare.ipynb](./code/prepare.ipynb):** Collects data directly from Zenodo and constructs a smaller example dataset.
2. **[main.ipynb](./code/main.ipynb):** Demonstrates how to compile the example dataset to be InsectAI-CamtrapDP compliant.

Importantly, [main.ipynb](./code/main.ipynb) relies on the example dataset being stored in [data](./data), which can be reconstructed by running [prepare.ipynb](./code/prepare.ipynb). To facilitate a more transportable example, the results of [prepare.ipynb](./code/prepare.ipynb) will be committed to the git tree, such that the example compilation via [main.ipynb](./code/main.ipynb) can be run immediately after cloning this repository.