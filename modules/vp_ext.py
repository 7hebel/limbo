import abc

from modules import nodes as nodes_mod
from modules import pos


class TargetViewport(abc.ABC):
    selected_node: nodes_mod.Node | None
    nodes: list[nodes_mod.Node]
    edit_node_mode: bool
    __edit_node_source_pointer: nodes_mod.NodeInput | nodes_mod.NodeOutput | None

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
        
        if self.selected_node is None:
            self.selected_node = self.nodes[0]
            return
        
        candidate = None

        for node in self.nodes:
            if node == self.selected_node or node.position.x == self.selected_node.position.x:
                continue

            if node.position.x < (self.selected_node.position.x + self.selected_node.rect.w):
                if candidate is None or candidate and node.position.x > candidate.position.x:
                    candidate = node

        if candidate is not None:
            self.selected_node = candidate
            self.render()
        
    def shift_focus_right(self) -> None:
        if not self.nodes:
            return
        
        if self.selected_node is None:
            self.selected_node = self.nodes[0]
            return
        
        candidate = None

        for node in self.nodes:
            if node == self.selected_node or node.position.x == self.selected_node.position.x:
                continue
            
            if self.selected_node.position.x < node.position.x:
                if candidate is None or candidate and node.position.x < candidate.position.x:
                    candidate = node

        if candidate is not None:
            self.selected_node = candidate
            self.render()
        
    def shift_focus_up(self) -> None:
        if not self.nodes:
            return
        
        if self.selected_node is None:
            self.selected_node = self.nodes[0]
            return
        
        candidate = None

        for node in self.nodes:
            if node == self.selected_node or node.position.y == self.selected_node.position.y:
                continue
            
            if (self.selected_node.position.y + self.selected_node.rect.h) > (node.position.y + node.rect.h):
                if candidate is None or candidate and (node.position.y + node.rect.h) > (candidate.position.y + candidate.rect.h):
                    candidate = node

        if candidate is not None:
            self.selected_node = candidate
            self.render()
        
    def shift_focus_down(self) -> None:
        if not self.nodes:
            return
        
        if self.selected_node is None:
            self.selected_node = self.nodes[0]
            return
        
        candidate = None

        for node in self.nodes:
            if node == self.selected_node or node.position.y == self.selected_node.position.y:
                continue
            
            if self.selected_node.position.y < node.position.y:
                if candidate is None or candidate and node.position.y < candidate.position.y:
                    candidate = node

        if candidate is not None:
            self.selected_node = candidate
            self.render()
        

class MovableNodes(TargetViewport):
    def move_node_left(self) -> None:
        if self.selected_node is None:
            return
        
        self.selected_node.position.x -= 2
        
        for node in self.nodes:
            if node == self.selected_node:
                continue
            
            if node_safe_rect(node).intersects(self.selected_node.rect):
                return self.move_node_left()
                
        self.render()
                
    def move_node_right(self) -> None:
        if self.selected_node is None:
            return
        
        self.selected_node.position.x += 2
        
        for node in self.nodes:
            if node == self.selected_node:
                continue
            
            if node_safe_rect(node).intersects(self.selected_node.rect):
                return self.move_node_right()
                
        self.render()
                
    def move_node_up(self) -> None:
        if self.selected_node is None:
            return
        
        self.selected_node.position.y -= 1
        
        for node in self.nodes:
            if node == self.selected_node:
                continue
            
            if node_safe_rect(node).intersects(self.selected_node.rect):
                return self.move_node_up()
                
        self.render()
        
    def move_node_down(self) -> None:
        if self.selected_node is None:
            return
        
        self.selected_node.position.y += 1
        
        for node in self.nodes:
            if node == self.selected_node:
                continue
            
            if node_safe_rect(node).intersects(self.selected_node.rect):
                return self.move_node_down()
                
        self.render()
