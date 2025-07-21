# BJJ Scheduler

A modern, user-friendly app for scheduling Brazilian Jiu-Jitsu classes, coaches, and time slots. Supports manual class assignment, export to CSV/iCal, and saving/loading your gym's configuration.

## Features
- Easy management of coaches, classes, and time slots
- Manual assignment of fixed classes to specific slots
- Automatic schedule generation respecting coach/class constraints
- Export schedule to CSV and iCalendar (for Google/Apple Calendar)
- Save and load your gym's configuration as a JSON file
- Mac-ready executable for easy installation

## App Install Guide for Mac Users

### 1. Download the App
- Go to the [Releases](https://github.com/AnthonyGreyFox/BJJ-class-scheduler/releases) page of the project.
- Download the latest `.dmg` file under the latest release.

### 2. Install on Mac
- Double-click the `.dmg` file to open it.
- Drag the `BJJ Scheduler` app to your `Applications` folder.
- Eject the disk image after copying.

### 3. Open the App
- In Finder, go to `Applications` and double-click `BJJ Scheduler` to launch.
- The first time you open it, you may see a security warning:
  - If you see "App can’t be opened because it is from an unidentified developer":
    1. Right-click the app and choose `Open`.
    2. Click `Open` in the dialog that appears.
  - Or, go to `System Preferences` > `Security & Privacy` > `General` and click `Open Anyway`.

### 4. Using the App
- Set up your coaches, classes, and time slots using the intuitive interface.
- Use `Manual Assignment` to fix classes to specific slots if needed.
- Click `Generate Schedule` to create your class schedule.
- Export your schedule to CSV or iCalendar, and save/load your settings as needed.

If you have any issues, please contact the developer or check the documentation for troubleshooting tips.

## Development
- Clone the repo and install dependencies from `requirements.txt`.
- Run the app with `python main.py` (Python 3.10+ recommended).
- Build a Mac executable using the provided build script.

## License
MIT
