from app.adapters.in_memory_item_repository import InMemoryItemRepository

from app.domain.service.item_service import ItemService


def test_create_item_returns_item_with_id ():
    service = ItemService(InMemoryItemRepository())

    item =  service.create_item(name="Notebook")

    assert item is not None
    assert item.name == "Notebook"


