from dataclasses import dataclass
from typing import Generator


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
        

def iter_alternately(a: list, b: list) -> Generator:
    a = a.copy()
    b = b.copy()
    
    while a or b:
        if a:
            yield a.pop(0)
        
        if b:
            yield b.pop(0)
