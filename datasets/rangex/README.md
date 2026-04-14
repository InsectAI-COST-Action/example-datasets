# 🐞 RangeX dataset (COCO format)

This folder contains all the code to convert the RangeX dataset from its original COCO format to the Camtrap DP standard. The original full dataset is not publicly available yet.

## 🖥️ Code folder contents

The code folder contains a Jupyter notebook `main.ipynb` that performs the conversion. It reads the original COCO annotations from `raw_labels/detections_val_20.json`, processes the data, and generates the required CSV files (`deployments.csv`, `media.csv`, `observations.csv`) and the `datapackage.json` descriptor in the parent directory.

This folder also contains the `requirements.txt` file listing the Python dependencies needed to run the conversion script.

## 📝 Technical Requirements

To run the conversion scripts and work with these datasets, please set up a Python environment and install the dependencies:

1. **Create a Python environment** (using `venv` or `conda`)
   Example using `venv`:
   ```bash
   python -m venv venv
   ```
2. **Activate the environment**
   Example for `venv`:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
3. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```