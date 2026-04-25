<!-- Image: media/HE22_01_83_2037_2.jpg -->
# 🐞 RangeX dataset (COCO format)

<img src="media/HE22_01_83_2037_2.jpg" alt="RangeX example image" width="300"/>

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

## InsectAI Camtrap DP suggestions

- not mentioned in the report yet, the `featureType` column in `deployments` should have different enum values, like `flower`, `soil`, `board` etc... Although this may also be captured in "attractantType" if it is an artifical feature?
- support for regions of media is something I think is a priority. The images represented in our media are regions of source media, and I would like to recognize this in the standardized data - perhaps a "parentMedia" field. I don't necessarily want to share the mdeia, but at least reference it and allow the user to know this is from the same image as another region.
- if we were to store detections from multiple users or models, a detections table would be needed to not "mess up" the observations table. This might also be useful to represent different stages of processing of media, for example detection and classification, with a chain of detections linked by e.g. "sourceDetectionID". However, I would also like to link each detection to the most recent processing stage, whether a model or annotation protocol. I wonder if what we have as the models table can actually capture processes, whether human or machine (agents?!). However, I can see that the fields for such a table might be difficult to capture... Maybe related to taxonomic scope and task... And a link to e.g. a huggingface model or an annotation protocol.
- i understand that an effective way to capture active periods of devices may be in the deployments structure, which I formerly thought was to capture device placement periods rather than device activity periods. We discussed using "deployments" for active periods and "deploymentGroups" for placement periods (inclusive of downtime). However, in my opinion a much more elegant solution would be to call active periods "sessions" and placement periods "deployments".
- i think we should have taxonID in the observations/detection table, and reference to taxonomic checklists or backbones should be more clear.
- i don't think cameraSetupType seems very useful and may be confusing (there are many different camera setup types in the insect world and we are actively trying to capture in a standardized way). Perhaps a boolean for "calibration"?
- i think we need to give advice to pepole on how to supplement their data package with "unstandardized" data, and I am starting to believe an assertions table(s) might be the way to do this. Allowing a table that can capture somewhat freeform supplementary information that related to any of the keys in the other tables would be really valuable, and would bring people in to using the standard who are otherwise put off by the fact parts of their data seemingly "don't fit"
