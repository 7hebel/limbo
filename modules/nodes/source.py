from modules.status_bar import status_bar
from modules import helpers
from modules import types
from modules import style
from modules import chars

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from modules.nodes.node import Node


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
        x = self.node.calc_node_width() - 1
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
