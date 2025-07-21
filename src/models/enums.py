from enum import Enum

class ClassType(Enum):
    GI = "gi"
    NO_GI = "no-gi"
    OPEN_MAT = "open-mat"

class GiSubType(Enum):
    FOUNDATIONS = "foundations"
    ESSENTIALS = "essentials"
    ADVANCED = "advanced"
    TEAM_TRAINING = "team-training"

class NoGiSubType(Enum):
    FOUNDATIONS = "foundations"
    ESSENTIALS = "essentials"

class ScheduleMode(Enum):
    BALANCED = "balanced"
    SEQUENTIAL = "sequential" 