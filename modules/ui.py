from modules import terminal
from modules import style
from modules import pos

from abc import ABC, abstractmethod


initalized_components: list["TextUIComponent"] = []


def render_all(skip_component: "TextUIComponent | None" = None) -> None:
    """ Render all initialized UI components and their borders. """
    style.clear_screen()

    for component in initalized_components:
        if component == skip_component:
            continue
        
        component.draw_borders()
        component.render()


class TextUIComponent(ABC):
    def __init__(self) -> None:
        initalized_components.append(self)

    @abstractmethod
    def get_rect(self) -> pos.Rect | None:
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
        
    def clean_contents(self, custom_rect: pos.Rect | None = None) -> None:
        """ Clean component's contents (not including border.) """
        area = self.get_rect()
        if custom_rect is not None:
            area = custom_rect
        
        if area is None:
            return
        
        border_connections = self.get_border_connections()
        
        yrange = range(area.pos.y + 2, area.pos.y + area.h)
        if border_connections.n:
            yrange = range(area.pos.y + 2, area.pos.y + area.h - 1)
            
        xrange = range(area.pos.x + 1, area.pos.x + area.w)
        if border_connections.e:
            xrange = range(area.pos.x + 1, area.pos.x + area.w - 1)
        
        for y in yrange:
            for x in xrange:
                terminal.set_cursor_pos(x, y)
                print(" ", end="")
                
    def draw_borders(self) -> None:
        """ Draw borders inside component's rectangle. """
        rect = self.get_rect()
        if rect is not None:
            style.outline_rect(rect, self.get_border_connections())
