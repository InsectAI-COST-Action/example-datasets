import os
from enum import Enum
from datetime import datetime
from .utils import generate_uuid, generate_id
from .media import Media, MediaType, CaptureMethod


class MinimonFile:

    def __init__(self, filename: str, filepath: str | None ):
        # ## Path magic ##
        #
        # if no path is passed, attempt to retrieve it from the filename
        if filepath is None:
            filepath = filename

        # remove dir info from filename
        self.filename = os.path.basename(filename)

        # check if filepath contains the filename
        _, ext = os.path.splitext(filepath)
        if len(ext) == 0:  # the filepath only contain the path to the dir, not to the file
            self.filepath = os.path.join(filepath, filename)
        else:  # filepath already contains the full path to the file
            self.filepath = filepath

        self.filedir = os.path.dirname(filepath) # path to the dir that contains the file

        # ## Extract info/metadata from filename ##
        #
        # split extension from filename, e.g., 'foo.jpg' --> ('foo', '.jpg')
        basename, extension = os.path.splitext(filename)
        if extension in [".jpg", ".jpeg"]:
            self.filetype = MediaType.IMG_JPG
        elif extension == ".log":
            self.filetype = MediaType.LOG_TXT
        else:
            self.filetype = MediaType.OTHER

        # ## Image format: DEVID_DATETIME_BURST_MS.jpg
        # ## Log format: DEVID_DATETIME.log
        #
        # split metadata from filename.
        nameparts = basename.split('_')

        self.device_id = nameparts[0]
        self.datetime_str = nameparts[1]
        if self.datetime_str.startswith("2000"):
            self.datetime_str = self.datetime_str[:7] + "1" + self.datetime_str[8:]
            # self.datetime_str = "20000101000000"
        self.datetime = datetime.strptime(self.datetime_str, "%Y%m%d%H%M%S")
        self.datetime_iso = self.datetime.isoformat(timespec='seconds')

        if self.filetype == MediaType.IMG_JPG:
            self.burst_id = int(nameparts[2][:2])
            self.burst_target = int(nameparts[2][2:])
            self.ms = int(nameparts[3])


    def to_media(self, deploymentID:str):
        mediaID = generate_uuid()

        return Media(mediaID=mediaID,
                     deploymentID=deploymentID,
                     captureMethod=CaptureMethod.TIME_LAPSE,
                     timestamp=self.datetime_iso,
                     filePath=self.filepath,
                     fileName=self.filename,
                     fileMediatype=self.filetype)
