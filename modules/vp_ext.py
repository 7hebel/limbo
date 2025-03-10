from modules.nodes import source
from modules.nodes import node
from modules import helpers
from modules import measure

import typing
import math
import abc

if typing.TYPE_CHECKING:
    from modules import workspace


class TargetViewport(abc.ABC):
    selection: "workspace.SelectionState"
    nodes: list[node.Node]
    edit_node_mode: bool
    camera: measure.Camera
    _nodes_state_cache: dict[str, str]
    _is_saved: bool

    @abc.abstractmethod
    def render(self) -> None: ...


def node_safe_rect(node: node.Node) -> measure.Rect:
    if node.position is None:
        raise ValueError("cannot calc safe rect for node with no position")

    w, h = node.calc_output_size()
    rect = measure.Rect(
        measure.Position(node.position.x - 2, node.position.y - 1),
        w + 4,
        h + 2
    )

    return rect


class ShiftableFocus(TargetViewport):
    """ 
    Allows to shift focus between nodes. 
    The algorithm selects the closest node in given direction. 
    When calculating distance between nodes, Y coordinate is mulitplied
      because visually, the chars are twice as high as they are wide,
      so it feels much more natural and smooth.
    """
    
    def __can_shift(self) -> bool:
        """ Check if can shift to any other node. """
        if not self.nodes:
            return False

        if self.selection.node is None:
            self.selection.node = self.nodes[0]
            return False
    
        return True
    
    def shift_focus_left(self) -> None:
        if not self.__can_shift():
            return

        candidate = None
        candidate_dist = 1000

        for node in self.nodes:
            if node.position.x < self.selection.node.position.x:
                distance = math.dist((node.position.x, node.position.y * 2), (self.selection.node.position.x, self.selection.node.position.y * 2))
                
                if candidate is None or candidate and distance < candidate_dist:
                    candidate = node
                    candidate_dist = distance
                
        if candidate is not None:
            self.selection.node = candidate
            self.render()

    def shift_focus_right(self) -> None:
        if not self.__can_shift():
            return

        candidate = None
        candidate_dist = 1000

        for node in self.nodes:
            if node.position.x > self.selection.node.position.x:
                distance = math.dist((node.position.x, node.position.y * 2), (self.selection.node.position.x, self.selection.node.position.y * 2))

                if candidate is None or candidate and distance < candidate_dist:
                    candidate = node
                    candidate_dist = distance

        if candidate is not None:
            self.selection.node = candidate
            self.render()

    def shift_focus_up(self) -> None:
        if not self.__can_shift():
            return

        candidate = None
        candidate_dist = 1000
        
        for node in self.nodes:
            node_bottom_y = node.position.y + node.rect.h
            
            if (self.selection.node.position.y + self.selection.node.rect.h) > node_bottom_y:
                distance = math.dist((node.position.x, node_bottom_y * 2), (self.selection.node.position.x, self.selection.node.position.y * 2))

                if candidate is None or candidate and distance < candidate_dist:
                    candidate = node
                    candidate_dist = distance

        if candidate is not None:
            self.selection.node = candidate
            self.render()

    def shift_focus_down(self) -> None:
        if not self.__can_shift():
            return

        candidate = None
        candidate_dist = 1000

        for node in self.nodes:
            if self.selection.node.position.y < node.position.y:
                distance = math.dist((node.position.x, node.position.y * 2), (self.selection.node.position.x, self.selection.node.position.y * 2))
                
                if candidate is None or candidate and distance < candidate_dist:
                    candidate = node
                    candidate_dist = distance

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
        self._is_saved = False

    def move_node_right(self) -> None:
        if self.selection.node is None:
            return

        self.selection.node.position.x += 2
        while self.node_intersects():
            self.selection.node.position.x += 2

        self.render()
        self._is_saved = False

    def move_node_up(self) -> None:
        if self.selection.node is None:
            return

        self.selection.node.position.y -= 1
        while self.node_intersects():
            self.selection.node.position.y -= 1

        self.render()
        self._is_saved = False

    def move_node_down(self) -> None:
        if self.selection.node is None:
            return

        self.selection.node.position.y += 1
        while self.node_intersects():
            self.selection.node.position.y += 1

        self.render()
        self._is_saved = False


class StateBasedNodeCache(TargetViewport):
    def eval_node_state(self, node: node.Node) -> str:
        """ Used for caching drawable nodes. """
        state = "0" if not node == self.scope.selection.node else "1"
        state += "0" if not self.scope.edit_node_mode else "1"
        state += f"{node.position.x}.{node.position.y}"
        state += f"{self.camera.x}.{self.camera.y}"

        if self.edit_node_mode and node == self.selection.node:
            if self.selection.highlighted_source == node.flow.input_src:
                state += "I"

            elif self.selection.highlighted_source == node.flow.output_src:
                state += "O"

        for index, src in enumerate(helpers.iter_alternately(node.inputs, node.outputs)):
            if isinstance(src, source.NodeInput):
                if src.source is not None:
                    state += f"c{index}"
            elif src.target is not None:
                state += f"c{index}"
            
            if self.edit_node_mode and self.selection.highlighted_source == src:
                state += f"h{index}"

            if src == self.selection.src:
                state += f"s{index}"

        return state

    def has_node_state_changed(self, node: node.Node) -> bool:
        state = self.eval_node_state(node)
        
        if node.node_id not in self._nodes_state_cache:
            self._nodes_state_cache[node.node_id] = (state, node.rect)
            return True
        
        if self._nodes_state_cache.get(node.node_id)[0] != state:
            self._nodes_state_cache[node.node_id] = (state, node.rect)
            return True
        
        return False
        