import csv
import io
from typing import List, Optional
from datetime import date, timedelta

from ..models.data_classes import ScheduledClass

def export_to_csv(schedule: List[ScheduledClass], filename: str, start_date: Optional[date] = None, weeks: int = 4):
    """Export schedule to CSV format"""
    if start_date is None:
        start_date = date.today()
    
    day_mapping = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Week', 'Date', 'Day', 'Time', 'Class', 'Coach', 'Fixed'])
        
        # Generate events for specified number of weeks
        for week in range(weeks):
            week_date = start_date + timedelta(weeks=week)
            
            for sc in schedule:
                if sc.time_slot.day.lower() not in day_mapping:
                    continue
                    
                day_offset = day_mapping[sc.time_slot.day.lower()]
                event_date = week_date + timedelta(days=day_offset)
                
                # Format time
                time_str = f"{sc.time_slot.start_time.strftime('%H:%M')}-{sc.time_slot.end_time.strftime('%H:%M')}"
                
                # Write row
                writer.writerow([
                    f"Week {week + 1}",
                    event_date.strftime('%Y-%m-%d'),
                    sc.time_slot.day.title(),
                    time_str,
                    sc.class_def.get_display_name(),
                    sc.coach.name,
                    "Yes" if sc.is_fixed else "No"
                ])
                
    print(f"Schedule exported to {filename}")

def save_csv_file(filename: str, schedule: List[ScheduledClass], start_date: Optional[date] = None, weeks: int = 4):
    """Save schedule as CSV file with default naming"""
    if filename is None:
        filename = f"bjj_schedule_{date.today().strftime('%Y%m%d')}.csv"
        
    export_to_csv(schedule, filename, start_date, weeks)

def export_to_csv_string(schedule: List[ScheduledClass], start_date: Optional[date] = None, weeks: int = 4) -> str:
    """Export schedule to CSV format and return as string"""
    if start_date is None:
        start_date = date.today()
    
    day_mapping = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Week', 'Date', 'Day', 'Time', 'Class', 'Coach', 'Fixed'])
    
    # Generate events for specified number of weeks
    for week in range(weeks):
        week_date = start_date + timedelta(weeks=week)
        
        for sc in schedule:
            if sc.time_slot.day.lower() not in day_mapping:
                continue
                
            day_offset = day_mapping[sc.time_slot.day.lower()]
            event_date = week_date + timedelta(days=day_offset)
            
            # Format time
            time_str = f"{sc.time_slot.start_time.strftime('%H:%M')}-{sc.time_slot.end_time.strftime('%H:%M')}"
            
            # Write row
            writer.writerow([
                f"Week {week + 1}",
                event_date.strftime('%Y-%m-%d'),
                sc.time_slot.day.title(),
                time_str,
                sc.class_def.get_display_name(),
                sc.coach.name,
                "Yes" if sc.is_fixed else "No"
            ])
    return output.getvalue() 