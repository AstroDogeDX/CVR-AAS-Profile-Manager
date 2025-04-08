import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QLabel, QFileDialog, QMessageBox,
                            QHBoxLayout, QListWidget, QStackedWidget, QTextEdit,
                            QScrollArea, QCheckBox, QSplitter, QFrame, QGridLayout,
                            QInputDialog, QLineEdit, QProgressBar, QListWidgetItem,
                            QComboBox, QMenu, QGroupBox)
from PyQt6.QtCore import Qt, QMimeData, QSize
from PyQt6.QtGui import QDrag, QPixmap, QIcon
from settings_manager import SettingsManager
from cvr_api import CVRApi
from cache_manager import CacheManager

print("Starting application...")

class ProfileListItem(QWidget):
    def __init__(self, avatar_data, file_name, is_empty=False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Add thumbnail
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(50, 50)
        self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f8f8f8;
            }
        """)
        
        # Get avatar ID from filename
        avatar_id = os.path.splitext(file_name)[0]
        
        # Get thumbnail path from cache manager
        if parent and hasattr(parent, 'cache_manager'):
            thumbnail_path = parent.cache_manager.get_thumbnail_path(avatar_id)
            if thumbnail_path and os.path.exists(thumbnail_path):
                pixmap = QPixmap(thumbnail_path)
                if not pixmap.isNull():
                    self.thumbnail.setPixmap(pixmap.scaled(
                        50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                    ))
                else:
                    self.thumbnail.setText("No Image")
                    self.thumbnail.setStyleSheet("border: 1px solid #ccc; font-size: 7pt;")
            else:
                self.thumbnail.setText("No Image")
                self.thumbnail.setStyleSheet("border: 1px solid #ccc; font-size: 7pt;")
        else:
            self.thumbnail.setText("No Image")
            self.thumbnail.setStyleSheet("border: 1px solid #ccc; font-size: 7pt;")
        
        layout.addWidget(self.thumbnail)
        
        # Add text info
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)  # Reduce spacing between elements
        
        # Avatar name
        self.name_label = QLabel(avatar_data["name"])
        self.name_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        text_layout.addWidget(self.name_label)
        
        # Creator name
        creator_label = QLabel(f"by {avatar_data.get('creatorName', 'Unknown Creator')}")
        creator_label.setStyleSheet("color: #666666; font-size: 9pt;")
        text_layout.addWidget(creator_label)
        
        # File name
        self.file_label = QLabel(file_name)
        self.file_label.setStyleSheet("color: #888888; font-size: 8pt;")
        text_layout.addWidget(self.file_label)
        
        layout.addLayout(text_layout)
        
        # Add status indicators
        status_layout = QVBoxLayout()
        status_layout.setSpacing(2)
        
        # Check if the avatar is owned by the current user
        if parent and hasattr(parent, 'profile_view') and hasattr(parent.profile_view, 'cvr_api'):
            is_owned = parent.profile_view.cvr_api.username and avatar_data.get('creatorName') == parent.profile_view.cvr_api.username
            if is_owned:
                owned_label = QLabel("Owned")
                owned_label.setStyleSheet("""
                    color: #7b1fa2;
                    font-size: 8pt;
                    padding: 2px 6px;
                    background-color: #f3e5f5;
                    border-radius: 3px;
                """)
                status_layout.addWidget(owned_label)
        
        # Public status (formerly Published)
        if avatar_data.get("isPublished", False):
            public_label = QLabel("Public")
            public_label.setStyleSheet("""
                color: #2e7d32;
                font-size: 8pt;
                padding: 2px 6px;
                background-color: #e8f5e9;
                border-radius: 3px;
            """)
            status_layout.addWidget(public_label)
        
        # Shared status
        if avatar_data.get("isSharedWithMe", False):
            shared_label = QLabel("Shared")
            shared_label.setStyleSheet("""
                color: #1565c0;
                font-size: 8pt;
                padding: 2px 6px;
                background-color: #e3f2fd;
                border-radius: 3px;
            """)
            status_layout.addWidget(shared_label)
        
        layout.addLayout(status_layout)
        
        # Add empty indicator if needed
        if is_empty:
            empty_label = QLabel("[Empty]")
            empty_label.setStyleSheet("color: #999999; font-style: italic;")
            layout.addWidget(empty_label)
        
        # Set fixed height for the item
        self.setFixedHeight(70)  # Increased height to accommodate new information

class ProfileListView(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)  # Enable multi-selection
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def on_item_double_clicked(self, item):
        """Handle double-click on a list item."""
        if self.parent:
            self.parent.rename_profile()
    
    def dropEvent(self, event):
        """Handle drop events for reordering."""
        if not self.parent or not self.parent.settings_data or "savedSettings" not in self.parent.settings_data:
            return
            
        # Get the source and destination rows
        source_row = self.currentRow()
        destination_row = self.row(self.itemAt(event.position().toPoint()))
        
        if source_row == destination_row or source_row < 0 or destination_row < 0:
            return
            
        # Perform the move in the data
        saved_settings = self.parent.settings_data["savedSettings"]
        item = saved_settings.pop(source_row)
        saved_settings.insert(destination_row, item)
        
        # Let the parent class handle the UI update
        super().dropEvent(event)
        
        # Mark that changes have been made
        self.parent.has_unsaved_changes = True
        self.parent.update_button_states()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Delete and self.currentItem():
            self.parent.delete_selected_profile()
        else:
            super().keyPressEvent(event)

class ProfileContentView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.cvr_api = CVRApi()
        self.has_unsaved_changes = False
        self.current_profile_index = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Create layout
        layout = QVBoxLayout(self)
        
        # Add back button
        back_button = QPushButton("Back to Profiles")
        back_button.setFixedHeight(28)  # Make button height consistent
        back_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)
        
        # Create splitter for profile list and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create right panel for profile names
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Add profile list label
        profile_list_label = QLabel("Profiles:")
        right_layout.addWidget(profile_list_label)
        
        # Add profile list (using our custom ProfileListView)
        self.profile_list = ProfileListView(self)
        self.profile_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                padding: 4px;
            }
            QListWidget::item {
                padding: 4px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.profile_list.currentItemChanged.connect(self.on_profile_selected)
        right_layout.addWidget(self.profile_list)
        
        # Add profile action buttons
        profile_actions_layout = QHBoxLayout()
        
        # Add rename button
        self.rename_button = QPushButton("Rename Profile")
        self.rename_button.setFixedHeight(28)  # Make button height consistent
        self.rename_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.rename_button.clicked.connect(self.rename_profile)
        profile_actions_layout.addWidget(self.rename_button)
        
        # Add delete button
        self.delete_button = QPushButton("Delete Profile")
        self.delete_button.setFixedHeight(28)
        self.delete_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.delete_button.clicked.connect(self.delete_selected_profile)
        profile_actions_layout.addWidget(self.delete_button)
        
        # Add move up/down buttons
        self.move_up_button = QPushButton("↑")
        self.move_up_button.setFixedSize(28, 28)
        self.move_up_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.move_up_button.clicked.connect(self.move_profile_up)
        
        self.move_down_button = QPushButton("↓")
        self.move_down_button.setFixedSize(28, 28)
        self.move_down_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.move_down_button.clicked.connect(self.move_profile_down)
        profile_actions_layout.addWidget(self.move_up_button)
        profile_actions_layout.addWidget(self.move_down_button)
        
        right_layout.addLayout(profile_actions_layout)
        
        # Create left panel for profile values
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Add avatar info section
        avatar_info_layout = QHBoxLayout()
        
        # Add avatar thumbnail
        self.avatar_thumbnail = QLabel()
        self.avatar_thumbnail.setFixedSize(100, 100)
        self.avatar_thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_thumbnail.setStyleSheet("border: 1px solid #ccc;")
        avatar_info_layout.addWidget(self.avatar_thumbnail)
        
        # Add avatar info
        avatar_info_text = QVBoxLayout()
        self.avatar_name_label = QLabel("Unknown Avatar")
        self.avatar_name_label.setStyleSheet("font-weight: bold;")
        avatar_info_text.addWidget(self.avatar_name_label)
        
        self.avatar_id_label = QLabel("")
        avatar_info_text.addWidget(self.avatar_id_label)
        
        # Add creator name label
        self.creator_name_label = QLabel("")
        self.creator_name_label.setStyleSheet("color: #666666;")
        avatar_info_text.addWidget(self.creator_name_label)
        
        # Add publication status label
        self.publication_status_label = QLabel("")
        self.publication_status_label.setStyleSheet("color: #666666;")
        avatar_info_text.addWidget(self.publication_status_label)
        
        # Add sharing status label
        self.sharing_status_label = QLabel("")
        self.sharing_status_label.setStyleSheet("color: #666666;")
        avatar_info_text.addWidget(self.sharing_status_label)
        
        avatar_info_layout.addLayout(avatar_info_text)
        left_layout.addLayout(avatar_info_layout)
        
        # Add profile name label (moved here)
        self.profile_name_label = QLabel("Select a profile")
        self.profile_name_label.setStyleSheet("font-weight: bold; font-size: 14pt; margin: 10px 0;")
        left_layout.addWidget(self.profile_name_label)
        
        # Add edit mode checkbox
        edit_mode_layout = QHBoxLayout()
        self.edit_mode_checkbox = QCheckBox("Enable Edit Mode (Advanced Users Only)")
        self.edit_mode_checkbox.setChecked(False)
        self.edit_mode_checkbox.stateChanged.connect(self.toggle_edit_mode)
        edit_mode_layout.addWidget(self.edit_mode_checkbox)
        edit_mode_layout.addStretch()
        left_layout.addLayout(edit_mode_layout)
        
        # Add scroll area for values
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #ccc;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #999;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Create widget to hold the values
        self.values_widget = QWidget()
        self.values_layout = QGridLayout(self.values_widget)
        scroll_area.setWidget(self.values_widget)
        
        left_layout.addWidget(scroll_area)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set initial sizes (70% left, 30% right)
        splitter.setSizes([700, 300])
        
        layout.addWidget(splitter)
        
        # Add button layout for save and revert
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Changes")
        self.save_button.setFixedHeight(28)  # Make button height consistent
        self.save_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.save_button.clicked.connect(self.save_changes)
        self.revert_button = QPushButton("Revert Changes")
        self.revert_button.setFixedHeight(28)  # Make button height consistent
        self.revert_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.revert_button.clicked.connect(self.revert_changes)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.revert_button)
        layout.addLayout(button_layout)
        
        # Initialize variables
        self.current_file = None
        self.settings_data = None
        self.original_settings_data = None  # Store original data for revert
        self.current_profile_index = -1
        self.edit_mode_enabled = False
        self.value_widgets = []  # Store references to value widgets
        
        # Initialize button states
        self.update_button_states()
    
    def display_profile(self, file_path):
        """Display the contents of a profile file."""
        print(f"Displaying profile: {file_path}")
        try:
            with open(file_path, 'r') as file:
                # Read the raw file contents first
                raw_contents = file.read()
                print("Raw file contents:", raw_contents)
                
                # Parse the JSON
                self.settings_data = json.loads(raw_contents)
                print("Parsed settings data:", json.dumps(self.settings_data, indent=2))
                
                self.original_settings_data = json.loads(json.dumps(self.settings_data))  # Deep copy for revert
                self.current_file = file_path
                
                # Clear the profile list
                self.profile_list.clear()
                
                # Populate the profile list
                if "savedSettings" in self.settings_data and isinstance(self.settings_data["savedSettings"], list):
                    for i, profile in enumerate(self.settings_data["savedSettings"]):
                        if "profileName" in profile:
                            profile_name = profile["profileName"]
                            self.profile_list.addItem(profile_name)
                
                # Select the first profile if available
                if self.profile_list.count() > 0:
                    self.profile_list.setCurrentRow(0)
                else:
                    self.profile_name_label.setText("No profiles found")
                    self.clear_values_display()
                
                self.update_button_states()
                
                # Get avatar ID from filename and update avatar info
                avatar_id = os.path.splitext(os.path.basename(file_path))[0]
                self.update_avatar_info(avatar_id)
                
        except Exception as e:
            print(f"Error loading profile: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while loading the file: {str(e)}"
            )
    
    def update_avatar_info(self, avatar_id):
        """Update the avatar information display."""
        if not self.parent or not hasattr(self.parent, 'cache_manager'):
            return
            
        # Get avatar data from cache
        avatar_data = self.parent.cache_manager.get_avatar_data(avatar_id, self.cvr_api)
        
        # Update avatar name
        self.avatar_name_label.setText(avatar_data["name"])
        
        # Update avatar ID
        self.avatar_id_label.setText(f"ID: {avatar_id}")
        
        # Update creator name
        self.creator_name_label.setText(f"Creator: {avatar_data['creatorName']}")
        
        # Update publication status
        publication_status = "Published" if avatar_data["isPublished"] else "Not Published"
        self.publication_status_label.setText(f"Status: {publication_status}")
        
        # Update sharing status
        if self.cvr_api.username and avatar_data['creatorName'] == self.cvr_api.username:
            sharing_status = "Owned by you"
        else:
            sharing_status = "Shared with you" if avatar_data["isSharedWithMe"] else "Not shared with you"
        self.sharing_status_label.setText(f"Sharing: {sharing_status}")
        
        # Update thumbnail
        thumbnail_path = self.parent.cache_manager.get_thumbnail_path(avatar_id)
        if thumbnail_path:
            pixmap = QPixmap(thumbnail_path)
            if not pixmap.isNull():
                self.avatar_thumbnail.setPixmap(pixmap.scaled(
                    100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                ))
            else:
                self.avatar_thumbnail.setText("No Image")
        else:
            self.avatar_thumbnail.setText("No Image")
    
    def on_profile_selected(self, current, previous):
        """Handle profile selection."""
        if not current:
            self.profile_name_label.setText("Select a profile")
            self.clear_values_display()
            return
        
        # Get the selected profile index
        self.current_profile_index = self.profile_list.row(current)
        
        # Update the profile name label
        self.profile_name_label.setText(current.text())
        
        # Display the values
        self.display_profile_values(self.current_profile_index)
        
        # Update button states
        self.update_button_states()
    
    def display_profile_values(self, profile_index):
        """Display the values for the selected profile."""
        print(f"Displaying values for profile index: {profile_index}")
        # Clear the current values display
        self.clear_values_display()
        
        if not self.settings_data or "savedSettings" not in self.settings_data:
            return
        
        saved_settings = self.settings_data["savedSettings"]
        if not isinstance(saved_settings, list) or profile_index >= len(saved_settings):
            return
        
        profile = saved_settings[profile_index]
        if "values" not in profile or not isinstance(profile["values"], list):
            return
        
        # Add header row
        name_label = QLabel("Setting Name")
        name_label.setStyleSheet("font-weight: bold;")
        value_label = QLabel("Value")
        value_label.setStyleSheet("font-weight: bold;")
        
        self.values_layout.addWidget(name_label, 0, 0)
        self.values_layout.addWidget(value_label, 0, 1)
        
        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.values_layout.addWidget(separator, 1, 0, 1, 2)
        
        # Add each value
        for i, value_obj in enumerate(profile["values"]):
            if "name" in value_obj and "value" in value_obj:
                name = value_obj["name"]
                value = value_obj["value"]
                
                # Create labels for name and value
                name_label = QLabel(name)
                
                # Create either a label or line edit for the value based on edit mode
                if self.edit_mode_enabled:
                    value_widget = QLineEdit(str(value))
                    value_widget.setObjectName(f"value_edit_{i+2}")  # +2 for header row and separator
                    value_widget.textChanged.connect(lambda text, row=i+2: self.update_value(row, text))
                    self.value_widgets.append(value_widget)
                else:
                    value_widget = QLabel(str(value))
                
                # Add to layout
                self.values_layout.addWidget(name_label, i + 2, 0)
                self.values_layout.addWidget(value_widget, i + 2, 1)
    
    def clear_values_display(self):
        """Clear the values display."""
        # Remove all widgets from the layout
        while self.values_layout.count():
            item = self.values_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def go_back(self):
        """Return to the profile list view."""
        if self.parent:
            self.parent.show_profile_list()
    
    def move_profile_up(self):
        """Move the selected profile up in the list."""
        if not self.settings_data or "savedSettings" not in self.settings_data:
            return
            
        current_row = self.profile_list.currentRow()
        if current_row <= 0:
            return
            
        # Swap profiles in the data
        saved_settings = self.settings_data["savedSettings"]
        saved_settings[current_row], saved_settings[current_row - 1] = \
            saved_settings[current_row - 1], saved_settings[current_row]
            
        # Update the list widget
        current_item = self.profile_list.takeItem(current_row)
        self.profile_list.insertItem(current_row - 1, current_item)
        self.profile_list.setCurrentRow(current_row - 1)
        
        # Mark that changes have been made
        self.has_unsaved_changes = True
        self.update_button_states()

    def move_profile_down(self):
        """Move the selected profile down in the list."""
        if not self.settings_data or "savedSettings" not in self.settings_data:
            return
            
        current_row = self.profile_list.currentRow()
        if current_row < 0 or current_row >= self.profile_list.count() - 1:
            return
            
        # Swap profiles in the data
        saved_settings = self.settings_data["savedSettings"]
        saved_settings[current_row], saved_settings[current_row + 1] = \
            saved_settings[current_row + 1], saved_settings[current_row]
            
        # Update the list widget
        current_item = self.profile_list.takeItem(current_row)
        self.profile_list.insertItem(current_row + 1, current_item)
        self.profile_list.setCurrentRow(current_row + 1)
        
        # Mark that changes have been made
        self.has_unsaved_changes = True
        self.update_button_states()

    def rename_profile(self):
        """Rename the currently selected profile."""
        if not self.settings_data or "savedSettings" not in self.settings_data:
            return
            
        current_row = self.profile_list.currentRow()
        if current_row < 0:
            return
            
        # Get current profile name
        current_item = self.profile_list.currentItem()
        if not current_item:
            return
            
        current_name = current_item.text()
        
        # Show dialog to get new name
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Profile",
            "Enter new profile name:",
            QLineEdit.EchoMode.Normal,
            current_name
        )
        
        if ok and new_name and new_name != current_name:
            # Update the profile name in the data
            saved_settings = self.settings_data["savedSettings"]
            if "profileName" in saved_settings[current_row]:
                saved_settings[current_row]["profileName"] = new_name
                
                # Update the list widget
                current_item.setText(new_name)
                
                # Update the profile name label
                self.profile_name_label.setText(new_name)
                
                # Mark that changes have been made
                self.has_unsaved_changes = True
                self.update_button_states()

    def update_button_states(self):
        """Update the state of all buttons based on current selection and changes."""
        # Update reorder buttons
        current_row = self.profile_list.currentRow()
        self.move_up_button.setEnabled(current_row > 0)
        self.move_down_button.setEnabled(current_row >= 0 and current_row < self.profile_list.count() - 1)
        
        # Update rename button
        self.rename_button.setEnabled(current_row >= 0)
        
        # Update delete button
        self.delete_button.setEnabled(current_row >= 0)
        
        # Update save/revert buttons
        self.save_button.setEnabled(self.has_unsaved_changes)
        self.revert_button.setEnabled(self.has_unsaved_changes)

    def save_changes(self):
        """Save changes to the profile file."""
        if not self.current_file or not self.settings_data:
            return
        
        # Check if any profiles were deleted
        profiles_deleted = False
        if self.original_settings_data and "savedSettings" in self.original_settings_data:
            original_count = len(self.original_settings_data["savedSettings"])
            current_count = len(self.settings_data["savedSettings"])
            if current_count < original_count:
                profiles_deleted = True
        
        # Check if any values were modified in edit mode
        values_modified = False
        if self.edit_mode_enabled and self.value_widgets:
            values_modified = True
            
        # Show confirmation dialog if needed
        if profiles_deleted or values_modified:
            message = []
            if profiles_deleted:
                message.append("You have deleted one or more profiles.")
            if values_modified:
                message.append("You have modified values in edit mode.")
            
            reply = QMessageBox.question(
                self,
                "Confirm Save",
                "Are you sure you want to save these changes?\n\n" + "\n".join(message),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        try:
            # Save the raw JSON content
            with open(self.current_file, 'w') as file:
                json.dump(self.settings_data, file, indent=4)
            
            # Update the original data and reset change tracking
            self.original_settings_data = json.loads(json.dumps(self.settings_data))
            self.has_unsaved_changes = False
            self.update_button_states()
            
            QMessageBox.information(
                self,
                "Success",
                "Profile saved successfully."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while saving the file: {str(e)}"
            )

    def revert_changes(self):
        """Revert changes back to the original state."""
        if self.original_settings_data:
            self.settings_data = json.loads(json.dumps(self.original_settings_data))  # Deep copy
            self.display_profile(self.current_file)  # Refresh the display
            
            # Reset change tracking
            self.has_unsaved_changes = False
            self.update_button_states()
            
            QMessageBox.information(
                self,
                "Success",
                "Changes have been reverted."
            )

    def toggle_edit_mode(self, state):
        """Toggle edit mode for value fields."""
        self.edit_mode_enabled = state == Qt.CheckState.Checked.value
        
        # Update all value widgets
        for i in range(1, self.values_layout.rowCount()):
            # Skip header row
            if i == 0:
                continue
                
            # Get the value widget (should be in column 1)
            value_widget = self.values_layout.itemAtPosition(i, 1)
            if value_widget and value_widget.widget():
                widget = value_widget.widget()
                
                # If it's a QLabel, replace it with a QLineEdit
                if isinstance(widget, QLabel) and self.edit_mode_enabled:
                    # Store the original value
                    original_value = widget.text()
                    
                    # Create a new QLineEdit
                    line_edit = QLineEdit(original_value)
                    line_edit.setObjectName(f"value_edit_{i}")
                    
                    # Replace the QLabel with the QLineEdit
                    self.values_layout.removeWidget(widget)
                    widget.deleteLater()
                    self.values_layout.addWidget(line_edit, i, 1)
                    
                    # Store reference to the new widget
                    self.value_widgets.append(line_edit)
                    
                    # Connect the textChanged signal to update the data
                    line_edit.textChanged.connect(lambda text, row=i: self.update_value(row, text))
                
                # If it's a QLineEdit and edit mode is disabled, replace it with a QLabel
                elif isinstance(widget, QLineEdit) and not self.edit_mode_enabled:
                    # Get the current value
                    current_value = widget.text()
                    
                    # Create a new QLabel
                    label = QLabel(current_value)
                    
                    # Replace the QLineEdit with the QLabel
                    self.values_layout.removeWidget(widget)
                    widget.deleteLater()
                    self.values_layout.addWidget(label, i, 1)
        
        # Update button states
        self.update_button_states()
    
    def update_value(self, row, text):
        """Update the value in the settings data when edited."""
        if not self.settings_data or "savedSettings" not in self.settings_data:
            return
            
        saved_settings = self.settings_data["savedSettings"]
        if not isinstance(saved_settings, list) or self.current_profile_index >= len(saved_settings):
            return
            
        profile = saved_settings[self.current_profile_index]
        if "values" not in profile or not isinstance(profile["values"], list):
            return
            
        # Adjust row index to account for header row
        value_index = row - 2  # -2 for header row and separator
        
        if 0 <= value_index < len(profile["values"]):
            value_obj = profile["values"][value_index]
            if "value" in value_obj:
                # Try to convert the text to the appropriate type
                try:
                    # First try to convert to float
                    value_obj["value"] = float(text)
                except ValueError:
                    # If that fails, keep it as a string
                    value_obj["value"] = text
                
                # Mark that changes have been made
                self.has_unsaved_changes = True
                self.update_button_states()

    def delete_selected_profile(self):
        """Delete the selected profile after confirmation."""
        selected_item = self.profile_list.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self,
                "No Profile Selected",
                "Please select a profile to delete."
            )
            return
        
        # Get the widget associated with the item
        item_widget = self.profile_list.itemWidget(selected_item)
        if not item_widget:
            return
        
        # Get the file name from the widget's file label
        file_name = item_widget.file_label.text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the profile '{file_name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get the file path
                profiles_dir = self.settings_manager.get_profiles_directory()
                if not profiles_dir:
                    return
                
                file_path = os.path.join(profiles_dir, file_name)
                
                # Delete the file
                os.remove(file_path)
                
                # Refresh the profile list
                self.refresh_profiles()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Profile '{file_name}' has been deleted."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while deleting the profile: {str(e)}"
                )

class CVRProfileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CVR Advanced Avatar Settings Manager")
        self.setMinimumSize(800, 900)
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize cache manager
        self.cache_manager = CacheManager()
        
        # Create stacked widget for multiple views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create main page
        self.main_page = QWidget()
        self.setup_main_page()
        self.stacked_widget.addWidget(self.main_page)
        
        # Create profile content view
        self.profile_view = ProfileContentView(self)
        self.stacked_widget.addWidget(self.profile_view)
        
        # Store profile data for sorting and filtering
        self.profile_data = []
        
        # Show the window first
        self.show()
        
        # Then check and set CVR directory
        self.check_cvr_directory()
    
    def check_cvr_directory(self):
        """Check if CVR directory is set and valid."""
        print("Checking CVR directory...")
        cvr_dir = self.settings_manager.get_cvr_directory()
        if cvr_dir:
            print(f"CVR directory found: {cvr_dir}")
            self.directory_label.setText(f"CVR Directory: {cvr_dir}")
            self.initialize_api()  # Initialize API after directory is found
            self.load_initial_profiles()  # Load profiles without cache first
            self.refresh_profiles()  # Then refresh with cache
        else:
            print("CVR directory not found")
            self.directory_label.setText("CVR Directory: Not Set")
            self.prompt_cvr_directory()
    
    def load_initial_profiles(self):
        """Load profiles without cache data first to show the UI quickly."""
        print("Loading initial profiles...")
        self.profile_list.clear()
        self.profile_data = []  # Clear stored profile data
        
        profiles_dir = self.settings_manager.get_profiles_directory()
        if not profiles_dir:
            print("Could not find profiles directory")
            self.status_label.setText("Could not find profiles directory")
            return
        
        try:
            # Get all .advavtr files in the directory
            total_profiles = 0
            empty_profiles = 0
            show_empty = self.show_empty_checkbox.isChecked()
            
            # Get list of files first
            profile_files = []
            for file_name in os.listdir(profiles_dir):
                if file_name.endswith(".advavtr"):
                    total_profiles += 1
                    file_path = os.path.join(profiles_dir, file_name)
                    
                    # Check if the profile is empty
                    is_empty = self.is_empty_profile(file_path)
                    if is_empty:
                        empty_profiles += 1
                        if not show_empty:
                            continue
                    
                    profile_files.append((file_name, file_path, is_empty))
            
            # Create initial profile data with default values
            for file_name, file_path, is_empty in profile_files:
                # Get avatar ID from filename
                avatar_id = os.path.splitext(file_name)[0]
                
                # Create default avatar data
                avatar_data = {
                    "name": "Loading...",
                    "imageUrl": "",
                    "lastUpdated": 0
                }
                
                # Store profile data for sorting and filtering
                self.profile_data.append((file_name, avatar_data, file_path, is_empty))
            
            # Sort and display profiles
            self.sort_profiles()
            
            print(f"Found {total_profiles} profiles ({empty_profiles} empty)")
            self.status_label.setText(f"Found {total_profiles} profiles ({empty_profiles} empty)")
        except Exception as e:
            print(f"Error loading profiles: {str(e)}")
            self.status_label.setText(f"Error loading profiles: {str(e)}")
    
    def initialize_api(self):
        """Initialize the CVR API with credentials from autologin profile."""
        print("Initializing CVR API...")
        autologin_path = self.settings_manager.get_autologin_profile_path()
        if autologin_path:
            if self.profile_view.cvr_api.load_credentials_from_file(autologin_path):
                print("Successfully authenticated with CVR API")
            else:
                print("Failed to authenticate with CVR API")
        else:
            print("Autologin profile not found")
    
    def setup_main_page(self):
        """Set up the main page with directory selection and profile list."""
        layout = QVBoxLayout(self.main_page)
        layout.setSpacing(5)  # Reduce spacing between widgets
        
        # Add welcome label
        welcome_label = QLabel("CVR Advanced Avatar Settings Manager")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px 0;")
        layout.addWidget(welcome_label)
        
        # Add CVR directory section
        directory_layout = QHBoxLayout()
        self.directory_label = QLabel("CVR Directory: Not Set")
        directory_layout.addWidget(self.directory_label)
        
        self.change_dir_button = QPushButton("Change Directory")
        self.change_dir_button.setFixedHeight(28)  # Make button height consistent
        self.change_dir_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.change_dir_button.clicked.connect(self.select_cvr_directory)
        directory_layout.addWidget(self.change_dir_button)
        
        layout.addLayout(directory_layout)
        
        # Add search bar
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search profiles...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 6px 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #999;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_profiles)
        search_layout.addWidget(self.search_bar)
        layout.addLayout(search_layout)
        
        # Add sorting options
        sort_layout = QHBoxLayout()
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #666;
            }
            QComboBox:hover {
                border: 1px solid #999;
            }
        """)
        self.sort_combo.addItems(["Avatar Name (A-Z)", "Filename (A-Z)"])
        self.sort_combo.currentIndexChanged.connect(self.sort_profiles)
        sort_layout.addWidget(sort_label)
        sort_layout.addWidget(self.sort_combo)

        # Add filter options
        filter_label = QLabel("Filter:")
        self.filter_combo = QComboBox()
        self.filter_combo.setStyleSheet(self.sort_combo.styleSheet())  # Reuse the same style
        self.filter_combo.addItems(["All", "Owned by me", "Shared with me", "Public"])
        self.filter_combo.currentIndexChanged.connect(self.filter_profiles)
        sort_layout.addWidget(filter_label)
        sort_layout.addWidget(self.filter_combo)

        # Add show empty profiles checkbox
        self.show_empty_checkbox = QCheckBox("Show Empty Profiles")
        self.show_empty_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #f0f0f0;
                border: 1px solid #999;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #999;
            }
        """)
        self.show_empty_checkbox.setChecked(False)
        self.show_empty_checkbox.stateChanged.connect(self.refresh_profiles)
        sort_layout.addWidget(self.show_empty_checkbox)
        
        # Add purge empty profiles button next to the checkbox
        self.purge_empty_button = QPushButton("Purge Empty")
        self.purge_empty_button.setFixedHeight(28)
        self.purge_empty_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.purge_empty_button.clicked.connect(self.purge_empty_profiles)
        sort_layout.addWidget(self.purge_empty_button)
        
        sort_layout.addStretch()
        layout.addLayout(sort_layout)
        
        # Add profile list section
        profile_label = QLabel("Available Profiles:")
        layout.addWidget(profile_label)
        
        # Create a container for the list widget to control its size
        list_container = QWidget()
        list_container_layout = QVBoxLayout(list_container)
        list_container_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        self.profile_list = QListWidget()
        self.profile_list.itemDoubleClicked.connect(self.load_selected_profile)
        self.profile_list.setSpacing(0)  # Remove spacing between items
        self.profile_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.profile_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.profile_list.customContextMenuRequested.connect(self.show_context_menu)
        list_container_layout.addWidget(self.profile_list)
        
        # Add the container to the main layout
        layout.addWidget(list_container, 1)  # Give it a stretch factor of 1
        
        # Add profile management buttons
        profile_management_layout = QHBoxLayout()
        
        # Create a group for profile actions
        profile_actions_group = QGroupBox("Profile Actions")
        profile_actions_layout = QHBoxLayout()
        
        # Add delete selected profile button
        self.delete_profile_button = QPushButton("Delete Selected")
        self.delete_profile_button.setFixedHeight(28)
        self.delete_profile_button.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f0f0f0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)
        self.delete_profile_button.clicked.connect(self.delete_selected_profile)
        profile_actions_layout.addWidget(self.delete_profile_button)
        
        # Add load from elsewhere button to Profile Actions group
        self.load_button = QPushButton("Load Profile")
        self.load_button.setFixedHeight(28)
        self.load_button.setStyleSheet(self.delete_profile_button.styleSheet())
        self.load_button.clicked.connect(self.load_file_from_elsewhere)
        profile_actions_layout.addWidget(self.load_button)
        
        profile_actions_group.setLayout(profile_actions_layout)
        profile_management_layout.addWidget(profile_actions_group)
        
        # Create a group for import/export actions
        import_export_group = QGroupBox("Import/Export")
        import_export_layout = QHBoxLayout()
        
        # Add import button
        self.import_button = QPushButton("Import Profiles")
        self.import_button.setFixedHeight(28)
        self.import_button.setStyleSheet(self.delete_profile_button.styleSheet())
        self.import_button.clicked.connect(self.import_profile)
        import_export_layout.addWidget(self.import_button)
        
        # Add export button
        self.export_button = QPushButton("Export Selected")
        self.export_button.setFixedHeight(28)
        self.export_button.setStyleSheet(self.delete_profile_button.styleSheet())
        self.export_button.clicked.connect(lambda: self.export_profile())
        import_export_layout.addWidget(self.export_button)
        
        import_export_group.setLayout(import_export_layout)
        profile_management_layout.addWidget(import_export_group)
        
        # Create a group for other actions
        other_actions_group = QGroupBox("Other Actions")
        other_actions_layout = QHBoxLayout()
        
        # Add refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFixedHeight(28)
        self.refresh_button.setStyleSheet(self.delete_profile_button.styleSheet())
        self.refresh_button.clicked.connect(self.refresh_profiles)
        other_actions_layout.addWidget(self.refresh_button)
        
        other_actions_group.setLayout(other_actions_layout)
        profile_management_layout.addWidget(other_actions_group)
        
        layout.addLayout(profile_management_layout)
        
        # Add progress bar for cache operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Add status label
        self.status_label = QLabel("No file loaded")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def sort_profiles(self):
        """Sort the profiles based on the selected option."""
        if not self.profile_data:
            return
            
        sort_by = self.sort_combo.currentText()
        if sort_by == "Avatar Name (A-Z)":
            self.profile_data.sort(key=lambda x: x[1]["name"].lower())
        else:  # Filename (A-Z)
            self.profile_data.sort(key=lambda x: x[0].lower())
            
        self.update_profile_list()
    
    def filter_profiles(self):
        """Filter the profiles based on the search text and selected filter."""
        search_text = self.search_bar.text().lower()
        self.update_profile_list(search_text)
    
    def update_profile_list(self, search_text=""):
        """Update the profile list with the current sort and filter."""
        self.profile_list.clear()
        
        filter_option = self.filter_combo.currentText()
        
        for file_name, avatar_data, file_path, is_empty in self.profile_data:
            # Apply search filter
            if search_text and search_text not in file_name.lower() and search_text not in avatar_data["name"].lower():
                continue
            
            # Apply filter options
            if filter_option == "Owned by me":
                if not self.profile_view.cvr_api.username or avatar_data["creatorName"] != self.profile_view.cvr_api.username:
                    continue
            elif filter_option == "Shared with me":
                if not avatar_data["isSharedWithMe"]:
                    continue
            elif filter_option == "Public":
                if not avatar_data["isPublished"]:
                    continue
                
            # Create custom list item widget
            item_widget = ProfileListItem(avatar_data, file_name, is_empty, self)
            
            # Create list widget item and set its size
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            
            # Add the item to the list
            self.profile_list.addItem(list_item)
            self.profile_list.setItemWidget(list_item, item_widget)
    
    def refresh_profiles(self):
        """Refresh the list of available profiles."""
        print("Refreshing profiles...")
        self.profile_list.clear()
        self.profile_data = []  # Clear stored profile data
        
        profiles_dir = self.settings_manager.get_profiles_directory()
        if not profiles_dir:
            print("Could not find profiles directory")
            self.status_label.setText("Could not find profiles directory")
            return
        
        try:
            # Get all .advavtr files in the directory
            total_profiles = 0
            empty_profiles = 0
            show_empty = self.show_empty_checkbox.isChecked()
            
            # Get list of files first
            profile_files = []
            for file_name in os.listdir(profiles_dir):
                if file_name.endswith(".advavtr"):
                    total_profiles += 1
                    file_path = os.path.join(profiles_dir, file_name)
                    
                    # Check if the profile is empty
                    is_empty = self.is_empty_profile(file_path)
                    if is_empty:
                        empty_profiles += 1
                        if not show_empty:
                            continue
                    
                    profile_files.append((file_name, file_path, is_empty))
            
            # Update UI with progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, len(profile_files))
            self.progress_bar.setValue(0)
            
            # Process files and update cache
            for i, (file_name, file_path, is_empty) in enumerate(profile_files):
                # Get avatar ID from filename
                avatar_id = os.path.splitext(file_name)[0]
                
                # Get avatar data from cache or API
                avatar_data = self.cache_manager.get_avatar_data(avatar_id, self.profile_view.cvr_api)
                
                # Store profile data for sorting and filtering
                self.profile_data.append((file_name, avatar_data, file_path, is_empty))
                
                # Update progress
                self.progress_bar.setValue(i + 1)
                QApplication.processEvents()  # Keep UI responsive
            
            # Sort and display profiles
            self.sort_profiles()
            
            # Hide progress bar when done
            self.progress_bar.setVisible(False)
            
            print(f"Found {total_profiles} profiles ({empty_profiles} empty)")
            self.status_label.setText(f"Found {total_profiles} profiles ({empty_profiles} empty)")
        except Exception as e:
            print(f"Error loading profiles: {str(e)}")
            self.status_label.setText(f"Error loading profiles: {str(e)}")
            self.progress_bar.setVisible(False)
    
    def is_empty_profile(self, file_path):
        """Check if a profile is empty (has no saved settings)."""
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                # Check if savedSettings is an empty array
                if "savedSettings" in data and isinstance(data["savedSettings"], list) and len(data["savedSettings"]) == 0:
                    return True
                return False
        except:
            # If there's any error reading the file, consider it non-empty
            return False
    
    def load_selected_profile(self, item):
        """Load the selected profile and switch to the profile view."""
        if not item:
            return
        
        profiles_dir = self.settings_manager.get_profiles_directory()
        if not profiles_dir:
            return
        
        # Get the widget associated with the item
        item_widget = self.profile_list.itemWidget(item)
        if not item_widget:
            return
        
        # Get the file name from the widget's file label
        file_name = item_widget.file_label.text()
        
        file_path = os.path.join(profiles_dir, file_name)
        print(f"Loading profile: {file_path}")
        self.profile_view.display_profile(file_path)
        self.show_profile_content()
    
    def load_file_from_elsewhere(self):
        """Load a profile file from elsewhere on the system."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select .advavtr File",
            "",
            "Advanced Avatar Settings (*.advavtr);;All Files (*.*)"
        )
        
        if file_name:
            print(f"Loading profile from elsewhere: {file_name}")
            self.profile_view.display_profile(file_name)
            self.show_profile_content()
    
    def show_profile_content(self):
        """Switch to the profile content view."""
        self.stacked_widget.setCurrentWidget(self.profile_view)
    
    def show_profile_list(self):
        """Switch back to the profile list view."""
        self.stacked_widget.setCurrentWidget(self.main_page)
    
    def prompt_cvr_directory(self):
        """Prompt user to select CVR directory if not found."""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("ChilloutVR directory not found.")
        msg.setInformativeText("Would you like to select the ChilloutVR directory now?")
        msg.setWindowTitle("Directory Not Found")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.select_cvr_directory()
    
    def select_cvr_directory(self):
        """Open file dialog to select ChilloutVR.exe."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select ChilloutVR.exe",
            "",
            "ChilloutVR.exe (ChilloutVR.exe);;All Files (*.*)"
        )
        
        if file_name:
            # Get the directory containing the exe
            cvr_dir = os.path.dirname(file_name)
            if os.path.basename(file_name).lower() == "chilloutvr.exe":
                print(f"Setting CVR directory: {cvr_dir}")
                self.settings_manager.set_cvr_directory(cvr_dir)
                self.check_cvr_directory()  # This will now also initialize the API
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Please select the ChilloutVR.exe file."
                )

    def delete_selected_profile(self):
        """Delete the selected profile after confirmation."""
        selected_item = self.profile_list.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self,
                "No Profile Selected",
                "Please select a profile to delete."
            )
            return
        
        # Get the widget associated with the item
        item_widget = self.profile_list.itemWidget(selected_item)
        if not item_widget:
            return
        
        # Get the file name from the widget's file label
        file_name = item_widget.file_label.text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the profile '{file_name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get the file path
                profiles_dir = self.settings_manager.get_profiles_directory()
                if not profiles_dir:
                    return
                
                file_path = os.path.join(profiles_dir, file_name)
                
                # Delete the file
                os.remove(file_path)
                
                # Refresh the profile list
                self.refresh_profiles()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Profile '{file_name}' has been deleted."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while deleting the profile: {str(e)}"
                )
    
    def purge_empty_profiles(self):
        """Delete all empty profiles after confirmation."""
        # Count empty profiles
        empty_profiles = [profile for profile in self.profile_data if profile[3]]  # profile[3] is is_empty
        
        if not empty_profiles:
            QMessageBox.information(
                self,
                "No Empty Profiles",
                "There are no empty profiles to purge."
            )
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Purge",
            f"Are you sure you want to delete all {len(empty_profiles)} empty profiles?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get the profiles directory
                profiles_dir = self.settings_manager.get_profiles_directory()
                if not profiles_dir:
                    return
                
                # Delete each empty profile
                deleted_count = 0
                for file_name, _, file_path, _ in empty_profiles:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting {file_name}: {str(e)}")
                
                # Refresh the profile list
                self.refresh_profiles()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"{deleted_count} empty profiles have been deleted."
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"An error occurred while purging empty profiles: {str(e)}"
                )
    
    def show_context_menu(self, position):
        """Show the context menu for the list item."""
        item = self.profile_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu()
        
        # Add Delete Profile action
        delete_action = menu.addAction("Delete Profile")
        delete_action.triggered.connect(self.delete_selected_profile)
        
        # Add Export Profile action
        export_action = menu.addAction("Export Profile")
        export_action.triggered.connect(lambda: self.export_profile(item))
        
        menu.exec(self.profile_list.mapToGlobal(position))
    
    def export_profile(self, item=None):
        """Export the selected profile(s) to a new location."""
        # If no item is provided, get all selected items
        items_to_export = [item] if item else self.profile_list.selectedItems()
        
        if not items_to_export:
            QMessageBox.warning(
                self,
                "No Profiles Selected",
                "Please select one or more profiles to export."
            )
            return
            
        # If only one profile is selected, use the single file dialog
        if len(items_to_export) == 1:
            item = items_to_export[0]
            # Get the widget associated with the item
            item_widget = self.profile_list.itemWidget(item)
            if not item_widget:
                return
                
            # Get the file name from the widget's file label
            file_name = item_widget.file_label.text()
            
            # Get the source file path
            profiles_dir = self.settings_manager.get_profiles_directory()
            if not profiles_dir:
                return
                
            source_path = os.path.join(profiles_dir, file_name)
            
            # Open file dialog for saving
            target_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Profile",
                file_name,  # Pre-populate with original filename
                "Advanced Avatar Settings (*.advavtr);;All Files (*.*)"
            )
            
            if target_path:
                try:
                    # Copy the file to the new location
                    import shutil
                    shutil.copy2(source_path, target_path)
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Profile has been exported successfully."
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"An error occurred while exporting the profile: {str(e)}"
                    )
        else:
            # For multiple profiles, ask for a directory to export to
            export_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Export Directory",
                "",
                QFileDialog.Option.ShowDirsOnly
            )
            
            if export_dir:
                try:
                    profiles_dir = self.settings_manager.get_profiles_directory()
                    if not profiles_dir:
                        return
                        
                    success_count = 0
                    error_count = 0
                    
                    for item in items_to_export:
                        item_widget = self.profile_list.itemWidget(item)
                        if not item_widget:
                            continue
                            
                        file_name = item_widget.file_label.text()
                        source_path = os.path.join(profiles_dir, file_name)
                        target_path = os.path.join(export_dir, file_name)
                        
                        try:
                            import shutil
                            shutil.copy2(source_path, target_path)
                            success_count += 1
                        except Exception as e:
                            print(f"Error exporting {file_name}: {str(e)}")
                            error_count += 1
                    
                    # Show results
                    message = []
                    if success_count > 0:
                        message.append(f"Successfully exported {success_count} profile(s).")
                    if error_count > 0:
                        message.append(f"Failed to export {error_count} profile(s).")
                    
                    QMessageBox.information(
                        self,
                        "Export Results",
                        "\n".join(message)
                    )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"An error occurred while exporting profiles: {str(e)}"
                    )

    def import_profile(self):
        """Import profile file(s) and copy them to the profiles directory."""
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Select .advavtr File(s) to Import",
            "",
            "Advanced Avatar Settings (*.advavtr);;All Files (*.*)"
        )
        
        if not file_names:
            return
            
        try:
            # Get the profiles directory
            profiles_dir = self.settings_manager.get_profiles_directory()
            if not profiles_dir:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Could not find profiles directory. Please set CVR directory first."
                )
                return
            
            success_count = 0
            error_count = 0
            skipped_count = 0
            
            for file_name in file_names:
                # Get the source filename and construct target path
                source_filename = os.path.basename(file_name)
                target_path = os.path.join(profiles_dir, source_filename)
                
                # Check if file already exists
                if os.path.exists(target_path):
                    reply = QMessageBox.question(
                        self,
                        "File Exists",
                        f"A profile with the name '{source_filename}' already exists. Do you want to overwrite it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.YesToAll | QMessageBox.StandardButton.NoToAll,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.No:
                        skipped_count += 1
                        continue
                    elif reply == QMessageBox.StandardButton.NoToAll:
                        skipped_count += 1
                        break
                
                try:
                    # Copy the file
                    import shutil
                    shutil.copy2(file_name, target_path)
                    success_count += 1
                except Exception as e:
                    print(f"Error importing {source_filename}: {str(e)}")
                    error_count += 1
            
            # Refresh the profile list to update cache
            self.refresh_profiles()
            
            # Show results
            message = []
            if success_count > 0:
                message.append(f"Successfully imported {success_count} profile(s).")
            if error_count > 0:
                message.append(f"Failed to import {error_count} profile(s).")
            if skipped_count > 0:
                message.append(f"Skipped {skipped_count} profile(s).")
            
            QMessageBox.information(
                self,
                "Import Results",
                "\n".join(message)
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while importing profiles: {str(e)}"
            )

def main():
    print("Creating application...")
    app = QApplication(sys.argv)
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    window = CVRProfileManager()
    window.show()
    print("Application started")
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 