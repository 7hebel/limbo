from modules.nodes.source import NodeInput, NodeOutput
from modules.nodes.collection import NodesCollections
from modules.nodes.factory import NodeFactory
from modules.nodes.node import FlowControl
from modules import types

# Equal ==
def are_equal(ins: dict[str, float]) -> dict[str, bool]:
    x, y = ins.get("x"), ins.get("y")
    return {"==": x == y}

NodeFactory(
    title="==",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput("==", types.BOOLEAN)],
    handler=are_equal,
)

# Not equal !=
def are_not_equal(ins: dict[str, float]) -> dict[str, bool]:
    x, y = ins.get("x"), ins.get("y")
    return {"!=": x == y}

NodeFactory(
    title="!=",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput("!=", types.BOOLEAN)],
    handler=are_not_equal,
)

# Greater than >
def is_greater_than(ins: dict[str, float]) -> dict[str, bool]:
    x, y = ins.get("x"), ins.get("y")
    return {">": x > y}

NodeFactory(
    title=">",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput(">", types.BOOLEAN)],
    handler=is_greater_than,
)

# Greater than or equal >=
def is_greater_than_equal(ins: dict[str, float]) -> dict[str, bool]:
    x, y = ins.get("x"), ins.get("y")
    return {">=": x >= y}

NodeFactory(
    title=">=",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput(">=", types.BOOLEAN)],
    handler=is_greater_than_equal,
)

# Less than <
def is_less_than(ins: dict[str, float]) -> dict[str, bool]:
    x, y = ins.get("x"), ins.get("y")
    return {"<": x < y}

NodeFactory(
    title="<",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput("<", types.BOOLEAN)],
    handler=is_less_than,
)

# Less than or equal <=
def is_less_than_equal(ins: dict[str, float]) -> dict[str, bool]:
    x, y = ins.get("x"), ins.get("y")
    return {"<=": x <= y}

NodeFactory(
    title="<=",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput("<=", types.BOOLEAN)],
    handler=is_less_than_equal,
)

# Add +
def add(ins: dict[str, float]) -> dict[str, float]:
    x, y = ins.get("x"), ins.get("y")
    return {"=": x + y}

NodeFactory(
    title="Add",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput("=", types.NUMBER)],
    handler=add,
)

# Sub -
def sub(ins: dict[str, float]) -> dict[str, float]:
    x, y = ins.get("x"), ins.get("y")
    return {"=": x - y}

NodeFactory(
    title="Sub",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput("=", types.NUMBER)],
    handler=sub,
)

# Multiply *
def multiply(ins: dict[str, float]) -> dict[str, float]:
    x, y = ins.get("x"), ins.get("y")
    return {"=": x * y}

NodeFactory(
    title="Multiply",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput("=", types.NUMBER)],
    handler=multiply,
)

# Divide /
def divide(ins: dict[str, float]) -> dict[str, float]:
    x, y = ins.get("x"), ins.get("y")
    return {"=": x / y}

NodeFactory(
    title="Divide",
    collection=NodesCollections.MATH,
    flow=FlowControl(False),
    inputs=[NodeInput("x", types.NUMBER), NodeInput("y", types.NUMBER)],
    outputs=[NodeOutput("=", types.NUMBER)],
    handler=divide,
)

