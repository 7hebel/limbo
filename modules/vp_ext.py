from modules import nodes as nodes_mod
from modules import pos

import typing
import abc

if typing.TYPE_CHECKING:
    from modules import viewport


class TargetViewport(abc.ABC):
    selection: "viewport.SelectionState"
    nodes: list[nodes_mod.Node]
    edit_node_mode: bool

    @abc.abstractmethod
    def render(self) -> None: ...
    

def node_safe_rect(node: nodes_mod.Node) -> pos.Rect:
    if node.position is None:
        raise ValueError("cannot calc safe rect for node with no position")
    
    w, h = node.calc_output_size()
    rect = pos.Rect(
        pos.Position(node.position.x - 1, node.position.y - 1),
        w + 2,
        h + 2
    )
    
    return rect


class ShiftableFocus(TargetViewport):
    def shift_focus_left(self) -> None:
        if not self.nodes:
            return
        
        if self.selection.node is None:
            self.selection.node = self.nodes[0]
            return
        
        candidate = None

        for node in self.nodes:
            if node == self.selection.node or node.position.x == self.selection.node.position.x:
                continue

            if node.position.x < (self.selection.node.position.x + self.selection.node.rect.w):
                if candidate is None or candidate and node.position.x > candidate.position.x:
                    candidate = node

        if candidate is not None:
            self.selection.node = candidate
            self.render()
        
    def shift_focus_right(self) -> None:
        if not self.nodes:
            return
        
        if self.selection.node is None:
            self.selection.node = self.nodes[0]
            return
        
        candidate = None

        for node in self.nodes:
            if node == self.selection.node or node.position.x == self.selection.node.position.x:
                continue
            
            if self.selection.node.position.x < node.position.x:
                if candidate is None or candidate and node.position.x < candidate.position.x:
                    candidate = node

        if candidate is not None:
            self.selection.node = candidate
            self.render()
        
    def shift_focus_up(self) -> None:
        if not self.nodes:
            return
        
        if self.selection.node is None:
            self.selection.node = self.nodes[0]
            return
        
        candidate = None

        for node in self.nodes:
            if node == self.selection.node or node.position.y == self.selection.node.position.y:
                continue
            
            if (self.selection.node.position.y + self.selection.node.rect.h) > (node.position.y + node.rect.h):
                if candidate is None or candidate and (node.position.y + node.rect.h) > (candidate.position.y + candidate.rect.h):
                    candidate = node

        if candidate is not None:
            self.selection.node = candidate
            self.render()
        
    def shift_focus_down(self) -> None:
        if not self.nodes:
            return
        
        if self.selection.node is None:
            self.selection.node = self.nodes[0]
            return
        
        candidate = None

        for node in self.nodes:
            if node == self.selection.node or node.position.y == self.selection.node.position.y:
                continue
            
            if self.selection.node.position.y < node.position.y:
                if candidate is None or candidate and node.position.y < candidate.position.y:
                    candidate = node

        if candidate is not None:
            self.selection.node = candidate
            self.render()
        

class MovableNodes(TargetViewport):
    def node_intersects(self) -> bool:
        for node in self.nodes:
            if node == self.selection.node:
                continue
            
            if node_safe_rect(node).intersects(self.selection.node.rect):
                return True
        return False    
        
    def move_node_left(self) -> None:
        if self.selection.node is None:
            return
        
        self.selection.node.position.x -= 2
        while self.node_intersects():
            self.selection.node.position.x -= 2
                
        self.render()
                
    def move_node_right(self) -> None:
        if self.selection.node is None:
            return
        
        self.selection.node.position.x += 2
        while self.node_intersects():
            self.selection.node.position.x += 2
                
        self.render()
                
    def move_node_up(self) -> None:
        if self.selection.node is None:
            return
        
        self.selection.node.position.y -= 1
        while self.node_intersects():
            self.selection.node.position.y -= 1
                
        self.render()
        
    def move_node_down(self) -> None:
        if self.selection.node is None:
            return
        
        self.selection.node.position.y += 1
        while self.node_intersects():
            self.selection.node.position.y += 1
                
        self.render()
