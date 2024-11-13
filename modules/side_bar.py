from modules import terminal
from modules import measure
from modules import string
from modules import style
from modules import chars
from modules import ui

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.nodes.collection import Collection
    from modules.nodes.factory import NodeFactory 
    from modules.nodes.node import Node


class SideBarComponent(ui.TextUIComponent):
    def __init__(self) -> None:
        self.is_focused = False
        self.is_folded = False
        self.width = 22
        self.optimized_renderer = ui.OptimizedRenderer(self)
        self.in_factories_level: bool = False
        self.__focused_object: "Collection | NodeFactory | None" = None
        self.__workspace_id: str | None = None
        
        self.collections_folds: dict["Collection", bool] = {}
        self.collections_array: list["Collection"] = []
        
        self.help_keys = {
            "(ctrl?)" + chars.VT_ARROWS: "navigate",
            chars.HZ_ARROWS + "/enter": "(un)fold collection",
            "space/enter": "spawn node",
            "esc/tab": "exit"
        }
        
        super().__init__()

    def set_collections(self, collections: list["Collection"]) -> None:
        self.collections_array = [c.value for c in collections]
        self.collections_folds = {
            collection.value: False for collection in collections
        }
        
        self.__focused_object = self.collections_array[0]
        
    def set_workspace_id(self, workspace_id: str) -> None:
        self.__workspace_id = workspace_id
        
    def flip(self) -> None:
        """ Flip is_folded value. """
        self.is_folded = not self.is_folded
        ui.render_all()
    
    def focus(self) -> None:
        self.is_folded = False
        self.is_focused = True
        self.render()
        
    def unfocus(self) -> None:
        self.is_focused = False
        self.render()
    
    def move_focus_down(self) -> None:
        if not self.in_factories_level:
            collection_index = self.collections_array.index(self.__focused_object)

            if not self.collections_folds[self.__focused_object] and self.__focused_object.factories:
                self.in_factories_level = True
                self.__focused_object = self.__focused_object.factories[0]
                
            else:
                new_index = collection_index + 1
                
                if len(self.collections_array) - 1 < new_index:
                    new_index = 0
                    
                self.__focused_object = self.collections_array[new_index]
            
        else:
            factories = self.__focused_object.collection.factories
            new_index = factories.index(self.__focused_object) + 1
            
            if len(factories) - 1 < new_index:
                self.in_factories_level = False
                collection = self.__focused_object.collection
                new_index = self.collections_array.index(collection) + 1
                
                if len(self.collections_array) - 1 < new_index:
                    new_index = 0
                    
                self.__focused_object = self.collections_array[new_index]
            
            else:
                self.__focused_object = factories[new_index]
            
        self.render()
    
    def move_focus_up(self) -> None:
        if not self.in_factories_level:
            collection_index = self.collections_array.index(self.__focused_object)
            new_index = collection_index - 1
            
            if new_index < 0:
                new_index = len(self.collections_array) - 1
                
            new_collection = self.collections_array[new_index]
            
            if not self.collections_folds[new_collection] and new_collection.factories:
                self.in_factories_level = True
                self.__focused_object = new_collection.factories[-1]
                
            else:
                self.__focused_object = new_collection
            
        else:
            factories = self.__focused_object.collection.factories
            new_index = factories.index(self.__focused_object) - 1
            
            if new_index < 0:
                self.in_factories_level = False
                self.__focused_object = self.__focused_object.collection
            
            else:
                self.__focused_object = factories[new_index]

        self.render()
        
    def move_focus_category_down(self) -> None:
        if self.in_factories_level:
            self.__focused_object = self.__focused_object.collection
            self.in_factories_level = False
        
        collection_index = self.collections_array.index(self.__focused_object)
        new_index = collection_index + 1
        if len(self.collections_array) - 1 < new_index:
            new_index = 0
            
        self.__focused_object = self.collections_array[new_index]
        self.render()
        
    def move_focus_category_up(self) -> None:
        if self.in_factories_level:
            self.__focused_object = self.__focused_object.collection
            self.in_factories_level = False
            return self.render()
        
        collection_index = self.collections_array.index(self.__focused_object)
        new_index = collection_index - 1
        if new_index < 0:
            new_index = len(self.collections_array) - 1
            
        self.__focused_object = self.collections_array[new_index]
        self.render()
        
    def unfold_collection(self) -> None:
        if self.in_factories_level:
            return
        
        self.collections_folds[self.__focused_object] = False
        self.render()
        
    def fold_collection(self) -> None:
        collection = self.__focused_object
        if self.in_factories_level:
            collection = self.__focused_object.collection
        
        self.collections_folds[collection] = True
        self.in_factories_level = False
        self.__focused_object = collection
        self.render()
        
    def flip_collection_fold(self) -> None:
        if self.in_factories_level:
            return
        
        collection = self.__focused_object
        self.collections_folds[collection] = not self.collections_folds[collection]
        self.render()
    
    def spawn_node(self) -> "Node | None":
        if not self.in_factories_level:
            return None
        
        if self.__workspace_id is None:
            raise RuntimeError("cannot spawn node without workspace_id linked.")
        
        return self.__focused_object.build_instance(self.__workspace_id)
    
    def get_rect(self) -> measure.Rect | None:
        if self.is_folded:
            return None
            
        x, y = 0, 0
        w, h = self.width - 1, terminal.get_h()
            
        if self.get_border_connections().e:
            w += 1
            
        return measure.Rect(measure.Position(x, y), w, h)
    
    def work_rect(self) -> measure.Rect | None:
        if self.is_folded:
            return None
            
        rect = self.get_rect()
        work_pos = measure.Position(1, 1)
        return measure.Rect(work_pos, rect.w - 1, rect.h - 1)
    
    def get_border_connections(self) -> style.BorderConnection:
        return style.BorderConnection(
            e = True,
        )
    
    def draw_borders(self) -> None:
        rect = self.get_rect()
        if rect is not None:
            style.outline_rect(rect, self.get_border_connections(), not self.is_focused)
            
    def total_rows(self) -> int:
        total_rows = 0
        for collection, is_folded in self.collections_folds.items():
            total_rows += 1
            
            if not is_folded:
                total_rows += len(collection.factories)
                
        return total_rows
        
    def overflowing_rows(self) -> int:
        max_rows = self.get_rect().h - 2
        overflowing = self.total_rows() - max_rows
        return overflowing if overflowing >= 0 else 0
    
    def focused_object_index(self) -> int:
        index = -1
        
        for collection, is_folded in self.collections_folds.items():
            index += 1
            
            if self.__focused_object == collection:
                return index
            
            if not is_folded:
                for factory in collection.factories:
                    index += 1
                    
                    if self.__focused_object == factory:
                        return index
                    
        return index if index >= 0 else 0

    def render(self) -> None:
        content_rect = self.get_rect()
        if content_rect is None:
            return
    
        content_rect.pos.x += 1
        content_rect.w -= 1
    
        visible_rows = self.total_rows() - self.overflowing_rows()
        scroll_range = range(0, visible_rows)

        if self.focused_object_index() + 1 > visible_rows:
            scroll_y = self.focused_object_index() - visible_rows + 2
            scroll_range = range(scroll_y, visible_rows + scroll_y)
            
        line_index = 0
        scroll_skip_indexes = 0
        
        for collection, is_folded in self.collections_folds.items():
            icon = chars.COLLECTION_FOLDED if is_folded else chars.COLLECTION_UNFOLDED
            styles = [style.AnsiStyle.DIM] if not self.is_focused else [style.AnsiStyle.ITALIC, style.AnsiStyle.INVERT] if self.__focused_object == collection else []
            
            content = string.ColoredStringObject()
            content.feed_char(icon, collection.color, styles=[style.AnsiStyle.DIM] if not self.is_focused else [])
            content.feed_char(" ")
            content.feed_string(collection.name, collection.color, styles)
            
            if line_index in scroll_range:
                term_line = 2 + line_index - scroll_skip_indexes
            
                for pos, char in content.stream_positioned_chars(3, term_line):
                    self.optimized_renderer.feed_buffer({pos: char})

            else:
                scroll_skip_indexes += 1
            
            if is_folded:
                line_index += 1
                continue
            
            for i, factory in enumerate(collection.factories):
                line_index += 1
                
                styles = [style.AnsiStyle.DIM] if not self.is_focused else [style.AnsiStyle.ITALIC, style.AnsiStyle.INVERT] if factory == self.__focused_object  else []
                tree_char = chars.ROUNDED_LINE.vr if (i + 1) != len(collection.factories) else chars.ROUNDED_LINE.sw
                
                content = string.ColoredStringObject()
                content.feed_string(tree_char + "╴", collection.color, styles=[style.AnsiStyle.DIM] if not self.is_focused else [])
                content.feed_string(factory.title, styles=styles)
                content.feed_char(" ")
                
                if factory.get_char_indicator():
                    content.feed_string(factory.get_char_indicator(), factory.output_datatype().color, styles=[style.AnsiStyle.DIM])

                if line_index in scroll_range:
                    term_line = 2 + line_index - scroll_skip_indexes
                    
                    for pos, char in content.stream_positioned_chars(5, term_line):
                        self.optimized_renderer.feed_buffer({pos: char})
                    
                else:
                    scroll_skip_indexes += 1

            line_index += 1
        
        self.optimized_renderer.diff_render()
    
    
side_bar = SideBarComponent()
