from modules.nodes import *
from modules import types

# Length.
def length_string(ins: dict[str, str]) -> dict[str, int]:
    text = ins.get("text")
    return {"length": len(text)}

NodeFactory(
    title="Length",
    collection=NodesCollections.STRINGS,
    flow=FlowControl(False),
    inputs=[NodeInput("text", types.TEXT)],
    outputs=[NodeOutput("length", types.NUMBER)],
    handler=length_string,
)

# Uppercase.
def uppercase_string(ins: dict[str, str]) -> dict[str, str]:
    text = ins.get("text")   
    return {"upper": text.upper()}

UPPERCASE_FACTORY = NodeFactory(
    title="Uppercase",
    collection=NodesCollections.STRINGS,
    flow=FlowControl(False),
    inputs=[NodeInput("text", types.TEXT)],
    outputs=[NodeOutput("upper", types.TEXT)],
    handler=uppercase_string,
)

# Lowercase.
def lowercase_string(ins: dict[str, str]) -> dict[str, str]:
    text = ins.get("text")   
    return {"lower": text.lower()}

NodeFactory(
    title="Lowercase",
    collection=NodesCollections.STRINGS,
    flow=FlowControl(False),
    inputs=[NodeInput("text", types.TEXT)],
    outputs=[NodeOutput("lower", types.TEXT)],
    handler=lowercase_string,
)
