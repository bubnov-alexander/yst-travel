from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.Models import catamaran
from app import keyboard as kb
import datetime as dt

class FindOrderByDate(StatesGroup):
    search_order_by_date = State()

def register_find_order_by_date_handlers(dp, bot):
    @dp.callback_query_handler(text='search_date_order')
    async def search_date_order(callback: types.CallbackQuery):
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='🟢 Напиши дату заказа который хочешь найти:', reply_markup=kb.close2)
        await FindOrderByDate.search_order_by_date.set()


    @dp.message_handler(state=FindOrderByDate.search_order_by_date)
    async def process_order_search(message: types.Message, state: FSMContext):
        date = message.text

        try:
            try:
                date = dt.datetime.strptime(date, '%d.%m.%y').strftime('%d.%m.%Y')
            except:
                date = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%d.%m.%Y')

            db_date = await catamaran.get_order_by_date(date)
            if db_date:
                for i in db_date:
                    text = await kb.info_text(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10])
                    await message.answer(text, reply_markup=kb.main)
            else:
                await message.answer('Заказ не найден.', reply_markup=kb.sort_orders)
        except Exception as e:
            print(e)
            await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)

        await state.finish()