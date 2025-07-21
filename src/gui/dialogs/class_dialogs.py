import tkinter as tk
from tkinter import ttk, messagebox

from ...models.data_classes import ClassDefinition
from ...models.enums import ClassType
from .base_dialog import ConfigurationDialog

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
        
        # Duration
        ttk.Label(main_frame, text="Duration (minutes):").grid(row=2, column=0, sticky="w", pady=5)
        self.duration_var = tk.StringVar(value=str(self.class_def.duration_minutes) if self.class_def else "60")
        ttk.Entry(main_frame, textvariable=self.duration_var, width=10).grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))

        # Weekly count
        ttk.Label(main_frame, text="Weekly Classes:").grid(row=3, column=0, sticky="w", pady=5)
        self.weekly_count_var = tk.StringVar(value=str(self.class_def.weekly_count) if self.class_def else "0")
        ttk.Entry(main_frame, textvariable=self.weekly_count_var, width=10).grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))
        
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
            duration = int(self.duration_var.get())
            weekly_count = int(self.weekly_count_var.get())
            
            if duration <= 0:
                messagebox.showerror("Error", "Duration must be positive")
                return
            if weekly_count < 0:
                messagebox.showerror("Error", "Weekly classes must be zero or positive")
                return
                
            self.result = ClassDefinition(
                name=name,
                class_type=class_type,
                duration_minutes=duration,
                weekly_count=weekly_count
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
                self.class_listbox.insert(tk.END, f"{class_def.get_display_name()} ({class_def.duration_minutes} min, {class_def.weekly_count} per week)")
            
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