import os
import sys
import platform
import subprocess
import shutil
import json # Import json for handling embedded data
from PyQt6.QtWidgets import QMessageBox # type: ignore

# Determine the base path for resources, accommodating PyInstaller
try:
    # If running as a PyInstaller bundle
    BASE_PATH = sys._MEIPASS
except AttributeError:
    # If running as a normal script
    BASE_PATH = os.path.abspath(os.path.dirname(__file__))

# Define folders relative to the script's location (qt_app)
PRESETS_FOLDER = os.path.join(BASE_PATH, "presets")
ASSETS_FOLDER = os.path.join(BASE_PATH, "assets")
ICONS_FOLDER = os.path.join(ASSETS_FOLDER, "app_icons")

# Ensure necessary folders exist at startup
os.makedirs(PRESETS_FOLDER, exist_ok=True)
os.makedirs(ICONS_FOLDER, exist_ok=True)
# RECORDS_FOLDER is no longer strictly needed by utils for saving/loading presets
# os.makedirs(RECORDS_FOLDER, exist_ok=True) # Keep if recording_module still uses it independently

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # This function might be less necessary now BASE_PATH is correctly defined
    # but can be kept for consistency if used elsewhere.
    return os.path.join(BASE_PATH, relative_path)

def get_icon_path(icon_name):
    """ Get the full path to an icon file within the qt_app/assets/app_icons folder. """
    if not icon_name or icon_name == 'none':
        return None
    return os.path.join(ICONS_FOLDER, icon_name)

def load_presets():
    """ Loads all presets from the presets folder. """
    presets = []
    if not os.path.exists(PRESETS_FOLDER):
        print(f"Warning: Presets folder not found at {PRESETS_FOLDER}")
        return presets

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
    """ Saves a single preset data dictionary to a .slaunch file.
        Embeds JSON for 'recorded' type.
        Returns a tuple: (success: bool, message_or_data: str or dict)
    """
    file_name = preset_data.get('file_name')
    is_new = not file_name
    if is_new:
        # Generate a new file name if one doesn't exist
        existing = [f for f in os.listdir(PRESETS_FOLDER) if f.endswith(".slaunch")]
        next_index = 1
        while f"preset{next_index}.slaunch" in existing:
            next_index += 1
        file_name = f"preset{next_index}.slaunch"
        preset_data['file_name'] = file_name # Update the dict with the new name

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

        print(f"Preset saved: {preset_path}")
        return True, preset_data # Return success and the (potentially updated) data
    except Exception as e:
        error_message = f"Could not save preset {file_name}:\n{e}"
        print(f"Error saving preset: {error_message}")
        QMessageBox.critical(None, "Save Error", error_message)
        return False, error_message # Return failure and the error message


def delete_preset(file_name):
    """ Deletes a preset file. """
    preset_path = os.path.join(PRESETS_FOLDER, file_name)
    try:
        if os.path.exists(preset_path):
            os.remove(preset_path)
            print(f"Preset deleted: {preset_path}")
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
    # Use a more unique temp file name, potentially in system temp dir?
    # For simplicity, keep it in PRESETS_FOLDER for now.
    temp_script_path = os.path.join(PRESETS_FOLDER, f"temp_script_{os.getpid()}.sh")

    try:
        # Write script to a temporary file with UTF-8 encoding
        with open(temp_script_path, 'w', encoding='utf-8') as f:
            # Add shebang for Linux/macOS if not present
            if os_platform in ["Linux", "Darwin"] and not script_content.startswith("#!"):
                 f.write("#!/bin/bash\n")
            f.write(script_content)

        # Make executable on Linux/macOS
        if os_platform in ["Linux", "Darwin"]:
            try:
                os.chmod(temp_script_path, 0o755) # rwxr-xr-x
            except OSError as e:
                print(f"Warning: Could not chmod temp script {temp_script_path}: {e}")
                # Proceed anyway, the terminal might still execute it

        # --- Execute in a new terminal --- 
        cmd_list = []
        shell_cmd = f"cd && \"{temp_script_path}\"; exec bash" # Command to run inside the terminal

        if os_platform == "Linux":
            terminals = {
                "gnome-terminal": ["gnome-terminal", "--", "bash", "-c"],
                "konsole": ["konsole", "-e", "bash", "-c"],
                "xfce4-terminal": ["xfce4-terminal", "--command="],
                "lxterminal": ["lxterminal", "-e"],
                "xterm": ["xterm", "-e"]
            }
            found_terminal = False
            for term, args in terminals.items():
                if shutil.which(term): # Use shutil.which to find executable
                    cmd_list = args
                    if term in ["xfce4-terminal", "lxterminal", "xterm"]:
                         cmd_list.append(f'bash -c " ; {shell_cmd}"') # Needs careful quoting
                    else:
                         cmd_list.append(shell_cmd)
                    found_terminal = True
                    break
            if not found_terminal:
                 QMessageBox.warning(None, "Terminal Error", "Could not find a supported terminal (gnome-terminal, konsole, xfce4-terminal, lxterminal, xterm). Please install one.")
                 return # Don't proceed if no terminal found

        elif os_platform == "Darwin": # macOS
            # Using osascript to run the script file directly in a new Terminal window
            osascript_cmd = f'''
            tell application "Terminal"
                activate
                do script "\"{temp_script_path}\"; exit"
            end tell
            '''
            cmd_list = ['osascript', '-e', osascript_cmd]

        elif os_platform == "Windows":
            # Use start command to open a new PowerShell window and execute the script
            # PowerShell needs the full path, properly quoted.
            # -NoExit keeps the window open after script finishes.
            cmd_list = ['powershell', '-NoExit', '-Command', f"Start-Process powershell -ArgumentList \"-NoExit -File '{temp_script_path}'\" -Verb RunAs"]
            # Simpler alternative (might have execution policy issues):
            # cmd_list = ['powershell', '-NoExit', '-File', temp_script_path]
            # Or using cmd:
            # cmd_list = ['cmd', '/c', 'start', 'cmd', '/k', temp_script_path]

        else:
            QMessageBox.warning(None, "OS Error", f"Unsupported operating system: {os_platform}")
            return

        # --- Run the command --- 
        if cmd_list:
            print(f"Running command: {' '.join(cmd_list)}")
            try:
                subprocess.Popen(cmd_list)
            except FileNotFoundError:
                 QMessageBox.critical(None, "Execution Error", f"Could not execute terminal command: {' '.join(cmd_list)}\nEnsure the terminal application is installed and in your PATH.")
            except Exception as e:
                 QMessageBox.critical(None, "Execution Error", f"Error launching terminal: {e}")

    except Exception as e:
        error_message = f"Could not prepare or run script:\n{e}"
        print(f"Error running script: {error_message}")
        QMessageBox.critical(None, "Script Error", error_message)
    finally:
        # Clean up the temporary script file after a short delay
        # Use threading to avoid blocking and handle potential errors
        import threading
        import time
        def cleanup_temp_file(path):
            time.sleep(2) # Wait a bit for the terminal to potentially read the file
            try:
                if os.path.exists(path):
                    os.remove(path)
                    print(f"Cleaned up temp file: {path}")
            except Exception as e:
                print(f"Warning: Could not remove temporary script file {path}: {e}")

        if os.path.exists(temp_script_path):
            cleanup_thread = threading.Thread(target=cleanup_temp_file, args=(temp_script_path,), daemon=True)
            cleanup_thread.start()



