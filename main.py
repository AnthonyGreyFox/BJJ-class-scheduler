#!/usr/bin/env python3
"""
BJJ Class Scheduler - Main Entry Point

A modular Brazilian Jiu-Jitsu class scheduling application that helps
gym owners and coaches create balanced weekly schedules.
"""

from src.models.scheduler import BJJScheduler
from src.gui.main_window import ScheduleCalendarGUI

def main():
    """Main entry point for the BJJ Scheduler application"""
    print("Starting BJJ Class Scheduler...")
    
    # Create scheduler with empty configuration
    scheduler = BJJScheduler()
    
    # Launch GUI - users can configure everything through the UI
    app = ScheduleCalendarGUI(scheduler)
    app.run()

if __name__ == "__main__":
    main() 