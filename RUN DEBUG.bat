@echo off
echo Starting CVR Advanced Avatar Settings Manager...
python main.py
if errorlevel 1 (
    echo An error occurred while running the application.
    echo Press any key to exit...
    pause > nul
) 