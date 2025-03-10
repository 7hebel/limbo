from modules.status_bar import status_bar
from modules.nodes.node import Node
from modules.nodes import source
from modules import helpers
from modules import measure
from modules import vp_ext
from modules import format
from modules import types
from modules import style
from modules import chars
from modules import ui

from typing import TYPE_CHECKING, Self
from collections.abc import Callable
from dataclasses import dataclass
import uuid
import os

if TYPE_CHECKING:
    from modules.viewport import ViewportComponent
    

@dataclass
class SelectionState:
    node: Node | None = None
    src: source.NodeInput | source.NodeOutput | None = None
    highlighted_source: source.NodeInput | source.NodeOutput | None = None
        

class Workspace(vp_ext.ShiftableFocus, vp_ext.MovableNodes):
    def __init__(self, name: str) -> None:
        self.name = name
        
        self.nodes: list[Node] = []
        self.camera = measure.Camera(0, 0)
        self.selection = SelectionState()
        self.id = uuid.uuid4().hex
        
        self.render: Callable[[None], None] | None = None
        self.viewport: "ViewportComponent | None" = None

        self.__edit_node_mode: bool = False
        self.__associated_file: str | None = None
        self._is_saved: bool = False
      
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
        
    def associate_file(self, path: str) -> None:
        """ Link file with this workspace. """
        self.__associated_file = path
        self._is_saved = True
        self.name = os.path.basename(path)
        ui.render_all()
        
    def export_state(self) -> None:
        """ Export current state into file. If no file is associated with this workspace, asks for path and links it. """
        path = self.__associated_file
        
        if path is None:
            path = self.viewport.prompt("Export path", "")
            if path is None:
                return
            
            self.associate_file(path)
        
        format.LimbFormat.export(self.nodes, (self.camera.x, self.camera.y), path)
        self._is_saved = True
        ui.render_all()
        
    def renderable_title(self) -> tuple[str, int]:
        """ Return styled version of workspace's name including singal chars and it's real length. """
        if self.__associated_file is None or not self.name:
            return ("", 0)
        
        indicator = " "
        total_length = len(self.name) + 2
        
        if not self._is_saved:
            indicator += style.tcolor("* ", style.AnsiFGColor.YELLOW, styles=[style.AnsiStyle.BLINK])
            total_length += 2
        
        return (indicator + style.tcolor(self.name, styles=[style.AnsiStyle.ITALIC]) + " ", total_length)
        
    def add_node(self, node: Node) -> None:
        """ 
        Add new node to the workspace. If it has no position set, 
        it will position it at the center avoiding collision with other nodes.
        """
        if node.position is None:
            node.position = self.camera.get_pos()

        self.nodes.append(node)
        self.selection.node = node

        if self.node_intersects():
            self.move_node_right()

        self._is_saved = False
        self.render()
        
    def remove_node(self) -> None:
        """ Remove selected node. Disconnect all wires. """
        node = self.selection.node
        if node is None:
            return

        if self.selection.src:
            source = self.selection.src
            if source.node == node:
                self.selection.src = None
                
        self.selection.node = None

        node.unlink()
        self.nodes.remove(node)

        self.selection.node = self.nodes[0] if self.nodes else None
        self._is_saved = False
        ui.render_all()
        return status_bar.set_message(f"Removed {style.node(node)}")

    def duplicate_node(self) -> None:
        if not self.selection.node:
            return
        
        new_node = self.selection.node.factory.build_instance(self.id)
        self.add_node(new_node)

    def shift_source_selection(self, direction: measure.VerticalDirection) -> None:
        if not self.edit_node_mode or self.selection.node is None:
            return

        flows_ctrls = self.selection.node.get_selectable_flow_controls()
        all_sources = flows_ctrls + list(helpers.iter_alternately(self.selection.node.inputs, self.selection.node.outputs))
        current_index = all_sources.index(self.selection.highlighted_source)
        next_index = helpers.wrapping_index_shift(all_sources, current_index, direction)

        self.selection.highlighted_source = all_sources[next_index]
        self.render()
        
    def disconnect_source(self) -> None:
        if not self.edit_node_mode or self.selection.node is None or self.selection.highlighted_source is None:
            return

        self.selection.highlighted_source.disconnect()
        self._is_saved = False
        ui.render_all()
        
    def choose_source(self) -> None:
        if not self.edit_node_mode or self.selection.node is None:
            return

        if self.selection.src is None:
            status_bar.set_message(f"Select target source for {style.source(self.selection.highlighted_source)}")

            self.selection.src = self.selection.highlighted_source
            self.edit_node_mode = False
            return self.render()

        status = source.connect_sources(self.selection.highlighted_source, self.selection.src)
        if status:
            status_bar.standard_keys_help()
        
        self.selection.src = None
        self.edit_node_mode = False
        
        self._is_saved = False
        ui.render_all()

    def edit_constant(self) -> None:
        if not self.selection.highlighted_source:
            return
        
        if self.selection.highlighted_source.data_type == types.FLOW:
            return status_bar.error(f"Cannnot set constant to source of type {style.datatype(types.FLOW)}")

        if isinstance(self.selection.highlighted_source, source.NodeOutput):
            return status_bar.error(f"Cannot set constant value to the output source: {style.source(self.selection.highlighted_source)}")

        edit_help = {
            "esc": "Remove constant.",
            "enter": "Accept constant."
        }
        status_bar.keys_help("Edit constant.", edit_help)

        self._is_saved = False
        current_value = self.selection.highlighted_source.constant_value or ""
        value = self.viewport.prompt(style.source(self.selection.highlighted_source), current_value)
        self.selection.highlighted_source.set_constant(value)
        