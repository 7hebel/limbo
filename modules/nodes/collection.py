from modules.nodes.factory import NodeFactory
from modules.side_bar import side_bar
from modules import style

from dataclasses import dataclass
from enum import Enum


@dataclass
class Collection:
    name: str
    color: style.AnsiFGColor

    def __post_init__(self) -> None:
        self.factories: list["NodeFactory"] = []

    def __hash__(self) -> int:
        return len(self.name) ** len(self.color.name)

    def register_factory(self, factory: "NodeFactory") -> None:
        self.factories.append(factory)


class NodesCollections(Enum):
    FLOW_CONTROL = Collection("Flow Control", style.AnsiFGColor.RED)
    LOGICAL = Collection("Logical", style.AnsiFGColor.BLUE)
    CASTING = Collection("Cast", style.AnsiFGColor.CYAN)
    MEMORY = Collection("Memory", style.AnsiFGColor.WHITE)
    MATH = Collection("Maths", style.AnsiFGColor.MAGENTA)
    STRINGS = Collection("Strings", style.AnsiFGColor.YELLOW)
    INTERACTION = Collection("Interaction", style.AnsiFGColor.GREEN)


""" Initialize all NodeFactories, feed NodesCollection, set sidebar collection. """
from modules import std_nodes

side_bar.set_collections(NodesCollections)
