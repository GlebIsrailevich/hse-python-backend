from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import NonNegativeInt, PositiveFloat, PositiveInt

from lecture_2.hw.shop_api.shop.shop_queries import (
    Item,
    ItemRequest,
    addItemToCart,
    addItemToItems,
    changeItemWithId,
    createNewCartInCarts,
    createNewItemInItems,
    deleteItemFromItems,
    getCartById,
    getCartList,
    getItemById,
    replaceItemWithId,
)

cart_router = APIRouter(prefix="/cart")
item_router = APIRouter(prefix="/item")


@cart_router.post(
    "/",
    responses={
        HTTPStatus.CREATED: {
            "description": "Successfully created new cart",
        }
    },
    status_code=HTTPStatus.CREATED,
)
def create_cart():
    id = createNewCartInCarts()
    return JSONResponse(
        content={"id": id},
        status_code=HTTPStatus.CREATED,
        headers={"location": f"/cart/{id}"},
    )


@cart_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Cart doesn't exist",
        },
    },
)
async def get_cart_by_id(id: int):
    return getCartById(id)


@cart_router.post(
    "/{cart_id}/add/{item_id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully added item to cart",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Cart or item doesn't exist",
        },
    },
)
def add_item_to_cart(cart_id: int, item_id: int):
    return addItemToCart(cart_id, item_id)


@cart_router.get("/")
def getCarts(
    offset: NonNegativeInt = 0,
    limit: PositiveInt = 10,
    min_price: PositiveFloat = None,
    max_price: PositiveFloat = None,
    min_quantity: NonNegativeInt = None,
    max_quantity: NonNegativeInt = None,
):
    try:
        carts_many = getCartList(
            offset, limit, min_price, max_price, min_quantity, max_quantity
        )
        return carts_many
    except Exception:
        return JSONResponse(
            content={"error": "Carts not found"}, status_code=HTTPStatus.NOT_FOUND
        )


@item_router.post("/")
def postItem_many(item: ItemRequest = None):
    if item is None:
        id = createNewItemInItems()
        return JSONResponse(
            content={"id": id},
            status_code=HTTPStatus.CREATED,
            headers={"location": f"/item/{id}"},
        )
    else:
        item = addItemToItems(item)
        return JSONResponse(
            content=item.toResponse(),
            status_code=HTTPStatus.CREATED,
            headers={"location": f"/item/{item.id}"},
        )


@item_router.get(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item doesn't exist",
        },
    },
)
def get_item(id: int):
    try:
        return getItemById(id)
    except Exception:
        return JSONResponse(
            content={"error": "Item not found"}, status_code=HTTPStatus.NOT_FOUND
        )


@item_router.put("/{id}")
def replace_item(id: int, item: ItemRequest = None):
    if item is not None:
        item = item.asItem()
    try:
        item = replaceItemWithId(id, item)
        return JSONResponse(content=item.toResponse(), status_code=HTTPStatus.OK)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail="Item not found")


@item_router.patch(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item doesn't exist",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY: {
            "description": "Cannot patch field deleted",
        },
        HTTPStatus.NOT_MODIFIED: {
            "description": "Not modified",
        },
    },
)
def change_item(id: int, newFields: dict = {}):
    try:
        for field in newFields.keys():
            if field not in ItemRequest.model_fields:
                raise HTTPException(
                    status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                    detail="Field not found",
                )

        item = Item(
            id=newFields.get("id") or id,
            name=newFields.get("name"),
            price=newFields.get("price"),
        )

        return changeItemWithId(id, item)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail="Item not modified")


@item_router.delete(
    "/{id}",
    responses={
        HTTPStatus.OK: {
            "description": "Successfully returned requested item",
        },
        HTTPStatus.NOT_FOUND: {
            "description": "Item doesn't exist",
        },
    },
)
def delete_item(id: int):
    try:
        deleteItemFromItems(id)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")
