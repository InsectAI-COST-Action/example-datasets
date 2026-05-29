"""
Camtrap Data Package media module
Modified to match the miniMon processing pipeline
"""
from enum import Enum
from .utils import generate_uuid, generate_id


class CaptureMethod(str, Enum):
    ACTIVITY_DETECTION = "activityDetection"
    TIME_LAPSE = "timeLapse"


class MediaType(str, Enum):
    IMG_JPG = "image/jpeg"
    LOG_TXT = "log/txt"
    OTHER = "other"


class Media:

    def __init__(self, mediaID: str = None, deploymentID: str = None,
                 captureMethod: CaptureMethod = CaptureMethod.TIME_LAPSE,
                 timestamp: str = None, filePath: str = None, filePublic: bool = False,
                 fileName: str = False, fileMediatype: MediaType = MediaType.IMG_JPG,
                 exifData: dict = None, favorite: bool = False,
                 mediaComments: str = None):

        self.mediaID = mediaID
        self.deploymentID = deploymentID
        self.captureMethod = captureMethod
        self.timestamp = timestamp
        self.filePath = filePath
        self.filePublic = filePublic
        self.fileName = fileName
        self.fileMediatype = fileMediatype
        self.exifData = exifData
        self.favorite = favorite
        self.mediaComments = mediaComments

        self._post_init()

    def _post_init(self):
        # @TODO: assert ISO time format of  `deploymentStart` and `deploymentEnd`

        if self.mediaID is None:
            self.mediaID = generate_id(4)

    def __str__(self):
        return str(self.__dict__)

    def get_field_names(self):
        return self.__dict__.keys()

    def as_dict(self):
        return self.__dict__


