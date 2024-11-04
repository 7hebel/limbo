from modules.nodes import *
from modules import types

# Equal.
def string_eq(ins: dict[str, str]) -> dict[str, bool]:
    a = ins.get("a")
    b = ins.get("b")
    return {"equal": a == b}

NodeFactory(
    title="Equal",
    collection=NodesCollections.STRINGS,
    flow=FlowControl(False),
    inputs=[NodeInput("a", types.TEXT), NodeInput("b", types.TEXT)],
    outputs=[NodeOutput("equal", types.BOOLEAN)],
    handler=string_eq,
)

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

# Count.
def count_string(ins: dict[str, str]) -> dict[str, int]:
    text = ins.get("text")
    phrase = ins.get("phrase")
    return {"count": text.count(phrase)}

NodeFactory(
    title="Count phrase",
    collection=NodesCollections.STRINGS,
    flow=FlowControl(False),
    inputs=[NodeInput("text", types.TEXT), NodeInput("phrase", types.TEXT)],
    outputs=[NodeOutput("lower", types.TEXT)],
    handler=count_string,
)

# Join.
def join_strings(ins: dict[str, str]) -> dict[str, str]:
    str1 = ins.get("text1")
    str2 = ins.get("text2")
    sep = ins.get("sep") or ""
    return {"joined": f"{str1}{sep}{str2}"}

NodeFactory(
    title="Join",
    collection=NodesCollections.STRINGS,
    flow=FlowControl(False),
    inputs=[NodeInput("text1", types.TEXT), NodeInput("text2", types.TEXT), NodeInput("sep", types.TEXT, False)],
    outputs=[NodeOutput("joined", types.TEXT)],
    handler=join_strings,
)
