from modules.status_bar import status_bar
from modules.side_bar import side_bar
from modules import wire_builder
from modules import user_input
from modules import terminal
from modules import helpers
from modules import string
from modules import vp_ext
from modules import format
from modules import chars
from modules import style
from modules import nodes
from modules import types
from modules import pos
from modules import run
from modules import ui

from dataclasses import dataclass
        

@dataclass
class SelectionState:
    node: nodes.Node | None = None
    source: nodes.NodeInput | nodes.NodeOutput | None = None
    highlighted_source: nodes.NodeInput | nodes.NodeOutput | None = None


class ViewportComponent(ui.TextUIComponent, vp_ext.ShiftableFocus, vp_ext.MovableNodes, vp_ext.StateBasedNodeCache):
    def __init__(self) -> None:
        self.camera_x = 0
        self.camera_y = 0
        self.nodes: list["nodes.Node"] = []
        self.selection = SelectionState()
        self._nodes_state_cache = {}
        self.__edit_node_mode = False
        
        super().__init__()

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

    def get_rect(self) -> pos.Rect:
        """ Return terminal total Viewport rect. """
        x, y = 1, 0
        w, h = terminal.get_w() - 1, terminal.get_h()

        if not side_bar.is_folded:
            x += side_bar.width - 1
            w -= side_bar.width - 1

        if status_bar.get_rect() is not None:
            h -= (status_bar.msg_height + status_bar.BASE_HEIGHT)

        if self.get_border_connections().s:
            h += 1

        return pos.Rect(pos.Position(x, y), w, h)

    def work_rect(self) -> pos.Rect:
        """ Returns Rect from the inside of the viewport border. """

        rect = self.get_rect()
        return pos.Rect(pos.Position(rect.pos.x + 1, rect.pos.y + 2), rect.w - 1, rect.h - 2)

    def get_cameraview_rect(self) -> pos.Rect:
        vp_rect = self.work_rect()
        view_w = vp_rect.w + vp_rect.pos.x
        view_h = vp_rect.h + vp_rect.pos.y

        start_render_pos = pos.Position(self.camera_x - (view_w // 2), self.camera_y - (view_h // 2))
        return pos.Rect(start_render_pos, view_w, view_h)

    def get_border_connections(self) -> style.BorderConnection:
        return style.BorderConnection(s=status_bar.get_rect() is not None)

    def add_node(self, node: "nodes.Node") -> None:
        if node.position is None:
            node.position = pos.Position(self.camera_x, self.camera_y)

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
            if isinstance(self.selection.source, tuple):
                source = self.selection.source[1]
                
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

    def shift_source_selection(self, direction: pos.VerticalDirection) -> None:
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

    def drawable_node(self, node: "nodes.Node") -> tuple[string.ColoredStringObject, pos.Rect]:
        """ Returns drawable representation of node, and it's rect. """
        w, h = node.calc_output_size()
        rect = pos.Rect(node.position, w, h)

        outline_color = node.color if node == self.selection.node else style.AnsiFGColor.LIGHTBLACK

        builder = string.ColoredStringObject()
        builder.feed_string(chars.ROUNDED_LINE.nw + (chars.ROUNDED_LINE.hz * (w - 2)) + chars.ROUNDED_LINE.ne, outline_color)
        builder.break_line()

        flow_in_char = chars.DOUBLE_LINE.vl if node.flow.enable_input else chars.ROUNDED_LINE.vt
        flow_out_char = chars.DOUBLE_LINE.vr if node.flow.enable_output else chars.ROUNDED_LINE.vt

        if self.edit_node_mode and node == self.selection.node:
            if self.selection.highlighted_source == node.flow.input_src:
                builder.feed_char(flow_in_char, style.AnsiFGColor.WHITE, styles=[style.AnsiStyle.BLINK, style.AnsiStyle.INVERT])
            else:
                builder.feed_char(flow_in_char, outline_color)
        else:
            builder.feed_char(flow_in_char, outline_color)

        title_line = f"{node.title}".center(w - 2)
        builder.feed_string(title_line, node.color or None, styles=[style.AnsiStyle.INVERT, style.AnsiStyle.ITALIC] if node == self.selection.node and self.edit_node_mode else [])

        if self.edit_node_mode and node == self.selection.node:
            if self.selection.highlighted_source == node.flow.output_src:
                builder.feed_char(flow_out_char, style.AnsiFGColor.WHITE, styles=[style.AnsiStyle.BLINK, style.AnsiStyle.INVERT])
            else:
                builder.feed_char(flow_out_char, outline_color)
        else:
            builder.feed_char(flow_out_char, outline_color)

        builder.break_line()

        builder.feed_string(chars.ROUNDED_LINE.vr + (chars.ROUNDED_LINE.hz * (w - 2)) + chars.ROUNDED_LINE.vl, outline_color)
        builder.break_line()

        for source in helpers.iter_alternately(node.inputs, node.outputs):
            source: "nodes.NodeInput | nodes.NodeOutput"

            is_selected_node = self.edit_node_mode and self.selection.highlighted_source == source
            is_selected_source = source == self.selection.source

            styles = [style.AnsiStyle.ITALIC]
            if is_selected_node:
                styles.append(style.AnsiStyle.INVERT)
            if is_selected_source:
                styles.append(style.AnsiStyle.UNDERLINE)

            if source in node.inputs:
                builder.feed_char(source.icon, source.data_type.color)

                color = None if source.required else style.AnsiFGColor.LIGHTBLACK

                builder.feed_char(" ")
                builder.feed_string(source.name, color, styles)
                builder.feed_string("".ljust(w - len(source.name) - 3))

                builder.feed_char(chars.ROUNDED_LINE.vt, outline_color)
                builder.break_line()

            if source in node.outputs:
                builder.feed_char(chars.ROUNDED_LINE.vt, outline_color)
                builder.feed_string("".rjust(w - 3 - len(source.name)))
                builder.feed_string(f"{source.name}", styles=styles)
                builder.feed_char(" ")
                builder.feed_char(source.icon, source.data_type.color)
                builder.break_line()

        builder.feed_string(chars.ROUNDED_LINE.sw + (chars.ROUNDED_LINE.hz * (w - 2)) + chars.ROUNDED_LINE.se, outline_color)
        return (builder, rect)

    def draw_wire(self,
                  rel_from: tuple[int, int],
                  rel_to: tuple[int, int],
                  charset: chars.LineChars,
                  avoid_rects: list[pos.Rect],
                  color: style.AnsiFGColor,
                  dimmed: bool,
                  highlight: bool
                  ) -> None:
        camera_rect = self.get_cameraview_rect()

        start_pos = (rel_from[0] - camera_rect.pos.x, rel_from[1] - camera_rect.pos.y)
        end_pos = (rel_to[0] - camera_rect.pos.x, rel_to[1] - camera_rect.pos.y)

        builder = wire_builder.WireBuilder(start_pos, end_pos, charset, avoid_rects, camera_rect)
        for (x, y), char in builder.positioned_chars.items():
            if not self.work_rect().contains_point(x, y):
                continue

            styles = []

            if highlight:
                styles.append(style.AnsiStyle.BOLD)
                styles.append(style.AnsiStyle.BLINK)

            if dimmed:
                styles.append(style.AnsiStyle.DIM)

            char = style.tcolor(char, color, styles=styles)

            terminal.set_cursor_pos(x, y)
            print(char)

    def prompt(self, text: str, placeholder: str) -> str | None:
        rect = self.get_rect()
        y = rect.pos.y + rect.h - 1

        prompt_x = rect.pos.x + 1
        x_end = rect.pos.x + rect.w - 1

        terminal.set_cursor_pos(prompt_x, y)
        print(text + style.tcolor(": ", style.AnsiFGColor.CYAN), end="")

        x_start = prompt_x + style.real_length(text) + 2

        terminal.set_cursor_pos(x_start, y)
        value = user_input.get_input("", x_end - x_start + 1, True, placeholder)
        ui.render_all()

        if value is None:
            status_bar.set_message("Prompt has been manually canceled...")
            return

        return value

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
        value = self.prompt(style.source(self.selection.highlighted_source), current_value)
        self.selection.highlighted_source.set_constant(value)

    def render(self):
        self.clean_contents()
        camera_rect = self.get_cameraview_rect()

        for node in self.nodes:
            # Draw data wires.
            for output in node.outputs + [node.flow.output_src]:
                if output is None:
                    continue
                
                if output.target:
                    rel_start = output.rel_pos
                    rel_end = output.target_rel_pos

                    dimmed = not (node == self.selection.node or output.target.node == self.selection.node)
                    selected = self.edit_node_mode and self.selection.highlighted_source in (output, output.target)
                    charset = chars.DOUBLE_LINE if output.data_type == types.FLOW else chars.ROUNDED_LINE if not selected else chars.ROUNDED_DOTTED

                    self.draw_wire(rel_start, rel_end, charset, [node.rect, output.target.node.rect], output.data_type.color, dimmed, selected)

        # Draw nodes.
        for node in self.nodes:
            string_object, rect = self.drawable_node(node)

            x = rect.pos.x - camera_rect.pos.x
            y = rect.pos.y - camera_rect.pos.y
            
            for char, (c_x, c_y) in string_object.stream_positioned_chars(x, y):
                if self.work_rect().contains_point(c_x, c_y):
                    terminal.set_cursor_pos(c_x, c_y)
                    print(char)

    def run_program(self) -> None:
        if not nodes.builtin.START_FACTORY.instances:
            return status_bar.error(f"Missing {style.node(nodes.builtin.START_FACTORY)} node!")

        for node in self.nodes:
            for input_source in node.inputs:
                if input_source.required:
                    if input_source.constant_value is None and input_source.source is None:
                        self.camera_x, self.camera_y = node.position.x, node.position.y
                        self.render()
                        return status_bar.error(f"Undefined required value: {style.source(input_source)}")

        start_node = nodes.builtin.START_FACTORY.instances[0]
        run.NodeRunner(start_node, self.nodes).run()

    def export_state(self) -> None:
        path = self.prompt("Export path", "")
        if path is None:
            return
        
        format.LimbFormat.export(self.nodes, path)

    def import_state(self) -> None:
        path = self.prompt("Import path", "")
        if path is None:
            return
        
        self.remove_node()
        for node in self.nodes:
            self.selection.node = node
            self.remove_node()
            
        self.selection.node = None
        self.selection.source = None
        self.selection.highlighted_source = None
        self.edit_node_mode = False
            
        imported_nodes = format.LimbFormat.import_state(path)
        if imported_nodes is None:
            return
        
        for node in imported_nodes:
            self.add_node(node)
            