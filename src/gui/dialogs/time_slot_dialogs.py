import tkinter as tk
from tkinter import ttk, messagebox
from datetime import time

from ...models.data_classes import TimeSlot
from .base_dialog import ConfigurationDialog

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