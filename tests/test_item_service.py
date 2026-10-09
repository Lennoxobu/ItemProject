from app.domain.ports.in_memory_item_repository import InMemoryItemRepository
from app.domain.service.item_service import ItemService


def test_create_item_returns_item_with_name():
    service = ItemService(InMemoryItemRepository())

    item = service.create_item(name="Notebook")

    assert item is not None
    assert item.name == "Notebook"



def test_created_item_should_have_an_id():
    service = ItemService(InMemoryItemRepository())

    item = service.create_item(name="Notebook")

    assert item is not None
    assert item.id == 1


def test_two_created_items_should_have_different_ids():
    service = ItemService(InMemoryItemRepository())

    item1 = service.create_item(name="Notebook")
    item2 = service.create_item(name="Pen")


    assert item1 is not None and item2 is not None
    assert item1.id != item2.id



