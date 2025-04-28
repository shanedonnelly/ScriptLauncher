import sys
import os
import shutil
import threading
# import json # Import json for replay_events

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QPushButton,
    QScrollArea, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSizePolicy, QMessageBox,
    QFileDialog, QMenuBar, QMenu, QInputDialog, QSpacerItem # Import QSpacerItem
)
from PyQt6.QtGui import QIcon, QPixmap, QAction, QPainter, QColor, QBrush, QActionGroup, QFontMetrics
# Import QRect for click position check
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QTimer, QRect

from preset_dialog import PresetDialog
from styles import STYLESHEET_LIGHT, STYLESHEET_DARK

try:
    # Pass events list directly to replay_events
    from recording_module import replay_events # Removed RECORDS_FOLDER import if not needed here
except ImportError as e:
    print(f"Error importing from recording_module: {e}")
    # Dummy function signature updated
    def replay_events(events_data, how_many_times, speed=1, stop_event=None):
        print(f"Dummy Replay: {len(events_data)} events, times: {how_many_times}")
    # RECORDS_FOLDER = "records" # Define in utils.py

from utils import (
    load_presets, delete_preset, run_script, get_icon_path, PRESETS_FOLDER,
    save_preset
)

MAX_COLUMNS = 5
# --- Define fixed size and title constraints ---
PRESET_WIDGET_WIDTH = 200 # Adjust as needed for 16 chars + icon + buttons
PRESET_WIDGET_HEIGHT = 80  # Adjust as needed for 2 lines + icon
ICON_SIZE = 24
ACTION_BUTTON_SIZE = 25 # Size for buttons on the right
TITLE_LINE_LENGTH = 16
TITLE_MAX_CHARS = 32

class PresetWidget(QFrame):
    """ Custom widget representing a single preset button in the grid. """
    request_edit = pyqtSignal(str)
    request_delete = pyqtSignal(str)

    def __init__(self, preset_data, parent=None):
        super().__init__(parent)
        self.preset_data = preset_data
        self.file_name = preset_data['file_name']
        self.preset_type = preset_data['type']
        self.on_off_state = preset_data.get('on_off_state', False)

        self._replay_thread = None
        self._replay_stop_event = None
        self._is_replaying = False

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        # --- Set Fixed Size ---
        self.setFixedSize(PRESET_WIDGET_WIDTH, PRESET_WIDGET_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed) # Enforce fixed size

        # Main horizontal layout
        self.main_hbox = QHBoxLayout(self)
        self.main_hbox.setContentsMargins(5, 5, 5, 5)
        self.main_hbox.setSpacing(10)

        # --- Left Section: Icon and Title ---
        left_vbox = QVBoxLayout()
        left_vbox.setContentsMargins(0,0,0,0)
        left_vbox.setSpacing(3)

        self.icon_label = QLabel(self)
        self.icon_label.setObjectName("icon_label") # Add object name for styling if needed
        self.icon_label.setFixedSize(ICON_SIZE, ICON_SIZE)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.update_icon()
        left_vbox.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.title_label.setWordWrap(True) # Enable word wrap
        font = self.title_label.font()
        font.setPointSize(10)
        self.title_label.setFont(font)
        # Set minimum height to accommodate two lines roughly
        fm = QFontMetrics(font)
        self.title_label.setMinimumHeight(fm.lineSpacing() * 2 + fm.leading())
        self.update_title_text() # Set formatted title
        left_vbox.addWidget(self.title_label, stretch=1)

        self.main_hbox.addLayout(left_vbox, stretch=1)

        # --- Right Section: Buttons ---
        right_vbox = QVBoxLayout()
        right_vbox.setContentsMargins(0,0,0,0)
        right_vbox.setSpacing(3)
        right_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Edit Button
        self.edit_button = QPushButton("✎")
        self.edit_button.setObjectName("EditButton")
        self.edit_button.setToolTip("Edit Preset")
        self.edit_button.setFixedSize(ACTION_BUTTON_SIZE, ACTION_BUTTON_SIZE)
        self.edit_button.clicked.connect(self.emit_edit_request)
        right_vbox.addWidget(self.edit_button)

        # Delete Button
        self.delete_button = QPushButton("🗑")
        self.delete_button.setObjectName("DeleteButton")
        self.delete_button.setToolTip("Delete Preset")
        self.delete_button.setFixedSize(ACTION_BUTTON_SIZE, ACTION_BUTTON_SIZE)
        self.delete_button.clicked.connect(self.emit_delete_request)
        right_vbox.addWidget(self.delete_button)

        # Action Button (On/Off, Replay - NOT Standard)
        self.action_button = QPushButton()
        self.action_button.setFixedSize(ACTION_BUTTON_SIZE, ACTION_BUTTON_SIZE)
        right_vbox.addWidget(self.action_button)

        # Spacer
        self.button_spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        right_vbox.addSpacerItem(self.button_spacer)

        self.main_hbox.addLayout(right_vbox, stretch=0)

        # Initial setup based on type
        self.update_action_button_state() # Connects signals and sets text/name
        self.update_button_visibility()   # Sets visibility

        # --- Make standard type clickable ---
        if self.preset_type == "standard":
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)


    def mousePressEvent(self, event):
        """ Handle clicks ONLY for standard type presets on the main widget area. """
        if event.button() == Qt.MouseButton.LeftButton and self.preset_type == "standard":
            # --- Check if click is not on one of the right-column buttons ---
            # Calculate the approximate rectangle occupied by the right buttons
            right_buttons_width = ACTION_BUTTON_SIZE + self.main_hbox.spacing() # Button width + spacing
            right_buttons_x = self.width() - right_buttons_width - self.main_hbox.contentsMargins().right()
            right_buttons_rect = QRect(right_buttons_x, 0, right_buttons_width, self.height())

            if not right_buttons_rect.contains(event.pos()):
                 print(f"Running standard preset (widget click): {self.file_name}")
                 run_script(self.preset_data.get('script', ''))
            else:
                 # Click was on a button, let the button handle it
                 super().mousePressEvent(event)
        else:
             # Not a left click or not a standard preset, pass event up
             super().mousePressEvent(event)


    def format_title(self, title):
        """Formats the title to fit 2 lines of TITLE_LINE_LENGTH chars, padding with spaces."""
        title = title[:TITLE_MAX_CHARS] # Ensure max length first
        # --- Pad with spaces to exactly TITLE_MAX_CHARS ---
        padded_title = title.ljust(TITLE_MAX_CHARS)
        # Insert newline character after TITLE_LINE_LENGTH characters
        formatted_title = padded_title[:TITLE_LINE_LENGTH] + '\n' + padded_title[TITLE_LINE_LENGTH:]
        return formatted_title

    def update_title_text(self):
        """Sets the formatted title text."""
        original_title = self.preset_data.get('title', '')
        # --- Use format_title ---
        formatted_title = self.format_title(original_title)
        self.title_label.setText(formatted_title)
        self.title_label.setToolTip(original_title) # Show full original title on hover

    def update_button_visibility(self):
        """Sets visibility of edit and action buttons based on type."""
        is_standard = (self.preset_type == "standard")
        is_recorded = (self.preset_type == "recorded")

        self.edit_button.setVisible(not is_recorded)
        # --- Hide action button for standard ---
        self.action_button.setVisible(not is_standard)

        # Spacer adjustment might not be strictly necessary if layout handles it well


    def update_action_button_state(self):
        """Sets the text, tooltip, object name, and connects the correct slot for the action button."""
         # Disconnect any previous connections first
        try: self.action_button.clicked.disconnect()
        except TypeError: pass # No connection existed

        if self.preset_type == "standard":
            # --- No action button logic needed, it's hidden ---
            self.action_button.setText("")
            self.action_button.setToolTip("")
            self.action_button.setObjectName("") # Clear object name
            self.action_button.setCheckable(False)
            # --- Remove connection to run_standard_script ---
            # self.action_button.clicked.connect(self.run_standard_script)
        elif self.preset_type == "on_off":
            self.action_button.setObjectName("OnOffToggleButton")
            self.action_button.setCheckable(True)
            self.action_button.setChecked(self.on_off_state)
            self.update_on_off_button_icon()
            self.action_button.setToolTip("Toggle On/Off")
            self.action_button.clicked.connect(self.toggle_on_off)
        elif self.preset_type == "recorded":
            self.action_button.setObjectName("ReplayButton")
            self.action_button.setCheckable(False)
            if self._is_replaying:
                 self.action_button.setText("■")
                 self.action_button.setToolTip("Stop Replay")
            else:
                 self.action_button.setText("▶")
                 self.action_button.setToolTip("Play Recording")
            self.action_button.clicked.connect(self.toggle_replay)

    def toggle_on_off(self):
        """ Handles the click on the on/off sub-button. """
        # ... (logic remains the same) ...
        self.on_off_state = self.action_button.isChecked()
        self.update_on_off_button_icon()
        print(f"Toggling On/Off preset: {self.file_name}, New state: {'ON' if self.on_off_state else 'OFF'}")
        script_to_run = self.preset_data.get('script_on') if self.on_off_state else self.preset_data.get('script_off')
        run_script(script_to_run)
        self.preset_data['on_off_state'] = self.on_off_state
        success, message = save_preset(self.preset_data)
        if not success:
             QMessageBox.warning(self, "Save Error", f"Could not update preset state:\n{message}")


    def toggle_replay(self):
        """Starts or stops the replay of a recorded preset."""
        # ... (logic remains the same) ...
        if self._is_replaying:
            print("Stop requested.")
            if self._replay_stop_event:
                self._replay_stop_event.set()
        else:
            recorded_events = self.preset_data.get('recorded_events')
            how_many = self.preset_data.get('how_many', 1)
            print(f"Attempting to replay embedded events for: {self.file_name}")

            if recorded_events and isinstance(recorded_events, list) and len(recorded_events) > 0:
                times_to_play = int(how_many)
                self._replay_stop_event = threading.Event()
                self._replay_thread = threading.Thread(
                    target=self._run_replay_thread,
                    args=(recorded_events, times_to_play, self._replay_stop_event),
                    daemon=True
                )
                self._is_replaying = True
                self.action_button.setText("■")
                self.action_button.setToolTip("Stop Replay")
                self._replay_thread.start()
                print(f"Replay thread started for {self.file_name}.")
            else:
                QMessageBox.warning(self, "Replay Error", f"No valid recorded events found for preset: {self.file_name}")


    def _run_replay_thread(self, events_data, times, stop_event):
        """Target function for the replay thread."""
        # ... (logic remains the same) ...
        try:
            print(f"Replay thread ({threading.get_ident()}) starting for {self.file_name}")
            replay_events(events_data, times, stop_event=stop_event) # Pass data directly
            print(f"Replay thread ({threading.get_ident()}) finished execution for {self.file_name}")
        except Exception as e:
            # Use QTimer.singleShot to show message box from main thread
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "Replay Runtime Error", f"Error during replay:\n{e}"))
            print(f"Error during replay thread: {e}")
        finally:
            print(f"Replay thread ({threading.get_ident()}) entering finally block for {self.file_name}")
            # Use QTimer.singleShot to call GUI update from main thread
            QTimer.singleShot(0, self._on_replay_finished)
            print(f"Replay thread ({threading.get_ident()}) scheduled _on_replay_finished for {self.file_name}")


    def _on_replay_finished(self):
        """Called via QTimer when the replay thread finishes or is stopped."""
        # ... (logic remains the same) ...
        print(">>> _on_replay_finished called")
        self._is_replaying = False
        self._replay_thread = None
        self._replay_stop_event = None

        # Check if action_button still exists and type is correct before updating
        if hasattr(self, 'action_button') and self.action_button and hasattr(self.action_button, 'setText') and self.preset_type == "recorded":
            print(">>> Resetting ReplayButton icon and tooltip")
            self.action_button.setText("▶")
            self.action_button.setToolTip("Play Recording")
        print(">>> _on_replay_finished finished")


    def update_on_off_button_icon(self):
        """ Sets the play/pause icon based on the state. """
        # ... (logic remains the same) ...
        if self.action_button and self.preset_type == "on_off":
            self.action_button.setText("⏸" if self.on_off_state else "▶")


    def update_icon(self):
        """ Loads and sets the icon pixmap. """
        # ... (logic remains the same) ...
        icon_path = get_icon_path(self.preset_data.get('icon', 'none'))
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(ICON_SIZE, ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.clear()


    def update_data(self, new_preset_data):
        """ Updates the widget display when preset data changes. """
        type_changed = self.preset_type != new_preset_data.get('type')
        self.preset_data = new_preset_data
        self.preset_type = self.preset_data['type']

        self.update_title_text()
        self.update_icon()
        self.update_action_button_state() # Update connections/text first
        self.update_button_visibility()   # Then update visibility

        # --- Update cursor based on new type ---
        if self.preset_type == "standard":
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        # Update state for existing type if not changed during update
        if not type_changed:
            if self.preset_type == "on_off":
                self.on_off_state = self.preset_data.get('on_off_state', False)
                self.action_button.setChecked(self.on_off_state)
                self.update_on_off_button_icon()
            elif self.preset_type == "recorded":
                 if self._is_replaying and self._replay_stop_event:
                      self._replay_stop_event.set()
                 self._on_replay_finished()

    def emit_edit_request(self):
        # ... (logic remains the same) ...
        self.request_edit.emit(self.file_name)

    def emit_delete_request(self):
        # ... (logic remains the same) ...
        confirm = QMessageBox.question(self, "Confirm Delete",
                                       f"Are you sure you want to delete preset '{self.preset_data['title']}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if self._is_replaying and self._replay_stop_event:
                self._replay_stop_event.set()
            self.request_delete.emit(self.file_name)


# --- MainWindow Class ---
class MainWindow(QMainWindow):
    # ... (__init__ remains the same) ...
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
        self.grid_layout.setSpacing(10) # Adjust spacing slightly
        # --- Set alignment to top-left ---
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)


        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.main_layout.addWidget(self.scroll_area)

        self.load_and_display_presets()

        self.apply_theme(dark_mode=False) # Apply default theme initially

    # ... (_create_menu_bar remains the same) ...
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

        file_menu.addSeparator()

        # Exit Action
        exit_action = QAction(QIcon(), "E&xit", self)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- View Menu ---
        view_menu = menu_bar.addMenu("&Theme")
        self.light_mode_action = QAction("Light Mode", self, checkable=True)
        self.light_mode_action.setChecked(True) # Default
        self.light_mode_action.triggered.connect(lambda: self.apply_theme(dark_mode=False))
        view_menu.addAction(self.light_mode_action)

        self.dark_mode_action = QAction("Dark Mode", self, checkable=True)
        self.dark_mode_action.triggered.connect(lambda: self.apply_theme(dark_mode=True))
        view_menu.addAction(self.dark_mode_action)

        theme_group = QActionGroup(self)
        theme_group.addAction(self.light_mode_action)
        theme_group.addAction(self.dark_mode_action)
        theme_group.setExclusive(True)


    def load_and_display_presets(self):
        """ Clears the grid and reloads all presets from the folder. """
        # ... (Clear grid logic remains the same) ...
        add_button_ref = None
        if hasattr(self, 'add_button'):
            add_button_ref = self.add_button

        # Clear existing widgets safely
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget and widget != add_button_ref: # Don't delete the add button instance yet
                if isinstance(widget, PresetWidget) and widget._is_replaying and widget._replay_stop_event:
                    print(f"Stopping replay for widget {widget.file_name} before reload.")
                    widget._replay_stop_event.set() # Request stop
                    # Ideally wait for thread, but for simplicity just request stop
                widget.deleteLater() # Schedule for deletion

        self.presets = {p['file_name']: p for p in load_presets()}
        self.preset_widgets = {}

        row, col = 0, 0
        for file_name in sorted(self.presets.keys()):
            preset_data = self.presets[file_name]
            widget = PresetWidget(preset_data) # Uses new layout and fixed size
            widget.request_edit.connect(self.open_edit_dialog)
            widget.request_delete.connect(self.delete_preset_widget)

            self.grid_layout.addWidget(widget, row, col)
            self.preset_widgets[file_name] = widget

            col += 1
            if col >= MAX_COLUMNS:
                col = 0
                row += 1

        # Ensure the Add button exists and has the SAME fixed size
        if not hasattr(self, 'add_button') or not self.add_button: # Check if it was deleted
             self.add_button = QPushButton("➕")
             self.add_button.setObjectName("AddButton")
             self.add_button.clicked.connect(self.open_add_dialog)
        # --- Set Fixed Size for Add Button ---
        self.add_button.setFixedSize(PRESET_WIDGET_WIDTH, PRESET_WIDGET_HEIGHT)
        self.add_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed) # Enforce

        # Add the button to the next available slot
        self.grid_layout.addWidget(self.add_button, row, col)

        # Remove stretches, alignment should handle positioning
        # self.update_add_button_position() # Simplified - just add at the end


    # --- Remove or simplify update_add_button_position ---
    # def update_add_button_position(self): ...


    def open_add_dialog(self):
        """ Opens the dialog to add a new preset. """
        # ... (logic remains the same) ...
        dialog = PresetDialog(parent=self)
        dialog.preset_saved.connect(self.handle_preset_saved)
        dialog.exec() # Show modally

    def open_edit_dialog(self, file_name):
        """ Opens the dialog to edit an existing preset. """
        # ... (logic remains the same) ...
        if file_name in self.presets:
            preset_data = self.presets[file_name]
            dialog = PresetDialog(preset_data=preset_data, parent=self)
            dialog.preset_saved.connect(self.handle_preset_saved)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Error", f"Preset file '{file_name}' not found.")


    def handle_preset_saved(self, saved_preset_data):
        """ Slot to handle the preset_saved signal from PresetDialog. """
        # --- Reload everything to ensure correct placement and updates ---
        self.load_and_display_presets()


    def delete_preset_widget(self, file_name):
        """ Deletes the preset file and removes the widget from the grid. """
        if delete_preset(file_name): # Try deleting the file first
            # --- Reload everything after deletion ---
            self.load_and_display_presets()
        else:
            # delete_preset already showed an error message
            pass

    # ... (import_preset, export_preset, apply_theme remain the same) ...
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
                base_name = os.path.basename(file_path)
                dest_path = os.path.join(PRESETS_FOLDER, base_name)
                count = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(base_name)
                    dest_path = os.path.join(PRESETS_FOLDER, f"{name}_{count}{ext}")
                    count += 1
                shutil.copy2(file_path, dest_path)
                print(f"Imported '{file_path}' to '{dest_path}'")
                self.load_and_display_presets() # Reload to show imported
                QMessageBox.information(self, "Import Successful", f"Preset imported as '{os.path.basename(dest_path)}'.")

            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import preset:\n{e}")

    def export_preset(self):
        """ Opens a dialog to choose a preset and then a file dialog to export it. """
        preset_items = {fname: f"{data['title']} ({fname})" for fname, data in self.presets.items()}
        if not preset_items:
            QMessageBox.information(self, "Export Preset", "There are no presets to export.")
            return

        item_list = list(preset_items.values())
        selected_item, ok = QInputDialog.getItem(
            self, "Export Preset", "Select preset to export:", item_list, 0, False
        )

        if ok and selected_item:
            selected_fname = None
            for fname, display_text in preset_items.items():
                if display_text == selected_item:
                    selected_fname = fname
                    break

            if selected_fname and selected_fname in self.presets:
                source_path = os.path.join(PRESETS_FOLDER, selected_fname)
                suggested_name = selected_fname
                save_path, _ = QFileDialog.getSaveFileName(
                    self, "Export Preset As", suggested_name,
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
        # ... (logic remains the same) ...
        if dark_mode:
            QApplication.instance().setStyleSheet(STYLESHEET_DARK)
            self.dark_mode_action.setChecked(True)
        else:
            QApplication.instance().setStyleSheet(STYLESHEET_LIGHT)
            self.light_mode_action.setChecked(True)
        print(f"Applied {'Dark' if dark_mode else 'Light'} theme.")


# --- Main Execution ---
if __name__ == '__main__':
    # ... (folder creation remains the same) ...
    os.makedirs(PRESETS_FOLDER, exist_ok=True)
    # Ensure assets/app_icons exists if needed by get_icon_path
    assets_icons = os.path.join(os.path.dirname(__file__), 'assets', 'app_icons')
    os.makedirs(assets_icons, exist_ok=True)
    # Ensure records folder exists (moved from utils for clarity if recording_module is used)
    try:
        from recording_module import RECORDS_FOLDER
        os.makedirs(RECORDS_FOLDER, exist_ok=True)
    except (ImportError, NameError):
        pass # Only create if module/variable exists


    app = QApplication(sys.argv)
    app_icon_path = get_icon_path('icon.png')
    if app_icon_path and os.path.exists(app_icon_path):
         app.setWindowIcon(QIcon(app_icon_path))

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())