from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.Models import catamaran
from app import keyboard as kb

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
        order = await catamaran.get_catamaran_quantity(order_id)
        if order:
            await catamaran.status_catamaran(order_id)
            await bot.send_message(chat_id=message.chat.id, text=f'Статус заказа с ID {order_id} изменен',
                                   reply_markup=kb.main)
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} не найден', reply_markup=kb.main)
        await state.finish()