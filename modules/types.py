from modules import style

from dataclasses import dataclass


@dataclass
class DataType:
    name: str
    color: str
    base_t: type


TEXT = DataType("Text", style.AnsiFGColor.YELLOW, str)
NUMBER = DataType("Number", style.AnsiFGColor.MAGENTA, float)
BOOLEAN = DataType("Boolean", style.LOGICAL_COLOR, bool)
FLOW = DataType("Flow", style.FLOW_CONTROL_COLOR, None)


def string_to_boolean(text: str) -> bool | None:
    trueish = ["true", "t", "yes", "y", "1"]
    falseish = ["false", "f", "no", "n", "0"]
    
    if text not in trueish and text not in falseish:
        return None
    
    return text in trueish
    