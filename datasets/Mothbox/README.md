<!-- Image: raw-data/Mothbox cover photo.jpg -->

# Mothbox Cerro Hoya

<img src="raw-data/Mothbox%20cover%20photo.jpg" alt="Mothbox cover photo" width="480"/>

This example dataset is exported in **Camtrap DP** form from the Cerro Hoya expedition deployment (`Cerro_Hoya_Expedition`). It was produced with [`code/convert_mothbox_to_camtrapdp.py`](./code/convert_mothbox_to_camtrapdp.py).

The [**Mothbox**](https://mothbox.org/) is an open-source, low-cost autometed light trap for nocturnal insect monitoring. We have also developed 'Mothbot', a data processing and validation platform for Mothbox and similar devices.

Check out the paper introducing Mothbox and Mothbot [here](https://www.researchgate.net/publication/398459892).


## Dataset layout

- [`media/`](./media/): patch JPEG crops only (full-resolution source frames are omitted from this repository).
- [`raw-data/`](./raw-data/): source JSON, exports, `mothbot_metadata.csv`, and assets such as the cover image `Mothbox cover photo.jpg`.
- **Camtrap DP outputs** (dataset root): `deployments.csv`, `media.csv`, `observations.csv`, `unaccountedfor.csv`, and [`datapackage.json`](./datapackage.json).

