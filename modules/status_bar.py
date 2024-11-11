from modules.side_bar import side_bar
from modules import terminal
from modules import measure
from modules import chars
from modules import style
from modules import ui

import re


def split_styled_message(message: str, max_len: int) -> list[str]:
    """ Fit ANSI-styled string into lines of given size, wrapping words. """
    lines = []
    current_line = ""
    current_length = 0

    words = re.split(r'(\s+)', message)

    for word in words:
        word_length = style.real_length(word)

        if current_length + word_length > max_len:
            if current_line:
                lines.append(current_line)
            current_line = word
            current_length = word_length
        else:
            current_line += word
            current_length += word_length

    if current_line:
        lines.append(current_line)

    return lines


class StatusBarComponent(ui.TextUIComponent):
    def __init__(self) -> None:
        self.BASE_HEIGHT = 2
        self.msg_height = 0
        self.message: str = ""
        
        super().__init__()

    def get_rect(self, force: bool = False) -> measure.Rect | None:
        if self.msg_height == 0 and not force:
            return None
        
        x, y = 0, terminal.get_h() - self.BASE_HEIGHT - self.msg_height
        w, h = terminal.get_w(), self.BASE_HEIGHT + self.msg_height
        
        if not side_bar.is_folded:
            x += side_bar.width
            w -= side_bar.width - 1
        
        return measure.Rect(measure.Position(x, y), w, h)

    def get_border_connections(self) -> style.BorderConnection:
        return style.BorderConnection(n = True)

    def set_message(self, message: str) -> None:
        self.message = message
        
        rect = self.get_rect(force=True)
        max_len = rect.w - 4
        msg_lines = split_styled_message(self.message, max_len)
        
        self.msg_height = len(msg_lines)
        ui.render_all()

    def keys_help(self, mode: str, keys_info: dict[str, str]) -> None:
        content = style.tcolor(mode, styles=[style.AnsiStyle.INVERT, style.AnsiStyle.BOLD]) + "  " if mode else ""
        for key, info in keys_info.items():
            content += style.key(key) + f" {info}   "
            
        self.set_message(content.strip())

    def standard_keys_help(self) -> None:
        STD_KEYS = {
            chars.ALL_ARROWS: "shift focus",
            f"ctrl+{chars.ALL_ARROWS[0]}": "move camera",
            f"alt+{chars.ALL_ARROWS[0]}": "move node",
            "enter": "edit node",
            "tab": "nodes",
            "ctrl+e": "export",
            "ctrl+i": "import",
            "ctrl+w": "close",
            "F1": "run",
            "F2": "compile",
            "F12": "debug",
        }
        
        self.keys_help("", STD_KEYS)

    def error(self, message: str) -> None:
        content = style.tcolor(" E ", color=style.AnsiFGColor.BLACK, bg_color=style.AnsiBGColor.RED) + " " + message
        self.set_message(content)

    def render(self) -> None:
        rect = self.get_rect(force=True)
        max_len = rect.w - 4
        
        if side_bar.is_folded:
            max_len -= 1
        
        msg_lines = split_styled_message(self.message, max_len)
        
        if len(msg_lines) != self.msg_height:
            self.msg_height = len(msg_lines)
            ui.render_all(skip_component=self)
        
        rect = self.get_rect(force=True)
        style.outline_rect(rect, self.get_border_connections())
        
        x = rect.pos.x + 2
        y = rect.pos.y + 1
        
        if side_bar.is_folded:
            x += 1
        
        for i in range(self.msg_height):
            terminal.set_cursor_pos(x, y + i + 1)
            print(msg_lines[i], end="")
        

status_bar = StatusBarComponent()
