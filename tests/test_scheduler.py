import pytest
from src.models.scheduler import BJJScheduler
from src.models.data_classes import get_default_configuration, ScheduledClass, TimeSlot
from datetime import time

def test_default_config_loads():
    scheduler = BJJScheduler()
    assert len(scheduler.coaches) == 1
    assert len(scheduler.time_slots) == 5
    assert len(scheduler.class_definitions) == 3

def test_generate_schedule_respects_weekly_count():
    scheduler = BJJScheduler()
    schedule, conflicts = scheduler.generate_schedule()
    # Should schedule the sum of all weekly_counts
    total_classes = sum(cd.weekly_count for cd in scheduler.class_definitions)
    assert len(schedule) == total_classes
    assert not conflicts

def test_fixed_class_is_respected():
    scheduler = BJJScheduler()
    # Manually fix a class to a slot
    class_def = scheduler.class_definitions[0]
    coach = scheduler.coaches[0]
    fixed_slot = TimeSlot(day="saturday", start_time=time(13, 0), end_time=time(14, 0))
    fixed_class = ScheduledClass(class_def=class_def, time_slot=fixed_slot, coach=coach, is_fixed=True)
    scheduler.add_fixed_class(fixed_class)
    schedule, conflicts = scheduler.generate_schedule()
    # The fixed class should be in the schedule
    assert any(sc.is_fixed and sc.time_slot == fixed_slot for sc in schedule) 