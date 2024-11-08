from modules import style

from dataclasses import dataclass
from typing import Generator


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
        self.content.append("\n")
        
    def stream_chars(self) -> Generator[str, None, None]:
        for char_data in self.content:
            if char_data == "\n":
                yield char_data
                continue
            
            yield char_data.build()
    
    def stream_positioned_chars(self, x: int, y: int) -> Generator[tuple[tuple[int, int], str], None, None]:
        start_x = x

        for char in self.stream_chars():
            if char == "\n":
                y += 1
                x = start_x
                continue
            
            yield ((x, y), char)
            x += 1
            