from modules.chars import ROUNDED_LINE
from modules import style
from modules import types

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from modules.execution.runtime import RuntimeNode, RuntimeSourcePtr


DBG_PREFIX = f"  {style.DIM}dbg) {style.RESET }"


class DebugSession:
    def __init__(self) -> None:
        self.indent = 0
        
    def write_msg(self, msg: str) -> str:
        msg = DBG_PREFIX + f"{style.DIM}{ROUNDED_LINE.vt}{style.RESET} " * self.indent + msg
        print(msg)
        
    def begin_execution(self, rt_node: "RuntimeNode") -> None:
        message = style.tcolor(ROUNDED_LINE.nw + 3 * ROUNDED_LINE.hz + "(", styles=[style.AnsiStyle.DIM]) 
        message += style.tcolor("Begin execution: ", styles=[style.AnsiStyle.ITALIC]) + style.node(rt_node.node_model) 
        message += style.tcolor(") ...", styles=[style.AnsiStyle.DIM]) 
        self.write_msg("")
        self.write_msg(message)
        self.indent += 1

    def request_value(self, name: str, pointer: "RuntimeSourcePtr") -> None:
        message = f"Awaiting response from: {style.node(pointer.rt_node.node_model)}/{style.UNDERLINE}{pointer.src_name}{style.RESET} "
        message += f"to set: {style.highlight(name)}"
        self.write_msg(message)
        
    def received_value(self, name: str, value: Any, datatype: types.DataType) -> None:
        message = f"{style.highlight(name)} = `{style.tcolor(str(value), datatype.color)}`  {style.DIM}(response received){style.RESET}"
        self.write_msg(message)
        
    def use_constant(self, name: str, value: Any, datatype: types.DataType) -> None:
        message = f"{style.highlight(name)} = `{style.tcolor(str(value), datatype.color)}`  {style.DIM}(constant){style.RESET}"
        self.write_msg(message)
        
    def point_next_node(self, next: "RuntimeNode | None") -> None:
        if next is not None:
            message = f"Next -> {style.node(next.node_model)}"
        else:
            message = "Next -> (no next)"
        self.write_msg(message)
        
    def node_output(self, values: dict) -> None:
        message = f"Output -> `{style.highlight(str(values))}`"
        self.write_msg(message)
        
    def end_execution(self) -> None:
        message = f"{style.DIM}{ROUNDED_LINE.sw}{3 * ROUNDED_LINE.hz} finished"
        self.indent -= 1
        self.write_msg(message)
        self.write_msg("")
        