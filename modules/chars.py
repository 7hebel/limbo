"""
Module contains special ASCII chars used within application.
"""
from dataclasses import dataclass


@dataclass
class LineChars:
    nw: str = "╭"
    ne: str = "╮"
    sw: str = "╰"
    se: str = "╯"
    vt: str = "│"
    hz: str = "─"
    vl: str = "┤"
    vr: str = "├"
    fl: str = "╾"
    fr: str = "╼"


ROUNDED_LINE = LineChars()
ROUNDED_DOTTED = LineChars(hz="╴", vt="╎")
DOUBLE_LINE = LineChars(
    nw="╔",
    ne="╗",
    sw="╚",
    se="╝",
    vt="║",
    hz="═",
    vl="╡",
    vr="╞",
)


INPUT_FREE = "○"
INPUT_FULL = "◉"
OUTPUT_FREE = "◇"
OUTPUT_FULL = "◈"

ALL_ARROWS = "🠙🠛🠘🠚"

COLLECTION_FOLDED = "⮞"
COLLECTION_UNFOLDED = "⮟"

FUNCTION_NODE = "ƒ"
FLOW_NODE = "λ"
CONSTANT_VALUE = "*"

