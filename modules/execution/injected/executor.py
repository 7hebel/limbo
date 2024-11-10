"""
Code below is injected into compiler's build file that contains all required definitions
and is responsible for handling (preparing, executing) parsed nodes.
"""

from modules.execution.exit_codes import ExitCode
from modules import helpers

from sys import exit


NODES_REG: dict
FN_REG: dict
ENTRY_ID: str
    
    
def __prep_inputs(inputs: list[tuple[str, str, str | None]]) -> dict:
    values = {}
    
    for name, node_or_const, src_name in inputs:
        if src_name is None:
            values[name] = node_or_const
            continue
        
        target_return = NODES_REG.get(node_or_const)["__h_return"]
        if target_return is None:
            __execute(node_or_const)
            target_return = NODES_REG.get(node_or_const)["__h_return"]
            
        if target_return is None:
            continue
            
        NODES_REG.get(node_or_const)["__h_return"] = None
        for ret_key, ret_val in target_return.items():
            if ret_key == src_name:
                values[name] = ret_val

    return values

def __reset_state() -> None:
    for key in NODES_REG.keys():
        NODES_REG[key]["__next-flow"] = NODES_REG[key]["__default-next-flow"]
        NODES_REG[key]["__h_return"] = None

def __execute(node_id: str) -> None:
    node_data = NODES_REG.get(node_id)
    handler = FN_REG.get(node_data.get('handler'))
    inputs = __prep_inputs(node_data.get('inputs'))
    
    output = handler(inputs)
    
    if isinstance(output, dict):
        NODES_REG.get(node_id)['__h_return'] = output
        
    if isinstance(output, str):
        for out_name, out_target, _ in node_data.get('outputs'):
            if output == out_name:
                NODES_REG.get(node_id)['__next-flow'] = out_target
                break
            
def __run():
    _curr_node = ENTRY_ID
    
    while _curr_node is not None:
        try:
            __execute(_curr_node)
            
        except EOFError as exit_code:
            exit_code = int(str(exit_code))
            
            if exit_code == ExitCode.RESTART:
                helpers.MemoryJar.new_jar()
                __reset_state()
                return __run()
            
            if exit_code == ExitCode.RESTART_SAVE_MEMORY:
                __reset_state()
                return __run()
            
            return exit(exit_code)
        
        except RuntimeError as error:
            print(f"\nERROR: {error}")
            exit(ExitCode.ERROR)

        except RecursionError:
            print("\nERROR: Infinite recurrsion occured.")
            exit(ExitCode.INF_RECURSION)

        except KeyboardInterrupt:
            print("\nExecution manually terminated.")
            return exit(ExitCode.MANUAL_TERMINATION)
        
        _curr_node = NODES_REG.get(_curr_node)['__next-flow']
    
__run()
