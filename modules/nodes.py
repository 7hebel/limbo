from modules.status_bar import status_bar
from modules.side_bar import side_bar
from modules import types
from modules import style
from modules import chars
from modules import pos

from dataclasses import dataclass, replace
from collections.abc import Callable
from typing import Any
from enum import Enum
import uuid


def calc_node_height(node: "Node") -> int:
    h = 4  # Borders, title, separator
    h += len(node.inputs) + len(node.outputs)
    return h


def calc_node_width(node: "Node") -> int:
    w = 4  # Borders, padding
    
    longest_name = len(node.title)
    for field in node.inputs + node.outputs:
        name_len = len(field.name)

        if field in node.inputs:
            if not field.required:
                name_len += 1
            if field.constant_value is not None:
                name_len += 1
        
        if name_len > longest_name:
            longest_name = name_len
            
    w += longest_name
    return w


def copy_instance(source: "NodeInput | NodeOutput") -> "NodeInput | NodeOutput":
    return replace(source)


@dataclass
class NodeInput:
    name: str
    data_type: types.DataType
    required: bool = True
    constant_value: Any = None 
    node: "Node | None" = None

    def __post_init__(self) -> None:
        self.__source: NodeOutput | None = None
        
        if self.data_type == types.FLOW:
            raise ValueError(f"Created NodeInput with FLOW set as a type ({self.name})")

    def set_constant(self, const_value: str | None) -> None:
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

    @property
    def icon(self) -> str:
        if self.constant_value is not None:
            return chars.LineChars.vt
        
        if self.__source is None:
            return chars.INPUT_FREE
            
        return chars.INPUT_FULL

    @property
    def rel_pos(self) -> tuple[int, int]:
        """ Calculate relative icon's position for wire drawning. """  
        y = 3  # Top border, title, separator
        
        # Simulate drawing calculation to check which line belongs to this source.
        for source in pos.iter_alternately(self.node.inputs, self.node.outputs):
            if source == self:
                break

            y += 1
            
        x = self.node.position.x
        y += self.node.position.y
        return (x, y)

    @source.setter
    def source(self, data_source: "NodeOutput | None") -> None:
        """ Raises TypeError on source and input types conflict. """
        if data_source is None:
            self.__source = None
            return
        
        self.constant_value = None
        self.__source = data_source
        
    def disconnect(self) -> None:
        if self.__source is not None:
            self.__source.target = None
            
        self.__source = None
   
        
@dataclass
class NodeOutput:
    name: str
    data_type: types.DataType
    node: "Node | None" = None
    target: "NodeInput | Node | None" = None
    value: types.DataType | None = None
    
    def __post_init__(self) -> None:
        self._value = None

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
        
        # Simulate drawing calculation to check which line belongs to this source.
        for source in pos.iter_alternately(self.node.inputs, self.node.outputs):
            if source == self:
                break

            y += 1
            
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
    
    def connect_flow_target(self, node: "Node") -> None:
        """ Called by NodeOutput of type FLOW. """
        if not node.flow.enable_input:
            return status_bar.error(f"Target node: {style.node(node)} does not accept any flow input.")

        node.flow.input_source = self
        self.target = node
        status_bar.set_message(f"Connected flow output: {style.source(self)} to node: {style.node(node)}")
 

@dataclass
class FlowControl:
    enable_output: bool = False
    enable_input: bool = True
    input_source: "Node | None" = None
    output_target: "Node | None" = None


@dataclass
class Node:
    title: str
    color: style.AnsiFGColor
    flow: FlowControl
    inputs: list[NodeInput]
    outputs: list[NodeOutput]
    handler: Callable[[dict[str, NodeInput], dict[str, NodeOutput]], None]
    position: pos.Position | None = None
    node_hash: str = None
    factory: "NodeFactory | None" = None 
    
    def __post_init__(self) -> None:
        for input_node in self.inputs:
            input_node.node = self

        for output_node in self.outputs:
            output_node.node = self
            
        if self.node_hash is None:
            self.node_hash = uuid.uuid4().hex
            
        self.node = self
    
    def __eq__(self, value: "Node | Any") -> bool:
        if isinstance(value, Node):
            return self.node_hash == value.node_hash
        return False
            
    @property
    def rect(self) -> pos.Rect | None:
        if self.position is None:
            return None
        
        w, h = self.calc_output_size()
        return pos.Rect(self.position, w, h)
    
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
    
    def connect_flow_target(self, target: "Node") -> None:
        """ Called by input node. """
        if target == self:
            return status_bar.error(f"{style.node(self)} cannot connect to itself.")
        
        if not self.flow.enable_output:
            return status_bar.error(f"{style.node(self)} node has no flow output.")
        
        if not target.flow.enable_input:
            return status_bar.error(f"{style.node(target)} node does not accept flow input.")
        
        if target.flow.input_source is not None:
            target.flow.input_source.flow.output_target = None
            
        target.flow.input_source = self
        self.flow.output_target = target
        return status_bar.set_message(f"{style.node(self)} will pass flow to the {style.node(target)}")
        
    def unlink(self) -> None:
        """ Disconnect all connected data and flow wires. """
        for input_ in self.inputs:
            input_.disconnect()

        for output in self.outputs:
            output.disconnect()
        
        if self.flow.input_source:
            self.flow.input_source.flow.output_target = None
        self.flow.input_source = None
        
        if self.flow.output_target:
            self.flow.output_target.flow.input_source = None
        self.flow.output_target = None
        
        self.factory.instances.remove(self)


def connect_sources(s1: NodeInput | NodeOutput, s2: NodeInput | NodeOutput) -> None:
    if s1.node == s2.node:
        return status_bar.error(f"Cannot connect values of the same node {style.node(s1.node)}")
    
    if type(s1) == type(s2):
        source_type = "input" if isinstance(s1, NodeInput) else "output"
        return status_bar.error(f"Both {style.source(s1)} and {style.source(s2)} are {source_type}s!")
    
    if s1.data_type != s2.data_type:
        return status_bar.error(f"Data types for {style.source(s1)} and {style.source(s2)} are NOT equal. Use CAST block.")
    
    s1.disconnect()
    s2.disconnect()
    
    if isinstance(s1, NodeOutput):
        s1.connect(s2)
    else:
        s2.connect(s1)
        
        
@dataclass
class Collection:
    name: str
    color: style.AnsiFGColor
    
    def __post_init__(self) -> None:
        self.factories: list["NodeFactory"] = []
    
    def __hash__(self) -> str:
        return hash(f"{self.name}.{self.color}")
    
    def register_factory(self, factory: "NodeFactory") -> None:
        self.factories.append(factory)

  
@dataclass
class NodeFactory:
    title: str
    collection: Collection
    flow: FlowControl
    inputs: list[NodeInput]
    outputs: list[NodeOutput]
    handler: Callable[[dict[str, NodeInput], dict[str, NodeOutput]], None]
    singleton: bool = False
    
    def __post_init__(self) -> None:
        self.instances: list[Node] = []
        self.collection = self.collection.value
        self.collection.register_factory(self)
    
    def build_instance(self) -> Node | None:
        if self.singleton and self.instances:
            return status_bar.error(f"{style.node(self.instances[0])} can only be created once!")
        
        instanced_inputs = [copy_instance(in_src) for in_src in self.inputs]
        instanced_outputs = [copy_instance(out_src) for out_src in self.outputs]

        instance = Node(
            title=self.title,
            color=self.collection.color,
            flow=self.flow,
            inputs=instanced_inputs,
            outputs=instanced_outputs,
            handler=self.handler,
            factory=self
        )

        self.instances.append(instance)
        return instance

    def is_function_node(self) -> bool:
        """ Function node is a node with disabled output flow source and with at least one input and output. """
        return not self.flow.enable_output and self.inputs and self.outputs and not self.is_flow_node()

    def is_flow_node(self) -> bool:
        """ Flow node is a node that has at least one output of type FLOW (can't have other types). """
        return self.outputs and self.outputs[0].data_type == types.FLOW
  
  
class NodesCollections(Enum):
    FLOW_CONTROL = Collection("Flow Control", style.AnsiFGColor.RED)
    LOGICAL = Collection("Logical", style.AnsiFGColor.BLUE)
    CASTING = Collection("Cast", style.AnsiFGColor.CYAN)
    MATH = Collection("Maths", style.AnsiFGColor.MAGENTA) # add sub pow
    STRINGS = Collection("Strings", style.AnsiFGColor.YELLOW)  # lowercase, join etc.
    INTERACTION = Collection("Interaction", style.AnsiFGColor.GREEN)
    
  
from modules import builtin
side_bar.set_collections(NodesCollections)
