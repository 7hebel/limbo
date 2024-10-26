from modules.nodes import *
from modules import types


# Not.
def not_bool_handler(ins: dict[str, bool]) -> dict[str, bool]:
    value = ins.get("a")
    return {"NOT": not value}

NodeFactory(
    title="Not",
    collection=NodesCollections.LOGICAL,
    flow=FlowControl(False, False),
    inputs=[NodeInput("a", types.BOOLEAN)],
    outputs=[NodeOutput("NOT", types.BOOLEAN)],
    handler=not_bool_handler,
)

# And.
def and_bool_handler(ins: dict[str, bool]) -> dict[str, bool]:
    a, b = ins.get("a"), ins.get("b")
    return {"AND": a and b}

NodeFactory(
    title="And",
    collection=NodesCollections.LOGICAL,
    flow=FlowControl(False, False),
    inputs=[NodeInput("a", types.BOOLEAN), NodeInput("b", types.BOOLEAN)],
    outputs=[NodeOutput("AND", types.BOOLEAN)],
    handler=and_bool_handler,
)

# Or.
def or_bool_handler(ins: dict[str, bool]) -> dict[str, bool]:
    a, b = ins.get("a"), ins.get("b")
    return {"OR": a and b}

NodeFactory(
    title="Or",
    collection=NodesCollections.LOGICAL,
    flow=FlowControl(False, False),
    inputs=[NodeInput("a", types.BOOLEAN), NodeInput("b", types.BOOLEAN)],
    outputs=[NodeOutput("OR", types.BOOLEAN)],
    handler=or_bool_handler,
)

# Equal.
def bool_equal_check(ins: dict[str, bool]) -> dict[str, bool]:
    a, b = ins.get("a"), ins.get("b")
    return {"Result": a == b}

NodeFactory(
    title="Equal",
    collection=NodesCollections.LOGICAL,
    flow=FlowControl(False, False),
    inputs=[NodeInput("a", types.BOOLEAN), NodeInput("b", types.BOOLEAN)],
    outputs=[NodeOutput("Result", types.BOOLEAN)],
    handler=bool_equal_check,
)
