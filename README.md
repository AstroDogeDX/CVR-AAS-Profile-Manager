# CVR AAS Manager

A lightweight tool for managing Advanced Avatar Settings (AAS) profiles in ChilloutVR. This application helps you organize and maintain your avatar settings by providing an intuitive interface for viewing, modifying, and managing AAS profiles.

## Core Features

- **Profile Management**
  - View and modify AAS settings values per avatar
  - Rename, reorder, and delete saved settings profiles
  - Remove empty profiles (generated when using an avatar without setting AAS options)
  - Load external profiles from other locations

- **Visual Organization**
  - Automatic avatar name and thumbnail retrieval from CVR API
  - Search and sort profiles by name or filename
  - Clean, intuitive interface for easy navigation

## Requirements

- Python 3.6 or higher
- PyQt6
- Internet connection (for avatar data retrieval)

## Installation

### Windows Users
1. Download the application files
2. Run `INSTALL DEPENDENCIES.bat` first to ensure you have the required Python libraries. This only has to be done once
3. Run `CVR AAS Profile Manager.bat` to start the application

### Other Operating Systems
1. Install Python 3.6 or higher
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Usage

### First Run
1. The application will attempt to automatically locate your ChilloutVR installation
2. If automatic detection fails, you'll be prompted to manually select your ChilloutVR directory
3. Select the `ChilloutVR.exe` file when prompted
4. The application will scan for and load your AAS profiles

### Managing Avatar Profiles
- Double-click a profile to view and edit its settings
- Use the search bar to filter profiles
- Sort profiles by avatar name or filename
- Delete individual profiles or purge all empty profiles
- Load profiles from external locations if needed

### Managing Settings Profiles
- **Profile Renaming**
  - Double-click a profile to rename it
  - Or use the "Rename Profile" button below the list

- **Profile Reordering**
  - Drag and drop profiles to reorder them
  - Or use the "Move Up" and "Move Down" buttons below the list

- **Profile Deletion**
  - Select a profile and press the Delete key
  - Or use the "Delete Selected Profile" button below the list

## Notes

- This is an unofficial tool and is not associated with Alpha Blend Interactive or ChilloutVR
- The application requires an internet connection to fetch avatar data and thumbnails
- Profile values are stored as floats and should be modified with caution
- Empty profiles can be shown using the "Show Empty Profiles" checkbox

## Troubleshooting

- If the application can't find your ChilloutVR directory, use the "Change Directory" button to locate it manually
- If avatar thumbnails don't load, check your internet connection
- For any issues, run the application from the command line to view error messages

## Disclaimer

This application is provided as-is without any warranty. Use at your own risk. 
