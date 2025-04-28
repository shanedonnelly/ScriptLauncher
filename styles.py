# --- Light Mode Palette ---
PRIMARY_LIGHT = "#F5F5F5" # Main background (Very Light Grey)
SECONDARY_LIGHT = "#662B79" # Interactive elements (Dark Purple)
TEXT_COLOR_LIGHT = "#212529" # Dark text for readability
BORDER_COLOR_LIGHT = "#D3D3D3" # Light grey borders

# --- Dark Mode Palette ---
PRIMARY_DARK = "#212529" # Main background (Near Black)
SECONDARY_DARK = "#9E4FB8" # Lighter Purple for interactive elements in dark mode
TEXT_COLOR_DARK = "#F8F9FA" # Light text
BORDER_COLOR_DARK = "#495057" # Darker grey borders

# --- Font Settings ---
FONT_FAMILY = "Segoe UI, Ubuntu, Cantarell, sans-serif"
FONT_SIZE_BASE = "10pt"
FONT_SIZE_LARGE = "12pt"
FONT_SIZE_SMALL = "9pt"

# --- Button Size ---
# Define a standard size. Adjust as needed.
BUTTON_SIZE = 30 # Standard height for most buttons
BUTTON_PADDING_H = "10px" # Horizontal padding
BUTTON_PADDING_V = "5px" # Vertical padding
ROUND_BUTTON_SIZE = 35 # For Add button

# --- General ---
BORDER_RADIUS = "2px" # Minimal rounding

# =============================================
#          LIGHT MODE STYLESHEET
# =============================================
STYLESHEET_LIGHT = f"""
/* --- Global --- */
QWidget {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_BASE};
    color: {TEXT_COLOR_LIGHT};
}}

QMainWindow, QDialog {{
    background-color: {PRIMARY_LIGHT};
}}

/* --- Scroll Area --- */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

#presetGridWidget {{
    background-color: {PRIMARY_LIGHT};
    padding: 5px; /* Reduced padding */
}}

/* --- Preset Widget --- */
PresetWidget {{
    background-color: white; /* Keep presets distinct */
    border: 1px solid {BORDER_COLOR_LIGHT};
    border-radius: {BORDER_RADIUS};
    color: {TEXT_COLOR_LIGHT};
    padding: 5px; /* Reduced padding */
}}

PresetWidget:hover {{
    background-color: #EAEAEA; /* Subtle hover */
}}

/* Title Label within PresetWidget */
PresetWidget QLabel {{
    background-color: transparent;
    color: {TEXT_COLOR_LIGHT};
    font-weight: bold;
}}

/* --- Buttons --- */
QPushButton {{
    background-color: {SECONDARY_LIGHT};
    color: white;
    border: 1px solid {SECONDARY_LIGHT}; /* Add subtle border */
    padding: {BUTTON_PADDING_V} {BUTTON_PADDING_H};
    border-radius: {BORDER_RADIUS};
    font-size: {FONT_SIZE_BASE};
    min-height: {BUTTON_SIZE}px;
    /* min-width: {BUTTON_SIZE}px; */ /* Let padding define width generally */
}}

QPushButton:hover {{
    background-color: #522260; /* Darker purple */
    border-color: #522260;
}}

QPushButton:pressed {{
    background-color: #401A4B; /* Even darker */
    border-color: #401A4B;
}}

QPushButton:disabled {{
    background-color: #C8A2D3; /* Lighter purple disabled */
    border-color: #C8A2D3;
    color: #F5F5F5;
}}

QPushButton:checked {{ /* For toggle buttons */
    background-color: #8A3DA6; /* Slightly different shade when checked */
    border-color: #8A3DA6;
}}
QPushButton:checked:hover {{
    background-color: #9E4FB8;
}}


/* Specific Button Types */

/* Add Button (+) */
#AddButton {{
    font-size: {FONT_SIZE_LARGE};
    font-weight: bold;
    background-color: {SECONDARY_LIGHT};
    color: white;
    border: none; /* Remove border */
    min-width: {ROUND_BUTTON_SIZE}px;
    max-width: {ROUND_BUTTON_SIZE}px;
    min-height: {ROUND_BUTTON_SIZE}px;
    max-height: {ROUND_BUTTON_SIZE}px;
    border-radius: {ROUND_BUTTON_SIZE // 2}px; /* Make it round */
    padding: 0px; /* Reset padding for round button */
}}
#AddButton:hover {{
    background-color: #522260;
}}

/* Edit Button (✎) */
#EditButton {{
    /* Inherits general QPushButton style, ensure fixed size is removed in main.py */
    font-size: {FONT_SIZE_BASE}; /* Standardize font size */
    min-width: {BUTTON_SIZE}px; /* Enforce min width */
    padding: 0; /* Adjust padding if needed for icon alignment */
    /* Optional: Use a less prominent color if desired */
    /* background-color: #A0A0A0; */
    /* border-color: #A0A0A0; */
}}
#EditButton:hover {{
    /* background-color: #888888; */
}}

/* Delete Button (🗑) */
#DeleteButton {{
    /* Inherits general QPushButton style, ensure fixed size is removed in main.py */
    font-size: {FONT_SIZE_BASE};
    min-width: {BUTTON_SIZE}px;
    padding: 0;
    /* Optional: Use a distinct color for delete */
    background-color: #dc3545; /* Keep red for delete */
    border-color: #dc3545;
    color: white;
}}
#DeleteButton:hover {{
    background-color: #c82333;
    border-color: #c82333;
}}

/* On/Off Toggle Button (▶/⏸) */
#OnOffToggleButton {{
    /* Inherits general QPushButton style, ensure fixed size is removed in main.py */
    font-size: {FONT_SIZE_LARGE}; /* Keep icon large */
    min-width: {BUTTON_SIZE}px; /* Enforce min width */
    padding: 0;
}}
/* Checked state handled by general QPushButton:checked */


/* --- Input Fields --- */
QLineEdit, QTextEdit, QSpinBox {{
    border: 1px solid {BORDER_COLOR_LIGHT};
    padding: 5px;
    border-radius: {BORDER_RADIUS};
    background-color: white;
    color: {TEXT_COLOR_LIGHT};
    selection-background-color: {SECONDARY_LIGHT};
    selection-color: white;
}}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border-color: {SECONDARY_LIGHT};
    outline: none;
}}

/* --- ComboBox --- */
QComboBox {{
    border: 1px solid {BORDER_COLOR_LIGHT};
    border-radius: {BORDER_RADIUS};
    padding: 5px;
    background-color: white;
    min-width: 5em;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left-width: 1px;
    border-left-color: {BORDER_COLOR_LIGHT};
    border-left-style: solid;
    border-top-right-radius: {BORDER_RADIUS};
    border-bottom-right-radius: {BORDER_RADIUS};
}}

QComboBox::down-arrow {{
    /* Use a standard arrow or leave default */
    /* image: url(:/qt-project.org/styles/commonstyle/images/down_arrow.png); */
}}

QComboBox QAbstractItemView {{ /* Style for the dropdown list */
    border: 1px solid {BORDER_COLOR_LIGHT};
    background-color: white;
    color: {TEXT_COLOR_LIGHT};
    selection-background-color: {SECONDARY_LIGHT};
    selection-color: white;
    outline: none;
}}

/* --- CheckBox --- */
QCheckBox {{
    spacing: 5px; /* Space between indicator and text */
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border-radius: {BORDER_RADIUS};
}}
QCheckBox::indicator:unchecked {{
    border: 1px solid {BORDER_COLOR_LIGHT};
    background-color: white;
}}
QCheckBox::indicator:unchecked:hover {{
    border: 1px solid {SECONDARY_LIGHT};
}}
QCheckBox::indicator:checked {{
    background-color: {SECONDARY_LIGHT};
    border: 1px solid {SECONDARY_LIGHT};
    /* Add a checkmark image if desired */
    /* image: url(path/to/light-check.png); */
}}
QCheckBox::indicator:checked:hover {{
    background-color: #522260;
    border: 1px solid #522260;
}}

/* --- Menu Bar --- */
QMenuBar {{
    background-color: #EAEAEA; /* Slightly darker than main bg */
    border-bottom: 1px solid {BORDER_COLOR_LIGHT};
}}
QMenuBar::item {{
    padding: 4px 8px;
    background: transparent;
}}
QMenuBar::item:selected {{
    background: #D3D3D3;
}}
QMenuBar::item:pressed {{
    background: {SECONDARY_LIGHT};
    color: white;
}}

/* --- Menu --- */
QMenu {{
    background-color: white;
    border: 1px solid {BORDER_COLOR_LIGHT};
    padding: 3px; /* Reduced padding */
}}
QMenu::item {{
    padding: 4px 15px; /* Adjusted padding */
}}
QMenu::item:selected {{
    background-color: {SECONDARY_LIGHT};
    color: white;
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER_COLOR_LIGHT};
    margin: 3px 5px;
}}

/* --- Tooltips --- */
QToolTip {{
    color: {TEXT_COLOR_LIGHT};
    background-color: #FFFFE0; /* Light yellow tooltip */
    border: 1px solid {BORDER_COLOR_LIGHT};
    padding: 4px;
    border-radius: {BORDER_RADIUS};
}}

/* --- Message Box --- */
QMessageBox {{
    background-color: {PRIMARY_LIGHT};
}}
QMessageBox QLabel {{
    color: {TEXT_COLOR_LIGHT};
}}
/* MessageBox buttons inherit general QPushButton style */

/* --- Item Selection (for Icon Gallery, etc.) --- */
QListView::item:selected, QTreeView::item:selected, QTableView::item:selected {{
    background-color: {SECONDARY_LIGHT};
    color: white;
}}
/* Style for selected item in a generic QListWidget/QListView */
QListWidget::item:selected {{
    background-color: {SECONDARY_LIGHT};
    color: white;
    /* Add a border or outline for more emphasis */
    /* border: 1px solid #FFFFFF; */
}}
QListWidget::item:hover {{
    background-color: #EAEAEA; /* Subtle hover */
}}

/* Style for a potential Icon Button if used in gallery */
QPushButton#IconButton:checked {{ /* If icons are checkable buttons */
    background-color: {SECONDARY_LIGHT};
    border: 2px solid white; /* Highlight border when checked */
}}

"""

# =============================================
#           DARK MODE STYLESHEET
# =============================================
STYLESHEET_DARK = f"""
/* --- Global --- */
QWidget {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE_BASE};
    color: {TEXT_COLOR_DARK};
}}

QMainWindow, QDialog {{
    background-color: {PRIMARY_DARK};
}}

/* --- Scroll Area --- */
QScrollArea {{
    border: none;
    background-color: transparent;
}}

#presetGridWidget {{
    background-color: {PRIMARY_DARK};
    padding: 5px;
}}

/* --- Preset Widget --- */
PresetWidget {{
    background-color: #343A40; /* Darker background for presets */
    border: 1px solid {BORDER_COLOR_DARK};
    border-radius: {BORDER_RADIUS};
    color: {TEXT_COLOR_DARK};
    padding: 5px;
}}

PresetWidget:hover {{
    background-color: #495057; /* Slightly lighter hover */
}}

/* Title Label within PresetWidget */
PresetWidget QLabel {{
    background-color: transparent;
    color: {TEXT_COLOR_DARK};
    font-weight: bold;
}}

/* --- Buttons --- */
QPushButton {{
    background-color: {SECONDARY_DARK};
    color: {PRIMARY_DARK}; /* Dark text on lighter purple */
    border: 1px solid {SECONDARY_DARK};
    padding: {BUTTON_PADDING_V} {BUTTON_PADDING_H};
    border-radius: {BORDER_RADIUS};
    font-size: {FONT_SIZE_BASE};
    min-height: {BUTTON_SIZE}px;
    /* min-width: {BUTTON_SIZE}px; */
}}

QPushButton:hover {{
    background-color: #B362CC; /* Lighter purple */
    border-color: #B362CC;
}}

QPushButton:pressed {{
    background-color: #C87FE0; /* Even lighter */
    border-color: #C87FE0;
}}

QPushButton:disabled {{
    background-color: #5A3E63; /* Darker purple disabled */
    border-color: #5A3E63;
    color: #8A8A8A;
}}

QPushButton:checked {{ /* For toggle buttons */
    background-color: #8A3DA6; /* Darker shade when checked */
    border-color: #8A3DA6;
    color: {TEXT_COLOR_DARK}; /* Light text when checked */
}}
QPushButton:checked:hover {{
    background-color: #7B3694;
}}


/* Specific Button Types */

/* Add Button (+) */
#AddButton {{
    font-size: {FONT_SIZE_LARGE};
    font-weight: bold;
    background-color: {SECONDARY_DARK};
    color: {PRIMARY_DARK};
    border: none;
    min-width: {ROUND_BUTTON_SIZE}px;
    max-width: {ROUND_BUTTON_SIZE}px;
    min-height: {ROUND_BUTTON_SIZE}px;
    max-height: {ROUND_BUTTON_SIZE}px;
    border-radius: {ROUND_BUTTON_SIZE // 2}px;
    padding: 0px;
}}
#AddButton:hover {{
    background-color: #B362CC;
}}

/* Edit Button (✎) */
#EditButton {{
    font-size: {FONT_SIZE_BASE};
    min-width: {BUTTON_SIZE}px;
    padding: 0;
    /* Optional: Adjust color for dark mode */
    /* background-color: #6c757d; */
    /* border-color: #6c757d; */
}}
#EditButton:hover {{
    /* background-color: #5a6268; */
}}

/* Delete Button (🗑) */
#DeleteButton {{
    font-size: {FONT_SIZE_BASE};
    min-width: {BUTTON_SIZE}px;
    padding: 0;
    background-color: #dc3545; /* Keep red */
    border-color: #dc3545;
    color: white;
}}
#DeleteButton:hover {{
    background-color: #c82333;
    border-color: #c82333;
}}

/* On/Off Toggle Button (▶/⏸) */
#OnOffToggleButton {{
    font-size: {FONT_SIZE_LARGE};
    min-width: {BUTTON_SIZE}px;
    padding: 0;
}}
/* Checked state handled by general QPushButton:checked */


/* --- Input Fields --- */
QLineEdit, QTextEdit, QSpinBox {{
    border: 1px solid {BORDER_COLOR_DARK};
    padding: 5px;
    border-radius: {BORDER_RADIUS};
    background-color: #495057; /* Darker input background */
    color: {TEXT_COLOR_DARK};
    selection-background-color: {SECONDARY_DARK};
    selection-color: {PRIMARY_DARK};
}}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border-color: {SECONDARY_DARK};
    outline: none;
}}

/* --- ComboBox --- */
QComboBox {{
    border: 1px solid {BORDER_COLOR_DARK};
    border-radius: {BORDER_RADIUS};
    padding: 5px;
    background-color: #495057;
    color: {TEXT_COLOR_DARK};
    min-width: 5em;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left-width: 1px;
    border-left-color: {BORDER_COLOR_DARK};
    border-left-style: solid;
    border-top-right-radius: {BORDER_RADIUS};
    border-bottom-right-radius: {BORDER_RADIUS};
    background-color: #5A6268; /* Slightly different dropdown bg */
}}

QComboBox::down-arrow {{
    /* Use a standard arrow or leave default */
     /* image: url(path/to/dark-down-arrow.png); */
}}

QComboBox QAbstractItemView {{ /* Style for the dropdown list */
    border: 1px solid {BORDER_COLOR_DARK};
    background-color: #343A40; /* Dark dropdown background */
    color: {TEXT_COLOR_DARK};
    selection-background-color: {SECONDARY_DARK};
    selection-color: {PRIMARY_DARK};
    outline: none;
}}

/* --- CheckBox --- */
QCheckBox {{
    spacing: 5px;
}}
QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border-radius: {BORDER_RADIUS};
}}
QCheckBox::indicator:unchecked {{
    border: 1px solid {BORDER_COLOR_DARK};
    background-color: #495057;
}}
QCheckBox::indicator:unchecked:hover {{
    border: 1px solid {SECONDARY_DARK};
}}
QCheckBox::indicator:checked {{
    background-color: {SECONDARY_DARK};
    border: 1px solid {SECONDARY_DARK};
    /* Add a checkmark image if desired */
    /* image: url(path/to/dark-check.png); */
}}
QCheckBox::indicator:checked:hover {{
    background-color: #B362CC;
    border: 1px solid #B362CC;
}}

/* --- Menu Bar --- */
QMenuBar {{
    background-color: #343A40;
    border-bottom: 1px solid {BORDER_COLOR_DARK};
}}
QMenuBar::item {{
    padding: 4px 8px;
    background: transparent;
    color: {TEXT_COLOR_DARK};
}}
QMenuBar::item:selected {{
    background: #495057;
}}
QMenuBar::item:pressed {{
    background: {SECONDARY_DARK};
    color: {PRIMARY_DARK};
}}

/* --- Menu --- */
QMenu {{
    background-color: #343A40;
    border: 1px solid {BORDER_COLOR_DARK};
    padding: 3px;
    color: {TEXT_COLOR_DARK};
}}
QMenu::item {{
    padding: 4px 15px;
}}
QMenu::item:selected {{
    background-color: {SECONDARY_DARK};
    color: {PRIMARY_DARK};
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER_COLOR_DARK};
    margin: 3px 5px;
}}

/* --- Tooltips --- */
QToolTip {{
    color: {TEXT_COLOR_DARK};
    background-color: #495057; /* Dark tooltip background */
    border: 1px solid {BORDER_COLOR_DARK};
    padding: 4px;
    border-radius: {BORDER_RADIUS};
}}

/* --- Message Box --- */
QMessageBox {{
    background-color: {PRIMARY_DARK};
}}
QMessageBox QLabel {{
    color: {TEXT_COLOR_DARK};
}}
/* MessageBox buttons inherit general QPushButton style */

/* --- Item Selection (for Icon Gallery, etc.) --- */
QListView::item:selected, QTreeView::item:selected, QTableView::item:selected {{
    background-color: {SECONDARY_DARK};
    color: {PRIMARY_DARK};
}}
QListWidget::item:selected {{
    background-color: {SECONDARY_DARK};
    color: {PRIMARY_DARK};
    /* border: 1px solid #FFFFFF; */ /* Optional border */
}}
QListWidget::item:hover {{
    background-color: #495057;
}}

/* Style for a potential Icon Button if used in gallery */
QPushButton#IconButton:checked {{
    background-color: {SECONDARY_DARK};
    border: 2px solid {TEXT_COLOR_DARK}; /* Light border when checked */
}}

"""

# Default stylesheet (can be changed later)
STYLESHEET = STYLESHEET_LIGHT