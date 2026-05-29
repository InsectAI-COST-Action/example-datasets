<!-- Image: media/E41990/20250614/E41990_20250614094103_0105_012989.jpg -->
# 🐞 miniMon dataset

This folder contains example raw data captured with the `miniMon` camera, as well as python scripts to convert the (meta)-data to the `camtrapDP` format.



## 1. The `media` folder

The `media` folder contains the raw data recorded with a miniMon.
The data is saved in a nested structure as follows: `root_folder/device_id/date`.
For instance:

```
media/
     |__ E41900
               |_ 20250614
                          |_ E41990_20250614094103.log
                           _ E41990_20250614094103_0105_012989.jpg
                           _ E41990_20250614094103_0205_013829.jpg
                           _ E41990_20250614094103_0305_014668.jpg
                           _ ...
               
                _ ...
                   
```

Some metadata can be recovered from the filename. Looking at `E41990_20250614094103_0105_012989.jpg`, we have:
 - E41990: the unique identifier of the device
 - 20250614094103: timestamp (YYYYMMDDhhmmss)
 - 0105: burst sequence: frame 1 out of 5.
 - 012989: milliseconds since power on.

For each timelapse, one `.log` file is created. This log file records success/failures in capturing images.
Cases of camera failures can be inferred in two ways:

 1. number of log files >> number of images / burst
 1. timestamp between log files is >> timelapse duration (here, 1 minute).

Other information need to be written manually. 
Templates with default values for `deployments` and `media` can be created. 
These default values are then automatically filled when generating the tables from the raw data.

`@todo: upload and explain example of default values.`

## 2. The `raw_data` folder

This folder contains the raw, unprocessed outputs of computer vision models, namely `FlatBug` and `BioCLIP 2`.

  1. The images were first fed to `FlatBug` to detect the insects in the images.
  1. The crops (i.e., bboxes cropped from the images) were then fed to `BioCLIP 2` for species-level classification.

Note that both models were used out-of-the-box (so, no fine-tuning).

## 3. The `code` folder

The `code` folder contains python code and scripts for automatically generating camtrapDP tables from data recorded with the miniMon.

* `miniMonCDPConverter.py`: automatically generates `deployments.csv` and `media.csv` from a folder containing miniMon data.
* `pycamtrapdp`: my take at a python package for camptrapDP
  * `deployments.py`: Class initiating all the values needed for the `deployments` table.
  * `media.py`: Class initiating all the values needed for the `media` table.
  * `minimonfile.py`: Class initiating a minimonfile object, where the metadata is recovered from the filename.
  * `utils.py`: utilities functions

**N.B.: `observations.py` is missing. Will be added SOON$^{TM}$, or feel free to contribute. :)**
