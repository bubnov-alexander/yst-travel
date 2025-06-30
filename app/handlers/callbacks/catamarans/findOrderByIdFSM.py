from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.Models import catamaran
from app import keyboard as kb

class FindOrderById(StatesGroup):
    search_order = State()

def register_find_order_by_id_handlers(dp, bot):
    @dp.callback_query_handler(text='search_id_order')
    async def search_order(callback: types.CallbackQuery):
        await FindOrderById.search_order.set()
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Введите ID заказа, который хотите найти', reply_markup=kb.close4)


    @dp.message_handler(state=FindOrderById.search_order)
    async def search_order_by_id(message: types.Message, state: FSMContext):
        if message.text != int or message.text == '':
            try:
                order_id = int(message.text)
            except:
                await bot.send_message(chat_id=message.chat.id, text='ID заказа должен быть числом', reply_markup=kb.main)
                await state.finish()

        order = await catamaran.get_order_by_id(order_id)
        if order:
            text = await kb.info_text(order[0], order[1], order[2], order[3], order[4], order[5], order[6], order[7],
                                      order[8], order[9], order[10])
            await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=kb.main)
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} не найден', reply_markup=kb.main)
        await state.finish()