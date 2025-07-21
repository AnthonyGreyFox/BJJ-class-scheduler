from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import time
from .enums import ClassType, GiSubType, NoGiSubType

@dataclass
class TimeSlot:
    day: str  # "monday", "tuesday", etc.
    start_time: time
    end_time: time
    
    def __str__(self):
        return f"{self.day.title()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"

@dataclass
class Coach:
    name: str
    max_weekly_classes: int
    preferred_times: List[str]  # ["morning", "evening", "afternoon"]
    available_days: List[str] = field(default_factory=list)  # ["monday", "tuesday", etc.]
    can_teach_gi: bool = True
    can_teach_nogi: bool = True
    can_teach_open_mat: bool = True
    
@dataclass
class ClassDefinition:
    name: str
    class_type: ClassType
    duration_minutes: int = 60
    weekly_count: int = 0
    
    def __str__(self):
        return self.name
    
    def get_display_name(self):
        return self.name

@dataclass
class ScheduledClass:
    class_def: ClassDefinition
    time_slot: TimeSlot
    coach: Coach
    is_fixed: bool = False
    slot_position: int = 0  # Position within the time slot (0 = first class, 1 = second class, etc.)

@dataclass
class ScheduleRequirements:
    class_requirements: Optional[Dict[str, int]] = None  # class_name -> count
    
    def __post_init__(self):
        if self.class_requirements is None:
            self.class_requirements = {} 

def get_default_configuration():
    from .enums import ClassType
    coach = Coach(
        name="Default Coach",
        max_weekly_classes=10,
        preferred_times=["evening"],
        available_days=["monday", "tuesday", "wednesday", "thursday", "friday"],
        can_teach_gi=True,
        can_teach_nogi=True,
        can_teach_open_mat=True
    )
    time_slots = [
        TimeSlot(day=day, start_time=time(19, 0), end_time=time(21, 0))
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]
    ]
    classes = [
        ClassDefinition(name="Gi Essential Drills", class_type=ClassType.GI, duration_minutes=60, weekly_count=4),
        ClassDefinition(name="No-Gi Essentials", class_type=ClassType.NO_GI, duration_minutes=60, weekly_count=4),
        ClassDefinition(name="Open Mat", class_type=ClassType.OPEN_MAT, duration_minutes=60, weekly_count=2),
    ]
    return {
        "coaches": [coach],
        "time_slots": time_slots,
        "class_definitions": classes
    } 