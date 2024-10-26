from modules import user_input
from modules.nodes import *
from modules import types

# Input.
def input_interaction(ins: dict[str, str]) -> dict[str, str]:
    prompt = ins.get("prompt") or ""
    value = user_input.get_input(prompt)
    return {"value": value}

INPUT_FACTORY = NodeFactory(
    title="Input",
    collection=NodesCollections.INTERACTION,
    flow=FlowControl(False),
    inputs=[NodeInput("prompt", types.TEXT, False)],
    outputs=[NodeOutput("value", types.TEXT)],
    handler=input_interaction,
)


# Output.
def dispaly_text(ins: dict[str, str]) -> None:
    print(ins.get("text"))

OUTPUT_FACTORY = NodeFactory(
    title="Output",
    collection=NodesCollections.INTERACTION,
    flow=FlowControl(True),
    inputs=[NodeInput("text", types.TEXT)],
    outputs=[],
    handler=dispaly_text,
)
