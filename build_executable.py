#!/usr/bin/env python3
"""
Build script for creating standalone BJJ Scheduler executable
"""

import os
import subprocess
import sys

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully")

def build_executable():
    """Build the standalone executable"""
    print("Building BJJ Scheduler executable...")
    
    # PyInstaller command
    # Use ':' for macOS/Linux, ';' for Windows
    if sys.platform == "win32":
        add_data_sep = ";"
    else:
        add_data_sep = ":"
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window (GUI only)
        "--name=BJJ Scheduler",         # Executable name
        f"--add-data=README.md{add_data_sep}.",       # Include README
        "--hidden-import=tkinter",      # Ensure tkinter is included
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.filedialog",
        "main.py"
    ]
    
    # Add icon if available
    if os.path.exists("icon.ico"):
        cmd.extend(["--icon=icon.ico"])
    
    try:
        subprocess.check_call(cmd)
        print("\n✅ Build successful!")
        print("📁 Executable created in: dist/BJJ Scheduler")
        print("\n📋 Next steps:")
        print("1. Test the executable: dist/BJJ Scheduler")
        print("2. Share the executable file with users")
        print("3. Consider creating an installer for easier distribution")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def create_distribution_package():
    """Create a distribution package with documentation"""
    print("\n📦 Creating distribution package...")
    
    # Create dist folder structure
    dist_dir = "distribution"
    os.makedirs(dist_dir, exist_ok=True)
    
    # Copy executable
    if os.path.exists("dist/BJJ Scheduler"):
        import shutil
        shutil.copy("dist/BJJ Scheduler", dist_dir)
        print("✅ Executable copied to distribution folder")
    
    # Create user guide
    create_user_guide(dist_dir)
    
    # Create README for distribution
    create_distribution_readme(dist_dir)
    
    print(f"📁 Distribution package created in: {dist_dir}/")
    print("📋 Package includes:")
    print("  - BJJ Scheduler executable")
    print("  - User Guide.txt")
    print("  - README.txt")

def create_user_guide(dist_dir):
    """Create a simple user guide"""
    guide_content = """BJJ Scheduler - User Guide

QUICK START:
1. Double-click "BJJ Scheduler" to launch the application
2. Configure your gym setup:
   - Click "Manage Coaches" to add coaches
   - Click "Manage Time Slots" to set up available times
   - Click "Manage Class Types" to define class types
   - Click "Manage Available Days" to select operating days

3. Generate a schedule:
   - Set your class requirements (how many of each type)
   - Choose scheduling mode (Balanced or Sequential)
   - Click "Generate Schedule"

4. Export your schedule:
   - Use "Export to iCalendar" for calendar apps
   - Use "Save as CSV" for spreadsheets

FEATURES:
- Dynamic time slot filling (multiple classes per slot)
- Coach availability management
- Custom class types with durations
- Conflict detection and resolution
- Multiple export formats

SUPPORT:
For issues or questions, contact: [Your Contact Info]

Version: 1.0
"""
    
    with open(os.path.join(dist_dir, "User Guide.txt"), "w") as f:
        f.write(guide_content)

def create_distribution_readme(dist_dir):
    """Create README for distribution"""
    readme_content = """BJJ Class Scheduler

A comprehensive Brazilian Jiu-Jitsu class scheduling application.

INSTALLATION:
- Windows: Double-click "BJJ Scheduler"
- Mac: Double-click "BJJ Scheduler" (may need to allow in Security settings)
- Linux: Run "./BJJ Scheduler" in terminal

SYSTEM REQUIREMENTS:
- Windows 10+ / macOS 10.14+ / Linux
- 100MB free disk space
- No additional software required

FEATURES:
✅ Coach management with availability
✅ Dynamic time slot scheduling
✅ Custom class types and durations
✅ Export to calendar and spreadsheet formats
✅ Conflict detection and resolution

For detailed instructions, see "User Guide.txt"

© 2024 BJJ Scheduler
"""
    
    with open(os.path.join(dist_dir, "README.txt"), "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    print("🏗️ BJJ Scheduler Build Script")
    print("=" * 40)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        # Create distribution package
        create_distribution_package()
        
        print("\n🎉 Build process completed!")
        print("📁 Check the 'distribution' folder for your package")
    else:
        print("\n❌ Build process failed")
        sys.exit(1) 