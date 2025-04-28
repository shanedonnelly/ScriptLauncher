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
BUTTON_SIZE = 30 # Default height for most buttons
BUTTON_PADDING_H = "10px"
BUTTON_PADDING_V = "5px"
# ROUND_BUTTON_SIZE = 35 # No longer used?
ACTION_BUTTON_SIZE_PX = 25 # Define the size in pixels for fixed size buttons

# --- General ---
BORDER_RADIUS = "2px"

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
    padding: 5px;
}}

/* --- Preset Widget --- */
PresetWidget {{
    background-color: white;
    border: 1px solid {BORDER_COLOR_LIGHT};
    border-radius: {BORDER_RADIUS};
    color: {TEXT_COLOR_LIGHT};
    padding: 5px; /* Internal padding */
    /* Fixed size is set in Python code (setFixedSize) */
}}

PresetWidget:hover {{
    background-color: #EAEAEA;
}}

/* Title Label within PresetWidget */
PresetWidget QLabel {{
    background-color: transparent;
    color: {TEXT_COLOR_LIGHT};
}}
/* Icon label */
PresetWidget QLabel#icon_label {{
    font-weight: normal;
}}


/* --- Buttons --- */
QPushButton {{
    background-color: {SECONDARY_LIGHT};
    color: white;
    border: 1px solid {SECONDARY_LIGHT};
    padding: {BUTTON_PADDING_V} {BUTTON_PADDING_H};
    border-radius: {BORDER_RADIUS};
    font-size: {FONT_SIZE_BASE};
    min-height: {BUTTON_SIZE}px; /* Default min height for dialog buttons etc. */
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

/* Add Button (+) - Style for the large button filling a grid slot */
#AddButton {{
    font-size: 24pt;
    font-weight: lighter;
    background-color: #EAEAEA;
    color: #888888;
    border: 2px dashed {BORDER_COLOR_LIGHT};
    padding: 10px; /* Internal padding */
    border-radius: {BORDER_RADIUS};
    /* Fixed size is set in Python code (setFixedSize) */
    /* Remove min/max width/height */
}}
#AddButton:hover {{
    background-color: #DCDCDC;
    color: #666666;
    border-color: #C0C0C0;
}}

/* --- Right Column Buttons in PresetWidget --- */
/* Edit Button (✎) */
#EditButton {{
    font-size: {FONT_SIZE_BASE};
    min-width: {ACTION_BUTTON_SIZE_PX}px; /* Keep fixed size for these small buttons */
    max-width: {ACTION_BUTTON_SIZE_PX}px;
    min-height: {ACTION_BUTTON_SIZE_PX}px;
    max-height: {ACTION_BUTTON_SIZE_PX}px;
    padding: 0;
    background-color: #A0A0A0;
    border-color: #A0A0A0;
}}
#EditButton:hover {{
    background-color: #888888;
}}

/* Delete Button (🗑) */
#DeleteButton {{
    font-size: {FONT_SIZE_BASE};
    min-width: {ACTION_BUTTON_SIZE_PX}px;
    max-width: {ACTION_BUTTON_SIZE_PX}px;
    min-height: {ACTION_BUTTON_SIZE_PX}px;
    max-height: {ACTION_BUTTON_SIZE_PX}px;
    padding: 0;
    background-color: #dc3545;
    border-color: #dc3545;
    color: white;
}}
#DeleteButton:hover {{
    background-color: #c82333;
    border-color: #c82333;
}}

/* --- Remove RunButton style --- */
/* #RunButton {{ ... }} */

/* On/Off Toggle Button (▶/⏸) */
#OnOffToggleButton {{
    font-size: {FONT_SIZE_LARGE};
    min-width: {ACTION_BUTTON_SIZE_PX}px;
    max-width: {ACTION_BUTTON_SIZE_PX}px;
    min-height: {ACTION_BUTTON_SIZE_PX}px;
    max-height: {ACTION_BUTTON_SIZE_PX}px;
    padding: 0;
    /* Inherits base purple, checked state handled above */
}}

/* Replay Button (▶/■ for recorded) */
#ReplayButton {{
    font-size: {FONT_SIZE_LARGE};
    min-width: {ACTION_BUTTON_SIZE_PX}px;
    max-width: {ACTION_BUTTON_SIZE_PX}px;
    min-height: {ACTION_BUTTON_SIZE_PX}px;
    max-height: {ACTION_BUTTON_SIZE_PX}px;
    padding: 0;
    /* Inherits base purple */
}}

/* --- Input Fields, ComboBox, CheckBox, MenuBar, Menu, Tooltips, MessageBox, Item Selection --- */
/* ... (These styles remain largely the same) ... */
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
    /* image: url(:/qt-project.org/styles/commonstyle/images/down_arrow.png); */
}}

QComboBox QAbstractItemView {{
    border: 1px solid {BORDER_COLOR_LIGHT};
    background-color: white;
    color: {TEXT_COLOR_LIGHT};
    selection-background-color: {SECONDARY_LIGHT};
    selection-color: white;
    outline: none;
}}

QCheckBox {{
    spacing: 5px;
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
    /* image: url(path/to/light-check.png); */
}}
QCheckBox::indicator:checked:hover {{
    background-color: #522260;
    border: 1px solid #522260;
}}

QMenuBar {{
    background-color: #EAEAEA;
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

QMenu {{
    background-color: white;
    border: 1px solid {BORDER_COLOR_LIGHT};
    padding: 3px;
}}
QMenu::item {{
    padding: 4px 15px;
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

QToolTip {{
    color: {TEXT_COLOR_LIGHT};
    background-color: #FFFFE0;
    border: 1px solid {BORDER_COLOR_LIGHT};
    padding: 4px;
    border-radius: {BORDER_RADIUS};
}}

QMessageBox {{
    background-color: {PRIMARY_LIGHT};
}}
QMessageBox QLabel {{
    color: {TEXT_COLOR_LIGHT};
}}

QListView::item:selected, QTreeView::item:selected, QTableView::item:selected {{
    background-color: {SECONDARY_LIGHT};
    color: white;
}}
QListWidget::item:selected {{
    background-color: {SECONDARY_LIGHT};
    color: white;
}}
QListWidget::item:hover {{
    background-color: #EAEAEA;
}}

QPushButton#IconButton:checked {{
    background-color: {SECONDARY_LIGHT};
    border: 2px solid white;
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
    background-color: #343A40;
    border: 1px solid {BORDER_COLOR_DARK};
    border-radius: {BORDER_RADIUS};
    color: {TEXT_COLOR_DARK};
    padding: 5px;
    /* Fixed size is set in Python code (setFixedSize) */
}}

PresetWidget:hover {{
    background-color: #495057;
}}

/* Title Label within PresetWidget */
PresetWidget QLabel {{
    background-color: transparent;
    color: {TEXT_COLOR_DARK};
}}
PresetWidget QLabel#icon_label {{
    font-weight: normal;
}}


/* --- Buttons --- */
QPushButton {{
    background-color: {SECONDARY_DARK};
    color: {PRIMARY_DARK};
    border: 1px solid {SECONDARY_DARK};
    padding: {BUTTON_PADDING_V} {BUTTON_PADDING_H};
    border-radius: {BORDER_RADIUS};
    font-size: {FONT_SIZE_BASE};
    min-height: {BUTTON_SIZE}px;
}}

QPushButton:hover {{
    background-color: #B362CC;
    border-color: #B362CC;
}}

QPushButton:pressed {{
    background-color: #C87FE0;
    border-color: #C87FE0;
}}

QPushButton:disabled {{
    background-color: #5A3E63;
    border-color: #5A3E63;
    color: #8A8A8A;
}}

QPushButton:checked {{
    background-color: #8A3DA6;
    border-color: #8A3DA6;
    color: {TEXT_COLOR_DARK};
}}
QPushButton:checked:hover {{
    background-color: #7B3694;
}}


/* Specific Button Types */

/* Add Button (+) */
#AddButton {{
    font-size: 24pt;
    font-weight: lighter;
    background-color: #343A40;
    color: #888888;
    border: 2px dashed {BORDER_COLOR_DARK};
    padding: 10px;
    border-radius: {BORDER_RADIUS};
    /* Fixed size is set in Python code (setFixedSize) */
}}
#AddButton:hover {{
    background-color: #495057;
    color: #AAAAAA;
    border-color: #6c757d;
}}

/* --- Right Column Buttons in PresetWidget --- */
/* Edit Button (✎) */
#EditButton {{
    font-size: {FONT_SIZE_BASE};
    min-width: {ACTION_BUTTON_SIZE_PX}px;
    max-width: {ACTION_BUTTON_SIZE_PX}px;
    min-height: {ACTION_BUTTON_SIZE_PX}px;
    max-height: {ACTION_BUTTON_SIZE_PX}px;
    padding: 0;
    background-color: #6c757d;
    border-color: #6c757d;
    color: {TEXT_COLOR_DARK};
}}
#EditButton:hover {{
    background-color: #5a6268;
}}

/* Delete Button (🗑) */
#DeleteButton {{
    font-size: {FONT_SIZE_BASE};
    min-width: {ACTION_BUTTON_SIZE_PX}px;
    max-width: {ACTION_BUTTON_SIZE_PX}px;
    min-height: {ACTION_BUTTON_SIZE_PX}px;
    max-height: {ACTION_BUTTON_SIZE_PX}px;
    padding: 0;
    background-color: #dc3545;
    border-color: #dc3545;
    color: white;
}}
#DeleteButton:hover {{
    background-color: #c82333;
    border-color: #c82333;
}}

/* --- Remove RunButton style --- */
/* #RunButton {{ ... }} */

/* On/Off Toggle Button (▶/⏸) */
#OnOffToggleButton {{
    font-size: {FONT_SIZE_LARGE};
    min-width: {ACTION_BUTTON_SIZE_PX}px;
    max-width: {ACTION_BUTTON_SIZE_PX}px;
    min-height: {ACTION_BUTTON_SIZE_PX}px;
    max-height: {ACTION_BUTTON_SIZE_PX}px;
    padding: 0;
}}

/* Replay Button (▶/■ for recorded) */
#ReplayButton {{
    font-size: {FONT_SIZE_LARGE};
    min-width: {ACTION_BUTTON_SIZE_PX}px;
    max-width: {ACTION_BUTTON_SIZE_PX}px;
    min-height: {ACTION_BUTTON_SIZE_PX}px;
    max-height: {ACTION_BUTTON_SIZE_PX}px;
    padding: 0;
}}


/* --- Input Fields, ComboBox, CheckBox, MenuBar, Menu, Tooltips, MessageBox, Item Selection --- */
/* ... (These styles remain largely the same but adapted for dark mode) ... */
QLineEdit, QTextEdit, QSpinBox {{
    border: 1px solid {BORDER_COLOR_DARK};
    padding: 5px;
    border-radius: {BORDER_RADIUS};
    background-color: #495057;
    color: {TEXT_COLOR_DARK};
    selection-background-color: {SECONDARY_DARK};
    selection-color: {PRIMARY_DARK};
}}

QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {{
    border-color: {SECONDARY_DARK};
    outline: none;
}}

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
    background-color: #5A6268;
}}

QComboBox::down-arrow {{
     /* image: url(path/to/dark-down-arrow.png); */
}}

QComboBox QAbstractItemView {{
    border: 1px solid {BORDER_COLOR_DARK};
    background-color: #343A40;
    color: {TEXT_COLOR_DARK};
    selection-background-color: {SECONDARY_DARK};
    selection-color: {PRIMARY_DARK};
    outline: none;
}}

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
    /* image: url(path/to/dark-check.png); */
}}
QCheckBox::indicator:checked:hover {{
    background-color: #B362CC;
    border: 1px solid #B362CC;
}}

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

QToolTip {{
    color: {TEXT_COLOR_DARK};
    background-color: #495057;
    border: 1px solid {BORDER_COLOR_DARK};
    padding: 4px;
    border-radius: {BORDER_RADIUS};
}}

QMessageBox {{
    background-color: {PRIMARY_DARK};
}}
QMessageBox QLabel {{
    color: {TEXT_COLOR_DARK};
}}

QListView::item:selected, QTreeView::item:selected, QTableView::item:selected {{
    background-color: {SECONDARY_DARK};
    color: {PRIMARY_DARK};
}}
QListWidget::item:selected {{
    background-color: {SECONDARY_DARK};
    color: {PRIMARY_DARK};
}}
QListWidget::item:hover {{
    background-color: #495057;
}}

QPushButton#IconButton:checked {{
    background-color: {SECONDARY_DARK};
    border: 2px solid {TEXT_COLOR_DARK};
}}

"""

# Default stylesheet (can be changed later)
STYLESHEET = STYLESHEET_DARK # Or STYLESHEET_LIGHT