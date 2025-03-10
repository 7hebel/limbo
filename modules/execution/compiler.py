from modules.nodes.node import Node
from modules import terminal
from modules import types
from modules import style
from modules import ui

from typing import Callable
import subprocess
import inspect
import shutil
import time
import ast
import os


def get_python_command():
    commands = ["python3", "py", "py3"]

    for cmd in commands:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return cmd

        except FileNotFoundError:
            continue

    raise EnvironmentError("No suitable Python command found. Ensure Python is installed and accessible.")


def get_function_body(func: Callable) -> str:
    """ Returns function's code as a string. """
    return inspect.getsource(func).split("\n", 1)[1]


def get_input_param_name(func: Callable) -> str | None:
    """ Get function's first argument if any. """
    source = inspect.getsource(func).strip()
    parsed = ast.parse(source)
    body = parsed.body[0]

    args_list = [str(arg.arg) for arg in body.args.args]
    if not args_list:
        return None

    return args_list[0]


SKIP_IMPORTS = [
    "from modules.nodes.source import NodeInput, NodeOutput",
    "from modules.nodes.collection import NodesCollections",
    "from modules.nodes.factory import NodeFactory",
    "from modules.nodes.node import FlowControl",
    "from modules import types"
]

def get_imports(func: Callable) -> set[str]:
    """ Check provided node's handler function module and gather all imports. """

    module_path = func.__module__.replace(".", "/") + ".py"
    import_lines = []

    with open(module_path, "r") as mod_file:
        for line in mod_file.readlines():
            line = line.removesuffix("\n")

            if line.startswith("import") or line.startswith("from") and line not in SKIP_IMPORTS:
                import_lines.append(line)

    return set(import_lines)


class Compiler:
    """ Compile Limbo Nodes into executable. """

    def __init__(self, name: str, start_node: Node, all_nodes: list[Node]) -> None:
        self.name = name.removesuffix(".limb")
        self.start_node = start_node
        self.all_nodes = all_nodes

        ui.SCREEN_BUSY = True

        start_time = time.time_ns()
        terminal.clear_screen()
        print(f"Started compilation process for: {style.highlight(name + ".exe")}")

        self.__compilation_dir_path = "./__compilation/"
        if not os.path.exists(self.__compilation_dir_path):
            os.mkdir(self.__compilation_dir_path)
            
        self.__build_target_path = self.__compilation_dir_path + f"_compile_{name}.py"
        self.__dependecies_imports = set()

        defined_fns = self.define_functions()
        build_target_content = ""
        build_target_content += self.include_dependencies(defined_fns) + "\n"
        build_target_content += defined_fns + "\n"
        build_target_content += self.build_instances_register() + "\n"
        build_target_content += self.set_entry_node() + "\n"
        build_target_content += self.inject_executor()

        if os.path.exists(self.__build_target_path):
            os.remove(self.__build_target_path)

        with open(self.__build_target_path, "a+") as file:
            file.write(build_target_content)

        exe_path = self.compile_to_exe()
        total_time = (time.time_ns() - start_time) / 1e9
        self.cleanup()

        print(f"\n\nCompiled {style.highlight(name)} to: {style.highlight(exe_path)} in {style.highlight(f'{total_time}s')}\n\n")
        print(f"Press {style.key('enter')} to continue...")
        terminal.wait_for_enter()
        
        ui.SCREEN_BUSY = False

    def fn_name(self, node: Node) -> str:
        return f'f_{node.factory.title.replace(" ", "_").replace("-", "_").replace("/", "_")}'

    def define_functions(self) -> str:
        """ Define mapped functions with code from nodes' handlers. Includes FN_REG. """
        print("\nNodes definition:")
        
        defined_factories = []
        fn_reg = "{"
        content = ""

        for node in self.all_nodes:
            if node.factory.factory_id in defined_factories:
                continue

            func_name = self.fn_name(node)
            fn_content = get_function_body(node.handler)
            if not fn_content:
                fn_content = "\treturn None"

            if node.handler.__name__ == "<lambda>":
                input_arg = "*_"
            else:
                input_arg = get_input_param_name(node.handler)
                self.__dependecies_imports = self.__dependecies_imports.union(get_imports(node.handler))

            definition = f"def {func_name}({input_arg}):  # {node.title}\n"
            definition += fn_content + "\n\n"

            content += definition
            defined_factories.append(node.factory.factory_id)
            fn_reg += f'"{func_name}": {func_name}, '
            print(f"  - defined: {style.node(node)}")

        fn_reg += "}"
        content += f"\nFN_REG = {fn_reg}"

        return content

    def include_dependencies(self, defined_fns_code: str) -> str:
        """ Return all required import statemets. """
        content = ""
        used_deps = 0

        for dependency_import in self.__dependecies_imports:
            dependency_target = dependency_import.strip().split(" ")[-1] + "."
            if dependency_target in defined_fns_code:
                content += dependency_import + "\n"
                used_deps += 1

        print(f"\nIncluded {style.highlight(str(used_deps))} dependencies.")
        return content

    def build_instances_register(self) -> str:
        """
        Build register of all instances and their sources.

        Register format:
        {
            'node_id': {
                'handler': 'f_FactoryTitle',                          (key for FN_REG)
                'inputs': [
                    (inputName, targetNodeID, targetOutputSrcName),   <- Other node wire.
                    (inputName, constantValue, None)                  <- Constant value.
                ],
                'outputs': [(outputName, targetNodeID, targetInputSrcName)],
                'flow-output': targetNodeID / None,
                '__next-flow': targetNodeID / None,                   (by default set to flow-output or first output,
                                                                       can be modified by handler's response,
                                                                       exit if still None after handler call)
                '__default-next-flow': targetNodeID / None            (same as __next-flow but immutable, used at state reset)
                '__h_return': valReturnedByHandler / None
            }
        }
        """
        print("\nBuild instances register:")

        register = {}

        for node in self.all_nodes:
            node_data = {
                'handler': self.fn_name(node),
                'inputs': [],
                'outputs': [],
                'flow-output': None,
                '__default-next-flow': None,
                '__next-flow': None,
                '__h_return': None
            }

            if node.flow.enable_output and node.flow.output_src.target is not None:
                flow_target = node.flow.output_src.target.node.node_id
                node_data['flow-output'] = node_data['__next-flow'] = node_data['__default-next-flow'] = flow_target
                
            for src_in in node.inputs:
                if src_in.constant_value is not None:
                    node_data['inputs'].append(
                        (src_in.name, src_in.constant_value, None)
                    )
                
                elif src_in.source is not None and src_in.data_type != types.FLOW:
                    node_data['inputs'].append(
                        (src_in.name, src_in.source.node.node_id, src_in.source.name)
                    )

            for src_out in node.outputs:
                if src_out.target is not None:
                    node_data['outputs'].append(
                        (src_out.name, src_out.target.node.node_id, src_out.target.name)
                    )

            if node_data["__next-flow"] is None and node_data['outputs']:
                node_data['__default-next-flow'] = node_data["__next-flow"] = node_data['outputs'][0][1] or None

            register[node.node_id] = node_data
            print(f"  - registered: {style.node(node)}::{node.node_id}")

        return "NODES_REG = " + str(register)

    def set_entry_node(self) -> str:
        print(f"\nSet entry node to: {style.node(self.start_node)}::{self.start_node.node_id}")
        return f'ENTRY_ID = "{self.start_node.node_id}"'

    def inject_executor(self) -> str:
        with open("./modules/execution/injected/executor.py") as file:
            return file.read()

    def compile_to_exe(self) -> str:
        """ Call nuitka compiler. Returns absolute path to the executable. """
        print(f"\nCompile using {style.highlight('nuitka')}:\n")

        output_exe = f"{self.name}.exe"
        command = [
            "nuitka",
            "--standalone", "--onefile",
            self.__build_target_path,
            f"--output-filename={output_exe}",
            f"--output-dir={self.__compilation_dir_path}"
        ]

        subprocess.run(command, check=True, shell=True)
        
        target_exe_path = f"{self.__compilation_dir_path}../"
        if os.path.exists(target_exe_path + output_exe):
            os.rename(target_exe_path + output_exe, target_exe_path + output_exe + f".old_{int(time.time())}")
        
        if not os.path.exists(f"{self.__compilation_dir_path}{output_exe}"):
            return "<FAIL - No file>"
        
        shutil.move(f"{self.__compilation_dir_path}{output_exe}", target_exe_path)
        return os.path.abspath(f"{self.__compilation_dir_path}../{output_exe}")

    def cleanup(self) -> None:
        """ Remove all used files except the EXE. """

        for root, dirs, files in os.walk(self.__compilation_dir_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except:
                    pass

        os.removedirs(self.__compilation_dir_path)
