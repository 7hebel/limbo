from modules.status_bar import status_bar
from modules.nodes import source
from modules.nodes import node
from modules import types
from modules import style
from modules import chars

from dataclasses import dataclass, replace as copy_src
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.nodes.collection import Collection

factories_register: dict[str: "NodeFactory"] = {}


@dataclass
class NodeFactory:
    title: str
    collection: "Collection"
    flow: node.FlowControl
    inputs: list[source.NodeInput]
    outputs: list[source.NodeOutput]
    handler: Callable[[dict[str, source.NodeInput], dict[str, source.NodeOutput]], None]
    singleton: bool = False
    factory_id: str = None

    def __post_init__(self) -> None:
        self.instances: dict[str, list[node.Node]] = {}  # List of built instances per workspace
        self.collection = self.collection.value
        
        if self.factory_id is None:
            self.factory_id = f"std/{self.title}:{hash(self.collection)}"
        
        self.collection.register_factory(self)
        factories_register[self.factory_id] = self

    def build_instance(self, workspace_id: str) -> node.Node | None:
        if workspace_id not in self.instances:
            self.instances[workspace_id] = []
        
        if self.singleton and self.instances.get(workspace_id):
            return status_bar.error(f"{style.node(self)} can only be created once!")

        instanced_inputs = [copy_src(in_src) for in_src in self.inputs]
        instanced_outputs = [copy_src(out_src) for out_src in self.outputs]

        instance = node.Node(
            title=self.title,
            color=self.collection.color,
            flow=self.flow.init(),
            inputs=instanced_inputs,
            outputs=instanced_outputs,
            handler=self.handler,
            factory=self
        )

        self.instances[workspace_id].append(instance)
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
