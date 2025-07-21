import tkinter as tk
from tkinter import ttk, messagebox

from ...models.data_classes import Coach
from .base_dialog import ConfigurationDialog

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
        
        # Available days
        ttk.Label(main_frame, text="Available Days:").grid(row=3, column=0, sticky="w", pady=5)
        days_frame = ttk.Frame(main_frame)
        days_frame.grid(row=3, column=1, sticky="we", pady=5, padx=(10, 0))
        self.day_vars = {}
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, day in enumerate(days):
            var = tk.BooleanVar(value=day.lower() in (self.coach.available_days if self.coach else days))
            self.day_vars[day] = var
            ttk.Checkbutton(days_frame, text=day, variable=var).pack(anchor=tk.W, pady=1)
        
        # Can teach options
        ttk.Label(main_frame, text="Can Teach:").grid(row=4, column=0, sticky="w", pady=5)
        teach_frame = ttk.Frame(main_frame)
        teach_frame.grid(row=4, column=1, sticky="we", pady=5, padx=(10, 0))
        
        self.can_teach_gi_var = tk.BooleanVar(value=self.coach.can_teach_gi if self.coach else True)
        self.can_teach_nogi_var = tk.BooleanVar(value=self.coach.can_teach_nogi if self.coach else True)
        self.can_teach_open_mat_var = tk.BooleanVar(value=self.coach.can_teach_open_mat if self.coach else True)
        
        ttk.Checkbutton(teach_frame, text="Gi", variable=self.can_teach_gi_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(teach_frame, text="No-Gi", variable=self.can_teach_nogi_var).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(teach_frame, text="Open Mat", variable=self.can_teach_open_mat_var).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
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
                
            # Get available days
            available_days = []
            for day, var in self.day_vars.items():
                if var.get():
                    available_days.append(day.lower())
            if not available_days:
                messagebox.showerror("Error", "At least one available day must be selected")
                return
            self.result = Coach(
                name=name,
                max_weekly_classes=max_classes,
                preferred_times=preferred_times,
                available_days=available_days,
                can_teach_gi=self.can_teach_gi_var.get(),
                can_teach_nogi=self.can_teach_nogi_var.get(),
                can_teach_open_mat=self.can_teach_open_mat_var.get()
            )
            
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
                days_str = ", ".join([day.title() for day in coach.available_days])
                self.coach_listbox.insert(tk.END, f"{coach.name} ({coach.max_weekly_classes} classes/week) - {days_str}")
            
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