<!-- Image: raw-data/diopsis_soortherkenning_AI_231_2022_08_05_00_30_44.png -->

# Diopsis example dataset

<img src="raw-data/diopsis_soortherkenning_AI_231_2022_08_05_00_30_44.png" alt="Diopsis example image" width="300"/> <img src="raw-data/Diopsis_Camerading_in_bloemenveld_foto_Rotem_Zilber_1937204697.jpg" alt="Diopsis image" width="300"/>


This folder contains a subset of Diopsis recordings and annotations used in following study:

### Effects of pressure drainage on invertebrate and plant diversity in the Alblasserwaard. 
#### Final report November 2025. By Youri Siemer, Naturalis Biodiversity Center <img src="raw-data/logo.svg" alt="Diopsis image" width="7">

This research examined how pressure drainage and water infiltration systems influence the diversity of invertebrates and plants within the Alblasserwaard region. The study compared control plots against plots equipped with drainage systems to analyze shifts in biomass and species composition. 

While the full study encompassed 20 distinct plots across five different farms, the data provided here is a specific subset captured by Camera 231. This subset includes recordings from all five locations, with samples evenly selected over a three-month periods, over day and night time, and over amount of insects detected.


Dataset prepared for the InsectAI WG3 Datathon, Nis 2026.

Data controller: Elsbeth van Dam (elsebth.vandam@naturalis.nl)

## Camtrap DP suggestions
- Save 'event' for observations with duration, not for things about measurement itself (recording or processing).
- Introduce 'sequence_id' to group time-related media 
- In tracking literature, entities are: detections, tracklets, tracks and identities.
- I'd prefer ObservationMethod instead of model table, since this is not limited to a single model but allows also to include configuration, other type of algorithms, or multiple models for different steps (like Detection, Tracking, ReIdentification, Binary Insect/Non-Insect Classification and Species Classification).
- It would be nice to allow multiple annotations per dataset. For instance, manual annotation + annotation by some method. You could make multiple datasets, but that would involve either copying the media, or storing it elsewhere with the risk of decoupling. Alternatively, you could allow multiple observations.csv files?
