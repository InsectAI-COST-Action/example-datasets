# flatbug dataset (COCO format)
This is a subset of the [`flatbug` dataset](https://doi.org/10.5281/zenodo.14761447), which is a standardized insection detection and segmentation meta-dataset, compiled from 23 different sources. 

In this demo we include only a subset of 5 different sources, with up to 20 images per source, ensuring that the example dataset contains <100 images.

## Setup
The [code](./code) folder contains two scripts:

1. **[prepare.ipynb](./code/prepare.ipynb):** Collects data directly from Zenodo and constructs a smaller example dataset.
2. **[main.ipynb](./code/main.ipynb):** Demonstrates how to compile the example dataset to be InsectAI-CamtrapDP compliant.

Importantly, [main.ipynb](./code/main.ipynb) does not interface directly with Zenodo, but instead relies on the example dataset being stored in [data](./data), which is the result of running [prepare.ipynb](./code/prepare.ipynb). To facilitate a more transportable example, the results of [prepare.ipynb](./code/prepare.ipynb) will be committed to the git tree, such that the example compilation via [main.ipynb](./code/main.ipynb) can be run immediately after cloning this repository.