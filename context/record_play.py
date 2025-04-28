import time
import json
from pynput import mouse, keyboard  # type: ignore
from pynput.mouse import Listener as MouseListener, Controller as MouseController, Button  # type: ignore
from pynput.keyboard import Listener as KeyboardListener, Controller as KeyboardController, Key  # type: ignore

# Global variables to store events and control the loop
events = []
recording = True

# Track left mouse press and shift press to detect combination for 2s
left_pressed = False
shift_pressed = False
combination_pressed_start = None

def on_mouse_move(x, y):
    events.append({'type': 'mouse_move', 'x': x, 'y': y, 'time': time.time()})

def on_mouse_click(x, y, button, pressed):
    global left_pressed, combination_pressed_start
    events.append({
        'type': 'mouse_click',
        'x': x,
        'y': y,
        'button': str(button),
        'pressed': pressed,
        'time': time.time()
    })
    
    if button == Button.left:
        left_pressed = pressed

    # When left button is released, reset the combination timer
    if not left_pressed:
        combination_pressed_start = None

def on_scroll(x, y, dx, dy):
    events.append({
        'type': 'mouse_scroll',
        'x': x,
        'y': y,
        'dx': dx,
        'dy': dy,
        'time': time.time()
    })

def on_key_press(key):
    global shift_pressed
    events.append({'type': 'key_press', 'key': str(key), 'time': time.time()})
    if key in (Key.shift, Key.shift_r):
        shift_pressed = True

def on_key_release(key):
    global shift_pressed
    events.append({'type': 'key_release', 'key': str(key), 'time': time.time()})
    if key in (Key.shift, Key.shift_r):
        shift_pressed = False

# Replay events
def replay_events(events, speed_factor=1.0):
    mouse_controller = MouseController()
    keyboard_controller = KeyboardController()
    if not events:
        return
    start_time = events[0]['time']
    # play void and release all keys
    events.append({'type': 'void', 'time': events[-1]['time'] + 1})
    events.append({'type': 'key_release', 'key': 'Key.shift', 'time': events[-1]['time'] + 1})
    for event in events:
        time.sleep((event['time'] - start_time) / speed_factor)
        start_time = event['time']
        
        if event['type'] == 'mouse_move':
            mouse_controller.position = (event['x'], event['y'])
        elif event['type'] == 'mouse_click':
            button = Button[event['button'].split('.')[1]]
            if event['pressed']:
                mouse_controller.press(button)
            else:
                mouse_controller.release(button)
        elif event['type'] == 'key_press':
            key = eval(event['key'])
            keyboard_controller.press(key)
        elif event['type'] == 'key_release':
            key = eval(event['key'])
            keyboard_controller.release(key)
        elif event['type'] == 'mouse_scroll':
            mouse_controller.scroll(event['dx'], event['dy'])
        # 'void' event does nothing
        elif event['type'] == 'void':
            pass

def main():
    global recording, events, left_pressed, shift_pressed, combination_pressed_start
    print("Recording... Press and hold the left mouse button and the Shift key simultaneously for 2 seconds to stop.")

    with MouseListener(
            on_move=on_mouse_move,
            on_click=on_mouse_click,
            on_scroll=on_scroll) as ml, \
         KeyboardListener(
            on_press=on_key_press,
            on_release=on_key_release) as kl:
        while recording:
            # Check for left click + shift combination held for 2 seconds
            if left_pressed and shift_pressed:
                if combination_pressed_start is None:
                    combination_pressed_start = time.time()
                elif time.time() - combination_pressed_start >= 2.0:
                    recording = False
                    break
            else:
                combination_pressed_start = None
            time.sleep(0.1)

    # Remove the first 5 recorded events (if they exist)
    if len(events) > 5:
        events = events[5:]
    else:
        events = []

    # If shift (or any key) is still pressed, force a key_release event for shift
    if shift_pressed:
        events.append({'type': 'key_release', 'key': 'Key.shift', 'time': time.time()})
    # Append a final "void" event as a marker for end of recording
    events.append({'type': 'void', 'time': time.time()})
    print("Recording stopped.")
    # Save events to file
    with open('events.json', 'w') as f:
        json.dump(events, f)
    print("Recording saved to events.json.")
    time.sleep(3)
    print("Replaying events...")
    replay_events(events, speed_factor=1.0)

if __name__ == '__main__':
    main()