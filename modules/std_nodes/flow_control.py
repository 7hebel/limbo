from modules.nodes.source import NodeInput, NodeOutput
from modules.nodes.collection import NodesCollections
from modules.execution.exit_codes import ExitCode
from modules.nodes.factory import NodeFactory
from modules.nodes.node import FlowControl
from modules import types


# Start.
START_FACTORY = NodeFactory(
    title="Start",
    collection=NodesCollections.FLOW_CONTROL,
    flow=FlowControl(True, enable_input=False),
    inputs=[],
    outputs=[],
    handler=lambda *_: None,
    singleton=True
)


# Exit.
def exit_flow(ins: dict[str, int]) -> None:
    code = ins.get("Code") or ExitCode.OK
    raise EOFError(code)

NodeFactory(
    title="Exit",
    collection=NodesCollections.FLOW_CONTROL,
    flow=FlowControl(False),
    inputs=[NodeInput("Code", types.NUMBER, False)],
    outputs=[],
    handler=exit_flow
)

# If / else.
def if_else_flow(ins: dict[str, bool]) -> str:
    value = ins.get("Value")
    return "if" if value else "else"
    
NodeFactory(
    title="If/Else",
    collection=NodesCollections.FLOW_CONTROL,
    flow=FlowControl(False),
    inputs=[NodeInput("Value", types.BOOLEAN)],
    outputs=[NodeOutput("if", types.FLOW), NodeOutput("else", types.FLOW)],
    handler=if_else_flow
)

# Restart.
def restart(ins: dict[str, bool]) -> None:
    save_mem = ins.get("Save memory")
    code = ExitCode.RESTART if not save_mem else ExitCode.RESTART_SAVE_MEMORY
    raise EOFError(code)

NodeFactory(
    title="Restart",
    collection=NodesCollections.FLOW_CONTROL,
    flow=FlowControl(False, enable_input=True),
    inputs=[NodeInput("Save memory", types.BOOLEAN, required=False)],
    outputs=[],
    handler=restart,
)


# Loop.

NodeFactory(
    title="Loop",
    collection=NodesCollections.FLOW_CONTROL,
    flow=FlowControl(True, False),
    inputs=[NodeInput("in1", types.FLOW), NodeInput("in2", types.FLOW, required=False)],
    outputs=[],
    handler=lambda *_: None
)

