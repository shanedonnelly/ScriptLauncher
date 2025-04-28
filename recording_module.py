import time
import json
import os
import threading
from pynput import mouse, keyboard
from pynput.mouse import Listener as MouseListener, Controller as MouseController, Button
from pynput.keyboard import Listener as KeyboardListener, Controller as KeyboardController, Key

# Define the folder to save recordings
RECORDS_FOLDER = os.path.join(os.path.dirname(__file__), "records")
os.makedirs(RECORDS_FOLDER, exist_ok=True)

class Recorder:
    """Handles recording of mouse and keyboard events."""
    def __init__(self):
        self.events = []
        self._recording = False
        self._stop_event = threading.Event()
        self._mouse_listener = None
        self._keyboard_listener = None
        self._thread = None
        # Track key/button states to prevent abrupt stops leaving them 'pressed'
        self._pressed_keys = set()
        self._left_mouse_pressed = False
        self._shift_pressed = False
        self._combination_start_time = None

    def _on_mouse_move(self, x, y):
        if self._recording:
            self.events.append({'type': 'mouse_move', 'x': x, 'y': y, 'time': time.time()})

    def _on_mouse_click(self, x, y, button, pressed):
        if self._recording:
            self.events.append({
                'type': 'mouse_click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'time': time.time()
            })
            if button == Button.left:
                self._left_mouse_pressed = pressed
                if not pressed: # Reset combo timer on release
                    self._combination_start_time = None


    def _on_scroll(self, x, y, dx, dy):
        if self._recording:
            self.events.append({
                'type': 'mouse_scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'time': time.time()
            })

    def _on_key_press(self, key):
        if self._recording:
            key_str = str(key)
            self.events.append({'type': 'key_press', 'key': key_str, 'time': time.time()})
            self._pressed_keys.add(key_str)
            if key in (Key.shift, Key.shift_r):
                self._shift_pressed = True


    def _on_key_release(self, key):
        if self._recording:
            key_str = str(key)
            self.events.append({'type': 'key_release', 'key': key_str, 'time': time.time()})
            self._pressed_keys.discard(key_str)
            if key in (Key.shift, Key.shift_r):
                self._shift_pressed = False
                self._combination_start_time = None # Reset combo timer on release


    def _recording_thread(self):
        """Thread function to run listeners."""
        self.events = [] # Clear previous events
        self._pressed_keys = set()
        self._left_mouse_pressed = False
        self._shift_pressed = False
        self._combination_start_time = None
        self._recording = True
        self._stop_event.clear()

        # Use context managers for listeners
        with MouseListener(on_move=self._on_mouse_move, on_click=self._on_mouse_click, on_scroll=self._on_scroll) as self._mouse_listener, \
             KeyboardListener(on_press=self._on_key_press, on_release=self._on_key_release) as self._keyboard_listener:
            print("Recording started. Hold Left Click + Shift for 2s to stop.")
            while not self._stop_event.is_set():
                 # Check for stop combination (Left Click + Shift for 2 seconds)
                 if self._left_mouse_pressed and self._shift_pressed:
                     if self._combination_start_time is None:
                         self._combination_start_time = time.time()
                     elif time.time() - self._combination_start_time >= 2.0:
                         print("Stop combination detected.")
                         self.stop_recording() # Trigger stop
                         break
                 else:
                     self._combination_start_time = None # Reset if combo broken
                 time.sleep(0.05) # Small sleep to prevent busy-waiting

        print("Recording thread finished.")


    def start_recording(self):
        """Starts the recording process in a separate thread."""
        if self._thread and self._thread.is_alive():
            print("Recording already in progress.")
            return
        self._thread = threading.Thread(target=self._recording_thread, daemon=True)
        self._thread.start()

    def stop_recording(self):
        """Stops the recording and returns the recorded events."""
        if not self._recording:
            print("Not recording.")
            return []

        print("Stopping recording...")
        self._recording = False
        self._stop_event.set() # Signal the thread to stop

        # Stop listeners safely
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()

        # Wait for the thread to finish
        if self._thread:
            self._thread.join(timeout=2) # Wait max 2 seconds
            if self._thread.is_alive():
                print("Warning: Recording thread did not terminate cleanly.")
            self._thread = None


        # Clean up events: remove initial/final noise, add final releases
        processed_events = self._finalize_events(self.events)
        print(f"Recording stopped. {len(processed_events)} events captured.")
        return processed_events

    def _finalize_events(self, recorded_events):
        """Cleans up the recorded events."""
        if not recorded_events:
            return []

        # Trim first few events (often noise from starting) - configurable?
        trimmed_events = recorded_events[5:] if len(recorded_events) > 5 else recorded_events

        if not trimmed_events:
             return []

        final_time = time.time()

        # Ensure all pressed keys/buttons are released at the end
        mouse_controller = MouseController()
        if self._left_mouse_pressed: # Check if left mouse was held at stop time
             # Check if the last event for left mouse was a press
             last_left_click = None
             for e in reversed(trimmed_events):
                 if e['type'] == 'mouse_click' and e['button'] == str(Button.left):
                     last_left_click = e
                     break
             if last_left_click and last_left_click['pressed']:
                 print("Adding final left mouse release.")
                 trimmed_events.append({
                     'type': 'mouse_click', 'x': last_left_click['x'], 'y': last_left_click['y'],
                     'button': str(Button.left), 'pressed': False, 'time': final_time
                 })


        # Ensure all pressed keys are released
        keys_to_release = self._pressed_keys.copy() # Work on a copy
        if self._shift_pressed: # Specifically add shift if it was held
             keys_to_release.add(str(Key.shift)) # Use canonical shift key

        # Check last events for each key that needs release
        released_in_events = set()
        for key_str in keys_to_release:
             for e in reversed(trimmed_events):
                 if e['type'] == 'key_release' and e['key'] == key_str:
                     released_in_events.add(key_str)
                     break
                 if e['type'] == 'key_press' and e['key'] == key_str:
                     # Found the press, but no release after it
                     break

        for key_str in keys_to_release:
             if key_str not in released_in_events:
                 print(f"Adding final release for key: {key_str}")
                 trimmed_events.append({'type': 'key_release', 'key': key_str, 'time': final_time})


        # Add a small delay and a 'void' event at the end
        trimmed_events.append({'type': 'void', 'time': final_time + 0.1})

        return trimmed_events

    def is_recording(self):
        return self._recording

def save_record(events, base_path=RECORDS_FOLDER):
    """Saves the recorded events to a JSON file."""
    if not events:
        print("No events to save.")
        return None
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_name = f"record_{timestamp}.json"
    file_path = os.path.join(base_path, file_name)
    try:
        with open(file_path, 'w') as f:
            json.dump(events, f, indent=2) # Use indent for readability
        print(f"Recording saved to {file_path}")
        return file_path
    except IOError as e:
        print(f"Error saving recording to {file_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during saving: {e}")
        return None


def load_record(file_path):
    """Loads recorded events from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            events = json.load(f)
        print(f"Recording loaded from {file_path}")
        return events
    except FileNotFoundError:
        print(f"Error: Recording file not found at {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during loading: {e}")
        return None

# Modified replay_events to accept a stop_event
def replay_events(record_path, how_many_times=1, speed_factor=1.0, stop_event=None):
    """Replays recorded events from a file multiple times, allowing external stopping."""
    events = load_record(record_path)
    if not events:
        print(f"Could not load events from {record_path}")
        return

    # --- Moved the finally block inside the try for KeyboardInterrupt ---
    # --- This ensures cleanup happens even with Ctrl+C ---
    try:
        if how_many_times == -1:
            print("Replaying indefinitely (Stop signal can interrupt)...")
            while True:
                if stop_event and stop_event.is_set():
                    print("Stop signal received during infinite replay.")
                    break
                _play_sequence(events, speed_factor, stop_event)
                if stop_event and stop_event.is_set(): # Check again after sequence
                    break
                # Add a small delay between infinite loops if desired and not stopping
                if not (stop_event and stop_event.is_set()):
                    interrupted = stop_event.wait(0.1) if stop_event else time.sleep(0.1)
                    if interrupted: break
        else:
            print(f"Replaying {how_many_times} times...")
            for i in range(how_many_times):
                if stop_event and stop_event.is_set():
                    print(f"Stop signal received before repetition {i+1}.")
                    break
                print(f"  Repetition {i+1}/{how_many_times}")
                _play_sequence(events, speed_factor, stop_event)
                if stop_event and stop_event.is_set(): # Check after sequence finishes
                     print(f"Stop signal received during repetition {i+1}.")
                     break
                # Pause between repetitions only if not the last one and not stopping
                if i < how_many_times - 1 and not (stop_event and stop_event.is_set()):
                    interrupted = stop_event.wait(0.5) if stop_event else time.sleep(0.5)
                    if interrupted: break

        print("Replay loop finished or stopped.") # Changed message slightly

    except KeyboardInterrupt: # Keep Ctrl+C as a backup stop
        print("\nReplay stopped by user (KeyboardInterrupt).")
        if stop_event:
            stop_event.set() # Ensure stop event is set if Ctrl+C is used

    finally:
        # The _play_sequence function handles releasing keys pressed *during* its execution.
        # Avoid the potentially blocking global release here.
        print("replay_events finally block reached.") # DEBUG
        # _release_all_keys_buttons() # <-- Keep commented out for now
        pass


# Modified _play_sequence to accept and check stop_event more reliably
def _play_sequence(events, speed_factor=1.0, stop_event=None):
    """Plays a single sequence of events, checking for stop signal."""
    mouse_controller = MouseController()
    keyboard_controller = KeyboardController()
    if not events:
        return

    # Store original start time for relative calculations
    recording_start_time = events[0]['time']
    replay_start_time = time.time() # Wall clock time when replay sequence begins

    replay_pressed_keys = set()
    replay_pressed_buttons = set()

    # --- Moved the finally block inside the try ---
    try:
        for event in events:
            # --- Check stop event at the beginning of each event processing ---
            if stop_event and stop_event.is_set():
                print("Stop signal detected during sequence playback (start of loop).")
                break # Exit the loop immediately

            # Calculate the target execution time for this event relative to replay start
            time_since_recording_start = event['time'] - recording_start_time
            scaled_delay = time_since_recording_start / speed_factor
            target_execution_time = replay_start_time + scaled_delay

            # Wait until the target time, checking stop_event
            current_time = time.time()
            wait_time = target_execution_time - current_time

            if wait_time > 0:
                interrupted = False
                if stop_event:
                    # Wait for the calculated duration OR until stop_event is set
                    interrupted = stop_event.wait(timeout=wait_time)
                else:
                    time.sleep(wait_time) # Fallback if no stop_event provided

                if interrupted:
                    print("Stop signal detected during delay.")
                    break # Exit loop if stopped during wait

            # --- Check stop event again right before executing the action ---
            if stop_event and stop_event.is_set():
                 print("Stop signal detected before event execution.")
                 break

            # --- Execute Event ---
            try:
                if event['type'] == 'mouse_move':
                    mouse_controller.position = (event['x'], event['y'])
                elif event['type'] == 'mouse_click':
                    try:
                        button_str = event['button'].split('.')[-1]
                        button = getattr(Button, button_str)
                    except (AttributeError, IndexError):
                        print(f"Warning: Unknown button type '{event['button']}' in recording. Skipping.")
                        continue

                    if event['pressed']:
                        mouse_controller.press(button)
                        replay_pressed_buttons.add(button)
                    else:
                        # Check if button is actually pressed before releasing
                        if button in replay_pressed_buttons:
                            mouse_controller.release(button)
                            replay_pressed_buttons.discard(button)
                        else:
                            # This can happen if the recording started with a button already down
                            # or if the stop happened between press/release. Just log it.
                            print(f"Warning: Attempted to release button {button} which wasn't tracked as pressed.")

                elif event['type'] == 'key_press':
                     key = _parse_key(event['key'])
                     if key:
                         keyboard_controller.press(key)
                         replay_pressed_keys.add(event['key']) # Store the string representation
                elif event['type'] == 'key_release':
                     key = _parse_key(event['key'])
                     if key:
                         # Check if key is actually pressed before releasing
                         if event['key'] in replay_pressed_keys:
                             keyboard_controller.release(key)
                             replay_pressed_keys.discard(event['key'])
                         else:
                             print(f"Warning: Attempted to release key {event['key']} which wasn't tracked as pressed.")

                elif event['type'] == 'mouse_scroll':
                    mouse_controller.scroll(event['dx'], event['dy'])
                elif event['type'] == 'void':
                    pass # Do nothing for void events
            except Exception as e:
                # Log error but continue replay if possible? Or break? For now, log and continue.
                print(f"Error replaying event: {event}. Error: {e}")
                # Consider adding 'break' here if errors should stop the sequence

    finally:
        # Ensure keys/buttons pressed *during this sequence* are released at the end,
        # even if stopped prematurely by the stop_event or an error.
        print("_play_sequence finally block: Releasing potentially stuck keys/buttons...")
        _release_keys_buttons(keyboard_controller, mouse_controller, replay_pressed_keys, replay_pressed_buttons)


def _parse_key(key_str):
    """Parses a key string representation back into a Key object or character."""
    try:
        # Handle special keys like 'Key.shift', 'Key.ctrl_l', etc.
        if key_str.startswith("Key."):
            key_name = key_str.split('.')[-1]
            # Handle potential aliases like 'alt_gr' -> 'alt_r' if necessary
            # key_name = {'alt_gr': 'alt_r'}.get(key_name, key_name)
            return getattr(Key, key_name)
        # Handle character keys like "'a'", "'1'", "'@'"
        elif len(key_str) == 3 and key_str.startswith("'") and key_str.endswith("'"):
            return key_str[1]
        # Handle "<num>" keys (often numpad) - pynput usually handles these via Key.num_X or chars
        elif key_str.startswith("<") and key_str.endswith(">"):
             # Check if it's a known numeric representation like '<65437>' (Num 5)
             # This mapping might be OS/environment specific.
             # For now, just warn and return None as direct replay is unreliable.
             print(f"Warning: Replaying numeric/special key '{key_str}' might be unreliable. Skipping.")
             return None
        # Assume it's a single character if not quoted (less common from pynput)
        elif len(key_str) == 1:
             return key_str
        else:
             print(f"Warning: Unrecognized key format '{key_str}'. Skipping.")
             return None
    except AttributeError:
        print(f"Warning: Unknown special key name derived from '{key_str}'. Skipping.")
        return None
    except Exception as e:
        print(f"Error parsing key '{key_str}': {e}")
        return None

def _release_keys_buttons(keyboard_controller, mouse_controller, pressed_keys_str, pressed_buttons):
    """Releases specific keys and buttons that were tracked as pressed."""
    # Release keys first
    released_keys_count = 0
    for key_str in list(pressed_keys_str): # Iterate over a copy
        key = _parse_key(key_str)
        if key:
            try:
                keyboard_controller.release(key)
                # print(f"  Released key: {key_str}") # Optional: Verbose logging
                released_keys_count += 1
            except Exception as e:
                # This might happen if the key wasn't actually held by the OS state
                print(f"  Warning: Error releasing key {key_str}: {e}")
        pressed_keys_str.discard(key_str) # Ensure it's removed even if parse/release fails

    # Release mouse buttons
    released_buttons_count = 0
    for button in list(pressed_buttons): # Iterate over a copy
        try:
            mouse_controller.release(button)
            # print(f"  Released button: {button}") # Optional: Verbose logging
            released_buttons_count += 1
        except Exception as e:
            # This might happen if the button wasn't actually held by the OS state
            print(f"  Warning: Error releasing button {button}: {e}")
        pressed_buttons.discard(button) # Ensure it's removed

    if released_keys_count > 0 or released_buttons_count > 0:
        print(f"  Released {released_keys_count} keys and {released_buttons_count} buttons.")
    else:
        print("  No tracked keys or buttons needed explicit release.")


def _release_all_keys_buttons():
     """Attempts to release common modifier keys and mouse buttons globally. (DISABLED - POTENTIALLY BLOCKING)"""
     # This is a best-effort approach after replay stops unexpectedly.
     # It seems to cause hangs when called from the replay thread.
     print("Attempting to release common keys and buttons globally... (Currently Disabled)")
     return # Skip execution
     # kb_controller = KeyboardController()
     # ms_controller = MouseController()
     # common_keys = [
     #     Key.shift, Key.shift_r, Key.ctrl, Key.ctrl_l, Key.ctrl_r,
     #     Key.alt, Key.alt_l, Key.alt_r, Key.cmd, Key.cmd_l, Key.cmd_r # cmd for macOS
     # ]
     # common_buttons = [Button.left, Button.right, Button.middle]

     # for key in common_keys:
     #     try: kb_controller.release(key)
     #     except Exception: pass # Ignore errors here
     # for btn in common_buttons:
     #     try: ms_controller.release(btn)
     #     except Exception: pass # Ignore errors here
     # print("Global release attempt finished.")


# Example usage (optional, can be removed or kept for testing)
if __name__ == '__main__':
    # Example: Record and then replay
    recorder = Recorder()
    print("Starting recording for 10 seconds (or stop with LeftClick+Shift)...")
    recorder.start_recording()

    # Wait for recording to finish (either by timer or manual stop)
    start_wait = time.time()
    while recorder.is_recording() and time.time() - start_wait < 10:
        time.sleep(0.5)

    if recorder.is_recording():
        print("10 seconds elapsed, stopping recording.")
        events_data = recorder.stop_recording()
    else:
        print("Recording stopped manually.")
        events_data = recorder.events # Get events collected so far (might need finalize)
        # It's better to rely on the return value of stop_recording()
        # For simplicity here, we assume stop_recording was called by the combo thread
        # A more robust way would involve signaling between threads.


    if events_data:
        saved_file = save_record(events_data)
        if saved_file:
            print("\nStarting replay in 3 seconds...")
            time.sleep(3)
            replay_events(saved_file, how_many_times=1)
    else:
        print("No events were recorded.")
