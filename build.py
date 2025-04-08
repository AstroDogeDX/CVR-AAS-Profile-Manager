import os
import subprocess
import sys

def install_requirements():
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("Installing project requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def build_executable():
    print("Building executable...")
    # Get the absolute path to the icon file
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.ico")
    
    # PyInstaller command with common options
    cmd = [
        "pyinstaller",
        "--name=CVR AAS Profile Manager",
        "--onefile",  # Create a single executable
        "--windowed",  # Don't show console window
        f"--icon={icon_path}",  # Set the application icon
        "--add-data=app_settings.json;.",  # Include settings file
        "--add-data=cache;cache",  # Include cache directory
        "--add-data=resources;resources",  # Include resources directory
        "main.py"
    ]
    
    subprocess.check_call(cmd)
    print("\nBuild complete! Executable can be found in the 'dist' directory.")

if __name__ == "__main__":
    install_requirements()
    build_executable() 