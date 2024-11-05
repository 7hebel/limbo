from modules.nodes.source import NodeInput, NodeOutput
from modules.nodes.collection import NodesCollections
from modules.nodes.factory import NodeFactory
from modules.nodes.node import FlowControl
from modules import helpers
from modules import types

from typing import Any


def set_value(ins: dict[str, Any]) -> None:
    jar = helpers.MemoryJar.get_current()
    key = ins.get("key")
    value = ins.get("value")

    jar.set_value(key, value)

def get_value(ins: dict[str, Any]) -> dict[str, Any]:
    jar = helpers.MemoryJar.get_current()
    key = ins.get("key")
    default = ins.get("default")

    value = jar.get_value(key, default)
    if value is None:
        raise RuntimeError(f"Memory error: couldn't find value: {key} in the current jar.")

    return {"value": value}

# Save number.
NodeFactory(
    title="Save Number",
    collection=NodesCollections.MEMORY,
    flow=FlowControl(True),
    inputs=[NodeInput("key", types.TEXT), NodeInput("value", types.NUMBER)],
    outputs=[],
    handler=set_value,
)

# Save text.
NodeFactory(
    title="Save Text",
    collection=NodesCollections.MEMORY,
    flow=FlowControl(True),
    inputs=[NodeInput("key", types.TEXT), NodeInput("value", types.TEXT)],
    outputs=[],
    handler=set_value,
)

# Save bool.
NodeFactory(
    title="Save Boolean",
    collection=NodesCollections.MEMORY,
    flow=FlowControl(True),
    inputs=[NodeInput("key", types.TEXT), NodeInput("value", types.BOOLEAN)],
    outputs=[],
    handler=set_value,
)

# Get number.
NodeFactory(
    title="Get Number",
    collection=NodesCollections.MEMORY,
    flow=FlowControl(False),
    inputs=[NodeInput("key", types.TEXT), NodeInput("default", types.NUMBER, False)],
    outputs=[NodeOutput("value", types.NUMBER)],
    handler=get_value,
)

# Get text.
NodeFactory(
    title="Get Text",
    collection=NodesCollections.MEMORY,
    flow=FlowControl(False),
    inputs=[NodeInput("key", types.TEXT), NodeInput("default", types.TEXT, False)],
    outputs=[NodeOutput("value", types.TEXT)],
    handler=get_value,
)

# Get bool.
NodeFactory(
    title="Get Boolean",
    collection=NodesCollections.MEMORY,
    flow=FlowControl(False),
    inputs=[NodeInput("key", types.TEXT), NodeInput("default", types.BOOLEAN, False)],
    outputs=[NodeOutput("value", types.BOOLEAN)],
    handler=get_value,
)

