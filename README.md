# BJJ Class Scheduler

A comprehensive Brazilian Jiu-Jitsu class scheduling application that helps gym owners and coaches create balanced weekly schedules. The application features a modern GUI interface and supports dynamic class scheduling with configurable class types, coaches, and time slots.

## 🏗️ Project Structure

The application has been refactored into a modular structure for better maintainability and organization:

```
bjj_schedular/
├── README.md                 # This file
├── main.py                   # Application entry point
├── requirements.txt          # Dependencies (none external required)
├── bjj_scheduler.py         # Original single-file version (kept for reference)
└── src/                     # Modular source code
    ├── __init__.py
    ├── models/              # Data models and business logic
    │   ├── __init__.py
    │   ├── enums.py         # Enumerations (ClassType, ScheduleMode, etc.)
    │   ├── data_classes.py  # Data classes (TimeSlot, Coach, ClassDefinition, etc.)
    │   └── scheduler.py     # Core scheduling logic (BJJScheduler class)
    ├── gui/                 # User interface components
    │   ├── __init__.py
    │   ├── main_window.py   # Main application window
    │   ├── dialogs/         # Configuration dialogs
    │   │   ├── __init__.py
    │   │   ├── base_dialog.py      # Base dialog class
    │   │   ├── coach_dialogs.py    # Coach management dialogs
    │   │   ├── time_slot_dialogs.py # Time slot management dialogs
    │   │   ├── class_dialogs.py    # Class type management dialogs
    │   │   └── days_dialog.py      # Available days dialog
    │   └── widgets/         # Reusable UI components
    │       └── __init__.py
    └── utils/               # Utility functions
        ├── __init__.py
        └── export.py        # Export functionality (CSV, iCalendar)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (uses only Python standard library)

### Installation
1. Clone or download the project
2. Navigate to the project directory
3. Run the application:

```bash
python3 main.py
```

## 🎯 Key Features

### **Dynamic Class Scheduling**
- **Configurable Class Types**: Create custom class types with names, durations, and categories
- **Flexible Time Slots**: Schedule multiple classes within longer time slots based on class durations
- **Smart Scheduling**: Automatically fills time slots with classes according to balanced or sequential modes

### **Comprehensive Configuration**
- **Coach Management**: Add, edit, and remove coaches with preferences and capabilities
- **Time Slot Management**: Configure available time slots for each day
- **Class Type Management**: Define custom class types with durations
- **Available Days**: Select which days classes can be scheduled

### **Export Options**
- **iCalendar (.ics)**: Export schedules for calendar applications
- **CSV Export**: Export schedules in spreadsheet format
- **Multi-week Support**: Generate schedules for multiple weeks

### **User-Friendly Interface**
- **Visual Calendar**: Weekly schedule display with color-coded class types
- **Conflict Detection**: Automatic detection and display of scheduling conflicts
- **Real-time Updates**: Immediate feedback on schedule generation

## 📋 Usage Guide

### 1. Initial Setup
1. Launch the application: `python3 main.py`
2. Configure your gym's setup using the configuration buttons:
   - **Manage Coaches**: Add coaches with their preferences and capabilities
   - **Manage Time Slots**: Define available time slots for each day
   - **Manage Class Types**: Create custom class types with durations
   - **Manage Available Days**: Select which days classes can be scheduled

### 2. Creating a Schedule
1. Set your **Schedule Mode**:
   - **Balanced**: Distributes classes evenly across available slots
   - **Sequential**: Groups similar class types together
2. Enter **Class Requirements**: Specify how many of each class type you want per week
3. Click **Generate Schedule** to create your schedule
4. Review any scheduling conflicts in the bottom panel

### 3. Dynamic Time Slot Filling
The application intelligently fills time slots based on class durations:
- If you have a 2-hour time slot and 60-minute classes, multiple classes can be scheduled
- The system calculates available time and fits classes accordingly
- Classes are assigned to coaches based on availability and preferences

### 4. Exporting Schedules
- **iCalendar**: Click "Export to iCalendar" to save a .ics file for calendar applications
- **CSV**: Click "Save as CSV" to export schedule data for spreadsheets

## 🔧 Advanced Features

### Custom Class Types
Create custom class types with:
- **Name**: Custom display name (e.g., "Competition Training")
- **Type**: Gi, No-Gi, or Open Mat
- **Sub-type**: Additional categorization (e.g., "Advanced", "Competition")
- **Duration**: Length in minutes (supports dynamic slot filling)

### Coach Configuration
Configure coaches with:
- **Name and Contact Info**
- **Maximum Weekly Classes**: Prevent overloading coaches
- **Preferred Times**: Morning, afternoon, or evening preferences
- **Teaching Capabilities**: Which class types they can teach

### Time Slot Management
Define time slots with:
- **Day of Week**: Monday through Sunday
- **Start and End Times**: Precise time boundaries
- **Flexible Duration**: Support for various slot lengths

## 🎨 UI Features

### Visual Schedule Display
- **Color-coded Classes**: Different colors for Gi, No-Gi, and Open Mat classes
- **Time Information**: Clear display of class times
- **Coach Assignment**: Shows which coach is teaching each class
- **Fixed Class Indicators**: Highlights classes that are permanently scheduled

### Configuration Dialogs
- **Intuitive Forms**: Easy-to-use configuration dialogs
- **Validation**: Input validation to prevent errors
- **Real-time Updates**: Immediate feedback on changes

## 🔄 Migration from Single-File Version

If you were using the original `bjj_scheduler.py` file:

1. **Backward Compatibility**: The modular version maintains full compatibility
2. **Same Functionality**: All features from the original version are preserved
3. **Enhanced Organization**: Better code organization and maintainability
4. **Future Extensibility**: Easier to add new features and modifications

## 🛠️ Development

### Running the Modular Version
```bash
# From the project root
python3 main.py
```

### Running the Original Version
```bash
# If you prefer the single-file version
python3 bjj_scheduler.py
```

### Code Organization Benefits
- **Separation of Concerns**: Each module has a single responsibility
- **Easier Testing**: Individual components can be tested in isolation
- **Collaboration**: Multiple developers can work on different modules
- **Maintainability**: Smaller, focused files are easier to understand and modify

## 📝 Example Workflow

1. **Configure Coaches**:
   - Add Coach John (Gi/No-Gi, evenings, max 5 classes/week)
   - Add Coach Sarah (Gi only, mornings, max 3 classes/week)

2. **Set Up Time Slots**:
   - Monday: 19:00-21:00 (2-hour slot)
   - Tuesday: 19:00-20:00 (1-hour slot)
   - Wednesday: 19:00-21:00 (2-hour slot)

3. **Create Class Types**:
   - "Gi Foundations" (60 minutes)
   - "No-Gi Competition" (90 minutes)
   - "Open Mat" (60 minutes)

4. **Generate Schedule**:
   - Request 2 Gi Foundations, 1 No-Gi Competition, 1 Open Mat
   - System automatically fills the 2-hour slots with multiple classes
   - Assigns coaches based on preferences and availability

## 🤝 Contributing

The modular structure makes it easy to contribute:
- **GUI Improvements**: Work in `src/gui/`
- **Scheduling Logic**: Work in `src/models/scheduler.py`
- **Data Models**: Work in `src/models/data_classes.py`
- **Export Features**: Work in `src/utils/export.py`

## 📄 License

This project is open source and available under the MIT License.

---

**Note**: The original `bjj_scheduler.py` file is kept for reference and can still be used if you prefer the single-file approach. The modular version provides the same functionality with better organization and maintainability.

## Non-Technical User Guide: Downloading and Installing the App

### 1. Download the App
- Go to the [Releases](https://github.com/AnthonyGreyFox/BJJ-class-scheduler/releases) page of the project.
- Download the latest `.dmg` (Mac) or `.zip` file under the latest release.

### 2. Install on Mac
- If you downloaded a `.dmg` file:
  1. Double-click the `.dmg` to open it.
  2. Drag the `BJJ Scheduler` app to your `Applications` folder.
  3. Eject the disk image.
- If you downloaded a `.zip` file:
  1. Double-click the `.zip` to unzip it.
  2. Move the `BJJ Scheduler` app to your `Applications` folder (optional).

### 3. Open the App
- Double-click `BJJ Scheduler` to launch.
- The first time you open it, you may see a security warning:
  - If you see "App can’t be opened because it is from an unidentified developer":
    1. Right-click the app and choose `Open`.
    2. Click `Open` in the dialog that appears.
  - Or, go to `System Preferences` > `Security & Privacy` > `General` and click `Open Anyway`.

### 4. Using the App
- Follow the on-screen instructions to set up your coaches, classes, and time slots.
- Use the `Generate Schedule` button to create your class schedule.
- You can export your schedule to CSV or iCalendar, and save/load your settings.

If you have any issues, please contact the developer or check the documentation for troubleshooting tips.
