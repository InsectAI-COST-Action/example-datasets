import os

import pandas as pd
from sympy import false

from pycamtrapdp import Deployment, MinimonFile
from pycamtrapdp.media import MediaType
from pycamtrapdp.utils import str_time_to_ISO, obj_to_csv, generate_uuid, csv_path_with_prefix

def _exclude_dirs(dirnames):
    restart = True
    while restart:
        restart = False
        for di, dirname in enumerate(dirnames):
            if dirname.startswith('.') or dirname.startswith('_'):
                dirnames.pop(di)
                restart = True
                break

def generate_camtrapdp_data(data_dir: str, output_dir: str | None, files_prefix: str | None, depl_default_vals: str | None, overwrite_csv: bool):

    # init default values
    deployments = []
    df_defaults = None

    if depl_default_vals:
        df_defaults = pd.read_csv(depl_default_vals)

    if not output_dir:
        output_dir = data_dir

    # get path to deployments.csv and media.csv
    media_csv = csv_path_with_prefix("media.csv", output_dir, files_prefix)
    deployment_csv = csv_path_with_prefix("deployments.csv", output_dir, files_prefix)

    # remove existing deployment and media files is overwrite is set to true
    if overwrite_csv:
        if os.path.isfile(media_csv):
            os.remove(media_csv)
        if os.path.isfile(deployment_csv):
            os.remove(deployment_csv)


    # ### Walk through the files saved by the miniMon.
    # ### One day = one deployment
    # ### Media belongs to a deployment based on its date of recording
    for dirpath, dirnames, filenames in os.walk(data_dir, topdown=True):
        dirnames.sort() # sorting dirnames here will ensure that the subsequent walks will follow that order

        # prevent going in dirs that we don't want.
        _exclude_dirs(dirnames)


        if len(dirnames) == 0:  # we arrived at a leaf of the tree

            print(dirpath, len(filenames))
            filenames.sort()  # sort the files in ascending order

            ### MEDIA
            medias = []
            n_logs = 0
            n_burst = -1

            deployment_issues = None
            deploymentID = None
            cameraID = None
            deploymentStart = None
            deploymentEnd = None


            rel_filepath = os.path.relpath(dirpath, data_dir)
            for i, filename in enumerate(filenames):  # go through the list of files

                if filename.startswith('.') or '(' in filename:
                    continue

                minimon_file = MinimonFile(filename=filename, filepath=rel_filepath)
                # filename_dict = utils.parse_filename(filename)  # parse the metadata from the filename

                if minimon_file.filetype == MediaType.LOG_TXT:
                    n_logs += 1  # count the number of logs; +/- = to number of power cycles

                    if cameraID is None:  # this is the first log file
                        cameraID = minimon_file.device_id
                        deploymentStart = minimon_file.datetime_iso

                    deploymentEnd = minimon_file.datetime_iso  # time of the last log file

                elif minimon_file.filetype == MediaType.IMG_JPG:  # only save data from .jpg files in medias.csv

                    if deploymentID is None:  # generate deploymentID, e.g., DK_2025-06-20_MSG_E2905C
                        deploymentID = generate_uuid()

                    if n_burst <= 0: # find the target burst
                        n_burst = minimon_file.burst_target

                    media = minimon_file.to_media(deploymentID)
                    medias.append(media)

                else:
                    print(f"Unsupported file type for {filename}. Skipping.")
                    continue

            # end for filenames

            if len(medias) == 0:
                deployment_issues = "NO MEDIA"
                deploymentID = generate_uuid() if deploymentID is None else deploymentID

                if n_logs == 0:  # empty directory. attempt to get date and camera ID from path
                    deployment_issues += " / NO LOGS"
                    cameraID = dirpath.split('/')[-2]
                    date_str = dirpath.split('/')[-1]
                    deploymentStart = deploymentEnd = str_time_to_ISO(date_str, format="%Y%m%d")

            else:
                media_csv = csv_path_with_prefix("media.csv", output_dir, files_prefix)

                obj_to_csv(medias, media_csv, overwrite=false)

                expected_media_length = n_logs * n_burst  # we expect to get n_burst pictures per power-cycle

                # did we find less bursts than expected?
                # (- 1 burst to account for power-off mid-cycle)
                if (expected_media_length - n_burst) > len(medias):
                    deployment_issues = f"%d/%d (media/expected) power-cycles=%d" % (len(medias), expected_media_length, n_logs)

            ### DEPLOYMENTS
            # make deployment object (lat,lon are mandatory but we don't have that metadata. Needs manual intervention)
            deployment = Deployment(deploymentID=deploymentID,
                                    deploymentStart=deploymentStart, deploymentEnd=deploymentEnd,
                                    cameraID=cameraID,
                                    deploymentComments=deployment_issues
                                    )

            if df_defaults is not None:
                deployment.fill_default_values(df_defaults)


            # print(deployment)

            # add deployment to the list of deployments (1 day = 1 deployment)
            deployments.append(deployment)  # needs dict format for pandas

    # export list of deployments in csv format

    deployments_csv = csv_path_with_prefix("deployments.csv", output_dir, files_prefix)

    obj_to_csv(deployments, deployments_csv, overwrite=overwrite_csv)



if __name__ == '__main__':

    OUTPUT_PATH = "../"
    OVERWRITE_CSV = False

    # ### GR
    DATA_DIR = "../media"
    # FILES_PREFIX = "minimon-example"
    FILES_PREFIX = ""
    DEFAULT_DEPL_VALUES = None

    generate_camtrapdp_data(DATA_DIR, OUTPUT_PATH, FILES_PREFIX, DEFAULT_DEPL_VALUES, OVERWRITE_CSV)




