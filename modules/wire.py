from modules import chars
from modules import pos

import math


class WireBuilder:
    def __init__(self, start: tuple[int, int], end: tuple[int, int], charset: chars.LineChars, avoid_rects: list[pos.Rect], camera_rect: pos.Rect) -> None:
        self.charset = charset
        self.camera_rect = camera_rect
        
        self.avoid_rects: list[pos.Rect] = []
        for av_rect in avoid_rects:
            rect_copy = pos.Rect(
                pos.Position(av_rect.pos.x - camera_rect.pos.x, av_rect.pos.y - camera_rect.pos.y),
                av_rect.w,
                av_rect.h
            ) 
            
            self.avoid_rects.append(rect_copy)
        
        # Ensure wire not going below node's border.
        start = (start[0] + 1, start[1])
        end = (end[0] - 1, end[1])
        
        self.start = start
        self.end = end
        
        self.positioned_chars: dict[tuple[int, int], str] = {}
        self.choose_optimal_build_strategy()
        
    def collides_with_any_rect(self, x: int, y: int) -> bool:
        for avoid_rect in self.avoid_rects:
            if avoid_rect.contains_point(x, y):
                return True
        return False
        
    def choose_optimal_build_strategy(self) -> None:
        sx, sy = self.start
        ex, ey = self.end
        
        if ey == sy:
            return self.build_straight_line()
        
        if ex < sx:
            path_x_range = range(sx, ex) if sx < ex else range(ex, sx)
            mid_points_y = (
                (math.floor((sy + ey) / 2)),
                (math.ceil((sy + ey) / 2)),
                (math.floor((sy + ey) / 2)) + 1,
                (math.ceil((sy + ey) / 2)) - 1,
            )  # It looks much better when line turns near to the middle of Y.
            
            # Try to find common Y near to the middle of both points.
            for test_y in mid_points_y:
                collision = False
                
                for test_x in path_x_range:
                    if self.collides_with_any_rect(test_x, test_y):
                        collision = True
                        break
                
                if not collision:
                    return self.build_targetted_vertical_path(test_y)
            
            # Find any common Y.
            possible_target_y = range(sy, ey) if sy < ey else range(ey, sy)
            target_y = None
            
            for test_y in possible_target_y:
                collision = False

                for test_x in path_x_range:
                    if self.collides_with_any_rect(test_x, test_y):
                        collision = True
                        break
                        
                if not collision:
                    target_y = test_y
                    break
            
            if target_y is None:
                return self.build_vertical_path_auto()

            else:
                return self.build_targetted_vertical_path(target_y)
            
        else:
            # Horizontal path.
            return self.build_horizontal_path()
        
    def build_straight_line(self) -> None:
        sx, sy = self.start
        ex, ey = self.end
        
        x_range = range(sx, ex + 1) if sx < ex else range(ex, sx + 1)
        
        for x in x_range:
            self.positioned_chars[(x, sy)] = self.charset.hz
            
        if sx > ex:
            self.positioned_chars[(sx, sy)] = self.charset.fl
            self.positioned_chars[(ex, ey)] = self.charset.fr
        
    def build_horizontal_path(self) -> None:
        sx, sy = self.start
        ex, ey = self.end
        
        meet_x = False
        append_round = False
        
        while not meet_x:
            append_round = not append_round
            if sx == ex:
                meet_x = sx
                break
            
            if append_round:
                self.positioned_chars[(sx, sy)] = self.charset.hz
                sx += 1
                
            else:
                self.positioned_chars[(ex, ey)] = self.charset.hz
                ex -= 1
                
        # Add corners.
        if ey > sy:
            self.positioned_chars[(meet_x, ey)] = self.charset.sw
            self.positioned_chars[(meet_x, sy)] = self.charset.ne

            for y in range(sy + 1, ey):
                self.positioned_chars[(meet_x, y)] = self.charset.vt
            
        else:
            self.positioned_chars[(meet_x, ey)] = self.charset.nw
            self.positioned_chars[(meet_x, sy)] = self.charset.se

            for y in range(ey + 1, sy):
                self.positioned_chars[(meet_x, y)] = self.charset.vt
        
    def build_vertical_path_auto(self) -> None:
        sx, sy = self.start
        ex, ey = self.end
        
        meet_y = False
        append_round = False
        
        # Set headers to point to source.
        if sy >= ey:
            self.positioned_chars[(sx, sy)] = self.charset.se
        else:
            self.positioned_chars[(sx, sy)] = self.charset.ne
            
        if ey >= sy:
            self.positioned_chars[(ex, ey)] = self.charset.sw
        else:
            self.positioned_chars[(ex, ey)] = self.charset.nw
        
        # Find common Y pos.
        while not meet_y:
            append_round = not append_round
            if sy == ey:
                meet_y = sy
                break
            
            if append_round:
                if sy > ey:
                    sy -= 1
                else:
                    sy += 1
                self.positioned_chars[(sx, sy)] = self.charset.vt

            else:
                if ey > sy:
                    ey -= 1
                else:
                    ey += 1
                self.positioned_chars[(ex, ey)] = self.charset.vt
                    
        # Fill corners.
        if self.end[1] < self.start[1]:
            self.positioned_chars[(sx, meet_y)] = self.charset.ne
            self.positioned_chars[(ex, meet_y)] = self.charset.sw
            
        else:
            self.positioned_chars[(sx, meet_y)] = self.charset.se
            self.positioned_chars[(ex, meet_y)] = self.charset.nw
            
        # Fill horizontal line.
        for x in range(ex + 1, sx):
            self.positioned_chars[(x, sy)] = self.charset.hz
            
    def build_targetted_vertical_path(self, target_y: int) -> None:
        sx, sy = self.start
        ex, ey = self.end
        
        # Set headers to point to source.
        if sy >= ey:
            self.positioned_chars[(sx, sy)] = self.charset.se
        else:
            self.positioned_chars[(sx, sy)] = self.charset.ne
        
        if ey >= sy:
            self.positioned_chars[(ex, ey)] = self.charset.sw
        else:
            self.positioned_chars[(ex, ey)] = self.charset.nw
        
        # Build source's vertical lines to meet at targetted Y pos.
        sy_delta = 1 if sy < target_y else -1
        while sy != target_y:
            sy += sy_delta
            self.positioned_chars[(sx, sy)] = self.charset.vt
            
        ey_delta = 1 if ey < target_y else -1
        while ey != target_y:
            ey += ey_delta
            self.positioned_chars[(ex, ey)] = self.charset.vt
        
        # Fill corners.
        if self.end[1] < self.start[1]:
            self.positioned_chars[(sx, target_y)] = self.charset.ne
            self.positioned_chars[(ex, target_y)] = self.charset.sw
            
        else:
            self.positioned_chars[(sx, target_y)] = self.charset.se
            self.positioned_chars[(ex, target_y)] = self.charset.nw
            
        # Fill horizontal line.
        for x in range(ex + 1, sx):
            self.positioned_chars[(x, sy)] = self.charset.hz
            
            
