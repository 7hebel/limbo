from modules import user_input
from modules import terminal
from modules.nodes import *
from modules import style
from modules import types

# Input.
def input_interaction(ins: dict[str, str]) -> dict[str, str]:
    prompt = ins.get("prompt") or ""
    value = user_input.get_input(prompt)
    terminal.hide_cursor()
    return {"value": value}

NodeFactory(
    title="Input",
    collection=NodesCollections.INTERACTION,
    flow=FlowControl(False),
    inputs=[NodeInput("prompt", types.TEXT, False)],
    outputs=[NodeOutput("value", types.TEXT)],
    handler=input_interaction,
)


# Output.
def dispaly_text(ins: dict[str, str]) -> None:
    print(ins.get("text").replace("\\n", "\n"))

NodeFactory(
    title="Output",
    collection=NodesCollections.INTERACTION,
    flow=FlowControl(True),
    inputs=[NodeInput("text", types.TEXT)],
    outputs=[],
    handler=dispaly_text,
)

# Clear screen.
NodeFactory(
    title="Clear screen",
    collection=NodesCollections.INTERACTION,
    flow=FlowControl(True),
    inputs=[],
    outputs=[],
    handler=lambda *_: style.clear_screen(),
)


# Wait for enter.
NodeFactory(
    title="Await Enter",
    collection=NodesCollections.INTERACTION,
    flow=FlowControl(True),
    inputs=[],
    outputs=[],
    handler=lambda *_: terminal.wait_for_enter(),
)
