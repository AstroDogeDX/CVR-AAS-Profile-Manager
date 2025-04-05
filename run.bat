@echo off
echo Downloading/Updating Required Packages...
pip install -r requirements.txt
echo Starting CVR Advanced Avatar Settings Manager...
python main.py
if errorlevel 1 (
    echo An error occurred while running the application.
    echo Press any key to exit...
    pause > nul
) 