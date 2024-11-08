from modules import ui

import threading
import keyboard
import time
import sys
import os

try:
    import pygetwindow
    CONSOLE_WINDOW = pygetwindow.getActiveWindow()
    
except NotImplementedError:
    CONSOLE_WINDOW = None

MIN_W, MIN_H = 124, 33


def clear_screen():
    os.system("cls || clear")


def set_cursor_pos(x: int, y: int) -> None:
    print(f"\033[{y};{x}H", end="")


def write_at(content: str, x: int, y: int) -> None:
    set_cursor_pos(x, y)
    print(content)


def get_cursor_pos() -> tuple[int, int]:
    if os.name == 'nt':  # Windows.
        import ctypes

        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", ctypes.c_ushort),
                ("srWindow", ctypes.c_short * 4),
                ("dwMaximumWindowSize", COORD)
            ]

        # Get the console handle
        STD_OUTPUT_HANDLE = -11
        console_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        success = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
            console_handle, ctypes.byref(csbi)
        )

        if success:
            return csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y
        else:
            raise RuntimeError("Unable to get cursor position.")
        
    else:  # Linux / MacOS
        import re, termios, tty

        buff = ''
        stdin = sys.stdin.fileno()
        tattr = termios.tcgetattr(stdin)

        try:
            tty.setcbreak(stdin, termios.TCSANOW)
            sys.stdout.write('\033[6n')
            sys.stdout.flush()

            while True:
                buff += sys.stdin.read(1)
                if buff[-1] == 'R': break
        finally:
            termios.tcsetattr(stdin, termios.TCSANOW, tattr)

        matches = re.match(r'^\033\[(\d*);(\d*)R', buff)
        if matches == None: return None

        groups = matches.groups()
        return (int(groups[0]), int(groups[1]))


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
            hide_cursor()
            return
        
        time.sleep(0.1)


def is_active_window() -> bool:
    if CONSOLE_WINDOW is None:
        return True
    return pygetwindow.getActiveWindow() == CONSOLE_WINDOW


def on_too_small_display() -> None:
    clear_screen()
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
