from modules.execution.exit_codes import ExitCode
from modules.execution import runtime
from modules.nodes import node
from modules import terminal
from modules import helpers
from modules import style
from modules import ui

import time

                
class NodeRunner:
    MAX_RUN_COUNT = 100
    run_count = 0

    def __init__(self, start_node: node.Node, raw_nodes: list[node.Node]) -> None:
        self.start_node = start_node
        self.raw_nodes = raw_nodes
        
        self.runtime_nodes: dict[int, runtime.RuntimeNode] = {}
        self.start_time = time.time_ns()
        self.initialize_nodes(start_node, raw_nodes)
        helpers.MemoryJar.new_jar()

    def initialize_nodes(self, start_node: node.Node, raw_nodes: list[node.Node]) -> None:
        for raw_node in raw_nodes:
            rt_node = runtime.RuntimeNode(raw_node)
            self.runtime_nodes[raw_node.node_id] = rt_node

        for rt_node in self.runtime_nodes.values():
            rt_node.initialize(self.runtime_nodes)

        self.entry_node = self.runtime_nodes[start_node.node_id]

    def reset_values(self) -> None:
        for rt_node in self.runtime_nodes.values():
            rt_node.output_values = None

    def run(self):
        NodeRunner.run_count += 1
        if NodeRunner.run_count > NodeRunner.MAX_RUN_COUNT:
            self.error_dump(None, f"Program has been restarted over {NodeRunner.MAX_RUN_COUNT} times. Automatically terminated infinite loop.")
            return self.finish(ExitCode.INF_RECURSION)

        node = self.entry_node

        while node:
            try:
                node.execute()

            except EOFError as exit_code:
                exit_code = int(str(exit_code))

                if exit_code == ExitCode.RESTART:
                    helpers.MemoryJar.new_jar()
                    self.reset_values()
                    return self.run()
                
                if exit_code == ExitCode.RESTART_SAVE_MEMORY:
                    self.reset_values()
                    return self.run()
                
                return self.finish(exit_code)

            except RuntimeError as error:
                self.error_dump(node, error)
                return self.finish(ExitCode.ERROR)

            except RecursionError:
                self.error_dump(node, "Infinite recurrsion occured.")
                return self.finish(ExitCode.INF_RECURSION)

            except KeyboardInterrupt:
                self.error_dump(node, "Execution manually terminated.")
                return self.finish(ExitCode.MANUAL_TERMINATION)

            node = node.flow_next
            if node is None:
                return self.finish(ExitCode.OK)

    def finish(self, exit_code: int) -> int:
        NodeRunner.run_count = 0
        helpers.MemoryJar.current = None

        total_time_s = (time.time_ns() - self.start_time) / 1e9
        time_info = style.tcolor(str(total_time_s) + "s", style.AnsiFGColor.CYAN)
        exit_info = style.tcolor(str(exit_code), style.AnsiFGColor.RED if exit_code < 0 else style.AnsiFGColor.CYAN)

        print(f"\n{style.ITALIC}Program finished execution in {style.RESET}{time_info} {style.ITALIC}with exit code {style.RESET}{exit_info}")
        print(f"{style.key('enter')} to continue...")
        terminal.wait_for_enter()

        ui.render_all()
        return exit_code

    def error_dump(self, node: runtime.RuntimeNode | None, error: RuntimeError | str) -> None:
        content = style.tcolor("\n ERROR ", color=style.AnsiFGColor.WHITE, bg_color=style.AnsiBGColor.RED)

        if node is None:
            content += f" Execution failed!"
        else:
            content += f" Execution of node: {style.node(node.node_model)} failed!"

        print(content)
        print("\n    " + str(error))
