from modules.status_bar import status_bar
from modules.side_bar import side_bar
from modules import viewport
from modules import terminal
from modules import style
from modules import chars
from modules import nodes
from modules import ui

import keyboard
import time

terminal.hide_cursor()


vp = viewport.ViewportComponent()
start_node = nodes.builtin.START_FACTORY.build_instance()
vp.add_node(start_node)
vp.start_draw()
ui.render_all()

STD_KEYS = {
    chars.ALL_ARROWS: "shift focus",
    f"ctrl+{chars.ALL_ARROWS[0]}": "move camera",
    f"alt+{chars.ALL_ARROWS[0]}": "move node",
    "enter": "edit node",
    "tab": "nodes",
    "F1": "run"
}
status_bar.keys_help("", STD_KEYS)


while 1:
    time.sleep(0.08)
    
    if not terminal.is_active_window():
        continue

    # Sidebar.
    if keyboard.is_pressed("ctrl+b"):
        side_bar.unfocus()
        side_bar.flip()

    if side_bar.is_focused:
        if keyboard.is_pressed("tab") or keyboard.is_pressed("esc"):
            side_bar.unfocus()
            status_bar.keys_help("", STD_KEYS)

        if keyboard.is_pressed("down"):
            side_bar.move_focus_down()
            
        if keyboard.is_pressed("up"):
            side_bar.move_focus_up()
            
        if keyboard.is_pressed("right"):
            side_bar.unfold_collection()
            
        if keyboard.is_pressed("left"):
            side_bar.fold_collection()
            
        if keyboard.is_pressed("enter"):
            if not side_bar.in_factories_level:
                side_bar.flip_collection_fold()
            
            else:
                node = side_bar.spawn_node()
                if node is not None:
                    vp.add_node(node)
                    status_bar.set_message(f"Spawned new node: {style.node(node)}")

                    side_bar.unfocus()
                    vp.select_node(node)
            
        if keyboard.is_pressed("space"):
            node = side_bar.spawn_node()
            if node is not None:
                vp.add_node(node)
                status_bar.set_message(f"Spawned new node: {style.node(node)}")

                side_bar.unfocus()
                vp.select_node(node)
                

    elif not vp.edit_node_mode:
        # Camera movement.
        if keyboard.is_pressed("ctrl"):
            if keyboard.is_pressed("ctrl+left"):
                vp.camera_x += 2
                vp.render()
                                
            if keyboard.is_pressed("ctrl+right"):
                vp.camera_x -= 2
                vp.render()
                
            if keyboard.is_pressed("ctrl+down"):
                vp.camera_y -= 1
                vp.render()
                
            if keyboard.is_pressed("ctrl+up"):
                vp.camera_y += 1
                vp.render()
        
        # Node movement.
        elif keyboard.is_pressed("alt"):
            if keyboard.is_pressed("alt+right"):
                vp.move_node_right()
                
            if keyboard.is_pressed("alt+left"):
                vp.move_node_left()
                
            if keyboard.is_pressed("alt+up"):
                vp.move_node_up()
                
            if keyboard.is_pressed("alt+down"):
                vp.move_node_down()
        
        # Focus shifting.
        else:
            if keyboard.is_pressed("right"):
                vp.shift_focus_right()
                
            if keyboard.is_pressed("left"):
                vp.shift_focus_left()
                
            if keyboard.is_pressed("up"):
                vp.shift_focus_up()
                
            if keyboard.is_pressed("down"):
                vp.shift_focus_down()
        
        # Manage nodes.
        if keyboard.is_pressed("backspace") or keyboard.is_pressed("del"):
            vp.remove_node()
            
        if keyboard.is_pressed("enter"):
            if vp.selected_node is not None:
                vp.edit_node_mode = True
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

        if keyboard.is_pressed("esc"):
            vp.unselect_source()

        # Side bar.
        if keyboard.is_pressed("tab"):
            side_bar.focus()
            side_bar_help = {
                chars.ALL_ARROWS[:2]: "navigate",
                chars.ALL_ARROWS[2:] + "/enter": "(un)fold collection",
                "space/enter": "spawn node",
                "esc/tab": "exit"
            }
            
            status_bar.keys_help("NODES", side_bar_help)

        # Run program.
        if keyboard.is_pressed("f1"):
            vp.run_program()

    elif vp.edit_node_mode:
        
        # Exit edit mode.
        if keyboard.is_pressed("esc"):
            vp.edit_node_mode = False
            status_bar.keys_help("", STD_KEYS)
            
        # Shift focused source.
        if keyboard.is_pressed("right") or keyboard.is_pressed("down"):
            vp.select_next_node_source()
            
        if keyboard.is_pressed("left") or keyboard.is_pressed("up"):
            vp.select_prev_node_source()
            
        # Remove wire.
        if keyboard.is_pressed("backspace") or keyboard.is_pressed("del"):
            vp.disconnect_source()
        
        # Connect wire.
        if keyboard.is_pressed("space"):
            vp.connect_source()
        
        # Edit constant.
        if keyboard.is_pressed("c"):
            vp.edit_constant()
      
            