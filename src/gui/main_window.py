import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List
from datetime import time

from ..models.scheduler import BJJScheduler
from ..models.data_classes import ScheduleRequirements
from ..models.enums import ClassType, ScheduleMode
from ..utils.export import save_csv_file
from .dialogs.coach_dialogs import CoachManagementDialog
from .dialogs.time_slot_dialogs import TimeSlotManagementDialog
from .dialogs.class_dialogs import ClassDefinitionManagementDialog
from .dialogs.base_dialog import ExportOptionsDialog

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
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel for controls
        control_frame = ttk.LabelFrame(main_frame, text="Schedule Controls", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10))
        
        # Configuration buttons
        config_frame = ttk.LabelFrame(control_frame, text="Configuration", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(config_frame, text="Manage Coaches", 
                  command=self.manage_coaches).pack(fill=tk.X, pady=2)
        ttk.Button(config_frame, text="Manage Time Slots", 
                  command=self.manage_time_slots).pack(fill=tk.X, pady=2)
        ttk.Button(config_frame, text="Manage Class Types", 
                  command=self.manage_class_types).pack(fill=tk.X, pady=2)
        
        # Schedule mode selection
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(mode_frame, text="Schedule Mode:").pack(anchor=tk.W, pady=(0, 5))
        self.mode_var = tk.StringVar(value="balanced")
        ttk.Radiobutton(mode_frame, text="Balanced", variable=self.mode_var, 
                       value="balanced").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Sequential", variable=self.mode_var, 
                       value="sequential").pack(anchor=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Generate Schedule", 
                  command=self.generate_schedule).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Manual Assignment", 
                  command=self.manual_assignment).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Export to iCalendar", 
                  command=self.export_icalendar).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Save as CSV", 
                  command=self.export_csv).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Save Settings", 
                  command=self.save_settings).pack(pady=5, fill=tk.X)
        ttk.Button(button_frame, text="Load Settings", 
                  command=self.load_settings).pack(pady=5, fill=tk.X)
        
        # Calendar display frame
        calendar_frame = ttk.LabelFrame(main_frame, text="Weekly Schedule", padding="10")
        calendar_frame.grid(row=0, column=1, sticky="nsew")
        calendar_frame.columnconfigure(0, weight=1)
        calendar_frame.rowconfigure(0, weight=1)
        
        # Create calendar widget
        self.create_calendar_widget(calendar_frame)
        
        # Conflicts display
        conflicts_frame = ttk.LabelFrame(main_frame, text="Scheduling Conflicts", padding="10")
        conflicts_frame.grid(row=1, column=1, sticky="nsew", pady=(10, 0))
        conflicts_frame.columnconfigure(0, weight=1)
        conflicts_frame.rowconfigure(0, weight=1)
        
        self.conflicts_text = tk.Text(conflicts_frame, height=6, wrap=tk.WORD)
        conflicts_scrollbar = ttk.Scrollbar(conflicts_frame, orient=tk.VERTICAL, command=self.conflicts_text.yview)
        self.conflicts_text.configure(yscrollcommand=conflicts_scrollbar.set)
        
        self.conflicts_text.grid(row=0, column=0, sticky="nsew")
        conflicts_scrollbar.grid(row=0, column=1, sticky="ns")
        
    def create_calendar_widget(self, parent):
        # Create frame for calendar
        self.calendar_frame = ttk.Frame(parent)
        self.calendar_frame.grid(row=0, column=0, sticky="nsew")
        
        # Days of week headers
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day in enumerate(days):
            label = ttk.Label(self.calendar_frame, text=day, font=('TkDefaultFont', 10, 'bold'))
            label.grid(row=0, column=i, padx=2, pady=2, sticky="we")
            self.calendar_frame.columnconfigure(i, weight=1)
        
        # Create frames for each day
        self.day_frames = {}
        for i, day in enumerate(days):
            frame = ttk.Frame(self.calendar_frame, relief=tk.SUNKEN, borderwidth=1)
            frame.grid(row=1, column=i, padx=2, pady=2, sticky="nsew")
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
                    
                    # Calculate actual class start and end times based on position in slot
                    
                    # Calculate start time based on position and previous classes
                    slot_start_minutes = sc.time_slot.start_time.hour * 60 + sc.time_slot.start_time.minute
                    class_start_minutes = slot_start_minutes
                    
                    # Add time from previous classes in this slot
                    for prev_sc in classes[:i]:
                        if prev_sc.time_slot == sc.time_slot:
                            class_start_minutes += prev_sc.class_def.duration_minutes
                    
                    # Calculate end time
                    class_end_minutes = class_start_minutes + sc.class_def.duration_minutes
                    
                    # Convert back to time objects
                    class_start_hour = class_start_minutes // 60
                    class_start_minute = class_start_minutes % 60
                    class_end_hour = class_end_minutes // 60
                    class_end_minute = class_end_minutes % 60
                    
                    class_start_time = time(class_start_hour, class_start_minute)
                    class_end_time = time(class_end_hour, class_end_minute)
                    
                    # Display actual class times
                    time_label = ttk.Label(class_frame, 
                                         text=f"{class_start_time.strftime('%H:%M')}-{class_end_time.strftime('%H:%M')}",
                                         font=('TkDefaultFont', 8, 'bold'))
                    time_label.pack()
                    
                    # Class type with duration
                    class_text = f"{sc.class_def.get_display_name()} ({sc.class_def.duration_minutes}min)"
                    class_label = ttk.Label(class_frame, text=class_text, 
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
        # Generate schedule using class_definitions' weekly_count
        self.current_schedule, self.current_conflicts = self.scheduler.generate_schedule()
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
        # Show export options dialog
        dialog = ExportOptionsDialog(self.root)
        self.root.wait_window(dialog.dialog)
        if not dialog.result:
            return
        start_date = dialog.result["start_date"]
        weeks = dialog.result["weeks"]
        filename = filedialog.asksaveasfilename(
            defaultextension=".ics",
            filetypes=[("iCalendar files", "*.ics"), ("All files", "*.*")],
            title="Save iCalendar file"
        )
        if filename:
            try:
                self.scheduler.save_icalendar_file(self.current_schedule, filename, start_date=start_date, weeks=weeks)
                messagebox.showinfo("Success", f"Schedule exported to {filename}\n\nDouble-click the file to add to your Mac Calendar!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export schedule: {str(e)}")
    
    def export_csv(self):
        if not self.current_schedule:
            messagebox.showwarning("Warning", "Please generate a schedule first")
            return
        # Show export options dialog
        dialog = ExportOptionsDialog(self.root)
        self.root.wait_window(dialog.dialog)
        if not dialog.result:
            return
        start_date = dialog.result["start_date"]
        weeks = dialog.result["weeks"]
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV file"
        )
        if filename:
            try:
                save_csv_file(filename, self.current_schedule, start_date=start_date, weeks=weeks)
                messagebox.showinfo("Success", f"Schedule exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def manage_coaches(self):
        """Open coach management dialog"""
        dialog = CoachManagementDialog(self.root, self.scheduler)
        self.root.wait_window(dialog.dialog)
        self.current_schedule = []
        self.current_conflicts = []
        self.update_calendar_display()
        self.update_conflicts_display()

    def manage_time_slots(self):
        """Open time slot management dialog"""
        dialog = TimeSlotManagementDialog(self.root, self.scheduler)
        self.root.wait_window(dialog.dialog)
        self.current_schedule = []
        self.current_conflicts = []
        self.update_calendar_display()
        self.update_conflicts_display()

    def manage_class_types(self):
        """Open class type management dialog"""
        dialog = ClassDefinitionManagementDialog(self.root, self.scheduler)
        self.root.wait_window(dialog.dialog)
        self.current_schedule = []
        self.current_conflicts = []
        self.update_calendar_display()
        self.update_conflicts_display()
        
    def run(self):
        self.root.mainloop() 

    def save_settings(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Configuration as JSON"
        )
        if filepath:
            try:
                self.scheduler.save_to_json(filepath)
                messagebox.showinfo("Success", f"Configuration saved to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_settings(self):
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Configuration from JSON"
        )
        if filepath:
            try:
                self.scheduler.load_from_json(filepath)
                self.current_schedule = []
                self.current_conflicts = []
                self.update_calendar_display()
                self.update_conflicts_display()
                messagebox.showinfo("Success", f"Configuration loaded from {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {str(e)}") 

    def manual_assignment(self):
        from .dialogs.base_dialog import ManualAssignmentDialog
        dialog = ManualAssignmentDialog(self.root, self.scheduler)
        self.root.wait_window(dialog.dialog)
        if dialog.result:
            # Add the fixed class to the scheduler
            self.scheduler.add_fixed_class(dialog.result)
            self.current_schedule = []
            self.current_conflicts = []
            self.update_calendar_display()
            self.update_conflicts_display() 