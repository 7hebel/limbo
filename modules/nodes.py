from modules.status_bar import status_bar
from modules.side_bar import side_bar
from modules import helpers
from modules import measure
from modules import types
from modules import style
from modules import chars

from dataclasses import dataclass, replace as copy_src
from collections.abc import Callable
from typing import Any
from enum import Enum
import uuid


def calc_node_height(node: "Node") -> int:
    if not node.has_data_source():
        return 3  # Only borders, flow controls and title.
    return len(node.inputs) + len(node.outputs) + 4  # Borders, title, separator, sources


def calc_node_width(node: "Node") -> int:
    w = 4  # Borders, padding

    longest_name = len(node.title)

    for field in node.inputs + node.outputs:
        name_len = len(field.name)

        if field in node.inputs:
            if not field.required:
                name_len += 1

        if name_len > longest_name:
            longest_name = name_len

    w += longest_name
    return w


@dataclass
class NodeInput:
    name: str
    data_type: types.DataType
    required: bool = True
    constant_value: Any = None
    node: "Node | None" = None

    def __post_init__(self) -> None:
        self.__source: NodeOutput | None = None

    def disconnect(self) -> None:
        """ Disconnect from target output source. """
        if self.__source is not None:
            self.__source.target = None

        self.__source = None

    def set_constant(self, const_value: str | None) -> None:
        """
        Validate and set new constant value for this input source.
        It disconnects current source if any.
        If `const_value` is None, constant will be erased.
        """

        if const_value is None:
            self.constant_value = None
            return status_bar.set_message(f"Constant value for {style.source(self)} has been ereased.")

        try:
            self.disconnect()

            if self.data_type.base_t == bool:
                const_value = types.string_to_boolean(const_value.lower())
                if const_value is None:
                    return status_bar.error("Boolean convertion failed. Use (t)rue, (y)es, 1  or  (f)alse, (n)o, 0.")

            value = self.data_type.base_t(const_value)
            self.constant_value = value
            status_bar.set_message(f"Constant value for {style.source(self)} has been set to: `{self.constant_value}`")

        except ValueError:
            status_bar.error(f"Failed to convert `{const_value}` to: {style.datatype(self.data_type)}")

    @property
    def source(self) -> "NodeOutput | None":
        return self.__source

    @source.setter
    def source(self, data_source: "NodeOutput | None") -> None:
        if data_source is None:
            self.__source = None
            return

        self.constant_value = None
        self.__source = data_source

    @property
    def icon(self) -> str:
        """ Returns displayable icon in form of a ASCII char based on state. """
        if self.constant_value is not None:
            return chars.CONSTANT_VALUE

        if self.__source is None:
            return chars.INPUT_FREE

        return chars.INPUT_FULL

    @property
    def rel_pos(self) -> tuple[int, int]:
        """ Calculate relative icon's position for wire drawning. """
        y = 3  # Top border, title, separator

        for source in helpers.iter_alternately(self.node.inputs, self.node.outputs):
            if source == self:
                break
            y += 1

        if self == self.node.flow.input_src:
            y = 1

        x = self.node.position.x
        y += self.node.position.y
        return (x, y)


@dataclass
class NodeOutput:
    name: str
    data_type: types.DataType
    node: "Node | None" = None
    target: "NodeInput | None" = None

    @property
    def icon(self) -> str:
        if self.data_type == types.FLOW:
            return chars.DOUBLE_LINE.vr

        if self.target is None:
            return chars.OUTPUT_FREE

        return chars.OUTPUT_FULL

    @property
    def rel_pos(self) -> tuple[int, int]:
        """ Calculate relative icon's position for wire drawning. """
        x = calc_node_width(self.node) - 1
        y = 3  # Top border, title, separator

        for source in helpers.iter_alternately(self.node.inputs, self.node.outputs):
            if source == self:
                break

            y += 1
            
        if self == self.node.flow.output_src:
            y = 1

        x += self.node.position.x
        y += self.node.position.y
        return (x, y)

    @property
    def target_rel_pos(self) -> tuple[int, int]:
        if isinstance(self.target, NodeInput):
            return self.target.rel_pos

        return self.target.rel_flow_input_pos

    def connect(self, target: NodeInput) -> None:
        target.source = self
        self.target = target

    def disconnect(self) -> None:
        if self.target is None:
            return

        self.target.disconnect()
        self.target = None


class FlowSource(Enum):
    INPUT = "in"
    OUTPUT = "out"


@dataclass
class FlowControl:
    enable_output: bool = False
    enable_input: bool = True
    output_src: NodeOutput | None = None
    input_src: NodeInput | None = None
    
    def init(self) -> "FlowControl":
        """ Initialize copy of FlowControl with created sources. To be used by NodeFactory. """
        flow_control = FlowControl(self.enable_output, self.enable_input)

        if self.enable_output:
            flow_control.output_src = NodeOutput("(FlowOut)", types.FLOW)
    
        if self.enable_input:
            flow_control.input_src = NodeInput("(FlowIn)", types.FLOW)
    
        return flow_control
    
    def set_output_source(self, input_node: NodeInput) -> None:
        if input_node.data_type != types.FLOW:
            return status_bar.errorr(f"Cannot connect {style.source(input_node)} to a FLOW node as it's type is not {style.datatype(types.FLOW)}")
        
        self.output_src.disconnect()
        self.output_src.connect(input_node)
        
    def set_input_source(self, output_node: NodeOutput) -> None:
        if output_node.data_type != types.FLOW:
            return status_bar.errorr(f"Cannot connect {style.source(output_node)} to a FLOW node as it's type is not {style.datatype(types.FLOW)}")
        
        self.input_src.disconnect()
        self.input_src.constant_value(output_node)
        

@dataclass
class Node:
    title: str
    color: style.AnsiFGColor
    flow: FlowControl
    inputs: list[NodeInput]
    outputs: list[NodeOutput]
    handler: Callable[[dict[str, NodeInput], dict[str, NodeOutput]], None]
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
        return (self.position.x + calc_node_width(self) - 1, self.position.y + 1)

    def calc_output_size(self) -> tuple[int, int]:
        """ Returns output width and height. """
        return calc_node_width(self), calc_node_height(self)

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
            
        self.factory.instances.remove(self)

    def get_selectable_flow_controls(self) -> list[NodeInput | NodeOutput]:
        flows_ctrls = []

        if self.flow.enable_input:
            flows_ctrls.append(self.flow.input_src)
            
        if self.flow.enable_output:
            flows_ctrls.append(self.flow.output_src)
            
        return flows_ctrls

    def first_source(self) -> NodeInput | NodeOutput | None:
        if self.inputs:
            return self.inputs[0]

        if self.outputs:
            return self.outputs[0]
        
        flow_controls = self.get_selectable_flow_controls()
        if flow_controls:
            return flow_controls[0]

    def get_output_src(self, name: str) -> NodeOutput | None:
        if self.flow.enable_output and name == self.flow.output_src.name:
            return self.flow.output_src
        
        for output_src in self.outputs:
            if output_src.name == name:
                return output_src

    def get_input_src(self, name: str) -> NodeInput | None:
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


def connect_sources(s1: NodeInput | NodeOutput, s2: NodeInput | NodeOutput) -> None:
    """ Connect two node data sources. Perfroms basic validation. """

    if s1.node == s2.node:
        return status_bar.error(f"Cannot connect sources from the same node {style.node(s1.node)}")

    if type(s1) == type(s2):
        source_type = "input" if isinstance(s1, NodeInput) else "output"
        return status_bar.error(f"Both {style.source(s1)} and {style.source(s2)} are {source_type}s!")

    if s1.data_type != s2.data_type:
        return status_bar.error(f"Data types for {style.source(s1)} and {style.source(s2)} are NOT equal")

    s1.disconnect()
    s2.disconnect()

    s1.connect(s2) if isinstance(s1, NodeOutput) else s2.connect(s1)


@dataclass
class Collection:
    name: str
    color: style.AnsiFGColor

    def __post_init__(self) -> None:
        self.factories: list["NodeFactory"] = []

    def __hash__(self) -> int:
        return len(self.name) ** len(self.color.name)

    def register_factory(self, factory: "NodeFactory") -> None:
        self.factories.append(factory)


class NodesCollections(Enum):
    FLOW_CONTROL = Collection("Flow Control", style.AnsiFGColor.RED)
    LOGICAL = Collection("Logical", style.AnsiFGColor.BLUE)
    CASTING = Collection("Cast", style.AnsiFGColor.CYAN)
    MEMORY = Collection("Memory", style.AnsiFGColor.WHITE)
    MATH = Collection("Maths", style.AnsiFGColor.MAGENTA)
    STRINGS = Collection("Strings", style.AnsiFGColor.YELLOW)
    INTERACTION = Collection("Interaction", style.AnsiFGColor.GREEN)


factories_register: dict[str: "NodeFactory"] = {}


@dataclass
class NodeFactory:
    title: str
    collection: Collection
    flow: FlowControl
    inputs: list[NodeInput]
    outputs: list[NodeOutput]
    handler: Callable[[dict[str, NodeInput], dict[str, NodeOutput]], None]
    singleton: bool = False
    factory_id: str = None

    def __post_init__(self) -> None:
        self.instances: list[Node] = []
        self.collection = self.collection.value
        
        if self.factory_id is None:
            self.factory_id = f"std/{self.title}:{hash(self.collection)}"
        
        self.collection.register_factory(self)
        factories_register[self.factory_id] = self

    def build_instance(self) -> Node | None:
        if self.singleton and self.instances:
            return status_bar.error(f"{style.node(self.instances[0])} can only be created once!")

        instanced_inputs = [copy_src(in_src) for in_src in self.inputs]
        instanced_outputs = [copy_src(out_src) for out_src in self.outputs]

        instance = Node(
            title=self.title,
            color=self.collection.color,
            flow=self.flow.init(),
            inputs=instanced_inputs,
            outputs=instanced_outputs,
            handler=self.handler,
            factory=self
        )

        self.instances.append(instance)
        return instance

    def output_datatype(self) -> types.DataType | None:
        if not self.outputs:
            if self.flow.enable_output:
                return types.FLOW
            return None

        return self.outputs[0].data_type

    def is_function_node(self) -> bool:
        """ Function node is a node with at least one input and output. """
        return self.outputs or self.flow.enable_output

    def get_char_indicator(self) -> str:
        dt = self.output_datatype()
        
        if dt is None:
            return ""
        
        if dt == types.FLOW:
            return chars.FLOW_NODE

        return chars.FUNCTION_NODE

""" Initialize all NodeFactories, feed NodesCollection, set sidebar collection. """
from modules import builtin
side_bar.set_collections(NodesCollections)
