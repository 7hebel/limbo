from modules import style

from dataclasses import dataclass
from typing import Generator


BREAK_LINE = "\n"


@dataclass
class _CharData:
    char: str
    color: style.AnsiFGColor | None
    styles: list[style.AnsiStyle] | None
    
    def build(self) -> str:
        return style.tcolor(self.char, self.color, styles=self.styles)


class ColoredStringObject:
    def __init__(self) -> None:
        self.content: list[_CharData] = []
        
    def feed_char(self, char: str, color: style.AnsiFGColor | None = None, styles: list[style.AnsiStyle] | None = None) -> None:
        data = _CharData(char, color, styles)
        self.content.append(data)
        
    def feed_string(self, string: str, color: style.AnsiFGColor | None = None, styles: list[style.AnsiStyle] | None = None) -> None:
        for char in string:
            self.feed_char(char, color, styles)
    
    def break_line(self) -> None:
        self.content.append(BREAK_LINE)
        
    def stream_chars(self) -> Generator[str, None, None]:
        for char_data in self.content:
            if char_data == BREAK_LINE:
                yield char_data
                continue
            
            yield char_data.build()
    
    def stream_positioned_chars(self, x: int, y: int) -> Generator[tuple[str, tuple[int, int]], None, None]:
        start_x = x
        
        for char in self.stream_chars():
            if char == BREAK_LINE:
                y += 1
                x = start_x
                continue
            
            yield (char, (x, y))
            x += 1
                
