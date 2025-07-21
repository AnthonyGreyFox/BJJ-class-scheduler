import pytest
from src.models.scheduler import BJJScheduler
from src.utils.export import export_to_csv_string
from datetime import date

def test_export_to_csv_string_runs():
    scheduler = BJJScheduler()
    schedule, _ = scheduler.generate_schedule()
    csv_str = export_to_csv_string(schedule, start_date=date(2025, 1, 1), weeks=1)
    assert 'Week 1' in csv_str
    assert 'Date' in csv_str
    assert any(cd.get_display_name() in csv_str for cd in scheduler.class_definitions)

# If you want to test iCal export:
def test_export_to_icalendar_runs():
    scheduler = BJJScheduler()
    schedule, _ = scheduler.generate_schedule()
    ical_str = scheduler.export_to_icalendar(schedule, start_date=date(2025, 1, 1), weeks=1)
    assert 'BEGIN:VCALENDAR' in ical_str
    assert 'END:VCALENDAR' in ical_str
    assert any(cd.get_display_name() in ical_str for cd in scheduler.class_definitions) 