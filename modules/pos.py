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
        
        
class VerticalDirection(IntEnum):
    UP = -1
    DOWN = 1
        