from modules import style
from modules import ui

import pygetwindow
import threading
import keyboard
import time
import os


CONSOLE_WINDOW = pygetwindow.getActiveWindow()
MIN_W, MIN_H = 124, 33


def set_cursor_pos(x: int, y: int) -> None:
    print(f"\033[{y};{x}H", end="")


def hide_cursor():
    print("\033[?25l", end="")

    
def show_cursor():
    print("\033[?25h", end="")


def get_w() -> int:
    return os.get_terminal_size()[0]


def get_h() -> int:
    return os.get_terminal_size()[1]


def wait_for_enter() -> None:
    """ Block execution process until enter is pressed. """
    while keyboard.is_pressed("enter"):
        time.sleep(0.1)
    
    while True:
        if keyboard.is_pressed("enter") and is_active_window():
            return
        
        time.sleep(0.1)


def is_active_window() -> bool:
    return pygetwindow.getActiveWindow() == CONSOLE_WINDOW


def on_too_small_display() -> None:
    style.clear_screen()
    message1 = "The console is too small to correctly display all UI components."
    message2 = "Please resize the terminal in order to use program."
    print("\n" * ((get_h() // 2) - 6))
    print(message1.center(get_w()))
    print(message2.center(get_w()))
    
    width_info = f"Width: {get_w()} / {MIN_W}"
    height_info = f"Height: {get_h()} / {MIN_H}"
    print("\n" * 3)
    print(width_info.center(get_w()))
    print(height_info.center(get_w()))
    

def term_size_listener(test_run: bool = False) -> None:
    prev_w, prev_h = 0, 0
    
    while 1:
        w, h = os.get_terminal_size()
        if w != prev_w or h != prev_h:
            prev_w = w
            prev_h = h
            
            if w < MIN_W or h < MIN_H:
                on_too_small_display()
                continue

            if test_run:
                return
            
            ui.render_all()
        time.sleep(0.1)
        
        
if get_w() < MIN_W or get_h() < MIN_H:
    term_size_listener(test_run=True)
        
_listener = threading.Thread(target=term_size_listener, daemon=True)
_listener.start()
        
