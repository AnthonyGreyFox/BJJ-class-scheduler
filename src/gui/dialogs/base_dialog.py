import tkinter as tk
from tkinter import ttk
import datetime
from tkinter import messagebox
from src.models.data_classes import ScheduledClass, TimeSlot
from src.models.enums import ClassType

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

class ExportOptionsDialog(ConfigurationDialog):
    def __init__(self, parent):
        super().__init__(parent, "Export Options")
        self.result = None
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Start date
        ttk.Label(main_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=5)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.start_date_var = tk.StringVar(value=today_str)
        ttk.Entry(main_frame, textvariable=self.start_date_var, width=15).grid(row=0, column=1, sticky="w", pady=5, padx=(10, 0))

        # Number of weeks
        ttk.Label(main_frame, text="Number of Weeks:").grid(row=1, column=0, sticky="w", pady=5)
        self.weeks_var = tk.StringVar(value="4")
        weeks_combo = ttk.Combobox(main_frame, textvariable=self.weeks_var, values=["1", "2", "4"], state="readonly", width=5)
        weeks_combo.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="OK", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)

        main_frame.columnconfigure(1, weight=1)

    def save(self):
        try:
            start_date = datetime.datetime.strptime(self.start_date_var.get(), "%Y-%m-%d").date()
            weeks = int(self.weeks_var.get())
            self.result = {"start_date": start_date, "weeks": weeks}
            self.dialog.destroy()
        except Exception:
            messagebox.showerror("Error", "Please enter a valid date (YYYY-MM-DD) and number of weeks.")

    def cancel(self):
        self.result = None
        self.dialog.destroy() 

class ManualAssignmentDialog(ConfigurationDialog):
    def __init__(self, parent, scheduler):
        super().__init__(parent, "Manual Assignment", scheduler)
        self.result = None
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Day selection
        ttk.Label(main_frame, text="Day:").grid(row=0, column=0, sticky="w", pady=5)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.day_var = tk.StringVar(value=days[0])
        day_combo = ttk.Combobox(main_frame, textvariable=self.day_var, values=days, state="readonly")
        day_combo.grid(row=0, column=1, sticky="we", pady=5, padx=(10, 0))

        # Start time
        ttk.Label(main_frame, text="Start Time (HH:MM):").grid(row=1, column=0, sticky="w", pady=5)
        self.start_time_var = tk.StringVar(value="13:00")
        ttk.Entry(main_frame, textvariable=self.start_time_var, width=10).grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))

        # End time
        ttk.Label(main_frame, text="End Time (HH:MM):").grid(row=2, column=0, sticky="w", pady=5)
        self.end_time_var = tk.StringVar(value="14:00")
        ttk.Entry(main_frame, textvariable=self.end_time_var, width=10).grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))

        # Class type
        ttk.Label(main_frame, text="Class:").grid(row=3, column=0, sticky="w", pady=5)
        class_names = [c.get_display_name() for c in self.scheduler.class_definitions] if self.scheduler else []
        self.class_var = tk.StringVar(value=class_names[0] if class_names else "")
        class_combo = ttk.Combobox(main_frame, textvariable=self.class_var, values=class_names, state="readonly")
        class_combo.grid(row=3, column=1, sticky="we", pady=5, padx=(10, 0))

        # Coach
        ttk.Label(main_frame, text="Coach:").grid(row=4, column=0, sticky="w", pady=5)
        coach_names = [c.name for c in self.scheduler.coaches] if self.scheduler else []
        self.coach_var = tk.StringVar(value=coach_names[0] if coach_names else "")
        coach_combo = ttk.Combobox(main_frame, textvariable=self.coach_var, values=coach_names, state="readonly")
        coach_combo.grid(row=4, column=1, sticky="we", pady=5, padx=(10, 0))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="OK", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT)

        main_frame.columnconfigure(1, weight=1)

    def save(self):
        try:
            day = self.day_var.get().lower()
            start_time = datetime.datetime.strptime(self.start_time_var.get(), "%H:%M").time()
            end_time = datetime.datetime.strptime(self.end_time_var.get(), "%H:%M").time()
            if start_time >= end_time:
                messagebox.showerror("Error", "End time must be after start time")
                return
            class_name = self.class_var.get()
            coach_name = self.coach_var.get()
            class_def = next((c for c in self.scheduler.class_definitions if c.get_display_name() == class_name), None) if self.scheduler else None
            coach = next((c for c in self.scheduler.coaches if c.name == coach_name), None) if self.scheduler else None
            if not class_def or not coach:
                messagebox.showerror("Error", "Please select a valid class and coach")
                return
            time_slot = TimeSlot(day=day, start_time=start_time, end_time=end_time)
            self.result = ScheduledClass(class_def=class_def, time_slot=time_slot, coach=coach, is_fixed=True)
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def cancel(self):
        self.result = None
        self.dialog.destroy() 