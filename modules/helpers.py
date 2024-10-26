from typing import Generator


def iter_alternately(a: list, b: list) -> Generator:
    a = a.copy()
    b = b.copy()
    
    while a or b:
        if a:
            yield a.pop(0)
        
        if b:
            yield b.pop(0)


def flush_system_keyboard_buffer_win() -> None:
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
            
    except ImportError:
        return

