from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_products
from filters.chat_types import ChatFilters
from keyboard.inline_board import get_callback_btns

user_private_router = Router()
user_private_router.message.filter(ChatFilters(['private']))

@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}, я виртуальный помощник",
                         reply_markup=get_callback_btns(btns={
                             'Нажми на меня': 'some_1'
                         }))

@user_private_router.callback_query(F.data.startswith('some_'))
async def counter(callback: types.CallbackQuery):
    number = int(callback.data.split("_")[-1])

    await callback.message.edit_text(
        text=f'Нажатий: {number}', reply_markup=get_callback_btns(btns={
            'Нажми еще': f'some_{number+1}'
        })
    )

# @user_private_router.message(Command("start"))
# async def start(message: types.Message):
#     await message.answer(f"Добро пожаловать, {message.from_user.first_name}!", reply_markup=reply_board.start_kb)
#
# @user_private_router.message(F.text.lower() == 'меню')
# @user_private_router.message(Command("menu"))
# async def menu(message: types.Message, session: AsyncSession):
#     for product in await orm_get_products(session):
#         await message.answer_photo(
#             product.image,
#             caption=f"Товар: {product.name}\n"
#                     f"Описание товара: {product.description}\n"
#                     f"Цена: {round(product.price, 2)}"
#         )
#     await message.answer("Вот наше меню ⏫", reply_markup=reply_board.del_keyboard)
#
# @user_private_router.message(F.text.lower() == 'о магазине')
# @user_private_router.message(Command("about"))
# async def about(message: types.Message):
#     await message.answer("Наше описание")
#
# @user_private_router.message((F.text.lower().contains('оплат') or F.text.lower() == 'варианты оплаты'))
# @user_private_router.message(Command("payment"))
# async def payment(message: types.Message):
#     text = as_marked_section(
#         "Варианты оплаты",
#         "Картой в боте",
#         "При получении карта/кеш",
#         "В заведении",
#         marker='✅ '
#         )
#     await message.answer(text.as_html())
#
# @user_private_router.message((F.text.lower().contains('доставк') or F.text.lower() == 'варианты доставки'))
# @user_private_router.message(Command("shipping"))
# async def shipping(message: types.Message):
#     text = as_marked_section(
#         "Варианты доставки:",
#         "Курьер",
#         "Самовывоз (сейчас прибегу, заберу)",
#         "Покушаю у вас (сейчас прибегу)",
#         marker='✅ '
#     )
#     await message.answer(text.as_html(), reply_markup=reply_board.shipping_kb)
#
# @user_private_router.message(F.contact)
# async def get_contact(message: types.Message):
#     await message.answer(f"номер получен")
#     await message.answer(str(message.contact.phone_number))
#
# @user_private_router.message(F.location)
# async def get_location(message: types.Message):
#     await message.answer(f"локация получена")
#     await message.answer(f'Локация: {str(message.location.latitude), str(message.location.longitude)}')