from ..entity.item import Item


class ItemService:
    def __init__(self, in_memory_item_repository):
        self.in_memory_item_repository = in_memory_item_repository

    def create_item( self , name):
        return Item( name , 1)
