# ChilloutVR AAS Manager

A user-friendly application for managing Advanced Avatar Settings (AAS) profiles for ChilloutVR. This tool allows you to view, edit, organize, and manage your avatar settings profiles with ease.

![Main Page](main_page.png)

## Features

- **Automatic Profile Detection**: Automatically finds and loads your avatar settings profiles from the ChilloutVR directory
- **Profile Management**:
  - View all your avatar settings profiles in one place
  - Rename profiles for better organization
  - Reorder profiles using drag-and-drop or up/down buttons
  - Delete selected profiles
  - Purge all empty profiles (profiles without saved settings)
- **Advanced Editing**:
  - Edit profile values directly (for advanced users)
  - Save and revert changes
- **Search and Sort**:
  - Search profiles by name or filename
  - Sort profiles by avatar name or filename
- **Visual Interface**:
  - View avatar thumbnails
  - See avatar names and IDs
  - Clean, intuitive layout

![Profile View](profile_view.png)

## Requirements

- Python 3.6 or higher
- PyQt6
- Internet connection (for avatar data retrieval)

## Installation

### Windows Users (Recommended)

1. Download the application files
2. Run `run.bat` to start the application

### Alternative Setup (Non-Windows Users)

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

1. When you first run the application, it will automatically attempt to locate your ChilloutVR installation in common Steam directories
2. If the automatic detection fails, you will be prompted to manually select your ChilloutVR directory
3. Navigate to and select the `ChilloutVR.exe` file
4. The application will automatically scan for and load your avatar settings profiles

### Managing Profiles

- **View Profiles**: Double-click a profile to view its settings
- **Rename Profiles**: Select a profile and click "Rename Profile"
- **Reorder Profiles**: Use the "Move Up" and "Move Down" buttons or drag and drop
- **Delete Profiles**: Select a profile and click "Delete Selected Profile"
- **Purge Empty Profiles**: Click "Purge Empty Profiles" to remove all profiles without saved settings

### Advanced Features

- **Edit Mode**: Enable "Edit Mode" to modify profile values (for advanced users only)
- **Load External Profiles**: Use "Load Profile from file..." to load profiles from other locations
- **Search**: Use the search bar to filter profiles by name or filename
- **Sort**: Use the dropdown to sort profiles by avatar name or filename

## Notes

- The application requires an internet connection to fetch avatar data and thumbnails
- Profile values are stored as floats in the game, but may represent different types of settings (sliders, toggles, etc.)
- Editing values in edit mode should be done with caution, as incorrect values may affect avatar functionality
- Empty profiles (those without saved settings) can be shown using the "Show Empty Profiles" checkbox

## Troubleshooting

- If the application cannot find your ChilloutVR directory, you can manually select it using the "Change Directory" button
- If avatar thumbnails don't load, check your internet connection and try refreshing the profiles
- If you encounter any issues, try running the application from the command line to see error messages

## License

This application is provided as-is for the ChilloutVR community. Use at your own risk. 