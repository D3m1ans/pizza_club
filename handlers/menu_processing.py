from itertools import product

from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_get_banner,
    orm_get_categories, orm_get_products, Paginator, orm_delete_from_cart, orm_reduce_product_in_cart, orm_add_to_cart,
    orm_get_user_carts,
)
from keyboard.inline_board import (
    get_user_catalog_btns,
    get_user_main_btns, get_products_btns, get_user_cart,
)

async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds


async def catalog(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds

def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def products(session, level, category, page):
    products = await orm_get_products(session, category_id=category)

    paginator = Paginator(products, page=page)
    product = paginator.get_page()

    product_0 = product[0]

    image = InputMediaPhoto(
        media=product_0.image,
        caption=f"Продукт: {product_0.name}\n"
                f"Описание: {product_0.description}\n"
                f"Цена: {round(product_0.price, 2)}\n"
                f"Товар {paginator.page} из {paginator.pages}",
    )

    pagination_btns = pages(paginator)

    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product_0.id,
    )

    return image, kbds

async def carts(session, level, menu_name, page, user_id, product_id):
    if menu_name == 'delete':
        await orm_delete_from_cart(session, user_id, product_id)
        if page > 1: page -= 1
    elif menu_name == 'decrement':
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id)
        if page > 1 and not is_cart: page -= 1
    elif menu_name == 'increment':
        await orm_add_to_cart(session, user_id, product_id)

    carts = await orm_get_user_carts(session, user_id)

    if not carts:
        banner = await orm_get_banner(session, 'cart')
        image = InputMediaPhoto(media=banner.image, caption=banner.description)

        kbds = get_user_cart(
            level = level,
            page=None,
            pagination_btns=None,
            product_id=None,
        )

    else:
        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()
        cart_0 = cart[0]

        cart_price = round(cart_0.quantity * cart_0.product.price, 2)
        total_price = round(sum(cart_0.quantity * cart_0.product.price for cart_0 in carts), 2)
        image = InputMediaPhoto(
            media=cart_0.product.image,
            caption=f"Продукт: {cart_0.product.name}\n"
                    f"Цена: {cart_0.product.price} * {cart_0.quantity} = {cart_price}\n"
                    f"Товар {paginator.page} из {paginator.pages} в корзине.\n"
                    f"Общая стоимость товаров в корзине: {total_price}",
        )

        paginator_btns = pages(paginator)

        kbds = get_user_cart(
            level = level,
            page=page,
            pagination_btns=paginator_btns,
            product_id=cart_0.product.id,
        )

        return image, kbds

async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
    product_id: int | None = None,
    user_id: int | None = None,
):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, product_id)