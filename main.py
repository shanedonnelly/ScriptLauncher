import sys
import os
import shutil
import threading

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QPushButton,
    QScrollArea, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSizePolicy, QMessageBox,
    QFileDialog, QMenuBar, QMenu, QInputDialog
)
from PyQt6.QtGui import QIcon, QPixmap, QAction, QPainter, QColor, QBrush, QActionGroup
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QTimer

from preset_dialog import PresetDialog
# Import specific stylesheets instead of the default one
from styles import STYLESHEET_LIGHT, STYLESHEET_DARK


# Adjust path to import from parent directory and qt_app subdirectories
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    # Import specific functions/classes needed
    from recording_module import replay_events, load_record, RECORDS_FOLDER
except ImportError as e:
    print(f"Error importing from recording_module: {e}")
    # Provide dummy functions if import fails, useful for basic UI testing
    def replay_events(record_path, how_many_times, speed=1):
        print(f"Dummy Replay: {record_path}, times: {how_many_times}")
    def load_record(p): return None
    RECORDS_FOLDER = "records"


from utils import (
    load_presets, delete_preset, run_script, get_icon_path, PRESETS_FOLDER,
    save_preset # Import save_preset for import functionality
)

MAX_COLUMNS = 5 # As requested in context.txt
PRESET_BUTTON_MIN_HEIGHT = 100
PRESET_BUTTON_MIN_WIDTH = 150
ICON_SIZE = 24
EDIT_DELETE_BUTTON_SIZE = 20
ON_OFF_BUTTON_SIZE = 40

class PresetWidget(QFrame):
    """ Custom widget representing a single preset button in the grid. """
    request_edit = pyqtSignal(str) # file_name
    request_delete = pyqtSignal(str) # file_name

    def __init__(self, preset_data, parent=None):
        super().__init__(parent)
        self.preset_data = preset_data
        self.file_name = preset_data['file_name']
        self.preset_type = preset_data['type']
        self.on_off_state = preset_data.get('on_off_state', False) # Used only for on_off type

        # Replay specific state
        self._replay_thread = None
        self._replay_stop_event = None
        self._is_replaying = False

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setMinimumSize(PRESET_BUTTON_MIN_WIDTH, PRESET_BUTTON_MIN_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(3)

        # --- Top Row: Icon and Edit/Delete ---
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0,0,0,0)

        # Icon Label (top-left)
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(ICON_SIZE, ICON_SIZE)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.update_icon()
        top_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        top_layout.addStretch()

        # Edit/Delete Buttons (top-right)
        button_container = QVBoxLayout()
        button_container.setSpacing(2)

        # Edit Button (Hidden for 'recorded' type)
        if self.preset_type != "recorded":
            self.edit_button = QPushButton("✎")
            self.edit_button.setObjectName("EditButton")
            self.edit_button.setToolTip("Edit Preset")
            self.edit_button.clicked.connect(self.emit_edit_request)
            button_container.addWidget(self.edit_button, alignment=Qt.AlignmentFlag.AlignRight)
        else:
            self.edit_button = None # No edit button for recorded

        # Delete Button
        self.delete_button = QPushButton("🗑")
        self.delete_button.setObjectName("DeleteButton")
        self.delete_button.setToolTip("Delete Preset")
        self.delete_button.clicked.connect(self.emit_delete_request)
        button_container.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignRight)

        top_layout.addLayout(button_container, stretch=0)
        self.layout.addLayout(top_layout)

        # --- Middle: Title ---
        self.title_label = QLabel(preset_data['title'])
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        font = self.title_label.font()
        font.setPointSize(11) # Slightly smaller font
        self.title_label.setFont(font)
        self.layout.addWidget(self.title_label, stretch=1) # Allow title to take space

        # --- Bottom: Action Button (On/Off or Replay) ---
        self.action_button = None # Initialize
        if self.preset_type == "on_off":
            self.action_button = QPushButton()
            self.action_button.setObjectName("OnOffToggleButton")
            self.action_button.setCheckable(True)
            self.action_button.setChecked(self.on_off_state)
            self.update_on_off_button_icon()
            self.action_button.clicked.connect(self.toggle_on_off)
            self.layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignCenter)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False) # Frame receives events
            self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # Title doesn't block
        elif self.preset_type == "recorded":
            self.action_button = QPushButton("▶") # Play icon
            self.action_button.setObjectName("ReplayButton")
            self.action_button.setToolTip("Play Recording")
            self.action_button.clicked.connect(self.toggle_replay)
            self.layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignCenter)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False) # Frame receives events
            self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # Title doesn't block
        else: # Standard type
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Remove inline style, let the main stylesheet handle it
        # self.setStyleSheet("PresetWidget { background-color: #845ADC; color: white; border-radius: 5px; }")


    def mousePressEvent(self, event):
        """ Handle clicks ONLY for standard type presets. """
        # Only trigger if the click is on the frame itself, not on child widgets
        if event.button() == Qt.MouseButton.LeftButton and self.childAt(event.pos()) is None:
            if self.preset_type == "standard":
                print(f"Running standard preset: {self.file_name}")
                run_script(self.preset_data.get('script', ''))
        else:
             super().mousePressEvent(event)

    def toggle_on_off(self):
        """ Handles the click on the on/off sub-button. """
        self.on_off_state = self.action_button.isChecked()
        self.update_on_off_button_icon()
        print(f"Toggling On/Off preset: {self.file_name}, New state: {'ON' if self.on_off_state else 'OFF'}")
        script_to_run = self.preset_data.get('script_on') if self.on_off_state else self.preset_data.get('script_off')
        run_script(script_to_run)
        # Persist the state change in the .slaunch file
        self.preset_data['on_off_state'] = self.on_off_state
        # Use the imported save_preset function
        success, message = save_preset(self.preset_data)
        if not success:
             QMessageBox.warning(self, "Save Error", f"Could not update preset state:\n{message}")

    def toggle_replay(self):
        """Starts or stops the replay of a recorded preset."""
        if self._is_replaying:
            # --- Stop Replay ---
            print("Stop requested.")
            if self._replay_stop_event:
                self._replay_stop_event.set() # Signal the thread to stop
            # Button state is reset in _on_replay_finished
        else:
            # --- Start Replay ---
            record_path = self.preset_data.get('record_path')
            how_many = self.preset_data.get('how_many', 1)

            # Validate path
            if record_path and not os.path.isabs(record_path):
                if not os.path.dirname(record_path):
                    record_path = os.path.join(RECORDS_FOLDER, record_path)
                elif not os.path.exists(record_path):
                     potential_path = os.path.abspath(os.path.join(RECORDS_FOLDER, record_path))
                     if os.path.exists(potential_path):
                          record_path = potential_path

            print(f"Attempting to replay: {record_path}")

            if record_path and os.path.exists(record_path):
                times_to_play = int(how_many)
                self._replay_stop_event = threading.Event() # Create a new stop event

                # Create and start the replay thread
                self._replay_thread = threading.Thread(
                    target=self._run_replay_thread,
                    args=(record_path, times_to_play, self._replay_stop_event),
                    daemon=True
                )

                self._is_replaying = True
                self.action_button.setText("■") # Stop icon
                self.action_button.setToolTip("Stop Replay")
                self._replay_thread.start()
                print(f"Replay thread started for {os.path.basename(record_path)}.")
                # Optionally disable other interactions here
            else:
                QMessageBox.warning(self, "Replay Error", f"Recording file not found or invalid path: {record_path}")

    def _run_replay_thread(self, path, times, stop_event):
        """Target function for the replay thread."""
        try:
            print(f"Replay thread ({threading.get_ident()}) starting for {path}") # DEBUG
            print(f"Replay thread ({threading.get_ident()}) --- Calling replay_events ---") # ADDED DEBUG
            replay_events(path, times, stop_event=stop_event)
            print(f"Replay thread ({threading.get_ident()}) --- Returned from replay_events ---") # ADDED DEBUG
            print(f"Replay thread ({threading.get_ident()}) finished execution for {path}") # DEBUG
        except Exception as e:
            # Use QTimer to show message box from main thread
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Replay Runtime Error", f"Error during replay:\n{e}"))
            print(f"Error during replay thread: {e}")
        finally:
            print(f"Replay thread ({threading.get_ident()}) entering finally block for {path}") # DEBUG
            # Use QTimer to call the cleanup function in the main GUI thread
            QTimer.singleShot(0, self._on_replay_finished)
            print(f"Replay thread ({threading.get_ident()}) scheduled _on_replay_finished for {path}") # DEBUG

    def _on_replay_finished(self):
        """Called via QTimer when the replay thread finishes or is stopped."""
        print(">>> _on_replay_finished called") # DEBUG: Confirm execution
        print(f">>> self.action_button: {self.action_button}") # DEBUG: Check button existence
        print(f">>> self.preset_type: {self.preset_type}") # DEBUG: Check type
        print(f">>> self._is_replaying before reset: {self._is_replaying}") # DEBUG: Check state

        self._is_replaying = False
        self._replay_thread = None
        self._replay_stop_event = None

        # Check if the widget and button still exist and are valid before trying to modify
        # Using hasattr checks if the attribute exists and is callable (for setText)
        if self.action_button and hasattr(self.action_button, 'setText') and self.preset_type == "recorded":
            print(">>> Resetting ReplayButton icon and tooltip") # DEBUG: Confirm reset logic runs
            self.action_button.setText("▶") # Play icon
            self.action_button.setToolTip("Play Recording")
        else:
            # Log why the button wasn't reset
            if not self.action_button:
                print(">>> Button not reset: self.action_button is None or deleted.")
            elif not hasattr(self.action_button, 'setText'):
                 print(">>> Button not reset: self.action_button is not a valid widget anymore.")
            elif self.preset_type != "recorded":
                 print(f">>> Button not reset: self.preset_type is '{self.preset_type}', not 'recorded'.")

        # Optionally re-enable interactions here
        print(">>> _on_replay_finished finished") # DEBUG: Confirm end

    def update_on_off_button_icon(self):
        """ Sets the play/pause icon based on the state. """
        if self.action_button and self.preset_type == "on_off":
            self.action_button.setText("⏸" if self.on_off_state else "▶") # Using Unicode symbols

    def update_icon(self):
        """ Loads and sets the icon pixmap. """
        icon_path = get_icon_path(self.preset_data.get('icon', 'none'))
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.clear() # No icon or icon not found

    def update_data(self, new_preset_data):
        """ Updates the widget display when preset data changes. """
        # Ensure action_button state is correct if type changes - unlikely here
        self.preset_data = new_preset_data
        self.title_label.setText(self.preset_data['title'])
        self.update_icon()
        # Update on/off state if applicable
        if self.preset_type == "on_off":
            self.on_off_state = self.preset_data.get('on_off_state', False)
            if self.action_button:
                self.action_button.setChecked(self.on_off_state)
                self.update_on_off_button_icon()
        elif self.preset_type == "recorded":
             # Reset replay state if data is updated
             if self._is_replaying and self._replay_stop_event:
                  self._replay_stop_event.set() # Stop current replay if editing
             self._on_replay_finished() # Reset button state


    def emit_edit_request(self):
        self.request_edit.emit(self.file_name)

    def emit_delete_request(self):
        confirm = QMessageBox.question(self, "Confirm Delete",
                                       f"Are you sure you want to delete preset '{self.preset_data['title']}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            # Stop replay if running before deleting
            if self._is_replaying and self._replay_stop_event:
                self._replay_stop_event.set()
            self.request_delete.emit(self.file_name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScriptLauncher Qt")
        self.setGeometry(100, 100, 900, 700) # x, y, width, height

        self.presets = {} # Dictionary to store preset data {file_name: data}
        self.preset_widgets = {} # Dictionary to store preset widgets {file_name: widget}

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_menu_bar() # Creates actions, store them if needed for checking state

        # --- Scroll Area for Presets ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("presetGridWidget") # For styling
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setSpacing(15) # Spacing between presets

        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.main_layout.addWidget(self.scroll_area)

        self.load_and_display_presets()
        self.update_add_button_position()

        self.apply_theme(dark_mode=False) # Apply default theme initially

    def _create_menu_bar(self):
        """ Creates the main menu bar. """
        menu_bar = self.menuBar()

        # --- File Menu ---
        file_menu = menu_bar.addMenu("&File")

        # Import Action
        import_action = QAction(QIcon(), "&Import Preset...", self) # Add icon later if desired
        import_action.setStatusTip("Import a .slaunch preset file")
        import_action.triggered.connect(self.import_preset)
        file_menu.addAction(import_action)

        # Export Action
        export_action = QAction(QIcon(), "&Export Preset...", self)
        export_action.setStatusTip("Export a selected preset to a .slaunch file")
        export_action.triggered.connect(self.export_preset) # We'll need a way to select a preset first
        file_menu.addAction(export_action)
        # TODO: Disable export initially, enable when a preset is selected? Or show a dialog to choose.

        file_menu.addSeparator()

        # Exit Action
        exit_action = QAction(QIcon(), "E&xit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- View Menu ---
        view_menu = menu_bar.addMenu("&Theme")
        # Store actions as attributes to easily check/uncheck them later
        self.light_mode_action = QAction("Light Mode", self, checkable=True)
        self.light_mode_action.setChecked(True) # Default
        # Use self.apply_theme directly
        self.light_mode_action.triggered.connect(lambda: self.apply_theme(dark_mode=False))
        view_menu.addAction(self.light_mode_action)

        self.dark_mode_action = QAction("Dark Mode", self, checkable=True)
        # Use self.apply_theme directly
        self.dark_mode_action.triggered.connect(lambda: self.apply_theme(dark_mode=True))
        view_menu.addAction(self.dark_mode_action)

        # Action group to make them exclusive
        theme_group = QActionGroup(self)
        theme_group.addAction(self.light_mode_action)
        theme_group.addAction(self.dark_mode_action)
        theme_group.setExclusive(True)

        # --- Help Menu (Optional) ---
        # help_menu = menu_bar.addMenu("&Help")
        # about_action = QAction("About", self)
        # help_menu.addAction(about_action)


    def load_and_display_presets(self):
        """ Clears the grid and reloads all presets from the folder. """
        # Clear existing widgets from grid (except Add button if it exists)
        add_button_ref = None
        if hasattr(self, 'add_button'):
            add_button_ref = self.add_button

        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item is None: continue
            widget = item.widget()
            if widget and widget != add_button_ref: # Check if it's not the add button
                # Stop any running replay before deleting widget
                if isinstance(widget, PresetWidget) and widget._is_replaying and widget._replay_stop_event:
                    print(f"Stopping replay for widget {widget.file_name} before reload.")
                    widget._replay_stop_event.set()
                widget.setParent(None) # Remove from layout
                widget.deleteLater() # Schedule for deletion

        self.presets = {p['file_name']: p for p in load_presets()}
        self.preset_widgets = {}

        row, col = 0, 0
        for file_name in sorted(self.presets.keys()):
            preset_data = self.presets[file_name]
            widget = PresetWidget(preset_data)
            widget.request_edit.connect(self.open_edit_dialog)
            widget.request_delete.connect(self.delete_preset_widget)

            self.grid_layout.addWidget(widget, row, col)
            self.preset_widgets[file_name] = widget

            col += 1
            if col >= MAX_COLUMNS:
                col = 0
                row += 1

        # Ensure the Add button exists and doesn't have fixed size
        if not hasattr(self, 'add_button'):
            self.add_button = QPushButton("➕")
            self.add_button.setObjectName("AddButton")
            self.add_button.clicked.connect(self.open_add_dialog)
        elif add_button_ref: # If it existed, ensure it's put back
             self.add_button = add_button_ref


        self.update_add_button_position()


    def update_add_button_position(self):
        """ Places the Add button in the next available grid slot. """
        total_presets = len(self.preset_widgets)
        row = total_presets // MAX_COLUMNS
        col = total_presets % MAX_COLUMNS
        if hasattr(self, 'add_button') and self.add_button.parent():
             current_item = self.grid_layout.itemAtPosition(row, col)
             if current_item and current_item.widget() == self.add_button:
                  pass # Already in correct position
             else:
                  self.grid_layout.removeWidget(self.add_button)
                  self.grid_layout.addWidget(self.add_button, row, col)
        elif hasattr(self, 'add_button'): # Add if it exists but wasn't in layout
             self.grid_layout.addWidget(self.add_button, row, col)


        # Add stretch to push items to the top-left
        current_rows = (total_presets + 1 + MAX_COLUMNS -1) // MAX_COLUMNS # +1 for add button
        for r in range(current_rows + 1): # Stretch below the last row
             self.grid_layout.setRowStretch(r, 0) # Reset stretch
        self.grid_layout.setRowStretch(current_rows, 1)

        for c in range(MAX_COLUMNS + 1): # Stretch beyond last column
             self.grid_layout.setColumnStretch(c, 0) # Reset stretch
        self.grid_layout.setColumnStretch(MAX_COLUMNS, 1)


    def open_add_dialog(self):
        """ Opens the dialog to add a new preset. """
        dialog = PresetDialog(parent=self)
        # Connect the signal from the dialog to a slot in the main window
        dialog.preset_saved.connect(self.handle_preset_saved)
        dialog.exec() # Show modally

    def open_edit_dialog(self, file_name):
        """ Opens the dialog to edit an existing preset. """
        if file_name in self.presets:
            preset_data = self.presets[file_name]
            dialog = PresetDialog(preset_data=preset_data, parent=self)
            dialog.preset_saved.connect(self.handle_preset_saved)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", f"Preset file '{file_name}' not found.")

    def handle_preset_saved(self, saved_preset_data):
        """ Slot to handle the preset_saved signal from PresetDialog. """
        file_name = saved_preset_data['file_name']
        is_new = file_name not in self.presets # Check if it was a new preset

        # Update internal data store
        self.presets[file_name] = saved_preset_data

        if is_new:
            # Add a new widget
            widget = PresetWidget(saved_preset_data)
            widget.request_edit.connect(self.open_edit_dialog)
            widget.request_delete.connect(self.delete_preset_widget)
            self.preset_widgets[file_name] = widget
            # Add to grid (repositioning Add button happens in update_add_button_position)
            total_presets = len(self.preset_widgets) # Now includes the new one
            row = (total_presets - 1) // MAX_COLUMNS
            col = (total_presets - 1) % MAX_COLUMNS
            self.grid_layout.addWidget(widget, row, col)
            print(f"Added new preset widget: {file_name}")
        else:
            # Update existing widget
            if file_name in self.preset_widgets:
                self.preset_widgets[file_name].update_data(saved_preset_data)
                print(f"Updated preset widget: {file_name}")
            else:
                 print(f"Error: Widget for {file_name} not found during update.")
                 self.load_and_display_presets() # Fallback: reload everything

        self.update_add_button_position()


    def delete_preset_widget(self, file_name):
        """ Deletes the preset file and removes the widget from the grid. """
        if delete_preset(file_name): # Try deleting the file first
            if file_name in self.preset_widgets:
                widget = self.preset_widgets.pop(file_name)
                self.presets.pop(file_name)
                widget.setParent(None)
                widget.deleteLater()
                print(f"Deleted preset widget: {file_name}")
                self.update_add_button_position() # Rearrange grid
            else:
                 print(f"Error: Widget for {file_name} not found during delete.")
                 self.load_and_display_presets() # Fallback: reload everything
        else:
            # delete_preset already showed an error message
            pass

    def import_preset(self):
        """ Opens a file dialog to import a .slaunch file. """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Preset",
            "", # Start directory (empty means default/last used)
            "ScriptLauncher Presets (*.slaunch);;All Files (*)"
        )

        if file_path:
            try:
                # Determine a safe destination filename in the presets folder
                base_name = os.path.basename(file_path)
                dest_path = os.path.join(PRESETS_FOLDER, base_name)

                # Avoid overwriting existing presets silently
                count = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(base_name)
                    dest_path = os.path.join(PRESETS_FOLDER, f"{name}_{count}{ext}")
                    count += 1

                # Copy the file
                shutil.copy2(file_path, dest_path) # copy2 preserves metadata
                print(f"Imported '{file_path}' to '{dest_path}'")

                # Reload presets to show the newly imported one
                self.load_and_display_presets()
                QMessageBox.information(self, "Import Successful", f"Preset imported as '{os.path.basename(dest_path)}'.")

            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import preset:\n{e}")

    def export_preset(self):
        """ Opens a dialog to choose a preset and then a file dialog to export it. """
        preset_items = {fname: f"{data['title']} ({fname})" for fname, data in self.presets.items()}
        if not preset_items:
            QMessageBox.information(self, "Export Preset", "There are no presets to export.")
            return

        # Use QInputDialog.getItem
        item_list = list(preset_items.values())
        selected_item, ok = QInputDialog.getItem(
            self,
            "Export Preset",
            "Select preset to export:",
            item_list,
            0, # Current index
            False # Editable?
        )

        if ok and selected_item:
            # Find the filename corresponding to the selected item
            selected_fname = None
            for fname, display_text in preset_items.items():
                if display_text == selected_item:
                    selected_fname = fname
                    break

            if selected_fname and selected_fname in self.presets:
                source_path = os.path.join(PRESETS_FOLDER, selected_fname)
                # Suggest a filename for saving
                suggested_name = selected_fname

                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Export Preset As",
                    suggested_name, # Start in current dir with suggested name
                    "ScriptLauncher Presets (*.slaunch);;All Files (*)"
                )

                if save_path:
                    try:
                        shutil.copy2(source_path, save_path)
                        QMessageBox.information(self, "Export Successful", f"Preset exported to '{os.path.basename(save_path)}'.")
                    except Exception as e:
                        QMessageBox.critical(self, "Export Error", f"Failed to export preset:\n{e}")
            else:
                 QMessageBox.warning(self, "Export Error", "Selected preset could not be found.")


    def apply_theme(self, dark_mode=False):
        """Applies the selected theme stylesheet to the application."""
        if dark_mode:
            QApplication.instance().setStyleSheet(STYLESHEET_DARK)
            self.dark_mode_action.setChecked(True) # Ensure correct menu item is checked
        else:
            QApplication.instance().setStyleSheet(STYLESHEET_LIGHT)
            self.light_mode_action.setChecked(True) # Ensure correct menu item is checked
        print(f"Applied {'Dark' if dark_mode else 'Light'} theme.")


if __name__ == '__main__':
    # Ensure necessary folders exist
    os.makedirs(PRESETS_FOLDER, exist_ok=True)
    os.makedirs(RECORDS_FOLDER, exist_ok=True)
    # Make sure assets/app_icons exists if needed by get_icon_path
    assets_icons = os.path.join(os.path.dirname(__file__), 'assets', 'app_icons')
    os.makedirs(assets_icons, exist_ok=True)

    app = QApplication(sys.argv)
    # Set an application icon (optional)
    app_icon_path = get_icon_path('icon.png') # Assuming you have icon.png
    if app_icon_path and os.path.exists(app_icon_path):
         app.setWindowIcon(QIcon(app_icon_path))

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
