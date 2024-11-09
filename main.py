from modules.status_bar import status_bar
from modules.side_bar import side_bar
from modules import std_nodes
from modules import workspace
from modules import viewport
from modules import terminal
from modules import helpers
from modules import measure
from modules import style
from modules import ui

import traceback
import keyboard
import time
import sys
    
    
terminal.hide_cursor()

default_workspace = workspace.Workspace("")
VIEWPORT = viewport.ViewportComponent(default_workspace)
side_bar.set_workspace_id(default_workspace.id)

# Import state file.
if len(sys.argv) > 1:
    VIEWPORT.import_state(sys.argv[1])
    
else:
    default_workspace.add_node(std_nodes.START_FACTORY.build_instance(default_workspace.id))


def main() -> None:    
    ui.render_all()

    status_bar.standard_keys_help()

    while 1:
        time.sleep(0.08)
        
        if not terminal.is_active_window():
            continue

        # Export state.
        if keyboard.is_pressed("ctrl+e"):
            VIEWPORT.scope.export_state()

        # Import state.
        if keyboard.is_pressed("ctrl+i"):
            VIEWPORT.import_state()

        # Close workspace.
        if keyboard.is_pressed("ctrl+w"):
            VIEWPORT.scope = workspace.Workspace("").initialize(VIEWPORT)
            side_bar.set_workspace_id(VIEWPORT.scope.id)
            ui.render_all()

        # Sidebar.
        if keyboard.is_pressed("ctrl+b"):
            side_bar.unfocus()
            side_bar.flip()

        if side_bar.is_focused:
            if keyboard.is_pressed("tab") or keyboard.is_pressed("esc"):
                side_bar.unfocus()
                status_bar.standard_keys_help()

            if keyboard.is_pressed("ctrl"):
                if keyboard.is_pressed("down"):
                    side_bar.move_focus_category_down()
                    
                if keyboard.is_pressed("up"):
                    side_bar.move_focus_category_up()

            else:
                if keyboard.is_pressed("down"):
                    side_bar.move_focus_down()
                    
                if keyboard.is_pressed("up"):
                    side_bar.move_focus_up()
                
            if keyboard.is_pressed("right"):
                side_bar.unfold_collection()
                
            if keyboard.is_pressed("left"):
                side_bar.fold_collection()
                
            if keyboard.is_pressed("enter") or keyboard.is_pressed("space"):
                if not side_bar.in_factories_level:
                    side_bar.flip_collection_fold()
                
                else:
                    node = side_bar.spawn_node()
                    if node is not None:
                        VIEWPORT.scope.add_node(node)
                        status_bar.set_message(f"Spawned new node: {style.node(node)}")

                        side_bar.unfocus()
                        VIEWPORT.scope.selection.node = node
                
        elif not VIEWPORT.scope.edit_node_mode:
            # Camera movement.
            if keyboard.is_pressed("ctrl"):
                if keyboard.is_pressed("ctrl+left"):
                    VIEWPORT.scope.camera.move_left()
                    VIEWPORT.render()
                                    
                if keyboard.is_pressed("ctrl+right"):
                    VIEWPORT.scope.camera.move_right()
                    VIEWPORT.render()
                    
                if keyboard.is_pressed("ctrl+down"):
                    VIEWPORT.scope.camera.move_down()
                    VIEWPORT.render()
                    
                if keyboard.is_pressed("ctrl+up"):
                    VIEWPORT.scope.camera.move_up()
                    VIEWPORT.render()
                    
            # Node movement.
            elif keyboard.is_pressed("alt"):
                if keyboard.is_pressed("alt+right"):
                    VIEWPORT.scope.move_node_right()
                    
                if keyboard.is_pressed("alt+left"):
                    VIEWPORT.scope.move_node_left()
                    
                if keyboard.is_pressed("alt+up"):
                    VIEWPORT.scope.move_node_up()
                    
                if keyboard.is_pressed("alt+down"):
                    VIEWPORT.scope.move_node_down()
            
            # Focus shifting.
            else:
                if keyboard.is_pressed("right"):
                    VIEWPORT.scope.shift_focus_right()
                    
                if keyboard.is_pressed("left"):
                    VIEWPORT.scope.shift_focus_left()
                    
                if keyboard.is_pressed("up"):
                    VIEWPORT.scope.shift_focus_up()
                    
                if keyboard.is_pressed("down"):
                    VIEWPORT.scope.shift_focus_down()
            
            # Manage nodes.
            if keyboard.is_pressed("backspace") or keyboard.is_pressed("del"):
                VIEWPORT.scope.remove_node()
                
            if keyboard.is_pressed("enter"):
                if VIEWPORT.scope.selection.node is not None:
                    VIEWPORT.scope.edit_node_mode = True

            if keyboard.is_pressed("esc"):
                if VIEWPORT.scope.selection.src:
                    status_bar.standard_keys_help()
                    VIEWPORT.scope.selection.src = None
                    VIEWPORT.render()
                    
            if keyboard.is_pressed("ctrl+d"):
                VIEWPORT.scope.duplicate_node()

            # Side bar.
            if keyboard.is_pressed("tab"):
                side_bar.focus()
                status_bar.keys_help("NODES", side_bar.help_keys)

            # Run program.
            if keyboard.is_pressed("f1"):
                VIEWPORT.run_program()
                
            # Compile program.
            if keyboard.is_pressed("f2"):
                VIEWPORT.compile_program()
                
            # Debug program.
            if keyboard.is_pressed("f12"):
                VIEWPORT.run_program(debug=True)

        elif VIEWPORT.scope.edit_node_mode:
            
            # Exit edit mode.
            if keyboard.is_pressed("esc"):
                VIEWPORT.scope.edit_node_mode = False
                status_bar.standard_keys_help()
                
            # Side bar.
            if keyboard.is_pressed("tab"):
                VIEWPORT.scope.edit_node_mode = False
                side_bar.focus()
                status_bar.keys_help("NODES", side_bar.help_keys)
                
            # Shift focused source.
            if keyboard.is_pressed("right") or keyboard.is_pressed("down"):
                VIEWPORT.scope.shift_source_selection(measure.VerticalDirection.DOWN)
                
            if keyboard.is_pressed("left") or keyboard.is_pressed("up"):
                VIEWPORT.scope.shift_source_selection(measure.VerticalDirection.UP)
                
            # Remove wire.
            if keyboard.is_pressed("backspace") or keyboard.is_pressed("del"):
                VIEWPORT.scope.disconnect_source()
            
            # Connect wire.
            if keyboard.is_pressed("space"):
                VIEWPORT.scope.choose_source()
            
            # Edit constant.
            if keyboard.is_pressed("c"):
                VIEWPORT.scope.edit_constant()
      

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        terminal.clear_screen()
        helpers.flush_system_keyboard_buffer_win()
        terminal.show_cursor()
        exit(0)
        
    except Exception as internal_error:
        terminal.clear_screen()
        helpers.flush_system_keyboard_buffer_win()
        terminal.show_cursor()
        
        print(style.tcolor(" INTERNAL ERROR! ", color=style.AnsiFGColor.WHITE, bg_color=style.AnsiBGColor.RED))
        traceback.print_exc()
        exit(1)
    