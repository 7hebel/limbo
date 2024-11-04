from modules.status_bar import status_bar
from modules import helpers
from modules import measure
from modules import vp_ext
from modules import nodes
from modules import types
from modules import style
from modules import chars

from typing import TYPE_CHECKING, Self
from collections.abc import Callable
from dataclasses import dataclass

if TYPE_CHECKING:
    from modules.viewport import ViewportComponent
    

@dataclass
class SelectionState:
    node: nodes.Node | None = None
    source: nodes.NodeInput | nodes.NodeOutput | None = None
    highlighted_source: nodes.NodeInput | nodes.NodeOutput | None = None


class Workspace(vp_ext.ShiftableFocus, vp_ext.MovableNodes):
    def __init__(self, name: str, dest_file: str | None = None) -> None:
        self.name = name
        self.associated_file = dest_file
        
        self.nodes: list[nodes.Node] = []
        self.camera = measure.Camera(0, 0)
        self.selection = SelectionState()
        
        self.render: Callable[[None], None] | None = None
        self.viewport: "ViewportComponent | None" = None
        self.__edit_node_mode = False
      
    def initialize(self, viewport: "ViewportComponent") -> Self:
        self.viewport = viewport
        self.render = viewport.render
        return self
        
    @property
    def edit_node_mode(self) -> bool:
        return self.__edit_node_mode

    @edit_node_mode.setter
    def edit_node_mode(self, state: bool) -> None:
        if state:
            self.selection.highlighted_source = self.selection.node.first_source()

            status_bar.keys_help(
                "EDIT NODE",
                {
                    "esc": "exit",
                    chars.ALL_ARROWS: "change source",
                    "del": "disconnect wire",
                    "space": "connect wire",
                    "c": "edit constant"
                }
            )

        else:
            self.selection.highlighted_source = None

        self.__edit_node_mode = state
        self.render()
        
    def render(self) -> None:
        if self.render is not None:
            self.render()
        
    def add_node(self, node: nodes.Node) -> None:
        if node.position is None:
            node.position = self.camera.get_pos()

        self.nodes.append(node)
        self.selection.node = node

        if self.node_intersects():
            self.move_node_right()

        self.render()
        
    def remove_node(self) -> None:
        """ Remove selected node. Disconnect all wires. """
        node = self.selection.node
        if node is None:
            return

        if self.selection.source:
            source = self.selection.source
            if source.node == node:
                self.selection.source = None
                
        self.selection.node = None

        node.unlink()
        self.nodes.remove(node)

        self.selection.node = self.nodes[0] if self.nodes else None
        self.render()
        return status_bar.set_message(f"Removed {style.node(node)}")

    def duplicate_node(self) -> None:
        if not self.selection.node:
            return
        
        new_node = self.selection.node.factory.build_instance()
        self.add_node(new_node)

    def shift_source_selection(self, direction: measure.VerticalDirection) -> None:
        if not self.edit_node_mode or self.selection.node is None:
            return

        flows_ctrls = self.selection.node.get_selectable_flow_controls()
        all_sources = flows_ctrls + list(helpers.iter_alternately(self.selection.node.inputs, self.selection.node.outputs))
        next_index = all_sources.index(self.selection.highlighted_source) + direction

        if next_index > len(all_sources) - 1:
            next_index = 0
        elif next_index == -1:
            next_index = len(all_sources) - 1

        self.selection.highlighted_source = all_sources[next_index]
        self.render()
        
    def disconnect_source(self) -> None:
        if not self.edit_node_mode or self.selection.node is None or self.selection.highlighted_source is None:
            return

        self.selection.highlighted_source.disconnect()
        self.render()
        
    def choose_source(self) -> None:
        if not self.edit_node_mode or self.selection.node is None:
            return

        if self.selection.source is None:
            status_bar.set_message(f"Select target source for {style.source(self.selection.highlighted_source)}")

            self.selection.source = self.selection.highlighted_source
            self.edit_node_mode = False
            return self.render()

        nodes.connect_sources(self.selection.highlighted_source, self.selection.source)
        self.selection.source = None
        self.edit_node_mode = False
        
        status_bar.standard_keys_help()
        self.render()
        
    def edit_constant(self) -> None:
        if not self.selection.highlighted_source:
            return
        
        if self.selection.highlighted_source.data_type == types.FLOW:
            return status_bar.error(f"Cannnot set constant to source of type {style.datatype(types.FLOW)}")

        if isinstance(self.selection.highlighted_source, nodes.NodeOutput):
            return status_bar.error(f"Cannot set constant value to the output source: {style.source(self.selection.highlighted_source)}")

        edit_help = {
            "esc": "Remove constant.",
            "enter": "Accept constant."
        }
        status_bar.keys_help("Edit constant.", edit_help)

        current_value = self.selection.highlighted_source.constant_value or ""
        value = self.viewport.prompt(style.source(self.selection.highlighted_source), current_value)
        self.selection.highlighted_source.set_constant(value)
        