from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3

from app import keyboard as kb
from app.database.Models.route import add_new_route


class MyFSM(StatesGroup):
    add_route = State()
    add_point_a = State()
    add_point_b = State()
    add_customer_name = State()


def register_add_route_handlers(dp, bot):
    @dp.callback_query_handler(lambda c: c.data == 'add_new_route', state=MyFSM.add_route)
    async def handle_add_new_route(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("🅰️ Введите название пункта А (откуда стартует маршрут):",
                                         reply_markup=kb.close2)
        await MyFSM.add_point_a.set()

    @dp.message_handler(state=MyFSM.add_point_a)
    async def save_point_a(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['point_a'] = message.text.strip()

        await message.answer("🅱️ Теперь введите название пункта B (куда направляется маршрут):", reply_markup=kb.close2)
        await MyFSM.add_point_b.set()

    @dp.message_handler(state=MyFSM.add_point_b)
    async def save_point_b(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            point_a = data['point_a']
            point_b = message.text.strip()

            route_id = add_new_route(
                point_a=point_a,
                point_b=point_b
            )

            data['route_id'] = route_id

        await message.answer("✅ Маршрут сохранён")
        await message.answer("👤 Напиши ФИО заказчика", reply_markup=kb.close2)

        await MyFSM.next()
