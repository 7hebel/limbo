from modules import terminal
from modules import measure
from modules import style

from abc import ABC, abstractmethod


SCREEN_BUSY: bool = False  # True whenever display shouldn't be overdrawn by UI. (execution/compilation)

initalized_components: list["TextUIComponent"] = []


def render_all(skip_component: "TextUIComponent | None" = None) -> None:
    """ Render all initialized UI components and their borders. """
    if SCREEN_BUSY:
        return
    
    for component in initalized_components:
        if component == skip_component:
            continue

        component.draw_borders()
        
        if hasattr(component, "optimized_renderer"):  # I couldn't find any better solution :/
            component.optimized_renderer.force_render()

        else:
            component.clean_contents()
            component.render()


class TextUIComponent(ABC):
    def __init__(self) -> None:
        initalized_components.append(self)

    @abstractmethod
    def get_rect(self) -> measure.Rect | None:
        """ Returns component's rectangle including borders. None if component is not visible. """
        ...

    @abstractmethod
    def get_border_connections(self) -> style.BorderConnection:
        """ Check which borders might connect with other component's borders. """
        ...

    @abstractmethod
    def render(self) -> None:
        """ Render component's contents (not including border.) """
        ...

    def clean_contents(self, custom_rect: measure.Rect | None = None) -> None:
        """ Clean component's contents (not including border.) """
        area = self.get_rect()
        if custom_rect is not None:
            area = custom_rect
        if area is None:
            return

        yrange = range(area.pos.y + 2, area.pos.y + area.h)
        xrange = range(area.pos.x + 1, area.pos.x + area.w)

        for y in yrange:
            for x in xrange:
                terminal.set_cursor_pos(x, y)
                print(" ", end="")

    def draw_borders(self) -> None:
        """ Draw borders inside component's rectangle. """
        rect = self.get_rect()
        if rect is not None:
            style.outline_rect(rect, self.get_border_connections())


class OptimizedRenderer:
    def __init__(self, component: TextUIComponent) -> None:
        self.current: dict[tuple[int, int], str] = {}
        self.buffer: dict[tuple[int, int], str] = {}
        self.component = component
        self.requires_force_redraw = False
        
    def feed_buffer(self, pos_chars: dict[tuple[int, int], str]) -> None:
        self.buffer.update(pos_chars)

    def force_render(self) -> None:
        self.requires_force_redraw = False
        self.current = {}
        self.buffer = {}
        
        self.component.clean_contents()
        self.component.draw_borders()
        self.component.render()

    def diff_render(self) -> None:
        if self.requires_force_redraw:
            return self.force_render()
        
        curr_keys = set(self.current.keys())
        buff_keys = set(self.buffer.keys())
        work_rect: measure.Rect = self.component.work_rect()

        for (x, y) in curr_keys.difference(buff_keys):
            if work_rect.contains_point(x, y):
                terminal.write_at(" ", x, y)

        for pos in sorted(buff_keys, key=lambda pos: pos[1]):
            if pos not in self.buffer:
                continue
            
            x, y = pos
            content = self.buffer[pos]

            if self.current.get(pos) != content and work_rect.contains_point(x, y):
                terminal.write_at(content, x, y)

        self.current = self.buffer
        self.buffer = {}
        