from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import datetime as dt

from app.database.Models import catamaran
from app import keyboard as kb

class SearchFreeOrders(StatesGroup):
    search_free_orders = State()

def register_search_free_catamaran_handlers(dp, bot):
    @dp.callback_query_handler(text='search_free_order')
    async def search_free_orders(callback: types.CallbackQuery):
        await SearchFreeOrders.search_free_orders.set()
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='🟢 Напиши дату, на которую хочешь найти свободные заказы:', reply_markup=kb.close2)


    @dp.message_handler(state=SearchFreeOrders.search_free_orders)
    async def process_free_orders_search(message: types.Message, state: FSMContext):
        date = message.text

        try:
            try:
                date = dt.datetime.strptime(date, '%d.%m.%y').strftime('%d.%m.%Y')
            except:
                date = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%d.%m.%Y')

            db_date = await catamaran.get_available_catamarans(date)
            if db_date:
                await message.answer(text=f'Свободных мест на эту дату {db_date}', reply_markup=kb.main)
            else:
                await message.answer('Свободных заказов не найдено.', reply_markup=kb.main)
        except Exception as e:
            print(e)
            await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)

        await state.finish()