from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.Models import catamaran
from app import keyboard as kb
from app.database.Models.order import get_order_by_id
from app.database.Models.route import get_route_by_id


class FindOrderById(StatesGroup):
    search_order = State()


def register_find_order_by_id_handlers(dp, bot):
    @dp.callback_query_handler(text='search_id_order')
    async def search_order(callback: types.CallbackQuery):
        await FindOrderById.search_order.set()
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Введите ID заказа, который хотите найти',
            reply_markup=kb.close4)

    @dp.message_handler(state=FindOrderById.search_order)
    async def search_order_by_id(message: types.Message, state: FSMContext):
        try:
            order_id = int(message.text)
        except ValueError:
            await message.answer('❌ ID заказа должен быть числом', reply_markup=kb.main)
            return

        order = await get_order_by_id(order_id)

        if order:
            route = get_route_by_id(order[5])

            text = await kb.info_order_text(
                order_id=order[0],
                date_arrival=order[1],
                time_arrival=order[2],
                date_departure=order[3],
                time_departure=order[4],
                route_id=route,
                customer_name=order[6],
                phone_link=order[7],
                additional_wishes=order[9],
                status=order[8]
            )

            buttons = await kb.generate_buttons_for_search('search_id_order')

            await message.answer(
                text=text,
                reply_markup=buttons,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
        else:
            await message.answer(
                text=f'❌ Заказ с ID <b>{order_id}</b> не найден',
                reply_markup=kb.main,
                parse_mode='HTML',
            )

        await state.finish()
