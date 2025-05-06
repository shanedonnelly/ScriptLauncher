import os
import sys
import platform
import subprocess
import shutil
import json
from PyQt6.QtWidgets import QMessageBox # type: ignore
import platformdirs # <-- Import platformdirs
import time # For cleanup delay
import threading # For cleanup thread

# --- Application Info for platformdirs ---
APP_NAME = "ScriptLauncher"
APP_AUTHOR = "ShaneDonnelly" # Or your company/developer name

# --- Determine Paths ---
try:
    # If running as a PyInstaller bundle (_MEIPASS is the temporary extracted folder)
    BUNDLE_DIR = sys._MEIPASS
    IS_BUNDLED = True
except AttributeError:
    # If running as a normal script
    BUNDLE_DIR = os.path.abspath(os.path.dirname(__file__))
    IS_BUNDLED = False

# Assets are relative to the bundle/script location
ASSETS_FOLDER = os.path.join(BUNDLE_DIR, "assets")
ICONS_FOLDER = os.path.join(ASSETS_FOLDER, "app_icons")

# Presets go into the user's data directory
USER_DATA_DIR = platformdirs.user_data_dir(APP_NAME, APP_AUTHOR)
PRESETS_FOLDER = os.path.join(USER_DATA_DIR, "presets") # <-- User-specific presets path

# --- Ensure necessary folders exist ---
# Ensure user data and presets folder exist
os.makedirs(PRESETS_FOLDER, exist_ok=True)
# Ensure bundled assets/icons folder exists (mainly for dev mode, PyInstaller handles bundled)
# We don't create ASSETS_FOLDER itself here, icons is enough
os.makedirs(ICONS_FOLDER, exist_ok=True)

# --- First Run: Copy Default Presets ---
def copy_default_presets_if_needed():
    """Copies default presets from bundle/source to user dir on first run."""
    # Check if the user presets folder is empty or just created
    # A simple check: does it contain any .slaunch files?
    if not any(f.endswith('.slaunch') for f in os.listdir(PRESETS_FOLDER)):
        print(f"User presets folder '{PRESETS_FOLDER}' appears empty. Copying defaults...")

        # Define the source of the default presets
        if IS_BUNDLED:
            # Path inside the PyInstaller bundle (using the name from build.sh)
            default_presets_source = os.path.join(BUNDLE_DIR, "presets_default")
        else:
            # Path relative to script in development mode
            default_presets_source = os.path.join(os.path.dirname(__file__), "presets")

        if os.path.exists(default_presets_source):
            try:
                # Copy each file from source to user presets folder
                for item_name in os.listdir(default_presets_source):
                    source_item = os.path.join(default_presets_source, item_name)
                    dest_item = os.path.join(PRESETS_FOLDER, item_name)
                    if os.path.isfile(source_item) and source_item.endswith(".slaunch"):
                        print(f"  Copying {item_name}...")
                        shutil.copy2(source_item, dest_item) # copy2 preserves metadata
                print("Default presets copied.")
            except Exception as e:
                print(f"Error copying default presets from '{default_presets_source}': {e}")
                QMessageBox.warning(None, "Preset Copy Error",
                                    f"Could not copy default presets on first run.\nSource: {default_presets_source}\nError: {e}")
        else:
            print(f"Warning: Default presets source not found at '{default_presets_source}'. Cannot copy defaults.")

# Call this function once at startup (e.g., here or early in main.py)
copy_default_presets_if_needed()
# --- End First Run Logic ---


def resource_path(relative_path):
    """ Get absolute path to resource within the bundle/script dir. """
    # Use BUNDLE_DIR now instead of BASE_PATH
    return os.path.join(BUNDLE_DIR, relative_path)

def get_icon_path(icon_name):
    """ Get the full path to an icon file within the assets/app_icons folder. """
    if not icon_name or icon_name == 'none':
        return None
    # Uses the ICONS_FOLDER defined above, which is relative to BUNDLE_DIR
    return os.path.join(ICONS_FOLDER, icon_name)

# --- load_presets, save_preset, delete_preset ---
# These functions should now correctly use the user-specific PRESETS_FOLDER
# No changes needed inside them as they rely on the global PRESETS_FOLDER variable.

def load_presets():
    """ Loads all presets from the user's presets folder. """ # <-- Docstring updated
    presets = []
    # PRESETS_FOLDER now points to the user data directory
    if not os.path.exists(PRESETS_FOLDER):
        print(f"Warning: User presets folder not found at {PRESETS_FOLDER}")
        # It should have been created, but handle defensively
        os.makedirs(PRESETS_FOLDER, exist_ok=True)
        return presets # Return empty list if just created

    for file_name in sorted(os.listdir(PRESETS_FOLDER)):
        if file_name.endswith(".slaunch"):
            preset_path = os.path.join(PRESETS_FOLDER, file_name)
            try:
                with open(preset_path, "r", encoding='utf-8') as f: # Specify encoding
                    lines = f.readlines()

                # Basic validation (at least title, type, icon)
                if len(lines) < 3:
                    print(f"Warning: Skipping malformed preset file (too short): {file_name}")
                    continue

                preset_data = {
                    'file_name': file_name,
                    'title': lines[0].strip().replace("title=", ""),
                    'type': lines[1].strip().replace("type=", ""),
                    'icon': lines[2].strip().replace("icon=", ""),
                    # Initialize all possible fields
                    'script': "",
                    'script_on': "",
                    'script_off': "",
                    'on_off_state': False,
                    # --- Remove record_path, add recorded_events ---
                    # 'record_path': None,
                    'recorded_events': None, # To store the parsed JSON data
                    'how_many': 1
                }

                content_lines = lines[3:] # Content starts from the 4th line
                current_section = None
                json_lines = []
                in_record_section = False

                for i, line in enumerate(content_lines):
                    stripped_line = line.strip()

                    # --- Stop processing other sections if we hit the record marker ---
                    if stripped_line == "record=":
                        in_record_section = True
                        current_section = None # Ensure no other section is active
                        continue

                    # --- If in record section, collect lines for JSON ---
                    if in_record_section:
                        json_lines.append(line) # Keep original lines including indentation/newlines
                        continue

                    # Detect section headers (only if not in record section)
                    if stripped_line == "script=":
                        current_section = "script"
                        continue
                    elif stripped_line == "script_on=":
                        current_section = "script_on"
                        continue
                    elif stripped_line == "script_off=":
                        current_section = "script_off"
                        continue
                    elif stripped_line.startswith("on_off_state="):
                        preset_data['on_off_state'] = stripped_line.replace("on_off_state=", "") == "True"
                        current_section = None
                        continue
                    elif stripped_line.startswith("how_many="):
                        try:
                            preset_data['how_many'] = int(stripped_line.replace("how_many=", ""))
                        except ValueError:
                            preset_data['how_many'] = 1 # Default if invalid
                        current_section = None
                        continue

                    # Append line to the current section if it's active
                    if current_section == "script":
                        preset_data['script'] += line
                    elif current_section == "script_on":
                        preset_data['script_on'] += line
                    elif current_section == "script_off":
                        preset_data['script_off'] += line

                # Strip trailing newlines from scripts
                preset_data['script'] = preset_data['script'].rstrip('\n')
                preset_data['script_on'] = preset_data['script_on'].rstrip('\n')
                preset_data['script_off'] = preset_data['script_off'].rstrip('\n')

                # --- Process collected JSON lines for recorded type ---
                if preset_data['type'] == "recorded":
                    if json_lines:
                        json_string = "".join(json_lines)
                        try:
                            preset_data['recorded_events'] = json.loads(json_string)
                            if not isinstance(preset_data['recorded_events'], list):
                                 print(f"Warning: Parsed JSON for {file_name} is not a list. Resetting.")
                                 preset_data['recorded_events'] = None
                        except json.JSONDecodeError as e:
                            print(f"Error decoding embedded JSON in {file_name}: {e}")
                            preset_data['recorded_events'] = None # Set to None if JSON is invalid
                    else:
                        print(f"Warning: 'record=' section missing or empty in recorded preset: {file_name}")
                        preset_data['recorded_events'] = None

                presets.append(preset_data)
            except Exception as e:
                print(f"Error loading preset {file_name}: {e}")
                import traceback
                traceback.print_exc()
    return presets


def save_preset(preset_data):
    """ Saves a single preset data dictionary to the user's .slaunch file. """ # <-- Docstring updated
    file_name = preset_data.get('file_name')
    is_new = not file_name
    if is_new:
        # Generate a new file name if one doesn't exist in the user's folder
        existing = [f for f in os.listdir(PRESETS_FOLDER) if f.endswith(".slaunch")]
        next_index = 1
        while f"preset{next_index}.slaunch" in existing:
            next_index += 1
        file_name = f"preset{next_index}.slaunch"
        preset_data['file_name'] = file_name # Update the dict with the new name

    # PRESETS_FOLDER now points to the user data directory
    preset_path = os.path.join(PRESETS_FOLDER, file_name)

    try:
        with open(preset_path, "w", encoding='utf-8') as f: # Specify encoding
            f.write(f"title={preset_data.get('title', '')}\n")
            f.write(f"type={preset_data.get('type', 'standard')}\n")
            f.write(f"icon={preset_data.get('icon', 'none')}\n")

            preset_type = preset_data.get('type')
            if preset_type == "on_off":
                f.write(f"script_on=\n{preset_data.get('script_on', '')}\n")
                f.write(f"script_off=\n{preset_data.get('script_off', '')}\n")
                f.write(f"on_off_state={preset_data.get('on_off_state', False)}\n")
            elif preset_type == "recorded":
                f.write(f"script=\n") # Empty script section for recorded type
                f.write(f"how_many={preset_data.get('how_many', 1)}\n")
                # --- Embed JSON data ---
                f.write("record=\n") # Marker for embedded JSON
                recorded_events = preset_data.get('recorded_events')
                if recorded_events and isinstance(recorded_events, list):
                    json.dump(recorded_events, f, indent=2) # Write JSON with indentation
                    f.write("\n") # Add a final newline for clarity
                else:
                    f.write("[]\n") # Write empty JSON array if no data
            else: # Standard
                f.write(f"script=\n{preset_data.get('script', '')}\n")

        print(f"Preset saved: {preset_path}") # Path is now user-specific
        return True, preset_data
    except Exception as e:
        error_message = f"Could not save preset {file_name}:\n{e}"
        print(f"Error saving preset: {error_message}")
        QMessageBox.critical(None, "Save Error", error_message)
        return False, error_message # Return failure and the error message


def delete_preset(file_name):
    """ Deletes a preset file from the user's presets folder. """ # <-- Docstring updated
    # PRESETS_FOLDER now points to the user data directory
    preset_path = os.path.join(PRESETS_FOLDER, file_name)
    try:
        if os.path.exists(preset_path):
            os.remove(preset_path)
            print(f"Preset deleted: {preset_path}") # Path is now user-specific
            return True
        else:
            print(f"Preset not found for deletion: {preset_path}")
            return False
    except Exception as e:
        error_message = f"Could not delete preset {file_name}:\n{e}"
        print(f"Error deleting preset: {error_message}")
        QMessageBox.critical(None, "Delete Error", error_message)
        return False

def run_script(script_content):
    """ Runs the given script content in a new terminal based on the OS. """
    if not script_content:
        print("Warning: Attempted to run empty script.")
        return

    os_platform = platform.system()
    import tempfile

    temp_script_path = None # Initialize to ensure it's always defined for finally

    def _prepare_subprocess_environment(platform_system, current_env):
        """Prepares a modified environment for the subprocess, especially the PATH."""
        env = current_env.copy()
        original_path = env.get("PATH", "")
        paths_to_prepend = []

        # Common user-specific bin directory
        local_bin = os.path.expanduser("~/.local/bin")
        if os.path.isdir(local_bin):
            paths_to_prepend.append(local_bin)

        if platform_system == "Linux":
            linuxbrew_paths = [
                os.path.expanduser("~/.linuxbrew/bin"),
                "/home/linuxbrew/.linuxbrew/bin",
            ]
            for p in linuxbrew_paths:
                if os.path.isdir(p):
                    paths_to_prepend.append(p)
        elif platform_system == "Darwin": # macOS
            mac_brew_paths = [
                "/opt/homebrew/bin",    # Apple Silicon & default for new Intel
                "/usr/local/bin",       # Older Homebrew, also general custom installs
            ]
            for p in mac_brew_paths:
                if os.path.isdir(p): # /usr/local/bin should exist, but check anyway
                    paths_to_prepend.append(p)
        
        # Add other common paths for package managers if needed here
        # e.g., for sdkman, nvm (though nvm is often handled by .bashrc/.profile sourcing)

        # Filter out duplicates and paths already in original_path
        unique_new_paths = []
        existing_path_parts = set(original_path.split(os.pathsep))
        for p in paths_to_prepend:
            if p not in existing_path_parts and p not in unique_new_paths:
                unique_new_paths.append(p)

        if unique_new_paths:
            new_path_str = os.pathsep.join(unique_new_paths)
            env["PATH"] = new_path_str + os.pathsep + original_path
            print(f"Modified PATH for subprocess: {env['PATH']}")
        else:
            print(f"PATH for subprocess not significantly modified, using: {original_path}")
            
        return env

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix=".sh" if os_platform != "Windows" else ".bat", delete=False, encoding='utf-8') as f:
            temp_script_path = f.name
            if os_platform in ["Linux", "Darwin"] and not script_content.startswith("#!"):
                f.write("#!/bin/bash\n")
            f.write(script_content)
        print(f"Temporary script created at: {temp_script_path}")

        if os_platform in ["Linux", "Darwin"]:
            try:
                os.chmod(temp_script_path, 0o755)
            except OSError as e:
                print(f"Warning: Could not chmod temp script {temp_script_path}: {e}")

        sub_env = _prepare_subprocess_environment(os_platform, os.environ)
        cmd_list = []

        # Command to be executed by bash -l -c "..."
        # This sources user profiles and then runs the temp script.
        script_runner_command = (
            f'if [ -f "$HOME/.profile" ]; then . "$HOME/.profile"; fi; '
            f'if [ -f "$HOME/.bashrc" ]; then . "$HOME/.bashrc"; fi; '
            f'cd "$HOME"; "{temp_script_path}"; exec bash'
        )

        if os_platform == "Linux":
            terminals = {
                "gnome-terminal": ["gnome-terminal", "--", "bash", "-l", "-c"],
                "konsole": ["konsole", "-e"],
                "xfce4-terminal": ["xfce4-terminal", "--command="],
                "lxterminal": ["lxterminal", "-e"],
                "xterm": ["xterm", "-e"],
            }
            found_term_executable = None
            for term_exec, base_args_list in terminals.items():
                if shutil.which(term_exec):
                    found_term_executable = term_exec
                    cmd_list = list(base_args_list)
                    if term_exec == "gnome-terminal":
                        cmd_list.append(script_runner_command)
                    elif term_exec == "xfce4-terminal": # Needs single quotes for its --command
                        cmd_list.append(f'bash -l -c \'{script_runner_command.replace("'", "'\\''")}\'')
                    else: # konsole, lxterminal, xterm typically use -e "bash -l -c \"...\""
                        cmd_list.append(f'bash -l -c "{script_runner_command.replace("\"", "\\\"")}"')
                    break
            
            if not found_term_executable:
                QMessageBox.warning(None, "Terminal Error", "Could not find a supported Linux terminal.")
                return
            print(f"Using terminal: {found_term_executable} with args: {cmd_list}")

        elif os_platform == "Darwin": # macOS
            # AppleScript to run the command in a new Terminal window
            # The script_runner_command (which sources .profile/.bashrc) is used here too.
            escaped_runner_cmd = script_runner_command.replace('"', '\\"')
            osascript_cmd = f'''
            tell application "Terminal"
                activate
                do script "{escaped_runner_cmd}"
            end tell
            '''
            cmd_list = ['osascript', '-e', osascript_cmd]

        elif os_platform == "Windows":
            win_path = temp_script_path.replace('/', '\\')
            # Using PowerShell to start a new PowerShell window that runs the script and stays open
            cmd_list = ['powershell', '-Command', f"Start-Process powershell -ArgumentList '-NoExit -File \"{win_path}\"'"]
            # Alternative for cmd.exe:
            # cmd_list = ['cmd.exe', '/c', f'start cmd.exe /k "{win_path}"']
        else:
            QMessageBox.warning(None, "OS Error", f"Unsupported operating system: {os_platform}")
            return

        if cmd_list:
            print(f"Running command: {' '.join(cmd_list if isinstance(cmd_list, list) else [str(cmd_list)])}") # Ensure joinable
            print(f"Using PATH for Popen: {sub_env.get('PATH')}")
            subprocess.Popen(cmd_list, env=sub_env)
        else:
            # This case should ideally be caught by earlier checks (no terminal found, unsupported OS)
            print("Command list is empty, cannot run script.")


    except Exception as e:
        error_message = f"Could not prepare or run script:\n{e}"
        print(f"Error running script: {error_message}")
        QMessageBox.critical(None, "Script Error", error_message)
    finally:
        if temp_script_path and os.path.exists(temp_script_path):
            # Threaded cleanup to avoid blocking and handle potential file locks
            path_to_clean = temp_script_path 
            def cleanup_task(path):
                time.sleep(3) # Give the terminal/script a moment
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        print(f"Cleaned up temp file: {path}")
                except Exception as e_clean:
                    print(f"Warning: Could not remove temp script {path}: {e_clean}")
            
            threading.Thread(target=cleanup_task, args=(path_to_clean,), daemon=True).start()

