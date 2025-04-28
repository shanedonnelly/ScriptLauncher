# qt_app/icon_gallery.py
import os
import sys
from PyQt6.QtWidgets import ( # type: ignore
    QDialog, QScrollArea, QWidget, QGridLayout, QPushButton, QVBoxLayout,
    QDialogButtonBox, QSizePolicy
)
from PyQt6.QtGui import QIcon, QPixmap # type: ignore
from PyQt6.QtCore import Qt, QSize, pyqtSignal # type: ignore

from utils import ICONS_FOLDER, get_icon_path # Use utils to get icon path

ICON_BUTTON_SIZE = 48
MAX_GALLERY_COLUMNS = 5

class IconGalleryDialog(QDialog):
    """ Dialog to display and select an icon. """
    icon_selected = pyqtSignal(str) # Emits the selected icon file name ('none' if deselected)

    def __init__(self, current_icon='none', parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Icon")
        self.setMinimumSize(400, 300)
        self.selected_icon = current_icon

        # Main layout
        layout = QVBoxLayout(self)

        # Scroll Area for icons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(scroll_area)

        # Widget inside Scroll Area
        icon_widget = QWidget()
        self.grid_layout = QGridLayout(icon_widget)
        self.grid_layout.setSpacing(10)
        icon_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(icon_widget)

        # Populate the grid with icons
        self.populate_icons()

        # Dialog buttons (OK/Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def populate_icons(self):
        """ Finds icons in the assets folder and adds them to the grid. """
        row, col = 0, 0

        # Add a 'None' button first
        none_button = QPushButton("None")
        none_button.setFixedSize(ICON_BUTTON_SIZE * 2, ICON_BUTTON_SIZE // 2)
        none_button.setCheckable(True)
        none_button.setChecked(self.selected_icon == 'none')
        none_button.clicked.connect(lambda: self.select_icon('none'))
        self.grid_layout.addWidget(none_button, row, col, 1, 2) # Span 2 columns
        col += 2
        if col >= MAX_GALLERY_COLUMNS:
            col = 0
            row += 1

        # Add icons from the folder
        try:
            icon_files = sorted([f for f in os.listdir(ICONS_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))])
        except FileNotFoundError:
            print(f"Warning: Icon folder not found at {ICONS_FOLDER}")
            icon_files = []

        for icon_file in icon_files:
            icon_path = get_icon_path(icon_file)
            if icon_path:
                button = QPushButton()
                button.setIcon(QIcon(icon_path))
                button.setIconSize(QSize(ICON_BUTTON_SIZE - 10, ICON_BUTTON_SIZE - 10))
                button.setFixedSize(ICON_BUTTON_SIZE, ICON_BUTTON_SIZE)
                button.setCheckable(True)
                button.setToolTip(icon_file)
                button.setChecked(self.selected_icon == icon_file)
                # Use lambda with default argument to capture current icon_file
                button.clicked.connect(lambda checked, name=icon_file: self.select_icon(name))

                self.grid_layout.addWidget(button, row, col)
                col += 1
                if col >= MAX_GALLERY_COLUMNS:
                    col = 0
                    row += 1

        # Add stretch at the end
        self.grid_layout.setRowStretch(row + 1, 1)
        self.grid_layout.setColumnStretch(MAX_GALLERY_COLUMNS, 1)

    def select_icon(self, icon_name):
        """ Handles button clicks, ensuring only one icon is selected. """
        self.selected_icon = icon_name
        # Uncheck all other buttons
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QPushButton):
                is_current = False
                if icon_name == 'none' and widget.text() == "None":
                    is_current = True
                elif widget.toolTip() == icon_name:
                    is_current = True

                widget.setChecked(is_current)

    def accept(self):
        """ Emit the selected icon name when OK is clicked. """
        self.icon_selected.emit(self.selected_icon)
        super().accept()

    def reject(self):
        """ Close without emitting signal when Cancel is clicked. """
        super().reject()

# Example usage (for testing)
if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication # type: ignore
    app = QApplication(sys.argv)

    # Create dummy icons folder and files for testing
    if not os.path.exists(ICONS_FOLDER):
        os.makedirs(ICONS_FOLDER)
    for i in range(15):
        dummy_path = os.path.join(ICONS_FOLDER, f"dummy_{i+1}.png")
        if not os.path.exists(dummy_path):
            # Create a tiny placeholder png if file doesn't exist
            try:
                from PIL import Image # type: ignore
                img = Image.new('RGB', (1, 1), color = 'red')
                img.save(dummy_path)
            except ImportError:
                 with open(dummy_path, 'w') as f: f.write("") # Create empty file as fallback

    dialog = IconGalleryDialog(current_icon='dummy_5.png')
    dialog.icon_selected.connect(lambda icon: print(f"Selected icon: {icon}"))
    dialog.exec()

    sys.exit()
