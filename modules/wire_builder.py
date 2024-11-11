from modules import measure
from modules import chars

import math


class WireBuilder:
    def __init__(self, start: tuple[int, int], end: tuple[int, int], charset: chars.LineChars, avoid_rects: list[measure.Rect], camera_rect: measure.Rect) -> None:
        self.charset = charset
        self.camera_rect = camera_rect
        
        self.avoid_rects: list[measure.Rect] = []
        for av_rect in avoid_rects:
            rel_rect = measure.Rect(
                measure.Position(av_rect.pos.x - camera_rect.pos.x, av_rect.pos.y - camera_rect.pos.y),
                av_rect.w,
                av_rect.h
            ) 
            
            self.avoid_rects.append(rel_rect)
        
        # Ensure wire is not going below node's border.
        self.start = (start[0] + 1, start[1])
        self.end = (end[0] - 1, end[1])
        
        self.positioned_chars: dict[tuple[int, int], str] = {}
        self.choose_optimal_build_strategy()
        
    def point_collides_with_any_rect(self, x: int, y: int) -> bool:
        """ Check if given (x, y) point collides with any defined rectangle to avoid. """
        for rect in self.avoid_rects:
            if rect.contains_point(x, y):
                return True
        return False
        
    def choose_optimal_build_strategy(self) -> None:
        """ 
        Based on the start and end point coordinates, choose the best 
        wire building strategy out of:
            - Straight horizontal line.
            - Horizontal path.
            - Vertical path.
        """
        
        sx, sy = self.start
        ex, ey = self.end
        
        # Straight horizontal line.
        if ey == sy:
            return self.build_straight_hz_line()
        
        # Horizontal path.
        if ex >= sx:
            return self.build_horizontal_path()
        
        # Vertical line.
        path_x_range = range(sx, ex) if sx < ex else range(ex, sx)
        mid_points_y = (
            (math.floor((sy + ey) / 2)),
            (math.ceil((sy + ey) / 2)),
            (math.floor((sy + ey) / 2)) + 1,
            (math.ceil((sy + ey) / 2)) - 1,
        )  # It looks much better when the line turns near to the middle of Y.
        
        # Try to find common Y near to the middle of both points.
        for test_y in mid_points_y:
            collision = False
            
            for test_x in path_x_range:
                if self.point_collides_with_any_rect(test_x, test_y):
                    collision = True
                    break
            
            if not collision:
                return self.build_targetted_vertical_path(test_y)
        
        # Find any common Y.
        possible_target_y = range(sy, ey) if sy < ey else range(ey, sy)
        target_y = None
        
        # Try to find Y level not colliding with any rectangle.
        for test_y in possible_target_y:
            collision = False

            for test_x in path_x_range:
                if self.point_collides_with_any_rect(test_x, test_y):
                    collision = True
                    break
                    
            if not collision:
                target_y = test_y
                break
        
        # If there is no other option, but to go through any rect, find ANY common Y.
        if target_y is None:
            sy, ey = self.start[1], self.end[1]
        
            s_delta = -1 if sy > ey else 1
            e_delta = -1 if ey > sy else 1
            
            common_y = False
            inc_round = False
            
            while not common_y:
                inc_round = not inc_round

                if sy == ey:
                    target_y = sy
                    break
                
                if inc_round:
                    sy += s_delta
                else:
                    ey += e_delta

        return self.build_targetted_vertical_path(target_y)
        
    def build_straight_hz_line(self) -> None:
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
                
        # Add corners and build bridge.
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
            
        # Apply narrow corner fix.
        if self.end[1] == self.start[1] + 1 or self.end[1] == self.start[1] - 1:
            self.positioned_chars[(self.end[0], self.end[1])] = self.charset.fr
            