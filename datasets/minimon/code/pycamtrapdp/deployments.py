"""
Camtrap Data Package deployment module
Modified to match the miniMon processing pipeline
"""
from enum import Enum
from .utils import generate_uuid
import math

class FeatureType(str, Enum):
        """
        Type of the feature (if any) associated with the deployment.
        """
        ROAD_PAVED = "roadPaved"
        ROAD_DIRT = "roadDirt"
        TRAIL_HIKING = "trailHiking"
        TRAIL_GAME = "trailGame"
        ROAD_UNDERPASS = "roadUnderpass"
        ROAD_OVERPASS = "roadOverpass"
        ROAD_BRIDGE = "roadBridge"
        CULVERT = "culvert"
        BURROW = "burrow"
        NEST_SITE = "nestSite"
        CARCASS = "carcass"
        WATER_SOURCE = "waterSource"
        FRUITING_TREE = "fruitingTree"


class Deployment:

    _valid_ranges = {
        "latitude" : [-90, 90],
        "longitude" : [-180, 180],
        "coordinateUncertainty": [1, math.inf],
        "cameraDelay": [0, math.inf],
        "cameraHeight": [0, math.inf],
        "cameraDepth": [0, math.inf],
        "cameraTilt": [-90, 90],
        "cameraHeading": [0, 360],
        "detectionDistance": [0, math.inf]
    }

    def __init__(self, deploymentID: str = None, locationID: str = None, locationName: str = None,
                 latitude: float = None, longitude: float = None, coordinateUncertainty: int = None,
                 deploymentStart: str = None, deploymentEnd: str = None, setupBy: str = None, cameraID: str = None,
                 cameraModel: str = None, cameraDelay: int = None, cameraHeight: float = None,
                 cameraDepth: float = None, cameraTilt: int = None, cameraHeading: int = None,
                 detectionDistance: float = None, timestampIssues: bool = None, baitUse: bool = None,
                 featureType: FeatureType = None, habitat: str = None, deploymentGroups: str = None,
                 deploymentTags: str = None, deploymentComments: str = None):


        self.deploymentID = deploymentID
        self.locationID = locationID
        self.locationName = locationName
        self.latitude = latitude
        self.longitude = longitude
        self.coordinateUncertainty = coordinateUncertainty
        self.deploymentStart = deploymentStart
        self.deploymentEnd = deploymentEnd
        self.setupBy = setupBy
        self.cameraID = cameraID
        self.cameraModel = cameraModel
        self.cameraDelay = cameraDelay
        self.cameraHeight = cameraHeight
        self.cameraDepth = cameraDepth
        self.cameraTilt = cameraTilt
        self.cameraHeading = cameraHeading
        self.detectionDistance = detectionDistance
        self.timestampIssues = timestampIssues
        self.baitUse = baitUse
        self.featureType = featureType
        self.habitat = habitat
        self.deploymentGroups = deploymentGroups
        self.deploymentTags = deploymentTags
        self.deploymentComments = deploymentComments

        self._post_init()

    def _post_init(self):
        # @TODO: assert ISO time format of  `deploymentStart` and `deploymentEnd`

        if self.deploymentID is None:
            self.deploymentID = generate_uuid()

        for k, v in self._valid_ranges.items():
            if self.__getattribute__(k) is not None:
                assert (v[0] <= self.__getattribute__(k) <= v[1]), "%s should be in range [%d, %d]" % (k, v[0], v[1])


    def __str__(self):
        return str(self.__dict__)

    def get_field_names(self):
        return self.__dict__.keys()

    def as_dict(self):
        return self.__dict__

    def fill_default_values(self, df):
        rows = df.loc[(df['deploymentStart'] <= self.deploymentStart)
                                    & (df['deploymentEnd'] >= self.deploymentEnd)
                                    & (df['cameraID'] == self.cameraID)]

        assert (rows.shape[0] == 1), f"Found {rows.shape[0]} values for [{self.deploymentStart} - {self.deploymentEnd}, {self.cameraID}]"

        for k in self.get_field_names():
            if (self.__getattribute__(k) is None) and (rows[k].iloc[0] is not None):
                self.__setattr__(k, rows[k].iloc[0])








