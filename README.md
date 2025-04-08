# CVR Advanced Avatar Settings Manager

A lightweight tool for managing Advanced Avatar Settings (AAS) profiles in ChilloutVR. This application helps you organize and maintain your avatar settings by providing an intuitive interface for viewing, modifying, and managing AAS profiles.

![Main Window](https://github.com/user-attachments/assets/dc8b9ad2-2590-4928-9928-af7b5b8ade07)

## Core Features

- **Profile Management**
  - View and modify AAS settings values per avatar
  - Rename, reorder, and delete saved settings profiles
  - Remove empty profiles (generated when using an avatar without setting AAS options)
  - Load external profiles from other locations
  - Import/Export profiles for easy sharing and backup

- **Visual Organization**
  - Automatic avatar name and thumbnail retrieval from CVR API
  - Search and sort profiles by name or filename
  - Clean, intuitive interface for easy navigation

## Installation

### Windows Users (Recommended)
1. Download the latest release from the [Releases](https://github.com/AstroDogeDX/CVR-AAS-Profile-Manager/releases/) page
2. Create a dedicated folder for the application
3. Place the downloaded .exe in the dedicated folder
4. Run the application - it will automatically create necessary folders for caching data

### For Developers
1. Clone the repository
2. Run `INSTALL DEPENDENCIES.bat` to install required Python libraries
3. Use `RUN DEBUG.bat` to run the application in debug mode with console output
4. Use `BUILD.bat` to create your own executable build

### Other Operating Systems
1. Download the repository as a [zip file](https://github.com/AstroDogeDX/CVR-AAS-Profile-Manager/archive/refs/heads/main.zip) and extract it
2. Install Python 3.6 or higher
3. Install required packages:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
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

### Import/Export Features
- **Import Profiles**
  - Click "Import Profiles" to select one or more .advavtr files
  - Choose whether to overwrite existing profiles
  - View import results with success/error counts

- **Export Profiles**
  - Select one or more profiles
  - Choose "Export Selected" to save to a new location
  - Single profile exports allow custom naming
  - Multiple profile exports maintain original filenames

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
- When using the executable release, ensure it's placed in a dedicated folder for proper cache management

## Troubleshooting

- If the application can't find your ChilloutVR directory, use the "Change Directory" button to locate it manually
- If avatar thumbnails don't load, check your internet connection
- For any issues, run the application from the command line to view error messages
- When using the executable release, ensure you have proper write permissions in the folder where it's located

## Disclaimer

This application is provided as-is without any warranty. Use at your own risk. 
