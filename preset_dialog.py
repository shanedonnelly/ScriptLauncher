import sys
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QWidget, 
    QPushButton, QComboBox, QFrame, QMessageBox, QFileDialog, QSpinBox, QCheckBox,
    QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt 
from PyQt6.QtGui import QIcon

# Assuming utils.py and recording_module.py are in the same directory or accessible
from utils import save_preset, get_icon_path, ICONS_FOLDER, RECORDS_FOLDER
from icon_gallery import IconGalleryDialog # Changed from IconGallery
from recording_module import Recorder, save_record # Import Recorder and save_record

class PresetDialog(QDialog):
    """ Dialog for creating and editing presets. """
    # Signal emitted when a preset is successfully saved, passing the updated preset data
    preset_saved = pyqtSignal(dict)

    def __init__(self, preset_data=None, parent=None):
        super().__init__(parent)
        self.preset_data = preset_data if preset_data else {} # Store existing data or empty dict
        self.is_editing = preset_data is not None
        self.selected_icon = self.preset_data.get('icon', 'none')
        self.recorder = Recorder() # Initialize the recorder instance
        self.recorded_file_path = self.preset_data.get('record_path') # Store path if editing

        self.setWindowTitle("Edit Preset" if self.is_editing else "Add New Preset")
        self.setMinimumSize(600, 500) # Adjust size as needed
        self.setModal(True)

        # Main layout
        layout = QVBoxLayout(self)

        # --- Title ---
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit(self.preset_data.get('title', ''))
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)

        # --- Icon ---
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(QLabel("Icon:"))
        self.icon_display_label = QLabel(self.selected_icon if self.selected_icon != 'none' else "(No Icon)")
        icon_layout.addWidget(self.icon_display_label)
        icon_layout.addStretch()
        choose_icon_button = QPushButton("Choose Icon...")
        choose_icon_button.clicked.connect(self.open_icon_gallery)
        icon_layout.addWidget(choose_icon_button)
        layout.addLayout(icon_layout)

        # --- Type ---
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["standard", "on_off", "recorded"])
        self.type_combo.setCurrentText(self.preset_data.get('type', 'standard'))
        self.type_combo.currentTextChanged.connect(self.update_ui_for_type)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # --- Type-Specific Widgets ---
        self.stacked_widget_frame = QFrame() # Use a frame to contain changing widgets
        self.stacked_layout = QVBoxLayout(self.stacked_widget_frame)
        layout.addWidget(self.stacked_widget_frame)

        # Widgets for Standard type
        self.standard_widget = QWidget()
        standard_layout = QVBoxLayout(self.standard_widget)
        standard_layout.addWidget(QLabel("Script Content:"))
        self.script_edit = QTextEdit(self.preset_data.get('script', ''))
        standard_layout.addWidget(self.script_edit)
        self.standard_widget.setVisible(False) # Initially hidden
        self.stacked_layout.addWidget(self.standard_widget)

        # Widgets for On/Off type
        self.on_off_widget = QWidget()
        on_off_layout = QVBoxLayout(self.on_off_widget)
        # Initial State Checkbox
        self.initial_state_check = QCheckBox("Start in 'ON' state")
        self.initial_state_check.setChecked(self.preset_data.get('on_off_state', False))
        on_off_layout.addWidget(self.initial_state_check)
        on_off_layout.addWidget(QLabel("Script ON:"))
        self.script_on_edit = QTextEdit(self.preset_data.get('script_on', ''))
        on_off_layout.addWidget(self.script_on_edit)
        on_off_layout.addWidget(QLabel("Script OFF:"))
        self.script_off_edit = QTextEdit(self.preset_data.get('script_off', ''))
        on_off_layout.addWidget(self.script_off_edit)
        self.on_off_widget.setVisible(False) # Initially hidden
        self.stacked_layout.addWidget(self.on_off_widget)

        # Widgets for Recorded type
        self.recorded_widget = QWidget()
        recorded_layout = QVBoxLayout(self.recorded_widget)
        # Recording Status/Info
        self.record_status_label = QLabel("No recording yet." if not self.recorded_file_path else f"Using: {os.path.basename(self.recorded_file_path)}")
        recorded_layout.addWidget(self.record_status_label)
        # Record Button
        self.record_button = QPushButton("Start Recording")
        self.record_button.setCheckable(True) # Toggle button state
        self.record_button.clicked.connect(self.toggle_recording)
        recorded_layout.addWidget(self.record_button)
        # Replay Options
        replay_layout = QHBoxLayout()
        replay_layout.addWidget(QLabel("Replay Count:"))
        self.replay_count_spin = QSpinBox()
        self.replay_count_spin.setMinimum(-1) # -1 for infinite
        self.replay_count_spin.setMaximum(9999)
        self.replay_count_spin.setSpecialValueText("Infinite (-1)")
        self.replay_count_spin.setValue(self.preset_data.get('how_many', 1))
        replay_layout.addWidget(self.replay_count_spin)
        replay_layout.addStretch()
        recorded_layout.addLayout(replay_layout)
        self.recorded_widget.setVisible(False) # Initially hidden
        self.stacked_layout.addWidget(self.recorded_widget)

        # --- Save/Cancel Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_and_close)
        button_layout.addWidget(self.save_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject) # Close dialog without saving
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Initial UI update based on current type
        self.update_ui_for_type(self.type_combo.currentText())

    def update_ui_for_type(self, type_text):
        """ Shows/hides widgets based on the selected preset type. """
        self.standard_widget.setVisible(type_text == "standard")
        self.on_off_widget.setVisible(type_text == "on_off")
        self.recorded_widget.setVisible(type_text == "recorded")
        # Adjust dialog size hint if necessary
        self.adjustSize()

    def open_icon_gallery(self):
        """ Opens the icon selection dialog. """
        gallery = IconGalleryDialog(parent=self) # Changed from IconGallery
        if gallery.exec(): # exec() returns True if accepted (icon selected)
            self.selected_icon = gallery.selected_icon
            self.icon_display_label.setText(self.selected_icon if self.selected_icon != 'none' else "(No Icon)")

    def toggle_recording(self):
        """ Starts or stops the recording process. """
        if self.record_button.isChecked(): # Start recording
            # Disable other controls during recording?
            self.set_controls_enabled(False)
            self.record_button.setText("Stop Recording (Hold LClick+Shift 2s)")
            self.record_status_label.setText("RECORDING... Hold Left Click + Shift for 2s to stop.")
            self.recorder.start_recording()
            # We rely on the Recorder's internal stop mechanism (LClick+Shift)
            # or the user clicking the button again.
            # We need a way to know when the recorder stops *itself*.
            # For now, assume the user clicks the button to stop.
        else: # Stop recording
            self.record_button.setText("Processing...")
            self.record_button.setEnabled(False)
            events = self.recorder.stop_recording()
            self.set_controls_enabled(True) # Re-enable controls
            self.record_button.setText("Start Recording") # Reset button text
            self.record_button.setChecked(False) # Ensure state is unchecked

            if events:
                # Save the recording
                saved_path = save_record(events) # Uses default path in RECORDS_FOLDER
                if saved_path:
                    self.recorded_file_path = saved_path # Store the path to the new recording
                    self.record_status_label.setText(f"Using: {os.path.basename(saved_path)}")
                    QMessageBox.information(self, "Recording Saved", f"Recording saved to {saved_path}")
                else:
                    self.record_status_label.setText("Error saving recording.")
                    QMessageBox.warning(self, "Save Error", "Could not save the recording.")
            else:
                self.record_status_label.setText("Recording stopped. No events captured or error occurred.")
                # Keep existing self.recorded_file_path if editing and recording failed

    def set_controls_enabled(self, enabled):
        """ Enable/disable controls, especially during recording. """
        self.title_edit.setEnabled(enabled)
        self.type_combo.setEnabled(enabled)
        # Find the choose icon button - needs a reference
        # self.choose_icon_button.setEnabled(enabled) # Assuming you have self.choose_icon_button
        self.standard_widget.setEnabled(enabled)
        self.on_off_widget.setEnabled(enabled)
        # Only partially disable recorded widget
        self.replay_count_spin.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        # Keep record button enabled, its state handles logic
        self.record_button.setEnabled(True)


    def save_and_close(self):
        """ Gathers data, saves the preset, emits signal, and closes. """
        new_title = self.title_edit.text().strip()
        if not new_title:
            QMessageBox.warning(self, "Input Error", "Title cannot be empty.")
            return

        # Prepare data dictionary
        updated_data = {
            'file_name': self.preset_data.get('file_name'), # Keep existing filename if editing
            'title': new_title,
            'icon': self.selected_icon,
            'type': self.type_combo.currentText(),
            # Clear fields not relevant to the current type
            'script': "",
            'script_on': "",
            'script_off': "",
            'on_off_state': False,
            'record_path': None,
            'how_many': 1
        }

        # Populate type-specific fields
        preset_type = updated_data['type']
        if preset_type == "standard":
            updated_data['script'] = self.script_edit.toPlainText().strip()
        elif preset_type == "on_off":
            updated_data['script_on'] = self.script_on_edit.toPlainText().strip()
            updated_data['script_off'] = self.script_off_edit.toPlainText().strip()
            updated_data['on_off_state'] = self.initial_state_check.isChecked()
        elif preset_type == "recorded":
            if not self.recorded_file_path:
                QMessageBox.warning(self, "Input Error", "No recording selected or created for 'recorded' type.")
                return
            updated_data['record_path'] = self.recorded_file_path
            updated_data['how_many'] = self.replay_count_spin.value()

        # Save the preset using the utility function
        success, message_or_data = save_preset(updated_data)

        if success:
            saved_data = message_or_data # save_preset returns the full data on success
            self.preset_saved.emit(saved_data) # Emit signal with the saved data
            self.accept() # Close the dialog successfully
        else:
            # save_preset already shows an error message via QMessageBox
            pass # Keep dialog open

# Example usage (for testing)
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    # Test adding a new preset
    # dialog = PresetDialog()

    # Test editing an existing preset (create dummy data)
    dummy_data = {
        'file_name': 'preset1.slaunch',
        'title': 'My Test Preset',
        'type': 'on_off',
        'icon': '001-social.png',
        'script_on': 'echo "Turning ON"',
        'script_off': 'echo "Turning OFF"',
        'on_off_state': True,
        'record_path': None,
        'how_many': 1
    }
    dialog = PresetDialog(preset_data=dummy_data)


    def handle_save(data):
        print("Preset saved signal received:", data)

    dialog.preset_saved.connect(handle_save)

    if dialog.exec():
        print("Dialog accepted (saved).")
    else:
        print("Dialog rejected (cancelled).")

    sys.exit(app.exec())
