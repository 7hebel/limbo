from modules.status_bar import status_bar
from modules.side_bar import side_bar
from modules import user_input
from modules import terminal
from modules import string
from modules import vp_ext
from modules import chars
from modules import style
from modules import nodes
from modules import types
from modules import wire
from modules import pos
from modules import run
from modules import ui


FLOW_CTRL_IN = 0
FLOW_CTRL_OUT = 1


def get_selectable_flow_controls(node: nodes.Node) -> list[int]:
    flows_ctrls = []
    if node.flow.enable_input:
        flows_ctrls.append(FLOW_CTRL_IN)
    if node.flow.enable_output:
        flows_ctrls.append(FLOW_CTRL_OUT)
        
    return flows_ctrls


def first_node_source(node: nodes.Node) -> nodes.NodeInput | nodes.NodeOutput | None:
    if node.inputs:
        return node.inputs[0]

    if node.outputs:
        return node.outputs[0]
    
    flow_controls = get_selectable_flow_controls(node)
    if flow_controls:
        return flow_controls[0]


def out(content: str) -> None:
    print(content, end="", flush=True)


class ViewportComponent(ui.TextUIComponent, vp_ext.ShiftableFocus, vp_ext.MovableNodes):
    def __init__(self) -> None:
        self.camera_x, self.camera_y = 0, 0
        self.nodes: list["nodes.Node"] = []
        self.charset = chars.ROUNDED_LINE
        self.selected_node: "nodes.Node | None" = None
        self.__enable_rendering = False

        self.__edit_node_mode = False
        self.__edit_node_source_pointer: nodes.NodeInput | nodes.NodeOutput | None = None
        self.__selected_source: nodes.NodeInput | nodes.NodeOutput | None = None

        super().__init__()

    @property
    def edit_node_mode(self) -> bool:
        return self.__edit_node_mode

    @edit_node_mode.setter
    def edit_node_mode(self, state: bool) -> None:
        if state:
            self.__edit_node_source_pointer = first_node_source(self.selected_node)

            # Flow control connection.
            if isinstance(self.__selected_source, tuple):
                n1_type, n1 = self.__selected_source
                n2 = self.selected_node
                
                if n1_type == FLOW_CTRL_OUT:
                    n1.connect_flow_target(n2)
                else:
                    n2.connect_flow_target(n1)
                    
                self.__selected_source = None
                status_bar.set_message(f"Connected {style.node(n1)} with {style.node(n2)} with flow wire.")
                return self.render()
            
            # Flow control output to node connection.
            if isinstance(self.__selected_source, nodes.NodeOutput):
                if self.__selected_source.data_type == types.FLOW:
                    flow_out = self.__selected_source
                    flow_in = self.selected_node
                    
                    flow_out.connect_flow_target(flow_in)
                    self.__selected_source = None
                    return self.render()
            
        else:
            self.__edit_node_source_pointer = None

        self.__edit_node_mode = state
        self.render()

    @property
    def work_rect(self) -> pos.Rect:
        """ Return terminal work area for this Viewport. """
        x, y = 1, 2
        w, h = terminal.get_w() - 1, terminal.get_h() - 2
        
        if not side_bar.is_folded:
            x += side_bar.width
            w -= side_bar.width
        
        if self.get_border_connections().s:
            h += 1
        
        if status_bar.get_rect() is not None:
            h -= (status_bar.msg_height + status_bar.BASE_HEIGHT)
        
        return pos.Rect(pos.Position(x, y), w, h)
    
    def get_rect(self) -> pos.Rect:
        """ Return terminal total Viewport rect. """
        x, y = 0, 0
        w, h = terminal.get_w(), terminal.get_h()
        
        if not side_bar.is_folded:
            x += side_bar.width
            w -= side_bar.width
        else:
            x += 1
            w -= 1
        
        if status_bar.get_rect() is not None:
            h -= (status_bar.msg_height + status_bar.BASE_HEIGHT)
        
        if self.get_border_connections().s:
            h += 1
        
        
        return pos.Rect(pos.Position(x, y), w, h)
    
    def get_border_connections(self) -> style.BorderConnection:
        south = status_bar.get_rect() is not None
        
        return style.BorderConnection(
            s = south
        )
        
    def select_next_node_source(self) -> None:
        if not self.edit_node_mode or self.selected_node is None:
            return

        flows_ctrls = get_selectable_flow_controls(self.selected_node)
        all_sources = flows_ctrls + list(pos.iter_alternately(self.selected_node.inputs, self.selected_node.outputs))
        current_index = all_sources.index(self.__edit_node_source_pointer)
        next_index = current_index + 1

        if next_index > len(all_sources) - 1:
            next_index = 0

        self.__edit_node_source_pointer = all_sources[next_index]
        self.render()

    def select_prev_node_source(self) -> None:
        if not self.edit_node_mode or self.selected_node is None:
            return

        flows_ctrls = get_selectable_flow_controls(self.selected_node)
        all_sources = flows_ctrls + list(pos.iter_alternately(self.selected_node.inputs, self.selected_node.outputs))
        current_index = all_sources.index(self.__edit_node_source_pointer)
        next_index = current_index - 1

        if next_index == -1:
            next_index = len(all_sources) - 1

        self.__edit_node_source_pointer = all_sources[next_index]
        self.render()

    def disconnect_source(self) -> None:
        if not self.edit_node_mode or self.selected_node is None or self.__edit_node_source_pointer is None:
            return

        if self.__edit_node_source_pointer == FLOW_CTRL_IN:
            if self.selected_node.flow.input_source:
                self.selected_node.flow.input_source.flow.output_target = None
            self.selected_node.flow.input_source = None
            return self.render()
            
        if self.__edit_node_source_pointer == FLOW_CTRL_OUT:
            if self.selected_node.flow.output_target:
                self.selected_node.flow.output_target.flow.input_source = None
            self.selected_node.flow.output_target = None

            return self.render()            
        
        self.__edit_node_source_pointer.disconnect()
        self.render()

    def connect_source(self) -> None:
        if not self.edit_node_mode or self.selected_node is None:
            return

        if self.__selected_source is None:
            if self.__edit_node_source_pointer in (FLOW_CTRL_IN, FLOW_CTRL_OUT):
                self.__edit_node_source_pointer = (self.__edit_node_source_pointer, self.selected_node)
                status_bar.set_message(f"Select target node for {style.node(self.selected_node)}")
            else:
                status_bar.set_message(f"Select target source for {style.source(self.__edit_node_source_pointer)}")
            
            self.__selected_source = self.__edit_node_source_pointer
            self.edit_node_mode = False
            return self.render()

        nodes.connect_sources(self.__edit_node_source_pointer, self.__selected_source)
        self.__selected_source = None
        self.render()

    def unselect_source(self) -> None:
        if self.__selected_source:
            self.__selected_source = None
            self.render()

    def get_cameraview_rect(self) -> pos.Rect:
        vp_rect = self.work_rect
        view_w = vp_rect.w + vp_rect.pos.x
        view_h = vp_rect.h + vp_rect.pos.y

        start_render_pos = pos.Position(self.camera_x - (view_w // 2), self.camera_y - (view_h // 2))
        return pos.Rect(start_render_pos, view_w, view_h)

    def drawable_node(self, node: "nodes.Node") -> tuple[string.ColoredStringObject, pos.Rect]:
        """ Returns drawable representation of node, and it's size (w, h). """
        w, h = node.calc_output_size()

        outline_color = node.color if node == self.selected_node else style.AnsiFGColor.LIGHTBLACK

        builder = string.ColoredStringObject()
        builder.feed_string(self.charset.nw + (self.charset.hz * (w - 2)) + self.charset.ne, outline_color)
        builder.break_line()

        flow_in_char = chars.DOUBLE_LINE.vl if node.flow.enable_input else self.charset.vt
        flow_out_char = chars.DOUBLE_LINE.vr if node.flow.enable_output else self.charset.vt
        
        if self.edit_node_mode and node == self.selected_node:
            if self.__edit_node_source_pointer == FLOW_CTRL_IN:
                builder.feed_char(flow_in_char, style.AnsiFGColor.RED, styles=[style.AnsiStyle.BLINK, style.AnsiStyle.INVERT])
            else:
                builder.feed_char(flow_in_char, outline_color)
        else:
            builder.feed_char(flow_in_char, outline_color)

        title_line = f"{node.title}".center(w - 2)
        builder.feed_string(title_line, node.color or None, styles=[style.AnsiStyle.BLINK, style.AnsiStyle.INVERT] if node == self.selected_node and self.edit_node_mode else [])
        
        if self.edit_node_mode and node == self.selected_node:
            if self.__edit_node_source_pointer == FLOW_CTRL_OUT:
                builder.feed_char(flow_out_char, style.AnsiFGColor.RED, styles=[style.AnsiStyle.BLINK, style.AnsiStyle.INVERT])
            else:
                builder.feed_char(flow_out_char, outline_color)
        else:
            builder.feed_char(flow_out_char, outline_color)
                
        builder.break_line()

        builder.feed_string(self.charset.vr + (self.charset.hz * (w - 2)) + self.charset.vl, outline_color)
        builder.break_line()

        for source in pos.iter_alternately(node.inputs, node.outputs):
            source: "nodes.NodeInput | nodes.NodeOutput"

            is_selected_node = self.edit_node_mode and self.__edit_node_source_pointer == source
            is_selected_source = source == self.__selected_source

            styles = [style.AnsiStyle.ITALIC]
            if is_selected_node:
                styles.append(style.AnsiStyle.INVERT)
            if is_selected_source:
                styles.append(style.AnsiStyle.UNDERLINE)

            if source in node.inputs:
                builder.feed_char(source.icon, source.data_type.color)

                color = None if source.required else style.AnsiFGColor.LIGHTBLACK

                builder.feed_char(" ")
                
                fill_len = w - len(source.name) - 3
                if source.constant_value is not None:
                    builder.feed_char("*", source.data_type.color)
                    fill_len -= 1
                
                builder.feed_string(source.name, color, styles)
                builder.feed_string("".ljust(fill_len))

                builder.feed_char(self.charset.vt, outline_color)
                builder.break_line()

            if source in node.outputs:
                builder.feed_char(self.charset.vt, outline_color)
                builder.feed_string("".rjust(w - 3 - len(source.name)))
                builder.feed_string(f"{source.name}", styles=styles)
                builder.feed_char(" ")
                builder.feed_char(source.icon, source.data_type.color)
                builder.break_line()

        builder.feed_string(self.charset.sw + (self.charset.hz * (w - 2)) + self.charset.se, outline_color)

        rect = pos.Rect(node.position, w, h)
        return (builder, rect)

    def add_node(self, node: "nodes.Node", position: pos.Position = None) -> None:
        if position is None:
            position = pos.Position(self.camera_x, self.camera_y)

        node.position = position
        self.nodes.append(node)
        self.select_node(node)

        # check if interssects
        for other_node in self.nodes:
            if other_node == node:
                continue

            if other_node.rect.intersects(node.rect):
                self.move_node_right()
                break

        self.render()

    def remove_node(self) -> None:
        """ Remove selected node. Disconnect all wires. """
        node = self.selected_node
        if node is None:
            return

        self.selected_node = None

        node.unlink()
        self.nodes.remove(node)
        self.select_node(self.nodes[0] if self.nodes else None)
        self.render()
        return status_bar.set_message(f"Removed {style.node(node)}")

    def select_node(self, node: "nodes.Node | None") -> None:
        self.selected_node = node
        self.render()

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

        wire_builder = wire.WireBuilder(start_pos, end_pos, charset, avoid_rects, camera_rect)
        for (x, y), char in wire_builder.positioned_chars.items():
            if not self.work_rect.contains_point(x, y):
                continue

            styles = []

            if highlight:
                styles.append(style.AnsiStyle.BOLD)
                styles.append(style.AnsiStyle.BLINK)

            if dimmed:
                styles.append(style.AnsiStyle.DIM)

            char = style.tcolor(char, color, styles=styles)

            terminal.set_cursor_pos(x, y)
            out(char)

    def start_draw(self):
        self.__enable_rendering = True
        self.render()

    def prompt(self, text: str, placeholder: str) -> str | None:
        rect = self.get_rect()
        y = rect.pos.y + rect.h - 1
        prompt_x = rect.pos.x + 1
        x_end = rect.pos.x + rect.w - 1
        
        terminal.set_cursor_pos(prompt_x, y)
        out(text)
        out(style.tcolor(": ", style.AnsiFGColor.CYAN))
        
        x_start = prompt_x + style.real_length(text) + 2
        
        terminal.set_cursor_pos(x_start, y)
        value = user_input.get_input("", x_end - x_start + 1, True, placeholder)
        ui.render_all()
        
        if value is None:
            status_bar.set_message("Prompt has been manually canceled...")
            return
        
        return value

    def edit_constant(self) -> None:
        if self.__edit_node_source_pointer:
            if isinstance(self.__edit_node_source_pointer, nodes.NodeOutput):
                return status_bar.error(f"Cannot set constant value to the output source: {style.source(self.__edit_node_source_pointer)}")
            
            edit_help = {
                "esc": "Remove constant.",
                "enter": "Accept constant."
            }
            status_bar.keys_help("Edit constant.", edit_help)
            
            current_value = self.__edit_node_source_pointer.constant_value or ""
            value = self.prompt(style.source(self.__edit_node_source_pointer), current_value)
            self.__edit_node_source_pointer.set_constant(value)

    def render(self):
        if not self.__enable_rendering:
            return

        self.clean_contents()
        camera_rect = self.get_cameraview_rect()

        for node in self.nodes:
            # Draw data wires.
            for output in node.outputs:
                if output.target:
                    rel_start = output.rel_pos
                    rel_end = output.target_rel_pos

                    dimmed = not (node == self.selected_node or output.target.node == self.selected_node)
                    selected = self.edit_node_mode and self.__edit_node_source_pointer in (output, output.target)
                    charset = chars.DOUBLE_LINE if output.data_type == types.FLOW else self.charset if not selected else chars.ROUNDED_DOTTED

                    self.draw_wire(rel_start, rel_end, charset, [node.rect, output.target.node.rect], output.data_type.color, dimmed, selected)

            # Draw flow wires.
            if node.flow.output_target is not None:
                rel_start = node.rel_flow_output_pos
                rel_end = node.flow.output_target.rel_flow_input_pos
                
                dimmed = not (node == self.selected_node or node.flow.output_target == self.selected_node)
                selected = False
                if self.edit_node_mode:
                    if self.__edit_node_source_pointer == FLOW_CTRL_OUT and node == self.selected_node:
                        selected = True
                        
                    if self.__edit_node_source_pointer == FLOW_CTRL_IN:
                        if node.flow.output_target == self.selected_node:
                            selected = True
                
                charset = chars.DOUBLE_LINE
                self.draw_wire(rel_start, rel_end, charset, [node.rect, node.flow.output_target.rect], style.FLOW_CONTROL_COLOR, dimmed, selected)

        # Draw nodes.
        for node in self.nodes:
            string_object, rect = self.drawable_node(node)

            x = -camera_rect.pos.x + rect.pos.x
            y = -camera_rect.pos.y + rect.pos.y
            
            for char, (c_x, c_y) in string_object.stream_positioned_chars(x, y):
                if self.work_rect.contains_point(c_x, c_y):
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

