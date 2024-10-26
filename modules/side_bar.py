from modules import terminal
from modules import style
from modules import chars
from modules import pos
from modules import ui

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules import nodes


class SideBarComponent(ui.TextUIComponent):
    def __init__(self) -> None:
        self.is_focused = False
        self.is_folded = False
        self.width = 22
        self.__focused_object: "nodes.Collection | nodes.NodeFactory | None" = None
        self.in_factories_level: bool = False
        
        self.collections_folds: dict["nodes.Collection", bool] = {}
        self.collections_array: list["nodes.Collection"] = []
        
        super().__init__()

    def set_collections(self, collections) -> None:
        self.collections_array = [c.value for c in collections]
        self.collections_folds = {
            collection.value: False for collection in collections
        }
        
        self.__focused_object = self.collections_array[0]
        
    def flip(self) -> None:
        """ Flip is_folded value. """
        self.is_folded = not self.is_folded
        ui.render_all()
    
    def focus(self) -> None:
        self.is_folded = False
        self.is_focused = True
        ui.render_all()
        
    def unfocus(self) -> None:
        self.is_focused = False
        ui.render_all()
    
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
    
    def spawn_node(self) -> "nodes.Node | None":
        if not self.in_factories_level:
            return None
        
        return self.__focused_object.build_instance()
    
    def get_rect(self) -> pos.Rect | None:
        if self.is_folded:
            return None
            
        x, y = 0, 0
        w, h = self.width - 1, terminal.get_h()
            
        if self.get_border_connections().e:
            w += 1
            
        return pos.Rect(pos.Position(x, y), w, h)
    
    def get_border_connections(self) -> style.BorderConnection:
        return style.BorderConnection(
            e = True,
        )
    
    def draw_borders(self) -> None:
        rect = self.get_rect()
        if rect is not None:
            style.outline_rect(rect, self.get_border_connections(), not self.is_focused)
            
    def render(self) -> None:
        content_rect = self.get_rect()
        if content_rect is None:
            return
        
        content_rect.pos.x += 1
        self.clean_contents(content_rect)

        line_index = 0
        
        for collection, is_folded in self.collections_folds.items():
            icon = chars.COLLECTION_FOLDED if is_folded else chars.COLLECTION_UNFOLDED
            styles = [style.AnsiStyle.DIM] if not self.is_focused else [style.AnsiStyle.ITALIC, style.AnsiStyle.INVERT] if self.__focused_object == collection else []
            
            content = style.tcolor(icon, collection.color, styles=[style.AnsiStyle.DIM] if not self.is_focused else []) + " "
            content += style.tcolor(f"{collection.name}", collection.color, styles=styles)
            
            terminal.set_cursor_pos(3, 2 + line_index)
            print(content)
            
            if not is_folded:
                for i, factory in enumerate(collection.factories):
                    line_index += 1
                    
                    node_type_char = chars.FUNCTION if factory.is_function_node() else chars.FLOW_NODE if factory.is_flow_node() else ""
                    node_type_indicator = " " + style.tcolor(node_type_char, factory.outputs[0].data_type.color, styles=[style.AnsiStyle.DIM]) if node_type_char else ""

                    styles = [style.AnsiStyle.DIM] if not self.is_focused else [style.AnsiStyle.ITALIC, style.AnsiStyle.INVERT] if factory == self.__focused_object  else []
                    tree_char = chars.ROUNDED_LINE.vr if (i + 1) != len(collection.factories) else chars.ROUNDED_LINE.sw

                    terminal.set_cursor_pos(5, 2 + line_index)
                    
                    print(style.tcolor(tree_char + "╴", collection.color, styles=[style.AnsiStyle.DIM] if not self.is_focused else []) + style.tcolor(factory.title, styles=styles) + node_type_indicator)

            line_index += 1
        
    


side_bar = SideBarComponent()
