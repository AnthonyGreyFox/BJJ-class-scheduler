from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import random
from datetime import datetime, time, date, timedelta
import calendar
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import uuid

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
    can_teach_gi: bool = True
    can_teach_nogi: bool = True
    can_teach_open_mat: bool = True
    
@dataclass
class ClassDefinition:
    class_type: ClassType
    sub_type: Optional[str] = None
    duration_minutes: int = 60
    name: Optional[str] = None
    
    def __str__(self):
        if self.name:
            return self.name
        if self.sub_type:
            return f"{self.class_type.value.title()} {self.sub_type.title()}"
        return self.class_type.value.title()
    
    def get_display_name(self):
        """Get a display name for the class"""
        if self.name:
            return self.name
        if self.sub_type:
            return f"{self.class_type.value.title()} {self.sub_type.title()}"
        return self.class_type.value.title()

@dataclass
class ScheduledClass:
    class_def: ClassDefinition
    time_slot: TimeSlot
    coach: Coach
    is_fixed: bool = False

@dataclass
class ScheduleRequirements:
    class_requirements: Optional[Dict[str, int]] = None  # class_name -> count
    
    def __post_init__(self):
        if self.class_requirements is None:
            self.class_requirements = {}

class BJJScheduler:
    def __init__(self):
        self.coaches: List[Coach] = []
        self.available_days: List[str] = []
        self.time_slots: List[TimeSlot] = []
        self.fixed_classes: List[ScheduledClass] = []
        self.schedule_mode: ScheduleMode = ScheduleMode.BALANCED
        self.class_definitions: List[ClassDefinition] = []
        
        # Initialize with default class definitions
        self._initialize_default_classes()
    
    def _initialize_default_classes(self):
        """Initialize with default class definitions"""
        default_classes = [
            ClassDefinition(ClassType.GI, GiSubType.FOUNDATIONS.value, 60, "Gi Foundations"),
            ClassDefinition(ClassType.GI, GiSubType.ESSENTIALS.value, 60, "Gi Essentials"),
            ClassDefinition(ClassType.GI, GiSubType.ADVANCED.value, 60, "Gi Advanced"),
            ClassDefinition(ClassType.GI, GiSubType.TEAM_TRAINING.value, 60, "Gi Team Training"),
            ClassDefinition(ClassType.NO_GI, NoGiSubType.FOUNDATIONS.value, 60, "No-Gi Foundations"),
            ClassDefinition(ClassType.NO_GI, NoGiSubType.ESSENTIALS.value, 60, "No-Gi Essentials"),
            ClassDefinition(ClassType.OPEN_MAT, duration_minutes=60, name="Open Mat"),
        ]
        self.class_definitions = default_classes
        
    def add_coach(self, coach: Coach):
        self.coaches.append(coach)
        
    def set_available_days(self, days: List[str]):
        self.available_days = days
        
    def add_time_slot(self, time_slot: TimeSlot):
        self.time_slots.append(time_slot)
        
    def add_fixed_class(self, scheduled_class: ScheduledClass):
        scheduled_class.is_fixed = True
        self.fixed_classes.append(scheduled_class)
        
    def set_schedule_mode(self, mode: ScheduleMode):
        self.schedule_mode = mode
        
    def add_class_definition(self, class_def: ClassDefinition):
        """Add a new class definition"""
        self.class_definitions.append(class_def)
        
    def remove_class_definition(self, class_def: ClassDefinition):
        """Remove a class definition"""
        if class_def in self.class_definitions:
            self.class_definitions.remove(class_def)
            
    def get_class_definition_by_name(self, name: str) -> Optional[ClassDefinition]:
        """Get a class definition by name"""
        for class_def in self.class_definitions:
            if class_def.name == name:
                return class_def
        return None
        
    def _get_time_category(self, time_slot: TimeSlot) -> str:
        """Categorize time slot as morning, afternoon, or evening"""
        hour = time_slot.start_time.hour
        if hour < 12:
            return "morning"
        elif hour < 17:
            return "afternoon"
        else:
            return "evening"
            
    def _can_coach_teach_class(self, coach: Coach, class_def: ClassDefinition, time_slot: TimeSlot) -> bool:
        """Check if coach can teach this class at this time"""
        # Check class type compatibility
        if class_def.class_type == ClassType.GI and not coach.can_teach_gi:
            return False
        if class_def.class_type == ClassType.NO_GI and not coach.can_teach_nogi:
            return False
        if class_def.class_type == ClassType.OPEN_MAT and not coach.can_teach_open_mat:
            return False
            
        # Check time preference
        time_category = self._get_time_category(time_slot)
        if time_category not in coach.preferred_times:
            return False
            
        return True
        
    def _get_coach_current_load(self, coach: Coach, current_schedule: List[ScheduledClass]) -> int:
        """Count how many classes this coach is already teaching"""
        return sum(1 for sc in current_schedule if sc.coach == coach)
        
    def _has_scheduling_conflict(self, time_slot: TimeSlot, coach: Coach, current_schedule: List[ScheduledClass]) -> bool:
        """Check if coach is already teaching at this time slot"""
        for sc in current_schedule:
            if sc.coach == coach and sc.time_slot == time_slot:
                return True
        return False
        
    def _create_class_requirements_list(self, requirements: ScheduleRequirements) -> List[ClassDefinition]:
        """Convert requirements into a list of classes to schedule"""
        classes = []
        
        if not requirements.class_requirements:
            return classes
            
        for class_name, count in requirements.class_requirements.items():
            # Find the class definition by name
            class_def = self.get_class_definition_by_name(class_name)
            if class_def:
                for _ in range(count):
                    classes.append(class_def)
            else:
                # Fallback to old system for backward compatibility
                if class_name == "Gi Foundations":
                    classes.append(ClassDefinition(ClassType.GI, GiSubType.FOUNDATIONS.value, 60, "Gi Foundations"))
                elif class_name == "Gi Essentials":
                    classes.append(ClassDefinition(ClassType.GI, GiSubType.ESSENTIALS.value, 60, "Gi Essentials"))
                elif class_name == "Gi Advanced":
                    classes.append(ClassDefinition(ClassType.GI, GiSubType.ADVANCED.value, 60, "Gi Advanced"))
                elif class_name == "Gi Team Training":
                    classes.append(ClassDefinition(ClassType.GI, GiSubType.TEAM_TRAINING.value, 60, "Gi Team Training"))
                elif class_name == "No-Gi Foundations":
                    classes.append(ClassDefinition(ClassType.NO_GI, NoGiSubType.FOUNDATIONS.value, 60, "No-Gi Foundations"))
                elif class_name == "No-Gi Essentials":
                    classes.append(ClassDefinition(ClassType.NO_GI, NoGiSubType.ESSENTIALS.value, 60, "No-Gi Essentials"))
                elif class_name == "Open Mat":
                    classes.append(ClassDefinition(ClassType.OPEN_MAT, duration_minutes=60, name="Open Mat"))
            
        return classes
        
    def _sort_classes_for_scheduling(self, classes: List[ClassDefinition]) -> List[ClassDefinition]:
        """Sort classes based on scheduling mode"""
        if self.schedule_mode == ScheduleMode.SEQUENTIAL:
            # Group by type (gi, no-gi, open-mat)
            return sorted(classes, key=lambda c: (c.class_type.value, c.sub_type or ""))
        else:
            # Balanced mode - shuffle for even distribution
            shuffled = classes.copy()
            random.shuffle(shuffled)
            return shuffled
            
    def _get_time_slot_duration_minutes(self, time_slot: TimeSlot) -> int:
        """Get the duration of a time slot in minutes"""
        start_minutes = time_slot.start_time.hour * 60 + time_slot.start_time.minute
        end_minutes = time_slot.end_time.hour * 60 + time_slot.end_time.minute
        return end_minutes - start_minutes
        
    def _get_available_time_in_slot(self, time_slot: TimeSlot, current_schedule: List[ScheduledClass]) -> int:
        """Get available time in a slot (in minutes)"""
        total_duration = self._get_time_slot_duration_minutes(time_slot)
        used_time = 0
        
        # Calculate time used by existing classes in this slot
        for sc in current_schedule:
            if sc.time_slot == time_slot:
                used_time += sc.class_def.duration_minutes
                
        return total_duration - used_time
        
    def _can_fit_class_in_slot(self, class_def: ClassDefinition, time_slot: TimeSlot, 
                              current_schedule: List[ScheduledClass]) -> bool:
        """Check if a class can fit in a time slot"""
        available_time = self._get_available_time_in_slot(time_slot, current_schedule)
        return available_time >= class_def.duration_minutes
        
    def _find_best_slot_for_class(self, class_def: ClassDefinition, available_slots: List[TimeSlot], 
                                  current_schedule: List[ScheduledClass]) -> Optional[Tuple[TimeSlot, Coach]]:
        """Find the best time slot and coach for a class"""
        candidates = []
        
        for time_slot in available_slots:
            # Check if class can fit in this slot
            if not self._can_fit_class_in_slot(class_def, time_slot, current_schedule):
                continue
                
            for coach in self.coaches:
                # Check basic compatibility
                if not self._can_coach_teach_class(coach, class_def, time_slot):
                    continue
                    
                # Check for conflicts (coach already teaching at this time)
                if self._has_scheduling_conflict(time_slot, coach, current_schedule):
                    continue
                    
                # Check coach load
                current_load = self._get_coach_current_load(coach, current_schedule)
                if current_load >= coach.max_weekly_classes:
                    continue
                    
                # Calculate slot utilization (prefer slots with more available time)
                available_time = self._get_available_time_in_slot(time_slot, current_schedule)
                candidates.append((time_slot, coach, current_load, available_time))
                
        if not candidates:
            return None
            
        # Sort by coach load first, then by available time (prefer slots with more space)
        candidates.sort(key=lambda x: (x[2], -x[3]))
        return candidates[0][0], candidates[0][1]
        
    def generate_schedule(self, requirements: ScheduleRequirements) -> Tuple[List[ScheduledClass], List[str]]:
        """Generate a schedule based on requirements"""
        schedule = self.fixed_classes.copy()
        conflicts = []
        
        # Get available time slots (excluding fixed classes)
        available_slots = []
        for time_slot in self.time_slots:
            if time_slot.day.lower() in [d.lower() for d in self.available_days]:
                # Check if this slot is already taken by a fixed class
                slot_taken = any(fc.time_slot == time_slot for fc in self.fixed_classes)
                if not slot_taken:
                    available_slots.append(time_slot)
        
        # Create list of classes to schedule
        classes_to_schedule = self._create_class_requirements_list(requirements)
        classes_to_schedule = self._sort_classes_for_scheduling(classes_to_schedule)
        
        # Schedule each class
        for class_def in classes_to_schedule:
            result = self._find_best_slot_for_class(class_def, available_slots, schedule)
            
            if result:
                time_slot, coach = result
                scheduled_class = ScheduledClass(class_def, time_slot, coach)
                schedule.append(scheduled_class)
                # Don't remove the slot - it can still fit more classes
            else:
                conflicts.append(f"Could not schedule {class_def}")
                
        return schedule, conflicts
        
    def print_schedule(self, schedule: List[ScheduledClass]):
        """Print the schedule in a readable format"""
        if not schedule:
            print("No classes scheduled.")
            return
            
        # Group by day
        days = {}
        for sc in schedule:
            day = sc.time_slot.day.title()
            if day not in days:
                days[day] = []
            days[day].append(sc)
            
        # Sort each day by time
        for day in days:
            days[day].sort(key=lambda sc: sc.time_slot.start_time)
            
        # Print schedule
        for day in sorted(days.keys()):
            print(f"\n{day}:")
            print("-" * 40)
            for sc in days[day]:
                fixed_marker = " [FIXED]" if sc.is_fixed else ""
                print(f"  {sc.time_slot.start_time.strftime('%H:%M')}-{sc.time_slot.end_time.strftime('%H:%M')} | "
                      f"{sc.class_def} | {sc.coach.name}{fixed_marker}")
    
    def export_to_icalendar(self, schedule: List[ScheduledClass], start_date: Optional[date] = None, weeks: int = 4) -> str:
        """Export schedule to iCalendar format (.ics file)"""
        if start_date is None:
            start_date = date.today()
            
        # Find the start of the week (Monday)
        days_since_monday = start_date.weekday()
        week_start = start_date - timedelta(days=days_since_monday)
        
        ical_content = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//BJJ Club//Schedule//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]
        
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        # Generate events for specified number of weeks
        for week in range(weeks):
            week_date = week_start + timedelta(weeks=week)
            
            for sc in schedule:
                if sc.time_slot.day.lower() not in day_mapping:
                    continue
                    
                day_offset = day_mapping[sc.time_slot.day.lower()]
                event_date = week_date + timedelta(days=day_offset)
                
                # Create datetime objects
                start_datetime = datetime.combine(event_date, sc.time_slot.start_time)
                end_datetime = datetime.combine(event_date, sc.time_slot.end_time)
                
                # Format for iCalendar (UTC)
                start_str = start_datetime.strftime('%Y%m%dT%H%M%S')
                end_str = end_datetime.strftime('%Y%m%dT%H%M%S')
                
                # Create unique ID
                uid = f"{start_str}-{sc.class_def.class_type.value}-{sc.class_def.sub_type or 'main'}@bjjclub.local"
                
                # Add event
                ical_content.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART:{start_str}",
                    f"DTEND:{end_str}",
                    f"SUMMARY:{sc.class_def}",
                    f"DESCRIPTION:Coach: {sc.coach.name}{'\\nFixed Class' if sc.is_fixed else ''}",
                    f"LOCATION:BJJ Club",
                    "BEGIN:VALARM",
                    "TRIGGER:-PT15M",
                    "ACTION:DISPLAY",
                    "DESCRIPTION:Class starting in 15 minutes",
                    "END:VALARM",
                    "END:VEVENT"
                ])
        
        ical_content.append("END:VCALENDAR")
        return "\n".join(ical_content)
    
    def save_icalendar_file(self, schedule: List[ScheduledClass], filename: Optional[str] = None, 
                           start_date: Optional[date] = None, weeks: int = 4):
        """Save schedule as iCalendar file"""
        if filename is None:
            filename = f"bjj_schedule_{date.today().strftime('%Y%m%d')}.ics"
            
        ical_content = self.export_to_icalendar(schedule, start_date, weeks)
        
        with open(filename, 'w') as f:
            f.write(ical_content)
            
        print(f"Schedule saved to {filename}")
        print("Double-click the file to add to your Mac Calendar app!")

class ConfigurationDialog:
    def __init__(self, parent, title, scheduler=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.scheduler = scheduler
        self.result = None
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")

class CoachConfigDialog(ConfigurationDialog):
    def __init__(self, parent, scheduler, coach=None):
        super().__init__(parent, "Configure Coach", scheduler)
        self.coach = coach
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Coach name
        ttk.Label(main_frame, text="Coach Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar(value=self.coach.name if self.coach else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # Max weekly classes
        ttk.Label(main_frame, text="Max Weekly Classes:").grid(row=1, column=0, sticky="w", pady=5)
        self.max_classes_var = tk.StringVar(value=str(self.coach.max_weekly_classes) if self.coach else "5")
        ttk.Entry(main_frame, textvariable=self.max_classes_var, width=10).grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Preferred times
        ttk.Label(main_frame, text="Preferred Times:").grid(row=2, column=0, sticky="w", pady=5)
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=2, column=1, sticky="we", pady=5, padx=(10, 0))
        
        self.morning_var = tk.BooleanVar(value="morning" in (self.coach.preferred_times if self.coach else []))
        self.afternoon_var = tk.BooleanVar(value="afternoon" in (self.coach.preferred_times if self.coach else []))
        self.evening_var = tk.BooleanVar(value="evening" in (self.coach.preferred_times if self.coach else []))
        
        ttk.Checkbutton(time_frame, text="Morning", variable=self.morning_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(time_frame, text="Afternoon", variable=self.afternoon_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(time_frame, text="Evening", variable=self.evening_var).pack(side=tk.LEFT)
        
        # Can teach options
        ttk.Label(main_frame, text="Can Teach:").grid(row=3, column=0, sticky="w", pady=5)
        teach_frame = ttk.Frame(main_frame)
        teach_frame.grid(row=3, column=1, sticky="we", pady=5, padx=(10, 0))
        
        self.can_teach_gi_var = tk.BooleanVar(value=self.coach.can_teach_gi if self.coach else True)
        self.can_teach_nogi_var = tk.BooleanVar(value=self.coach.can_teach_nogi if self.coach else True)
        self.can_teach_open_mat_var = tk.BooleanVar(value=self.coach.can_teach_open_mat if self.coach else True)
        
        ttk.Checkbutton(teach_frame, text="Gi", variable=self.can_teach_gi_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(teach_frame, text="No-Gi", variable=self.can_teach_nogi_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(teach_frame, text="Open Mat", variable=self.can_teach_open_mat_var).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def save(self):
        try:
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Coach name is required")
                return
                
            max_classes = int(self.max_classes_var.get())
            if max_classes <= 0:
                messagebox.showerror("Error", "Max weekly classes must be positive")
                return
                
            preferred_times = []
            if self.morning_var.get():
                preferred_times.append("morning")
            if self.afternoon_var.get():
                preferred_times.append("afternoon")
            if self.evening_var.get():
                preferred_times.append("evening")
                
            if not preferred_times:
                messagebox.showerror("Error", "At least one preferred time must be selected")
                return
                
            self.result = Coach(
                name=name,
                max_weekly_classes=max_classes,
                preferred_times=preferred_times,
                can_teach_gi=self.can_teach_gi_var.get(),
                can_teach_nogi=self.can_teach_nogi_var.get(),
                can_teach_open_mat=self.can_teach_open_mat_var.get()
            )
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            
    def cancel(self):
        self.dialog.destroy()

class TimeSlotConfigDialog(ConfigurationDialog):
    def __init__(self, parent, scheduler, time_slot=None):
        super().__init__(parent, "Configure Time Slot", scheduler)
        self.time_slot = time_slot
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Day selection
        ttk.Label(main_frame, text="Day:").grid(row=0, column=0, sticky="w", pady=5)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.day_var = tk.StringVar(value=self.time_slot.day.title() if self.time_slot else "Monday")
        day_combo = ttk.Combobox(main_frame, textvariable=self.day_var, values=days, state="readonly")
        day_combo.grid(row=0, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # Start time
        ttk.Label(main_frame, text="Start Time:").grid(row=1, column=0, sticky="w", pady=5)
        time_frame = ttk.Frame(main_frame)
        time_frame.grid(row=1, column=1, sticky="we", pady=5, padx=(10, 0))
        
        start_hour = self.time_slot.start_time.hour if self.time_slot else 19
        start_minute = self.time_slot.start_time.minute if self.time_slot else 0
        
        self.start_hour_var = tk.StringVar(value=str(start_hour))
        self.start_minute_var = tk.StringVar(value=str(start_minute).zfill(2))
        
        ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.start_hour_var, width=5).pack(side=tk.LEFT)
        ttk.Label(time_frame, text=":").pack(side=tk.LEFT, padx=2)
        ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.start_minute_var, width=5).pack(side=tk.LEFT)
        
        # End time
        ttk.Label(main_frame, text="End Time:").grid(row=2, column=0, sticky="w", pady=5)
        end_time_frame = ttk.Frame(main_frame)
        end_time_frame.grid(row=2, column=1, sticky="we", pady=5, padx=(10, 0))
        
        end_hour = self.time_slot.end_time.hour if self.time_slot else 20
        end_minute = self.time_slot.end_time.minute if self.time_slot else 0
        
        self.end_hour_var = tk.StringVar(value=str(end_hour))
        self.end_minute_var = tk.StringVar(value=str(end_minute).zfill(2))
        
        ttk.Spinbox(end_time_frame, from_=0, to=23, textvariable=self.end_hour_var, width=5).pack(side=tk.LEFT)
        ttk.Label(end_time_frame, text=":").pack(side=tk.LEFT, padx=2)
        ttk.Spinbox(end_time_frame, from_=0, to=59, textvariable=self.end_minute_var, width=5).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def save(self):
        try:
            day = self.day_var.get().lower()
            start_hour = int(self.start_hour_var.get())
            start_minute = int(self.start_minute_var.get())
            end_hour = int(self.end_hour_var.get())
            end_minute = int(self.end_minute_var.get())
            
            if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59 and 
                   0 <= end_hour <= 23 and 0 <= end_minute <= 59):
                messagebox.showerror("Error", "Please enter valid times")
                return
                
            start_time = time(start_hour, start_minute)
            end_time = time(end_hour, end_minute)
            
            if start_time >= end_time:
                messagebox.showerror("Error", "End time must be after start time")
                return
                
            self.result = TimeSlot(day, start_time, end_time)
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            
    def cancel(self):
        self.dialog.destroy()

class CoachManagementDialog(ConfigurationDialog):
    def __init__(self, parent, scheduler):
        super().__init__(parent, "Manage Coaches", scheduler)
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Coach Management", font=('TkDefaultFont', 12, 'bold')).pack(pady=(0, 20))
        
        # List frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Coach list
        self.coach_listbox = tk.Listbox(list_frame, height=10)
        coach_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.coach_listbox.yview)
        self.coach_listbox.configure(yscrollcommand=coach_scrollbar.set)
        
        self.coach_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        coach_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Add Coach", command=self.add_coach).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Edit Coach", command=self.edit_coach).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Coach", command=self.delete_coach).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        self.refresh_list()
        
    def refresh_list(self):
        self.coach_listbox.delete(0, tk.END)
        if self.scheduler and hasattr(self.scheduler, 'coaches'):
            for coach in self.scheduler.coaches:
                self.coach_listbox.insert(tk.END, f"{coach.name} ({coach.max_weekly_classes} classes/week)")
            
    def add_coach(self):
        if not self.scheduler:
            return
        dialog = CoachConfigDialog(self.dialog, self.scheduler)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.scheduler.add_coach(dialog.result)
            self.refresh_list()
            
    def edit_coach(self):
        if not self.scheduler or not hasattr(self.scheduler, 'coaches'):
            return
        selection = self.coach_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a coach to edit")
            return
            
        index = selection[0]
        coach = self.scheduler.coaches[index]
        
        dialog = CoachConfigDialog(self.dialog, self.scheduler, coach)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.scheduler.coaches[index] = dialog.result
            self.refresh_list()
            
    def delete_coach(self):
        if not self.scheduler or not hasattr(self.scheduler, 'coaches'):
            return
        selection = self.coach_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a coach to delete")
            return
            
        index = selection[0]
        coach = self.scheduler.coaches[index]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {coach.name}?"):
            del self.scheduler.coaches[index]
            self.refresh_list()

class TimeSlotManagementDialog(ConfigurationDialog):
    def __init__(self, parent, scheduler):
        super().__init__(parent, "Manage Time Slots", scheduler)
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Time Slot Management", font=('TkDefaultFont', 12, 'bold')).pack(pady=(0, 20))
        
        # List frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Time slot list
        self.slot_listbox = tk.Listbox(list_frame, height=10)
        slot_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.slot_listbox.yview)
        self.slot_listbox.configure(yscrollcommand=slot_scrollbar.set)
        
        self.slot_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        slot_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Add Time Slot", command=self.add_slot).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Edit Time Slot", command=self.edit_slot).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Time Slot", command=self.delete_slot).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        self.refresh_list()
        
    def refresh_list(self):
        self.slot_listbox.delete(0, tk.END)
        if self.scheduler and hasattr(self.scheduler, 'time_slots'):
            for slot in self.scheduler.time_slots:
                self.slot_listbox.insert(tk.END, str(slot))
            
    def add_slot(self):
        if not self.scheduler:
            return
        dialog = TimeSlotConfigDialog(self.dialog, self.scheduler)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.scheduler.add_time_slot(dialog.result)
            self.refresh_list()
            
    def edit_slot(self):
        if not self.scheduler or not hasattr(self.scheduler, 'time_slots'):
            return
        selection = self.slot_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a time slot to edit")
            return
            
        index = selection[0]
        slot = self.scheduler.time_slots[index]
        
        dialog = TimeSlotConfigDialog(self.dialog, self.scheduler, slot)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.scheduler.time_slots[index] = dialog.result
            self.refresh_list()
            
    def delete_slot(self):
        if not self.scheduler or not hasattr(self.scheduler, 'time_slots'):
            return
        selection = self.slot_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a time slot to delete")
            return
            
        index = selection[0]
        slot = self.scheduler.time_slots[index]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {slot}?"):
            del self.scheduler.time_slots[index]
            self.refresh_list()

class AvailableDaysDialog(ConfigurationDialog):
    def __init__(self, parent, scheduler):
        super().__init__(parent, "Manage Available Days", scheduler)
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Available Days", font=('TkDefaultFont', 12, 'bold')).pack(pady=(0, 20))
        
        # Days frame
        days_frame = ttk.Frame(main_frame)
        days_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Day checkboxes
        self.day_vars = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i, day in enumerate(days):
            var = tk.BooleanVar(value=day.lower() in [d.lower() for d in (self.scheduler.available_days if self.scheduler and hasattr(self.scheduler, 'available_days') else [])])
            self.day_vars[day] = var
            ttk.Checkbutton(days_frame, text=day, variable=var).grid(row=i//2, column=i%2, sticky="w", pady=2, padx=10)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT)
        
    def save(self):
        if not self.scheduler:
            return
        selected_days = [day.lower() for day, var in self.day_vars.items() if var.get()]
        self.scheduler.set_available_days(selected_days)
        messagebox.showinfo("Success", f"Available days updated: {', '.join(selected_days).title()}")
        self.dialog.destroy()

class ClassDefinitionConfigDialog(ConfigurationDialog):
    def __init__(self, parent, scheduler, class_def=None):
        super().__init__(parent, "Configure Class Type", scheduler)
        self.class_def = class_def
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Class name
        ttk.Label(main_frame, text="Class Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar(value=self.class_def.name if self.class_def else "")
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # Class type
        ttk.Label(main_frame, text="Class Type:").grid(row=1, column=0, sticky="w", pady=5)
        class_types = [ct.value for ct in ClassType]
        self.class_type_var = tk.StringVar(value=self.class_def.class_type.value if self.class_def else "gi")
        class_type_combo = ttk.Combobox(main_frame, textvariable=self.class_type_var, values=class_types, state="readonly")
        class_type_combo.grid(row=1, column=1, sticky="we", pady=5, padx=(10, 0))
        
        # Sub type
        ttk.Label(main_frame, text="Sub Type:").grid(row=2, column=0, sticky="w", pady=5)
        self.sub_type_var = tk.StringVar(value=self.class_def.sub_type if self.class_def else "")
        ttk.Entry(main_frame, textvariable=self.sub_type_var, width=20).grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Duration
        ttk.Label(main_frame, text="Duration (minutes):").grid(row=3, column=0, sticky="w", pady=5)
        self.duration_var = tk.StringVar(value=str(self.class_def.duration_minutes) if self.class_def else "60")
        ttk.Entry(main_frame, textvariable=self.duration_var, width=10).grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
    def save(self):
        try:
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Class name is required")
                return
                
            class_type = ClassType(self.class_type_var.get())
            sub_type = self.sub_type_var.get().strip() or None
            duration = int(self.duration_var.get())
            
            if duration <= 0:
                messagebox.showerror("Error", "Duration must be positive")
                return
                
            self.result = ClassDefinition(
                class_type=class_type,
                sub_type=sub_type,
                duration_minutes=duration,
                name=name
            )
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            
    def cancel(self):
        self.dialog.destroy()

class ClassDefinitionManagementDialog(ConfigurationDialog):
    def __init__(self, parent, scheduler):
        super().__init__(parent, "Manage Class Types", scheduler)
        self.setup_gui()
        
    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Class Type Management", font=('TkDefaultFont', 12, 'bold')).pack(pady=(0, 20))
        
        # List frame
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Class list
        self.class_listbox = tk.Listbox(list_frame, height=10)
        class_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.class_listbox.yview)
        self.class_listbox.configure(yscrollcommand=class_scrollbar.set)
        
        self.class_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        class_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Add Class Type", command=self.add_class).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Edit Class Type", command=self.edit_class).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Class Type", command=self.delete_class).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        self.refresh_list()
        
    def refresh_list(self):
        self.class_listbox.delete(0, tk.END)
        if self.scheduler and hasattr(self.scheduler, 'class_definitions'):
            for class_def in self.scheduler.class_definitions:
                self.class_listbox.insert(tk.END, f"{class_def.get_display_name()} ({class_def.duration_minutes} min)")
            
    def add_class(self):
        if not self.scheduler:
            return
        dialog = ClassDefinitionConfigDialog(self.dialog, self.scheduler)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.scheduler.add_class_definition(dialog.result)
            self.refresh_list()
            
    def edit_class(self):
        if not self.scheduler or not hasattr(self.scheduler, 'class_definitions'):
            return
        selection = self.class_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a class type to edit")
            return
            
        index = selection[0]
        class_def = self.scheduler.class_definitions[index]
        
        dialog = ClassDefinitionConfigDialog(self.dialog, self.scheduler, class_def)
        self.dialog.wait_window(dialog.dialog)
        if dialog.result:
            self.scheduler.class_definitions[index] = dialog.result
            self.refresh_list()
            
    def delete_class(self):
        if not self.scheduler or not hasattr(self.scheduler, 'class_definitions'):
            return
        selection = self.class_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a class type to delete")
            return
            
        index = selection[0]
        class_def = self.scheduler.class_definitions[index]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {class_def.get_display_name()}?"):
            del self.scheduler.class_definitions[index]
            self.refresh_list()

class ScheduleCalendarGUI:
    def __init__(self, scheduler: BJJScheduler):
        self.scheduler = scheduler
        self.current_schedule = []
        self.current_conflicts = []
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("BJJ Class Schedule")
        self.root.geometry("1200x800")
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel for controls
        control_frame = ttk.LabelFrame(main_frame, text="Schedule Controls", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Configuration buttons
        config_frame = ttk.LabelFrame(control_frame, text="Configuration", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(config_frame, text="Manage Coaches", 
                  command=self.manage_coaches).pack(fill=tk.X, pady=2)
        ttk.Button(config_frame, text="Manage Time Slots", 
                  command=self.manage_time_slots).pack(fill=tk.X, pady=2)
        ttk.Button(config_frame, text="Manage Class Types", 
                  command=self.manage_class_types).pack(fill=tk.X, pady=2)
        ttk.Button(config_frame, text="Manage Available Days", 
                  command=self.manage_available_days).pack(fill=tk.X, pady=2)
        
        # Schedule mode selection
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mode_frame, text="Schedule Mode:").pack(anchor=tk.W, pady=(0, 5))
        self.mode_var = tk.StringVar(value="balanced")
        ttk.Radiobutton(mode_frame, text="Balanced", variable=self.mode_var, 
                       value="balanced").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Sequential", variable=self.mode_var, 
                       value="sequential").pack(anchor=tk.W)
        
        # Class requirements
        req_frame = ttk.Frame(control_frame)
        req_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(req_frame, text="Class Requirements:", font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        self.requirements_vars = {}
        req_fields = [
            ("Gi Foundations", "gi_foundations"),
            ("Gi Essentials", "gi_essentials"),
            ("Gi Advanced", "gi_advanced"),
            ("Gi Team Training", "gi_team_training"),
            ("No-Gi Foundations", "nogi_foundations"),
            ("No-Gi Essentials", "nogi_essentials"),
            ("Open Mat", "open_mat")
        ]
        
        for label, key in req_fields:
            field_frame = ttk.Frame(req_frame)
            field_frame.pack(fill=tk.X, pady=2)
            ttk.Label(field_frame, text=f"{label}:").pack(side=tk.LEFT)
            var = tk.StringVar(value="0")
            self.requirements_vars[key] = var
            entry = ttk.Entry(field_frame, textvariable=var, width=5)
            entry.pack(side=tk.RIGHT)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Generate Schedule", 
                  command=self.generate_schedule).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Export to iCalendar", 
                  command=self.export_icalendar).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Save as CSV", 
                  command=self.export_csv).pack(pady=5, fill=tk.X)
        
        # Calendar display frame
        calendar_frame = ttk.LabelFrame(main_frame, text="Weekly Schedule", padding="10")
        calendar_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        calendar_frame.columnconfigure(0, weight=1)
        calendar_frame.rowconfigure(0, weight=1)
        
        # Create calendar widget
        self.create_calendar_widget(calendar_frame)
        
        # Conflicts display
        conflicts_frame = ttk.LabelFrame(main_frame, text="Scheduling Conflicts", padding="10")
        conflicts_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        conflicts_frame.columnconfigure(0, weight=1)
        conflicts_frame.rowconfigure(0, weight=1)
        
        self.conflicts_text = tk.Text(conflicts_frame, height=6, wrap=tk.WORD)
        conflicts_scrollbar = ttk.Scrollbar(conflicts_frame, orient=tk.VERTICAL, command=self.conflicts_text.yview)
        self.conflicts_text.configure(yscrollcommand=conflicts_scrollbar.set)
        
        self.conflicts_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        conflicts_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def create_calendar_widget(self, parent):
        # Create frame for calendar
        self.calendar_frame = ttk.Frame(parent)
        self.calendar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Days of week headers
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_frame, text=day, font=('TkDefaultFont', 10, 'bold'))
            label.grid(row=0, column=i, padx=2, pady=2, sticky=(tk.W, tk.E))
            self.calendar_frame.columnconfigure(i, weight=1)
        
        # Create frames for each day
        self.day_frames = {}
        for i, day in enumerate(days):
            frame = ttk.Frame(self.calendar_frame, relief=tk.SUNKEN, borderwidth=1)
            frame.grid(row=1, column=i, padx=2, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.day_frames[day.lower()] = frame
            
        self.calendar_frame.rowconfigure(1, weight=1)
        
    def update_calendar_display(self):
        # Clear existing content
        for frame in self.day_frames.values():
            for widget in frame.winfo_children():
                widget.destroy()
        
        if not self.current_schedule:
            return
            
        # Group schedule by day
        days_schedule = {}
        for sc in self.current_schedule:
            day = sc.time_slot.day.lower()
            if day not in days_schedule:
                days_schedule[day] = []
            days_schedule[day].append(sc)
        
        # Sort each day by time
        for day in days_schedule:
            days_schedule[day].sort(key=lambda sc: sc.time_slot.start_time)
        
        # Add classes to calendar
        for day, classes in days_schedule.items():
            if day in self.day_frames:
                frame = self.day_frames[day]
                
                for i, sc in enumerate(classes):
                    # Create class widget
                    class_frame = ttk.Frame(frame, relief=tk.RAISED, borderwidth=1)
                    class_frame.pack(fill=tk.X, padx=2, pady=1)
                    
                    # Time
                    time_label = ttk.Label(class_frame, 
                                         text=f"{sc.time_slot.start_time.strftime('%H:%M')}-{sc.time_slot.end_time.strftime('%H:%M')}",
                                         font=('TkDefaultFont', 8, 'bold'))
                    time_label.pack()
                    
                    # Class type
                    class_label = ttk.Label(class_frame, text=str(sc.class_def), 
                                          font=('TkDefaultFont', 8))
                    class_label.pack()
                    
                    # Coach
                    coach_label = ttk.Label(class_frame, text=sc.coach.name, 
                                          font=('TkDefaultFont', 7))
                    coach_label.pack()
                    
                    # Fixed indicator
                    if sc.is_fixed:
                        fixed_label = ttk.Label(class_frame, text="[FIXED]", 
                                              font=('TkDefaultFont', 7), foreground='red')
                        fixed_label.pack()
                    
                    # Color coding
                    if sc.class_def.class_type == ClassType.GI:
                        class_frame.configure(style='Gi.TFrame')
                    elif sc.class_def.class_type == ClassType.NO_GI:
                        class_frame.configure(style='NoGi.TFrame')
                    else:
                        class_frame.configure(style='OpenMat.TFrame')
    
    def generate_schedule(self):
        # Set schedule mode
        mode = ScheduleMode.BALANCED if self.mode_var.get() == "balanced" else ScheduleMode.SEQUENTIAL
        self.scheduler.set_schedule_mode(mode)
        
        # Get requirements
        try:
            class_requirements = {}
            for key, var in self.requirements_vars.items():
                count = int(var.get())
                if count > 0:
                    # Map old keys to class names
                    class_name_map = {
                        "gi_foundations": "Gi Foundations",
                        "gi_essentials": "Gi Essentials", 
                        "gi_advanced": "Gi Advanced",
                        "gi_team_training": "Gi Team Training",
                        "nogi_foundations": "No-Gi Foundations",
                        "nogi_essentials": "No-Gi Essentials",
                        "open_mat": "Open Mat"
                    }
                    class_name = class_name_map.get(key, key)
                    class_requirements[class_name] = count
                    
            requirements = ScheduleRequirements(class_requirements=class_requirements)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all requirements")
            return
        
        # Generate schedule
        self.current_schedule, self.current_conflicts = self.scheduler.generate_schedule(requirements)
        
        # Update displays
        self.update_calendar_display()
        self.update_conflicts_display()
        
        messagebox.showinfo("Success", f"Schedule generated with {len(self.current_schedule)} classes")
    
    def update_conflicts_display(self):
        self.conflicts_text.delete(1.0, tk.END)
        if self.current_conflicts:
            self.conflicts_text.insert(tk.END, "Scheduling conflicts found:\n\n")
            for conflict in self.current_conflicts:
                self.conflicts_text.insert(tk.END, f"• {conflict}\n")
        else:
            self.conflicts_text.insert(tk.END, "No scheduling conflicts found.")
    
    def export_icalendar(self):
        if not self.current_schedule:
            messagebox.showwarning("Warning", "Please generate a schedule first")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar files", "*.ics"), ("All files", "*.*")],
            title="Save iCalendar file"
        )
        
        if filename:
            try:
                self.scheduler.save_icalendar_file(self.current_schedule, filename)
                messagebox.showinfo("Success", f"Schedule exported to {filename}\n\nDouble-click the file to add to your Mac Calendar!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export schedule: {str(e)}")
    
    def export_csv(self):
        if not self.current_schedule:
            messagebox.showwarning("Warning", "Please generate a schedule first")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV file"
        )
        
        if filename:
            try:
                self.save_csv_file(filename)
                messagebox.showinfo("Success", f"Schedule exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def save_csv_file(self, filename: str):
        """Save schedule as CSV file"""
        import csv
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Day', 'Start Time', 'End Time', 'Class Type', 'Coach', 'Fixed'])
            
            for sc in sorted(self.current_schedule, key=lambda x: (x.time_slot.day, x.time_slot.start_time)):
                writer.writerow([
                    sc.time_slot.day.title(),
                    sc.time_slot.start_time.strftime('%H:%M'),
                    sc.time_slot.end_time.strftime('%H:%M'),
                    str(sc.class_def),
                    sc.coach.name,
                    'Yes' if sc.is_fixed else 'No'
                ])
    
    def manage_coaches(self):
        """Open coach management dialog"""
        dialog = CoachManagementDialog(self.root, self.scheduler)
        self.root.wait_window(dialog.dialog)
        
    def manage_time_slots(self):
        """Open time slot management dialog"""
        dialog = TimeSlotManagementDialog(self.root, self.scheduler)
        self.root.wait_window(dialog.dialog)
        
    def manage_class_types(self):
        """Open class type management dialog"""
        dialog = ClassDefinitionManagementDialog(self.root, self.scheduler)
        self.root.wait_window(dialog.dialog)
        
    def manage_available_days(self):
        """Open available days management dialog"""
        dialog = AvailableDaysDialog(self.root, self.scheduler)
        self.root.wait_window(dialog.dialog)
        
    def run(self):
        self.root.mainloop()

# Example usage
if __name__ == "__main__":
    # Create scheduler with empty configuration
    scheduler = BJJScheduler()
    
    # Launch GUI - users can configure everything through the UI
    app = ScheduleCalendarGUI(scheduler)
    app.run()
