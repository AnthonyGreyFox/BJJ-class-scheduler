import random
from typing import List, Dict, Optional, Tuple
from datetime import datetime, time, date, timedelta
import json
from pathlib import Path

from .enums import ClassType, GiSubType, NoGiSubType, ScheduleMode
from .data_classes import TimeSlot, Coach, ClassDefinition, ScheduledClass, ScheduleRequirements, get_default_configuration

class BJJScheduler:
    def __init__(self):
        self.coaches: List[Coach] = []
        self.time_slots: List[TimeSlot] = []
        self.fixed_classes: List[ScheduledClass] = []
        self.schedule_mode: ScheduleMode = ScheduleMode.BALANCED
        self.class_definitions: List[ClassDefinition] = []
        self.load_default()
    
    def add_coach(self, coach: Coach):
        self.coaches.append(coach)
        
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
            
        # Check day availability
        if time_slot.day.lower() not in [day.lower() for day in coach.available_days]:
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
        # Allow a coach to teach multiple classes in the same slot (back-to-back)
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
        
        return classes
        
    def _sort_classes_for_scheduling(self, classes: List[ClassDefinition]) -> List[ClassDefinition]:
        """Sort classes based on scheduling mode"""
        if self.schedule_mode == ScheduleMode.SEQUENTIAL:
            # Group by type (gi, no-gi, open-mat)
            return sorted(classes, key=lambda c: c.class_type.value)
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
        
    def _get_class_count_in_slot(self, time_slot: TimeSlot, current_schedule: List[ScheduledClass]) -> int:
        """Get the number of classes already scheduled in a time slot"""
        count = 0
        for sc in current_schedule:
            if sc.time_slot == time_slot:
                count += 1
        return count
        
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
        
    def generate_schedule(self, manual_assignments=None) -> Tuple[List[ScheduledClass], List[str]]:
        """Generate a schedule with manual assignments and slot preferences"""
        schedule = []
        conflicts = []
        manual_assignments = manual_assignments or []
        # 1. Place manual assignments first
        used_slots = set()
        used_classes = set()
        for ma in manual_assignments:
            # ma: dict with keys: class_def, time_slot, coach
            sc = ScheduledClass(ma['class_def'], ma['time_slot'], ma['coach'], is_fixed=True)
            schedule.append(sc)
            used_slots.add(ma['time_slot'])
            used_classes.add(ma['class_def'])
        # 2. Prepare slots by preference
        slots_by_pref = {'gi': [], 'no-gi': [], 'open-mat': [], None: []}
        for slot in self.time_slots:
            if slot in used_slots:
                continue
            pref = slot.primary_preference if slot.primary_preference else None
            slots_by_pref.setdefault(pref, []).append(slot)
        # 3. Prepare classes by type (excluding manual assignments)
        classes_by_type = {'gi': [], 'no-gi': [], 'open-mat': []}
        for class_def in self.class_definitions:
            if class_def in used_classes:
                continue
            for _ in range(class_def.weekly_count):
                classes_by_type[class_def.class_type.value].append(class_def)
        # 4. Distribute classes to preferred slots
        def assign_classes_to_slots(class_type, slots):
            assigned = set()
            slot_idx = 0
            for class_def in classes_by_type[class_type]:
                # Find a slot with enough space and a coach
                for _ in range(len(slots)):
                    slot = slots[slot_idx % len(slots)]
                    # Find a coach
                    for coach in self.coaches:
                        if self._can_coach_teach_class(coach, class_def, slot) and self._get_coach_current_load(coach, schedule) < coach.max_weekly_classes:
                            # Check available time
                            if self._get_available_time_in_slot(slot, schedule) >= class_def.duration_minutes:
                                sc = ScheduledClass(class_def, slot, coach)
                                schedule.append(sc)
                                assigned.add(class_def)
                                break
                    slot_idx += 1
                    if class_def in assigned:
                        break
            # Remove assigned classes
            classes_by_type[class_type] = [c for c in classes_by_type[class_type] if c not in assigned]
        # Assign by primary preference
        for ct in ['gi', 'no-gi', 'open-mat']:
            assign_classes_to_slots(ct, slots_by_pref.get(ct, []))
        # Assign by secondary preference
        for slot in self.time_slots:
            if slot in used_slots:
                continue
            sec = slot.secondary_preference
            if sec and sec in classes_by_type:
                assign_classes_to_slots(sec, [slot])
        # Assign remaining classes to no-preference slots
        for ct in ['gi', 'no-gi', 'open-mat']:
            assign_classes_to_slots(ct, slots_by_pref.get(None, []))
        # 5. Fill any remaining space in any slot
        for ct in ['gi', 'no-gi', 'open-mat']:
            for slot in self.time_slots:
                if slot in used_slots:
                    continue
                assign_classes_to_slots(ct, [slot])
        # 6. Report unfilled slots
        for slot in self.time_slots:
            if self._get_available_time_in_slot(slot, schedule) > 0:
                conflicts.append(f"Could not fill all time in slot {slot}")
        # 7. Report unassigned classes
        for ct, clist in classes_by_type.items():
            if clist:
                conflicts.append(f"Unassigned {ct} classes: {len(clist)}")
        # 8. Assign slot_position for each class in a slot
        from collections import defaultdict
        slot_groups = defaultdict(list)
        for sc in schedule:
            slot_groups[sc.time_slot].append(sc)
        for slot, sc_list in slot_groups.items():
            # Sort by class_def name for determinism, or keep as is for order of assignment
            sc_list.sort(key=lambda sc: sc.class_def.name)
            for i, sc in enumerate(sc_list):
                sc.slot_position = i
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
            week_date = start_date + timedelta(weeks=week)
            
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
                uid = f"{start_str}-{sc.class_def.class_type.value}-main@bjjclub.local"
                
                # Add event
                ical_content.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART:{start_str}",
                    f"DTEND:{end_str}",
                    f"SUMMARY:{sc.class_def}",
                    f"DESCRIPTION:Coach: {sc.coach.name}" + ("\\nFixed Class" if sc.is_fixed else ""),
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

    def to_dict(self):
        return {
            "coaches": [vars(c) for c in self.coaches],
            "time_slots": [
                {
                    "day": ts.day,
                    "start_time": ts.start_time.strftime("%H:%M"),
                    "end_time": ts.end_time.strftime("%H:%M"),
                    "primary_preference": ts.primary_preference,
                    "secondary_preference": ts.secondary_preference
                } for ts in self.time_slots
            ],
            "class_definitions": [
                {"name": cd.name, "class_type": cd.class_type.value, "duration_minutes": cd.duration_minutes, "weekly_count": cd.weekly_count} for cd in self.class_definitions
            ]
        }

    def from_dict(self, data):
        from .enums import ClassType
        from datetime import time
        self.coaches = [Coach(**c) for c in data.get("coaches", [])]
        self.time_slots = [
            TimeSlot(
                day=ts["day"],
                start_time=time.fromisoformat(ts["start_time"]),
                end_time=time.fromisoformat(ts["end_time"]),
                primary_preference=ts.get("primary_preference"),
                secondary_preference=ts.get("secondary_preference")
            ) for ts in data.get("time_slots", [])
        ]
        self.class_definitions = [
            ClassDefinition(
                name=cd["name"],
                class_type=ClassType(cd["class_type"]),
                duration_minutes=cd.get("duration_minutes", 60),
                weekly_count=cd.get("weekly_count", 0)
            ) for cd in data.get("class_definitions", [])
        ]

    def save_to_json(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_json(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        self.from_dict(data)

    def load_default(self):
        data = get_default_configuration()
        self.coaches = data["coaches"]
        self.time_slots = data["time_slots"]
        self.class_definitions = data["class_definitions"] 