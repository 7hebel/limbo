from modules.nodes.source import NodeInput, NodeOutput
from modules.nodes.collection import NodesCollections
from modules.nodes.factory import NodeFactory
from modules.nodes.node import FlowControl
from modules import types


# Number to text
def cast_number_text(ins: dict[str, float]) -> dict[str, str]:
    num = ins.get("num")
    if num.is_integer():
        num = int(num)
        
    return {"text": str(num)}

NodeFactory(
    title="Number-Text",
    collection=NodesCollections.CASTING,
    flow=FlowControl(),
    inputs=[NodeInput("num", types.NUMBER)],
    outputs=[NodeOutput("text", types.TEXT)],
    handler=cast_number_text,
)

# Boolean to text
def cast_bool_text(ins: dict[str, bool]) -> dict[str, str]:
    return {"text": str(ins.get("bool"))}

NodeFactory(
    title="Boolean-Text",
    collection=NodesCollections.CASTING,
    flow=FlowControl(),
    inputs=[NodeInput("bool", types.BOOLEAN)],
    outputs=[NodeOutput("text", types.TEXT)],
    handler=cast_bool_text,
)

# Text to number
def cast_text_number(ins: dict[str, str]) -> dict[str, float]:
    text = ins.get("text")
    default = ins.get("default")
    
    num_buff = ""
    for letter in text:
        if letter.isnumeric() or letter == ".":
            num_buff += letter
        
    if not num_buff or num_buff.count(".") > 1:
        if default is not None:
            return {"number": default}
        raise RuntimeError(f"Text-Number conversion failed for string: {text}")
    
    try:
        value = float(num_buff)
        return {"number": value}

    except ValueError:
        if default is not None:
            return {"number": default}
        
    raise RuntimeError(f"Text-Number conversion failed for string: {text}")
    

NodeFactory(
    title="Text-Number",
    collection=NodesCollections.CASTING,
    flow=FlowControl(),
    inputs=[NodeInput("text", types.TEXT), NodeInput("default", types.NUMBER, required=False)],
    outputs=[NodeOutput("number", types.NUMBER)],
    handler=cast_text_number,
)



