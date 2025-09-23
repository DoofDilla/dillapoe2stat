# pip install pynput
from pydualsense import *
from pynput.keyboard import Controller, Key
import os

os.environ["SDL_JOYSTICK_ENHANCED_REPORTS"] = "0"
os.environ["SDL_JOYSTICK_HIDAPI_PS5_RUMBLE"] = "0"
os.environ["SDL_JOYSTICK_HIDAPI_PS5_PLAYER_LED"] = "0"

kb = Controller()
dualsense = pydualsense()
dualsense.init()

r2_down = False
r3_down = False
combo_active = False

def maybe_fire_combo():
    global combo_active
    if r2_down and r3_down and not combo_active:
        combo_active = True
        print("R2+R3 → F2")
        kb.press(Key.f2); kb.release(Key.f2)
    if not (r2_down and r3_down):
        combo_active = False

def on_r2_changed(is_down: bool):
    global r2_down; r2_down = bool(is_down); maybe_fire_combo()

def on_r3_changed(is_down: bool):
    global r3_down; r3_down = bool(is_down); maybe_fire_combo()

dualsense.r2_changed += on_r2_changed
dualsense.r3_changed += on_r3_changed

try:
    while True: ...
finally:
    dualsense.close()
