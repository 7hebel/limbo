from modules import terminal
from modules import measure
from modules import chars

from tcolorpy import tcolor, AnsiFGColor, AnsiBGColor, AnsiStyle
from colorama import init, Fore, Back, Style
from dataclasses import dataclass
import re

init()

RESET = Fore.RESET + Back.RESET + Style.RESET_ALL
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
FLOW_CONTROL_COLOR = AnsiFGColor.RED
    
    
def real_length(styled_text: str) -> int:
    """ Returns length of ANSI-escaped string. """
    
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    plain_text = ansi_escape.sub('', styled_text)
    return len(plain_text)
    
    
@dataclass
class BorderConnection:
    """ 
    Borders are connected on the last bottom/left component's position. 
    The .e and .w values don't affect border itself, but tells get_rect() methods to expand.
    """
    n: bool = False
    e: bool = False
    s: bool = False
    w: bool = False
    

def outline_rect(rect: measure.Rect, connections: BorderConnection, dimmed: bool = False) -> None:
    if dimmed:
        print(DIM, end="")
        
    y_levels = (rect.pos.y + rect.h,) if connections.n else (rect.pos.y, rect.pos.y + rect.h)
    for y in y_levels:
        for x in range(rect.pos.x, rect.pos.x + rect.w):
            terminal.set_cursor_pos(x, y)
            print(chars.ROUNDED_LINE.hz, end="")
        
    for x in (rect.pos.x, rect.pos.x + rect.w):
        for y in range(rect.pos.y, rect.pos.y + rect.h):
            terminal.set_cursor_pos(x, y)
            print(chars.ROUNDED_LINE.vt, end="")

    nw = chars.ROUNDED_LINE.nw if not connections.n else chars.ROUNDED_LINE.vr
    ne = chars.ROUNDED_LINE.ne if not connections.n else chars.ROUNDED_LINE.vl
    sw = chars.ROUNDED_LINE.sw if not connections.s else chars.ROUNDED_LINE.vr
    se = chars.ROUNDED_LINE.se if not connections.s else chars.ROUNDED_LINE.vl
    
    terminal.set_cursor_pos(rect.pos.x, rect.pos.y)
    print(nw, end="")

    terminal.set_cursor_pos(rect.pos.x + rect.w, rect.pos.y)
    print(ne, end="")

    terminal.set_cursor_pos(rect.pos.x + rect.w, rect.pos.y + rect.h)
    print(se, end="")

    terminal.set_cursor_pos(rect.pos.x, rect.pos.y + rect.h)
    print(sw, end="")
    
    if dimmed:
        print(RESET, end="")

    
def key(key_name: str) -> str:
    """ Style keyname for statusbar text. """
    return tcolor(f"<{key_name}>", AnsiFGColor.CYAN) + RESET


def node(node) -> str:
    color = node.color if hasattr(node, "color") else node.collection.color
    return tcolor(f"[{node.title}]", color or None)
    

def datatype(dt) -> str:
    return tcolor("(", AnsiFGColor.LIGHTBLACK) + tcolor(dt.name, dt.color, styles=[AnsiStyle.ITALIC]) + tcolor(")", AnsiFGColor.LIGHTBLACK)
    
    
def source(src) -> str:
    return node(src.node) + tcolor("::", AnsiFGColor.LBLACK) + src.name + datatype(src.data_type)
    

def highlight(content: str) -> str:
    return tcolor(content, AnsiFGColor.MAGENTA, styles=[AnsiStyle.ITALIC])
    