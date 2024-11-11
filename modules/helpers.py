from modules.measure import VerticalDirection

from typing import Generator, Any


class MemoryJar:
    current: "MemoryJar | None" = None

    @staticmethod
    def get_current() -> "MemoryJar":
        if MemoryJar.current is None:
            MemoryJar.current = MemoryJar()
        return MemoryJar.current

    @staticmethod
    def new_jar() -> None:
        MemoryJar.current = MemoryJar()

    def __init__(self) -> None:
        self.data: dict[str, Any] = {}

    def set_value(self, key: str, value: str) -> None:
        self.data[key] = value

    def get_value(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


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
            
    except:
        return


def wrapping_index_shift(array: list, current_index: int, direction: VerticalDirection) -> int:
    next_index = current_index + direction
    
    if next_index > len(array) - 1:
        next_index = 0
    elif next_index == -1:
        next_index = len(array) - 1
        
    return next_index
    