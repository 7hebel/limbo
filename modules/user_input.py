from modules import terminal

import keyboard
import time


def clear_char():
    print("\033[1D", end="")
    print(" ", end="")
    print("\033[1D", end="", flush=True)


def show_char(char: str):
    print(char, end="", flush=True)


def get_input(prompt: str = "", max_len: int = 0, allow_cancel: bool = False, placeholder: str = "") -> str:
    buffer = str(placeholder)
    finished = False
    
    terminal.show_cursor()
    print(prompt, end="", flush=True)
    print(buffer, end="", flush=True)
    
    def handle_key(key: keyboard.KeyboardEvent):
        nonlocal buffer, finished
        
        if not terminal.is_active_window():
            return
        
        if key.name == "backspace" and buffer:
            buffer = buffer[:-1]
            clear_char()
            
        elif key.name == "enter":
            finished = True
            
        elif key.name == "esc":
            if allow_cancel:
                finished = True
                buffer = None
                return
            
        elif key.name == "space":
            if max_len > 0 and len(buffer) < max_len or max_len == 0:
                buffer += " "
                show_char(" ")
    
        else:
            if keyboard.is_modifier(key.scan_code) or len(key.name) != 1:
                return
            
            if max_len > 0 and len(buffer) < max_len or max_len == 0:
                buffer += key.name
                show_char(key.name)

    listener = keyboard.on_press(handle_key, False)

    try:
        while not finished:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        keyboard.unhook(listener)
        terminal.hide_cursor()
        print("")
        raise
        
    keyboard.unhook(listener)
    terminal.hide_cursor()
    print("")
    
    return buffer
