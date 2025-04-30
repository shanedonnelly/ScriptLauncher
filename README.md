# ScriptLauncher

A cross-plateform desktop application to easily organize, manage, and launch your scripts, commands, and recorded macros with a simple graphical interface.
Only Linux release currently available : [releases page](https://github.com/shanedonnelly/ScriptLauncher/releases)
## Features

*   **Multiple Preset Types:**
    *   **Standard:** Run any shell script or command.
    *   **On/Off:** Toggle between two different scripts (e.g., start/stop a service).
    *   **Recorded:** Record and replay sequences of mouse and keyboard actions.
*   **Customizable Presets:** Assign titles and icons to your presets.
*   **Import/Export:** Share your presets easily using `.slaunch` files.
*   **Recording:** Built-in recorder for mouse and keyboard events (uses `pynput`).
    *   *Stop recording by cliking back on the App. 
*   **Replay Control:** Play recorded macros once or multiple times (can be stopped).
*   **Theme Support:** Switch between Light and Dark themes. 
*   **Standalone Packaging:** Bundled into a single executable and `.deb` package for easy installation.

## Preset Types Explained

1.  **Standard:**
    *   Executes the content of the 'Script' field as a shell command or script.
    *   Ideal for launching applications, running maintenance tasks, etc.
2.  **On/Off:**
    *   Has two script fields: 'Script On' and 'Script Off'.
    *   Clicking the action button toggles the state and runs the corresponding script.
    *   Useful for starting/stopping services, toggling settings, etc.
    *   The current state (On/Off) is saved with the preset.
3.  **Recorded:**
    *   Stores a sequence of recorded mouse and keyboard events directly within the `.slaunch` file (in JSON format).
    *   Clicking the action button ('▶') replays the recorded sequence.
    *   You can specify how many times the sequence should repeat ('-1' for infinite).
    *   While replaying, the button changes to '■'; clicking it stops the replay.
    *   *Note:* Recording captures events system-wide. Be mindful of what you record.

## Installation

### Using the .deb Package (Recommended for Ubuntu/Debian)

1.  Download the latest `.deb` file (e.g., `scriptlauncher_X.Y_amd64.deb`) from the [releases page](https://github.com/shanedonnelly/ScriptLauncher/releases).

## Uninstallation for Ubuntu/Debian 
```bash
sudo apt remove scriptlauncher
sudo apt autoremove
```

### From Source (for Development / Other Linux Distros)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/shanedonnelly/ScriptLauncher.git
    cd ScriptLauncher/qt_app
    ```
2.  **Create and activate a virtual environment (Recommended):**
    ```bash
    python3 -m venv myenv
    source myenv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    # You might also need system packages for PyQt6 and pynput's backend
    # On Debian/Ubuntu: sudo apt install python3-tk python3-dev libx11-dev libxtst-dev libpng-dev libxkbcommon-x11-0
    ```
4.  **Run the application:**
    ```bash
    python main.py
    ```

## Usage

1.  **Launch ScriptLauncher** from your application menu.
2.  **Add Preset:** Click the large '➕' button.
3.  **Configure Preset:**
    *   Give it a **Title**.
    *   Select an **Icon** (optional).
    *   Choose the **Preset Type** (Standard, On/Off, Recorded).
    *   Fill in the relevant fields (Script, Script On/Off, Record options).
    *   **For Recorded type:** Click "Record", perform actions, stop by holding Left Click + Left Shift for 2s.
    *   Click **Save**.
4.  **Run Preset:**
    *   **Standard:** Click anywhere on the preset widget (except the small buttons).
    *   **On/Off:** Click the '▶'/'⏸' action button.
    *   **Recorded:** Click the '▶' action button to play, '■' to stop.
5.  **Edit/Delete:** Use the '✎' (Edit) and '🗑' (Delete) buttons on the preset widget.
6.  **Import/Export:** Use the File menu options.
7.  **Theme:** Use the Theme menu to switch between Light and Dark modes.

## Building (for Developers)

The `build.sh` script automates the process of creating a standalone executable using PyInstaller and packaging it into a `.deb` file.

**Prerequisites:**

*   Python 3, Pip, Venv
*   `pyinstaller` (installed via `pip`)
*   Debian packaging tools: `dpkg-dev`, `fakeroot` (`sudo apt install dpkg-dev fakeroot`)

**Build:**

```bash
cd qt_app
./build.sh
```
## Roadmap / Future Ideas

*   **Theme Persistence:** Save the selected theme (Light/Dark) so it persists.
*   **Improved Replay Interruption:** Allow stopping a recorded macro replay by just doing an action.
*   **Dynamic Grid Layout:** Make the preset grid automatically adjust the number of columns based on the window size.
*   **Grid Preferences:** Add settings to allow users to customize the grid layout.
*   **Expanded Icon Library:** Include a much larger selection of built-in icons for presets.
