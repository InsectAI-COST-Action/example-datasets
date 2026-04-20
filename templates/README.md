# Rmd Templates to map InsectAI data to Camtrap DP

Here are 2 R Markdown templates for mapping raw data to Camera Trap Data Package (Camtrap DP).

A Camtrap DP is a Frictionless Data Package that consists of
- datapackage.json: Metadata about the data package and camera trap project.
- deployments.csv: Table with camera trap placements (deployments).
- media.csv: Table with media files recorded during deployments.
- observations.csv: Table with observations derived from the media files.

`frictionless` and `camtrapdp` are used to create valid Camtrap DP.

The scripts have not been used yet with data, so assume that some bugs are present. Please write an issue in case you find any, or even better, submit a pull request with improvements.

## template-camtrapdp

Maps raw data to the current version of Camtrap DP.

## template-insectai-camtrapdp

Maps raw data to the adapted Camtrap DP version, with the current suggested changes proposed by the InsectAI community.
