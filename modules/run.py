from modules import terminal
from modules import helpers
from modules import style
from modules import nodes
from modules import ui

from dataclasses import dataclass
from typing import Any
import time


@dataclass
class RuntimeSourcePtr:
    src_name: str
    rt_node: "RuntimeNode"


class RuntimeNode:
    def __init__(self, node_model: nodes.Node) -> None:
        self.node_model = node_model
        self.name = node_model.title
        self.handler = node_model.handler

        self.flow_next = None
        self.in_sources: dict[str, RuntimeSourcePtr] = {}
        self.out_sources: dict[str, RuntimeSourcePtr] = {}
        self.output_values: dict[str, Any] | None = None

    def initialize(self, all_nodes: dict[int, "RuntimeNode"]) -> None:
        for raw_input in self.node_model.inputs:
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
        return self.request_output_value(src_name)

    def execute(self) -> None:
        ins = {}

        for name, pointer in self.in_sources.items():
            if isinstance(pointer, RuntimeSourcePtr):
                ins[name] = pointer.rt_node.request_output_value(pointer.src_name)

            else:
                ins[name] = pointer  # Constant.

        if self.node_model.factory.is_flow_node():
            next_src = self.out_sources.get(self.handler(ins))
            if next_src is not None:
                self.flow_next = next_src.rt_node

        else:
            self.output_values = self.handler(ins) or {}


class NodeRunner:
    def __init__(self, start_node: nodes.Node, raw_nodes: list[nodes.Node]) -> None:
        self.runtime_nodes: dict[int, RuntimeNode] = {}
        self.start_time = time.time_ns()
        self.initialize_nodes(start_node, raw_nodes)
        helpers.MemoryJar.new_jar()

    def initialize_nodes(self, start_node: nodes.Node, raw_nodes: list[nodes.Node]) -> None:
        for raw_node in raw_nodes:
            rt_node = RuntimeNode(raw_node)
            self.runtime_nodes[raw_node.node_id] = rt_node

        for rt_node in self.runtime_nodes.values():
            rt_node.initialize(self.runtime_nodes)

        self.entry_node = self.runtime_nodes[start_node.node_id]

    def run(self):
        node = self.entry_node

        while node:
            try:
                node.execute()

            except EOFError as exit_code:
                if str(exit_code) == "-100":
                    return self.run()
                return self.finish(exit_code)

            except RuntimeError as error:
                self.error_dump(node, error)
                return self.finish(-1)

            node = node.flow_next
            if node is None:
                return self.finish(0)

    def finish(self, exit_code: int) -> int:
        total_time_s = (time.time_ns() - self.start_time) / 1e9
        time_info = style.tcolor(str(total_time_s) + "s", style.AnsiFGColor.CYAN)
        exit_info = style.tcolor(str(exit_code), style.AnsiFGColor.CYAN)

        print(f"\n{style.ITALIC}Program finished execution in {style.RESET}{time_info} {style.ITALIC}with exit code {style.RESET}{exit_info}")
        print(f"{style.key('enter')} to continue...")
        terminal.wait_for_enter()

        ui.render_all()
        return exit_code

    def error_dump(self, node: RuntimeNode, error: RuntimeError) -> None:
        content = style.tcolor(" ERROR ", color=style.AnsiFGColor.WHITE, bg_color=style.AnsiBGColor.RED) + f" Execution of node: {style.node(node.node_model)} failed!"
        print(content)
        print(str(error))
