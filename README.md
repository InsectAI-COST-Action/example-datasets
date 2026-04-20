# InsectAI Example Datasets and Standards Development

<center>

<img src="resources/insectAI.svg" alt="InsectAI Logo" width="300"/>

[![Dataset Standards Validation](https://github.com/InsectAI-COST-Action/example-datasets/actions/workflows/validate-datasets.yaml/badge.svg)](https://github.com/InsectAI-COST-Action/example-datasets/actions/workflows/validate-datasets.yaml)

</center>

---

## 📁 Example Dataset Progress




<!-- START: DATASET PROGRESS TABLE -->
<!-- Do NOT manually edit! -->

<table width="100%">
  <thead>
    <tr>
      <th style="text-align: left;">Dataset</th>
      <th style="text-align: center;">Status</th>
      <th style="text-align: center;">Example Image</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align: left;"><a href="/datasets/plant-pollinator-interactions"><b>plant-pollinator-interactions</b></a></td>
      <td style="text-align: center;">🔴 Failed (1/5)</td>
      <td style="text-align: center;"><i>No image tag found</i></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/flower_visitors"><b>flower_visitors</b></a></td>
      <td style="text-align: center;">🔴 Failed (1/5)</td>
      <td style="text-align: center;"><i>No image tag found</i></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/flatbug"><b>flatbug</b></a></td>
      <td style="text-align: center;">🟠 Partial (2/7)</td>
      <td style="text-align: center;"><img src="datasets/flatbug/data/ALUS/Araneae_Unknown_2020_11_10_4723.jpg " height="150"></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/insect-detect"><b>insect-detect</b></a></td>
      <td style="text-align: center;">🔴 Failed (1/5)</td>
      <td style="text-align: center;"><i>No image tag found</i></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/rangex"><b>rangex</b></a></td>
      <td style="text-align: center;">🟡 Almost (4/5)</td>
      <td style="text-align: center;"><img src="datasets/rangex/media/HE22_01_83_2037_2.jpg " height="150"></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/amber"><b>amber</b></a></td>
      <td style="text-align: center;">🔴 Failed (1/5)</td>
      <td style="text-align: center;"><i>No image tag found</i></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/lepmon"><b>lepmon</b></a></td>
      <td style="text-align: center;">🟠 Partial (2/5)</td>
      <td style="text-align: center;"><i>No image tag found</i></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/antenna"><b>antenna</b></a></td>
      <td style="text-align: center;">🟠 Partial (2/5)</td>
      <td style="text-align: center;"><i>No image tag found</i></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/ias"><b>ias</b></a></td>
      <td style="text-align: center;">🟠 Partial (2/5)</td>
      <td style="text-align: center;"><img src="datasets/ias/data/20250613022959-snapshot.jpg " height="150"></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/minimon"><b>minimon</b></a></td>
      <td style="text-align: center;">🟡 Almost (3/5)</td>
      <td style="text-align: center;"><i>No image tag found</i></td>
    </tr>
    <tr>
      <td style="text-align: left;"><a href="/datasets/diopsis"><b>diopsis</b></a></td>
      <td style="text-align: center;">🟠 Partial (2/5)</td>
      <td style="text-align: center;"><i>No image tag found</i></td>
    </tr>
  </tbody>
</table>

<!-- Last updated: 2026-04-20 20:45:55 UTC -->
<!-- END: DATASET PROGRESS TABLE -->



---

## 🧪 Contents

- `datasets/` – example datasets
- `resources/` – logos and images for use in readmes, notebooks and presentations
- `templates/` – generic scripts to convert data to Camtrap DP or InsectAI extensions thereof
- `README.md` – this readme!
- `requirements.txt` – Python dependencies for running the conversion scripts
- `*_template.csv` – reference files used to initialize the Camtrap DP CSVs. These contain all necessary headers to ensure the final output meets the data package specifications

---

## 📂 Dataset Organization

The `datasets/` directory is structured to facilitate the conversion from raw data formats to the [Camtrap DP](https://tdwg.github.io/camtrap-dp/) standard.

### 📦 Dataset Subfolders
Each individual dataset is located in a folder named `<DATASET_NAME>` with the following internal structure:

| Component | Description |
| :--- | :--- |
| `media/` | Folder containing all images, potentially organized into subdirectories. |
| `raw-data/` | The original annotations in their source format (JSON, CSV, TXT, etc.). |
| `code/` | Folder containing the conversion scripts (Jupyter, R, etc.) used to convert the dataset in raw format to the Camtrap DP standard. |
| `README.md` | A readme file describing the dataset, its source, and any specific details about the conversion process. |
| `deployments.csv` | **Generated:** Records of camera/sensor deployments. |
| `media.csv` | **Generated:** Metadata for all media files. |
| `observations.csv`| **Generated:** Taxonomic or individual observations. |
| `datapackage.json`| **Generated:** The metadata descriptor for the data package. |

---

## The datathon

The "datathon" is a 2-day workshop where InsectAI members work together to standardize disparate insect “minidatasets”, creating reproducible examples for the wider community. 

Along the way, we reflect on and develop Camtrap DP and InsectAI data standards, produce scripts for data mapping, and journalize the experience of standardizing data and metadata.

We will prove to ourselves (and the world!) that we can store our data in a common format, laying foundations for future collaborations and insect image megadatasets 💾

The living document for the datathon, including the agenda, can be found [here](https://docs.google.com/document/d/1cKWa8PrLWBIouEVd4cDQMRyp790YwyWv_DP1zxm-vxc/edit?usp=drivesdk).

## InsectAI data challenges

The "minidatasets" presented here demonstrate one or more of the common challenges of InsectAI data:

- Detections or classifications from multiple models or multiple annotators for a single image
- Large datasets, of which not all needs to be pushed to e.g. GBIF
- Taxonomic ambiguity and coarse identifications
- Dense time-lapse data with tracks of individuals leaving and re-entering the frame; frequent occlusions
- Datasets that comprise regions of interest or "crops" of original source images
- Variable labelling scope. All pollinators vs. all insects vs. all arthropods?

## Outcomes of the datathon

- Several example standardized datasets to browse and learn from under `datasets/`
- Refined InsectAI/Camtrap DP standards (including github issues to petition the Camtrap DP team), feeding into the InsectAI WG3 report
- A presentation and online materials (especially READMEs under `datasets/<DATASET_NAME>`) to disseminate and demystify working with standards
- Scripts and tools to map data to, and read data from, Camtrap DP/InsectAI (also under `datasets/<DATASET_NAME>`)

## Link to 2025 InsectAI demo of CamtrapDP

[https://github.com/cpadubidri/insectAI-demo.git]

## Link to awesome-insectai

Please consider contributing links to models and other resources for insect detection and classification below:

[https://github.com/InsectAI-COST-Action/awesome-insectai.git]


