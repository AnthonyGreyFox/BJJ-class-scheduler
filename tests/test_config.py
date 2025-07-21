import pytest
import tempfile
import os
from src.models.scheduler import BJJScheduler

def test_save_and_load_json_config(tmp_path):
    scheduler = BJJScheduler()
    # Change something in the config
    scheduler.coaches[0].name = "Test Coach"
    file_path = tmp_path / "config.json"
    scheduler.save_to_json(file_path)
    # Load into a new scheduler
    scheduler2 = BJJScheduler()
    scheduler2.load_from_json(file_path)
    assert scheduler2.coaches[0].name == "Test Coach"
    assert len(scheduler2.class_definitions) == len(scheduler.class_definitions)
    assert len(scheduler2.time_slots) == len(scheduler.time_slots) 