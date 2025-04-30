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
from utils import save_preset, get_icon_path, ICONS_FOLDER
from icon_gallery import IconGalleryDialog
# Use embedded data, remove save_record/load_record if not needed for dialog logic
try:
    from recording_module import Recorder
except ImportError:
    # Dummy Recorder if module not found
    class Recorder:
        def start_recording(self): print("Dummy Recorder: Start")
        def stop_recording(self): print("Dummy Recorder: Stop"); return []
    print("Warning: recording_module not found, using dummy Recorder.")


# --- Change MAX_TITLE_LENGTH ---
MAX_TITLE_LENGTH = 48 # Strict 32 character limit (2 lines of 16)

class PresetDialog(QDialog):
    preset_saved = pyqtSignal(dict)

    def __init__(self, preset_data=None, parent=None):
        super().__init__(parent)
        self.preset_data = preset_data if preset_data else {}
        self.is_editing = preset_data is not None
        self.selected_icon = self.preset_data.get('icon', 'none')
        self.recorder = Recorder()
        # Store embedded data if editing
        self.recorded_events_data = self.preset_data.get('recorded_events') # Use embedded data

        self.setWindowTitle("Edit Preset" if self.is_editing else "Add New Preset")
        self.setMinimumSize(600, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # --- Title ---
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit(self.preset_data.get('title', ''))
        # --- Set strict MaxLength on QLineEdit ---
        self.title_edit.setMaxLength(MAX_TITLE_LENGTH)
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        # --- Update helper label ---
        self.title_limit_label = QLabel(f"(Max {MAX_TITLE_LENGTH} characters)")
        font = self.title_limit_label.font()
        font.setPointSize(8) # Smaller font for helper text
        self.title_limit_label.setFont(font)
        layout.addWidget(self.title_limit_label)


        # --- Icon ---
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(QLabel("Icon:"))
        self.icon_display_label = QLabel(self.selected_icon if self.selected_icon != 'none' else "(No Icon)")
        icon_layout.addWidget(self.icon_display_label)
        icon_layout.addStretch()
        self.choose_icon_button = QPushButton("Choose Icon...") # Store reference
        self.choose_icon_button.clicked.connect(self.open_icon_gallery)
        icon_layout.addWidget(self.choose_icon_button)
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
        self.stacked_widget_frame = QFrame()
        self.stacked_layout = QVBoxLayout(self.stacked_widget_frame)
        layout.addWidget(self.stacked_widget_frame)

        # Standard
        self.standard_widget = QWidget()
        standard_layout = QVBoxLayout(self.standard_widget)
        standard_layout.addWidget(QLabel("Script Content:"))
        # Fonction auxiliaire pour normaliser les sauts de ligne
        def normalize_newlines(text):
            if not text:
                return ''
            # Force tous les sauts de ligne à être \n (LF)
            normalized = text.replace('\r\n', '\n').replace('\r', '\n')
            return normalized
        
        # Initialisation des QTextEdit avec texte normalisé
        self.script_edit = QTextEdit()
        self.script_edit.setPlainText(normalize_newlines(self.preset_data.get('script', '')))
        
        # Idem pour les autres champs
        self.script_on_edit = QTextEdit()
        self.script_on_edit.setPlainText(normalize_newlines(self.preset_data.get('script_on', '')))
        
        self.script_off_edit = QTextEdit()
        self.script_off_edit.setPlainText(normalize_newlines(self.preset_data.get('script_off', '')))
        
        standard_layout.addWidget(self.script_edit)
        self.standard_widget.setVisible(False)
        self.stacked_layout.addWidget(self.standard_widget)

        # On/Off
        self.on_off_widget = QWidget()
        on_off_layout = QVBoxLayout(self.on_off_widget)
        self.initial_state_check = QCheckBox("Check if the current state is ON")
        self.initial_state_check.setChecked(self.preset_data.get('on_off_state', False))
        on_off_layout.addWidget(self.initial_state_check)
        on_off_layout.addWidget(QLabel("Script ON:"))
        on_off_layout.addWidget(self.script_on_edit)
        on_off_layout.addWidget(QLabel("Script OFF:"))
        on_off_layout.addWidget(self.script_off_edit)
        self.on_off_widget.setVisible(False)
        self.stacked_layout.addWidget(self.on_off_widget)

        # Recorded
        self.recorded_widget = QWidget()
        recorded_layout = QVBoxLayout(self.recorded_widget)
        status_text = "No recording data."
        if self.recorded_events_data and isinstance(self.recorded_events_data, list):
             status_text = f"Recording data available ({len(self.recorded_events_data)} events)."
        self.record_status_label = QLabel(status_text)
        recorded_layout.addWidget(self.record_status_label)
        self.record_button = QPushButton("Start Recording")
        self.record_button.setCheckable(True)
        self.record_button.clicked.connect(self.toggle_recording)
        recorded_layout.addWidget(self.record_button)
        replay_layout = QHBoxLayout()
        replay_layout.addWidget(QLabel("Replay Count:"))
        self.replay_count_spin = QSpinBox()
        self.replay_count_spin.setMinimum(-1)
        self.replay_count_spin.setMaximum(9999)
        self.replay_count_spin.setSpecialValueText("Infinite (-1)")
        self.replay_count_spin.setValue(self.preset_data.get('how_many', 1))
        replay_layout.addWidget(self.replay_count_spin)
        replay_layout.addStretch()
        recorded_layout.addLayout(replay_layout)
        self.recorded_widget.setVisible(False)
        self.stacked_layout.addWidget(self.recorded_widget)

        # --- Save/Cancel Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_and_close)
        button_layout.addWidget(self.save_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.update_ui_for_type(self.type_combo.currentText())

    def update_ui_for_type(self, type_text):
        """ Shows/hides widgets based on the selected preset type. """
        self.standard_widget.setVisible(type_text == "standard")
        self.on_off_widget.setVisible(type_text == "on_off")
        self.recorded_widget.setVisible(type_text == "recorded")
        self.adjustSize()

    def open_icon_gallery(self):
        """ Opens the icon selection dialog. """
        gallery = IconGalleryDialog(parent=self)
        if gallery.exec():
            self.selected_icon = gallery.selected_icon
            self.icon_display_label.setText(self.selected_icon if self.selected_icon != 'none' else "(No Icon)")


    def toggle_recording(self):
        """ Starts or stops the recording process (for embedded data). """
        if self.record_button.isChecked(): # Start recording
            self.set_controls_enabled(False)
            self.record_button.setText("Stop Recording (Hold LClick+Shift 2s)")
            self.record_status_label.setText("RECORDING... Hold Left Click + Shift for 2s to stop.")
            self.recorded_events_data = None # Clear previous data
            self.recorder.start_recording()
        else: # Stop recording
            self.record_button.setText("Processing...")
            self.record_button.setEnabled(False)
            events = self.recorder.stop_recording()
            self.set_controls_enabled(True)
            self.record_button.setText("Start Recording")
            self.record_button.setChecked(False) # Ensure unchecked after stop

            if events:
                self.recorded_events_data = events # Store the list directly
                self.record_status_label.setText(f"Recording data available ({len(self.recorded_events_data)} events).")
                QMessageBox.information(self, "Recording Captured", f"Captured {len(events)} events.")
            else:
                status_text = "Recording stopped. No events captured or error occurred."
                if self.is_editing and self.preset_data.get('recorded_events'): # Check original data if editing
                     prev_count = len(self.preset_data.get('recorded_events', []))
                     status_text += f"\nKeeping previous data ({prev_count} events)."
                     self.recorded_events_data = self.preset_data.get('recorded_events') # Restore previous
                else:
                     status_text += "\nNo previous data available."
                     self.recorded_events_data = None # Ensure it's cleared
                self.record_status_label.setText(status_text)


    def set_controls_enabled(self, enabled):
        """ Enable/disable controls, especially during recording. """
        self.title_edit.setEnabled(enabled)
        self.type_combo.setEnabled(enabled)
        self.choose_icon_button.setEnabled(enabled)
        self.standard_widget.setEnabled(enabled)
        self.on_off_widget.setEnabled(enabled)
        # Only enable record-specific controls if not recording
        self.replay_count_spin.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        # Keep record button always enabled, but text changes
        self.record_button.setEnabled(True)


    def save_and_close(self):
        """ Gathers data, validates, saves the preset, emits signal, and closes. """
        new_title = self.title_edit.text().strip()
        if not new_title:
            QMessageBox.warning(self, "Input Error", "Title cannot be empty.")
            return
        # --- Strict Title Length Check (redundant due to QLineEdit.maxLength, but safe) ---
        if len(new_title) > MAX_TITLE_LENGTH:
             QMessageBox.warning(self, "Input Error", f"Title cannot exceed {MAX_TITLE_LENGTH} characters.")
             return
        # --- Remove previous warning message box ---

        updated_data = {
            'file_name': self.preset_data.get('file_name'),
            'title': new_title,
            'icon': self.selected_icon,
            'type': self.type_combo.currentText(),
            'script': "", 'script_on': "", 'script_off': "",
            'on_off_state': False,
            'recorded_events': None, # Use embedded data field
            'how_many': 1
        }

        preset_type = updated_data['type']
        if preset_type == "standard":
            updated_data['script'] = self.script_edit.toPlainText().strip()
        elif preset_type == "on_off":
            updated_data['script_on'] = self.script_on_edit.toPlainText().strip()
            updated_data['script_off'] = self.script_off_edit.toPlainText().strip()
            updated_data['on_off_state'] = self.initial_state_check.isChecked()
        elif preset_type == "recorded":
            # Use the stored event data (could be from initial load or new recording)
            if not self.recorded_events_data or not isinstance(self.recorded_events_data, list):
                QMessageBox.warning(self, "Input Error", "No valid recording data available for 'recorded' type. Please record actions first.")
                return
            updated_data['recorded_events'] = self.recorded_events_data
            updated_data['how_many'] = self.replay_count_spin.value()

        # --- Pass data to save_preset (which now handles embedded data) ---
        success, message_or_data = save_preset(updated_data)

        if success:
            saved_data = message_or_data
            self.preset_saved.emit(saved_data)
            self.accept()
        else:
            # Error message already shown by save_preset
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
        'recorded_events': None, # Example: no recorded data initially
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
