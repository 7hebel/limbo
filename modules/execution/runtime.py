from modules.nodes import node
from modules import types
from modules import style

from dataclasses import dataclass
from typing import Any


@dataclass
class RuntimeSourcePtr:
    src_name: str
    rt_node: "RuntimeNode"


class RuntimeNode:
    def __init__(self, node_model: node.Node) -> None:
        self.node_model = node_model
        self.name = node_model.title
        self.handler = node_model.handler

        self.flow_next = None
        self.in_sources: dict[str, RuntimeSourcePtr] = {}
        self.out_sources: dict[str, RuntimeSourcePtr] = {}
        self.output_values: dict[str, Any] | None = None

    def initialize(self, all_nodes: dict[int, "RuntimeNode"]) -> None:
        for raw_input in self.node_model.inputs:
            if raw_input.data_type == types.FLOW:
                continue
            
            output_source = raw_input.source
            if output_source is None:
                if raw_input.constant_value is not None:
                    self.in_sources[raw_input.name] = raw_input.constant_value
                continue

            rt_output_node = all_nodes.get(output_source.node.node_id)
            if rt_output_node is None:
                raise RuntimeError(f"Expected initialized Runtime node of hash: {output_source.node.node_id} as input source for {self.name}")

            self.in_sources[raw_input.name] = RuntimeSourcePtr(output_source.name, rt_output_node)

        for raw_output in self.node_model.outputs:
            input_target = raw_output.target
            if input_target is None:
                continue

            rt_input_node = all_nodes.get(input_target.node.node_id)
            if rt_input_node is None:
                raise RuntimeError(f"Expected initialized Runtime node of hash: {input_target.node.node_id} as output target for {self.name}")

            self.out_sources[raw_output.name] = RuntimeSourcePtr(input_target.name, rt_input_node)

        if self.node_model.flow.enable_output:
            if self.node_model.flow.output_src.target is not None:
                self.flow_next = all_nodes.get(self.node_model.flow.output_src.target.node.node_id)

        if self.flow_next is None and self.out_sources:
            self.flow_next = list(self.out_sources.values())[0].rt_node

    def request_output_value(self, src_name: str) -> Any:
        if self.output_values is not None:
            if src_name not in self.output_values:
                raise RuntimeError(f"Requested output resource: <{src_name}> from evaluated node: {style.node(self.node_model)} is missing.")
            return self.output_values.get(src_name)

        self.execute()
        if self.output_values is not None:
            return self.output_values.get(src_name)

    def execute(self) -> None:
        ins = {}

        for name, pointer in self.in_sources.items():
            if isinstance(pointer, RuntimeSourcePtr):
                ins[name] = pointer.rt_node.request_output_value(pointer.src_name)

            else:
                ins[name] = pointer  # Constant.

        if self.node_model.factory.flow.enable_output:
            next_src = self.out_sources.get(self.handler(ins))
            if next_src is not None:
                self.flow_next = next_src.rt_node

        else:
            self.output_values = self.handler(ins) or {}

            if isinstance(self.output_values, str):  # Next flow pointer name.
                next_flow_name = self.output_values
                
                if next_flow_name not in self.out_sources:
                    self.flow_next = None
                    return
                
                self.flow_next = self.out_sources[next_flow_name].rt_node
                
    