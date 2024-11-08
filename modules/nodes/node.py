from modules.status_bar import status_bar
from modules.nodes import source
from modules import measure
from modules import types
from modules import style

from typing import Any, TYPE_CHECKING
from collections.abc import Callable
from dataclasses import dataclass
import uuid

if TYPE_CHECKING:
    from modules.nodes.factory import NodeFactory


@dataclass
class FlowControl:
    enable_output: bool = False
    enable_input: bool = True
    output_src: source.NodeOutput | None = None
    input_src: source.NodeInput | None = None
    
    def init(self) -> "FlowControl":
        """ Initialize copy of FlowControl with created sources. To be used by NodeFactory. """
        flow_control = FlowControl(self.enable_output, self.enable_input)

        if self.enable_output:
            flow_control.output_src = source.NodeOutput("(FlowOut)", types.FLOW)
    
        if self.enable_input:
            flow_control.input_src = source.NodeInput("(FlowIn)", types.FLOW)
    
        return flow_control
    
    def set_output_source(self, input_node: source.NodeInput) -> None:
        if input_node.data_type != types.FLOW:
            return status_bar.error(f"Cannot connect {style.source(input_node)} to a FLOW node as it's type is not {style.datatype(types.FLOW)}")
        
        self.output_src.disconnect()
        self.output_src.connect(input_node)
        
    def set_input_source(self, output_node: source.NodeOutput) -> None:
        if output_node.data_type != types.FLOW:
            return status_bar.error(f"Cannot connect {style.source(output_node)} to a FLOW node as it's type is not {style.datatype(types.FLOW)}")
        
        self.input_src.disconnect()
        self.input_src.constant_value(output_node)
        

@dataclass
class Node:
    title: str
    color: style.AnsiFGColor
    flow: FlowControl
    inputs: list[source.NodeInput]
    outputs: list[source.NodeOutput]
    handler: Callable[[dict[str, source.NodeInput]], dict[str, Any] | None]
    position: measure.Position | None = None
    node_id: str = None
    factory: "NodeFactory | None" = None

    def __post_init__(self) -> None:
        for input_node in self.inputs:
            input_node.node = self

        for output_node in self.outputs:
            output_node.node = self

        if self.node_id is None:
            self.node_id = uuid.uuid4().hex

        if self.flow.enable_input:
            self.flow.input_src.node = self
        if self.flow.enable_output:
            self.flow.output_src.node = self

        self.node = self
        
        if len(list(filter(lambda n_out: n_out.data_type != types.FLOW, self.outputs))) > 1:
            raise ValueError(f"Node: {self.title} contains over one NON-FLOW output!")
            
    def __eq__(self, value: "Node | Any") -> bool:
        if isinstance(value, Node):
            return self.node_id == value.node_id
        return False

    @property
    def rect(self) -> measure.Rect | None:
        if self.position is None:
            return None

        w, h = self.calc_output_size()
        return measure.Rect(self.position, w, h)

    @property
    def rel_flow_input_pos(self) -> tuple[int, int]:
        """ Calculate relative flow control input's position for control wire drawning. """
        return (self.position.x, self.position.y + 1)

    @property
    def rel_flow_output_pos(self) -> tuple[int, int]:
        """ Calculate relative flow control output's position for control wire drawning. """
        return (self.position.x + self.calc_node_width() - 1, self.position.y + 1)

    def calc_node_height(self) -> int:
        if not self.has_data_source():
            return 3  # Only borders, flow controls and title.
        return len(self.inputs) + len(self.outputs) + 4  # Borders, title, separator, sources

    def calc_node_width(self) -> int:
        w = 4  # Borders, padding

        longest_name = len(self.title)

        for field in self.inputs + self.outputs:
            name_len = len(field.name)

            if field in self.inputs:
                if not field.required:
                    name_len += 1

            if name_len > longest_name:
                longest_name = name_len

        w += longest_name
        return w

    def calc_output_size(self) -> tuple[int, int]:
        """ Returns output width and height. """
        return self.calc_node_width(), self.calc_node_height()

    def unlink(self) -> None:
        """ Disconnect all connected data and flow wires. """
        for input_ in self.inputs:
            input_.disconnect()

        for output in self.outputs:
            output.disconnect()

        if self.flow.enable_input:
            self.flow.input_src.disconnect()

        if self.flow.enable_output:
            self.flow.output_src.disconnect()
            
        for workspace_id in self.factory.instances.keys():
            if self in self.factory.instances[workspace_id]:
                self.factory.instances[workspace_id].remove(self)

    def get_selectable_flow_controls(self) -> list[source.NodeInput | source.NodeOutput]:
        flows_ctrls = []

        if self.flow.enable_input:
            flows_ctrls.append(self.flow.input_src)
            
        if self.flow.enable_output:
            flows_ctrls.append(self.flow.output_src)
            
        return flows_ctrls

    def first_source(self) -> source.NodeInput | source.NodeOutput | None:
        if self.inputs:
            return self.inputs[0]

        if self.outputs:
            return self.outputs[0]
        
        flow_controls = self.get_selectable_flow_controls()
        if flow_controls:
            return flow_controls[0]

    def get_output_src(self, name: str) -> source.NodeOutput | None:
        if self.flow.enable_output and name == self.flow.output_src.name:
            return self.flow.output_src
        
        for output_src in self.outputs:
            if output_src.name == name:
                return output_src

    def get_input_src(self, name: str) -> source.NodeInput | None:
        if self.flow.enable_input and name == self.flow.input_src.name:
            return self.flow.input_src
        
        for input_src in self.inputs:
            if input_src.name == name:
                return input_src

    def has_data_source(self) -> bool:
        for src in self.inputs + self.outputs:
            if src.data_type != types.FLOW:
                return True
        return False




