@echo off
echo Downloading/Updating Required Packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo An error occurred while running the application.
    echo Press any key to exit...
    pause > nul
) 
echo Dependencies installed successfully.
echo Press any key to exit...
pause > nul 