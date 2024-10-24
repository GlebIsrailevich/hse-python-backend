from http import HTTPStatus
from typing import Annotated, Iterable

from fastapi import HTTPException, Query
from pydantic import NonNegativeFloat, NonNegativeInt, PositiveFloat, PositiveInt

from lecture_2.hw.shop_api.api.schemas import ItemRequest
from lecture_2.hw.shop_api.api.shop_models import Cart, Item

cart_data = dict[int, Cart]()
item_data = dict[int, Item]()


def createNewItemInItems() -> int:
    item = Item.createItem()
    item_data[item.id] = item
    return item.id


def addItemToItems(itemRequest: ItemRequest):
    item = itemRequest.asItem()
    item_data[item.id] = item
    return item


def getItemById(id: int) -> Item:
    if id not in item_data.keys() or item_data[id].deleted:
        raise Exception
    return item_data[id].toResponse()


def createNewCartInCarts() -> int:
    cart = Cart.createCart()
    cart_data[cart.id] = cart
    return cart.id


def getCartById(id) -> Cart:
    return cart_data[id].toResponse()


def addItemToCart(cartId, itemId):
    cart = cart_data[cartId]
    for item in cart.items:
        if item.id == itemId:
            item.quantity += 1
            cart.price += item.price
            break
    else:
        item = item_data[itemId]
        cart.items.append(item.toCartItem())
        cart.price += item.price


def replaceItemWithId(itemId, item: Item = None):
    if itemId not in item_data.keys():
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
    if item is None:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Item not found"
        )

    item_data[itemId] = item
    return item


def deleteItemFromItems(itemId):
    item_data[itemId].deleted = True
    return ItemRequest(
        id=item_data[itemId].id,
        name=item_data[itemId].name,
        price=item_data[itemId].price,
        deleted=item_data[itemId].deleted,
    )


def changeItemWithId(itemId, item: Item):
    if itemId not in item_data.keys() or item_data[itemId].deleted is True:
        raise HTTPException(
            status_code=HTTPStatus.NOT_MODIFIED, detail="Item not found"
        )
    item_data[itemId].id = item.id or item_data[itemId].id
    item_data[itemId].name = item.name or item_data[itemId].name
    item_data[itemId].price = item.price or item_data[itemId].price
    if (
        item_data[itemId].id is None
        or item_data[itemId].name is None
        or item_data[itemId].price is None
    ):
        raise HTTPException(
            HTTPStatus.NOT_MODIFIED,
            "Item was not modified",
        )
    return ItemRequest(
        id=item_data[itemId].id or itemId,
        name=item_data[itemId].name,
        price=item_data[itemId].price,
        deleted=item_data[itemId].deleted,
    )


def getCartList(
    offset: Annotated[NonNegativeInt, Query()] = 0,
    limit: Annotated[PositiveInt, Query()] = 10,
    min_price: Annotated[NonNegativeFloat, Query()] = 0,
    max_price: Annotated[PositiveFloat, Query()] = None,
    min_quantity: Annotated[NonNegativeInt, Query()] = 0,
    max_quantity: Annotated[NonNegativeInt, Query()] = None,
) -> Iterable[Cart]:
    result = []

    for cart in cart_data.values():
        if min_price is not None and cart.price < min_price:
            continue
        if max_price is not None and cart.price > max_price:
            continue

        if (
            min_quantity is not None
            and sum(item.quantity for item in cart.items) < min_quantity
        ):
            continue
        if (
            max_quantity is not None
            and sum(item.quantity for item in cart.items) > max_quantity
        ):
            continue

        result.extend(
            [item.toResponse() for item in cart.items[offset : offset + limit]]
        )

    return result
