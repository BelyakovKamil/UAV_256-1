from enum import Enum

class DroneState(Enum):
    UNKNOWN = 0
    IS_FLYING = 1
    IS_LANDED = 2
    ON_MISSION = 3

class MissionType(Enum):
    NO_MISSION = 0
    OBSERVE_LINE = 1
    OBSERVE_PILLAR = 2

class MissionState(Enum):
    UNKNOWN = 0
    START = 1
    EXEC = 2
    COMPLETE = 3
    ERR = -1

