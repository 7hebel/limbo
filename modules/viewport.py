from modules.status_bar import status_bar
from modules.execution import interpreter
from modules.execution import compiler
from modules.side_bar import side_bar
from modules.nodes.node import Node
from modules import wire_builder
from modules.nodes import source
from modules import user_input
from modules import workspace
from modules import std_nodes
from modules import terminal
from modules import measure
from modules import helpers
from modules import string
from modules import format
from modules import chars
from modules import style
from modules import types
from modules import ui

import os


class ViewportComponent(ui.TextUIComponent):
    def __init__(self, scope: workspace.Workspace) -> None:
        self.optimized_renderer = ui.OptimizedRenderer(self)
        self.scope = scope.initialize(self)
        super().__init__()

    def get_rect(self) -> measure.Rect:
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

        return measure.Rect(measure.Position(x, y), w, h)

    def work_rect(self) -> measure.Rect:
        """ Returns Rect from the inside of the viewport border. """
        rect = self.get_rect()
        return measure.Rect(measure.Position(rect.pos.x + 1, rect.pos.y + 2), rect.w - 1, rect.h - 2)

    def get_cameraview_rect(self) -> measure.Rect:
        vp_rect = self.work_rect()
        view_w = vp_rect.w + vp_rect.pos.x
        view_h = vp_rect.h + vp_rect.pos.y

        start_render_pos = measure.Position(self.scope.camera.x - (view_w // 2), self.scope.camera.y - (view_h // 2))
        return measure.Rect(start_render_pos, view_w, view_h)

    def get_border_connections(self) -> style.BorderConnection:
        return style.BorderConnection(s=status_bar.get_rect() is not None)

    def drawable_node(self, node: Node) -> tuple[string.ColoredStringObject, measure.Rect]:
        """ Returns drawable representation of node, and it's rect. """
        w, h = node.calc_output_size()
        rect = measure.Rect(node.position, w, h)

        outline_color = node.color if node == self.scope.selection.node else style.AnsiFGColor.LIGHTBLACK

        builder = string.ColoredStringObject()
        builder.feed_string(chars.ROUNDED_LINE.nw + (chars.ROUNDED_LINE.hz * (w - 2)) + chars.ROUNDED_LINE.ne, outline_color)
        builder.break_line()

        flow_in_char = chars.DOUBLE_LINE.vl if node.flow.enable_input else chars.ROUNDED_LINE.vt
        flow_out_char = chars.DOUBLE_LINE.vr if node.flow.enable_output else chars.ROUNDED_LINE.vt

        if self.scope.edit_node_mode and node == self.scope.selection.node:
            if self.scope.selection.highlighted_source == node.flow.input_src:
                builder.feed_char(flow_in_char, style.AnsiFGColor.WHITE, styles=[style.AnsiStyle.BLINK, style.AnsiStyle.INVERT])
            else:
                builder.feed_char(flow_in_char, outline_color)
        else:
            if node.flow.enable_input and self.scope.selection.src == node.flow.input_src:
                builder.feed_char(flow_in_char, style.AnsiFGColor.WHITE, styles=[style.AnsiStyle.INVERT, style.AnsiStyle.UNDERLINE])
            else:
                builder.feed_char(flow_in_char, outline_color)

        title_line = f"{node.title}".center(w - 2)
        builder.feed_string(title_line, node.color or None, styles=[style.AnsiStyle.INVERT, style.AnsiStyle.ITALIC] if node == self.scope.selection.node and self.scope.edit_node_mode else [])

        if self.scope.edit_node_mode and node == self.scope.selection.node:
            if self.scope.selection.highlighted_source == node.flow.output_src:
                builder.feed_char(flow_out_char, style.AnsiFGColor.WHITE, styles=[style.AnsiStyle.BLINK, style.AnsiStyle.INVERT])
            else:
                builder.feed_char(flow_out_char, outline_color)
        else:
            if node.flow.enable_output and self.scope.selection.src == node.flow.output_src:
                builder.feed_char(flow_out_char, style.AnsiFGColor.WHITE, styles=[style.AnsiStyle.INVERT, style.AnsiStyle.UNDERLINE])
            else:
                builder.feed_char(flow_out_char, outline_color)

        builder.break_line()

        if not node.has_any_body_sources():
            builder.feed_string(chars.ROUNDED_LINE.sw + (chars.ROUNDED_LINE.hz * (w - 2)) + chars.ROUNDED_LINE.se, outline_color)
            return (builder, rect)

        builder.feed_string(chars.ROUNDED_LINE.vr + (chars.ROUNDED_LINE.hz * (w - 2)) + chars.ROUNDED_LINE.vl, outline_color)
        builder.break_line()

        for src in helpers.iter_alternately(node.inputs, node.outputs):
            src: source.NodeInput | source.NodeOutput

            is_selected_node = self.scope.edit_node_mode and self.scope.selection.highlighted_source == src
            is_selected_source = src == self.scope.selection.src

            styles = [style.AnsiStyle.ITALIC]
            if is_selected_node:
                styles.append(style.AnsiStyle.INVERT)
            if is_selected_source:
                styles.append(style.AnsiStyle.UNDERLINE)

            if src in node.inputs:
                builder.feed_char(src.icon, src.data_type.color)

                color = None if src.required else style.AnsiFGColor.LIGHTBLACK

                builder.feed_char(" ")
                builder.feed_string(src.name, color, styles)
                builder.feed_string("".ljust(w - len(src.name) - 3))

                builder.feed_char(chars.ROUNDED_LINE.vt, outline_color)
                builder.break_line()

            if src in node.outputs:
                builder.feed_char(chars.ROUNDED_LINE.vt, outline_color)
                builder.feed_string("".rjust(w - 3 - len(src.name)))
                builder.feed_string(f"{src.name}", styles=styles)
                builder.feed_char(" ")
                builder.feed_char(src.icon, src.data_type.color)
                builder.break_line()

        builder.feed_string(chars.ROUNDED_LINE.sw + (chars.ROUNDED_LINE.hz * (w - 2)) + chars.ROUNDED_LINE.se, outline_color)
        return (builder, rect)

    def draw_wire(self,
                  rel_from: tuple[int, int],
                  rel_to: tuple[int, int],
                  charset: chars.LineChars,
                  avoid_rects: list[measure.Rect],
                  color: style.AnsiFGColor,
                  dimmed: bool,
                  highlight: bool
                  ) -> dict[tuple[int, int], str]:
        camera_rect = self.get_cameraview_rect()
        work_rect = self.work_rect()
        pos_chars = {}

        start_pos = (rel_from[0] - camera_rect.pos.x, rel_from[1] - camera_rect.pos.y)
        end_pos = (rel_to[0] - camera_rect.pos.x, rel_to[1] - camera_rect.pos.y)

        builder = wire_builder.WireBuilder(start_pos, end_pos, charset, avoid_rects, camera_rect)
        for pos, char in builder.positioned_chars.items():
            if not work_rect.contains_point(pos[0], pos[1]):
                continue

            styles = []

            if highlight:
                styles.append(style.AnsiStyle.BOLD)
                styles.append(style.AnsiStyle.BLINK)

            if dimmed:
                styles.append(style.AnsiStyle.DIM)

            char = style.tcolor(char, color, styles=styles)
            pos_chars[pos] = char

        return pos_chars

    def prompt(self, text: str, placeholder: str = "") -> str | None:
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

    def render(self, force: bool = False, skip_cam_check: bool = False):
        if ui.SCREEN_BUSY:
            return
        
        # Check if selected node is within camera.
        selected_node = self.scope.selection.node
        if selected_node is not None and not skip_cam_check:
            node_rect = selected_node.rect

            if not node_rect.fully_within(self.get_cameraview_rect()):
                new_cam_pos = measure.Position(node_rect.pos.x - 2, node_rect.pos.y - 2)
                self.scope.camera.set_pos(new_cam_pos)
        
        camera_rect = self.get_cameraview_rect()
        work_rect = self.work_rect()
        vp_rect = self.get_rect()

        # Workspace name.
        title, title_length = self.scope.renderable_title()
        
        if title_length > 0 and title_length < vp_rect.w - 2:
            center_x = vp_rect.pos.x + (vp_rect.w // 2) - (title_length // 2)
            terminal.write_at(title, center_x, 0)

        if not self.scope.nodes:
            return self.clean_contents()

        # Draw data wires.
        for node in self.scope.nodes:
            for output in node.outputs + [node.flow.output_src]:
                if output is None or output.target is None:
                    continue
                
                rel_start = output.rel_pos
                rel_end = output.target_rel_pos

                dimmed = not (node == self.scope.selection.node or output.target.node == self.scope.selection.node)
                selected = self.scope.edit_node_mode and self.scope.selection.highlighted_source in (output, output.target)
                charset = chars.DOUBLE_LINE if output.data_type == types.FLOW else chars.ROUNDED_LINE if not selected else chars.ROUNDED_DOTTED

                wire_chars = self.draw_wire(rel_start, rel_end, charset, [node.rect, output.target.node.rect], output.data_type.color, dimmed, selected)
                self.optimized_renderer.feed_buffer(wire_chars)

        # Draw nodes.
        for node in self.scope.nodes:
            string_object, rect = self.drawable_node(node)

            x = rect.pos.x - camera_rect.pos.x
            y = rect.pos.y - camera_rect.pos.y
            
            for pos, char in string_object.stream_positioned_chars(x, y):
                if work_rect.contains_point(pos[0], pos[1]):
                    self.optimized_renderer.feed_buffer({pos: char})

        if force:
            self.optimized_renderer.force_render()
        else:
            self.optimized_renderer.diff_render()

    def import_state(self, path: str | None = None) -> bool | None:
        if path is None:
            path = self.prompt("Import path", "")
        
        if path is None:
            return
        
        if not os.path.exists(path) or not os.path.isfile(path):
            return status_bar.error(f"Couldn't import state from file: {path} (file not found)")
        
        ui.SCREEN_BUSY = True
        
        new_scope = workspace.Workspace("").initialize(self)
        side_bar.set_workspace_id(new_scope.id)
        imported_nodes, cam_pos = format.LimbFormat.import_state(path, new_scope.id)
        
        if imported_nodes is None:
            ui.SCREEN_BUSY = False
            side_bar.set_workspace_id(self.scope.id)
            return ui.render_all()
        
        cam_x, cam_y = cam_pos
        self.scope = new_scope
        self.scope.camera.set_pos(measure.Position(cam_x, cam_y))
        
        for node in imported_nodes:
            self.scope.add_node(node)

        ui.SCREEN_BUSY = False
        self.scope.associate_file(path)
        self.render()
        return True
        
    def prerun_check(self) -> bool:
        """ Check for missing nodes, undefined values before start. Returns if can start. """
        if not std_nodes.START_FACTORY.instances[self.scope.id]:
            status_bar.error(f"Missing {style.node(std_nodes.START_FACTORY)} node!")
            return False

        for node in self.scope.nodes:
            for input_source in node.inputs:
                if input_source.required and input_source.constant_value is None and input_source.source is None:
                    self.scope.camera.set_pos(node.position)
                    self.scope.selection.node = node
                    self.render()
                    
                    status_bar.error(f"Undefined required value: {style.source(input_source)}")
                    return False
                
        return True
        
    def run_program(self, debug: bool = False) -> None:
        if not self.prerun_check():
            return

        terminal.clear_screen()
        start_node = std_nodes.START_FACTORY.instances[self.scope.id][0]
        interpreter.NodeRunner(start_node, self.scope.nodes, debug).run()

    def compile_program(self) -> None:
        if not self.prerun_check():
            return
        
        name = self.scope.name

        if not name:
            name = self.prompt("Name")
        
        if name is None:
            return
        
        start_node = std_nodes.START_FACTORY.instances[self.scope.id][0]
        compiler.Compiler(name, start_node, self.scope.nodes)
        ui.render_all()
