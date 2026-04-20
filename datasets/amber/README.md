# AMBER dataset

This is a subset of the nocturnal insect images UKCEH has collected using the AMI (Automated Monitoring of Insects) system.

The dataset comes from one of four deployments in Anguilla. The wider dataset includes other deployments in Anguilla and other countries. The focus of the data collection is moths, although other insects (and lizards!) also appear in the images.

There are two sets of labels.

## Manual labels
The raw images are provided to Mothbot, which automatically detects individual insects, crops them and clusters them with other similar insects (producing files ending in _botdetection.json). A human reviewer then manually labels the crops (producing files ending in _identified.json). There is one botdetection file and one identified file per raw image.

## Classifier-generated labels
The raw images are cropped to individual insects using the flatbug model. Next, a binary classifier labels the insects as moth or non-moth. The moth crops are fed into a species classifier which labels them at species level. There is one output file for all images called dep000098_all_chunks_jasmin.csv, with one row per cropped insect.