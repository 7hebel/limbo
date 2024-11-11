from dataclasses import dataclass
from enum import IntEnum


@dataclass
class Position:
    x: int
    y: int


@dataclass
class Rect:
    pos: Position
    w: int
    h: int
    
    def intersects(self, r: "Rect") -> bool:
        if self.pos.x + self.w <= r.pos.x or r.pos.x + r.w <= self.pos.x:
            return False

        if self.pos.y + self.h <= r.pos.y or r.pos.y + r.h <= self.pos.y:
            return False
            
        return True
        
    def contains_point(self, x: int, y: int) -> bool:
        return x in range(self.pos.x, self.pos.x + self.w) and y in range(self.pos.y, self.pos.y + self.h)
      
    def fully_within(self, rect: "Rect") -> bool:
        """ Check if this rect is fully within other rect. """
        x_range = range(rect.pos.x, rect.pos.x + rect.w)
        y_range = range(rect.pos.y, rect.pos.y + rect.h)
      
        return all((
            self.pos.x in x_range,
            self.pos.x + self.w in x_range,
            self.pos.y in y_range,
            self.pos.y + self.h in y_range
        ))
      
      
@dataclass
class Camera:
    x: int
    y: int
    sensitivity: int = 1
    
    def get_pos(self) -> Position:
        return Position(self.x, self.y)
    
    def set_pos(self, pos: Position) -> None:
        self.x = pos.x
        self.y = pos.y
    
    def move_left(self) -> None:
        self.x += 2 * self.sensitivity
        
    def move_right(self) -> None:
        self.x -= 2 * self.sensitivity
        
    def move_up(self) -> None:
        self.y += 1 * self.sensitivity
        
    def move_down(self) -> None:
        self.y -= 1 * self.sensitivity
    
        
class VerticalDirection(IntEnum):
    UP = -1
    DOWN = 1
        