from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.order import get_order_by_id, change_status_order
from app.database.Models.route import get_route_by_id


class StatusOrder(StatesGroup):
    status_order = State()

def register_change_status_catamaran_handlers(dp, bot):
    @dp.callback_query_handler(text='status_order')
    async def status_order(callback: types.CallbackQuery):
        await StatusOrder.status_order.set()
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Введите ID заказа, который хотите изменить', reply_markup=kb.close2)


    @dp.message_handler(state=StatusOrder.status_order)
    async def status_order_by_id(message: types.Message, state: FSMContext):
        order_id = message.text
        order = await get_order_by_id(order_id)
        if order:
            route = get_route_by_id(order[5])
            change_status_order(order_id)
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

            await bot.send_message(
                chat_id=message.chat.id,
                text=f'Статус заказа с ID {order_id} изменен \n {text}',
                parse_mode='HTML',
                disable_web_page_preview=True,
                reply_markup=kb.main)
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} не найден', reply_markup=kb.main)
        await state.finish()