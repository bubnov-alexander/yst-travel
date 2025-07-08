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
        date_text = message.text.strip()

        for fmt in ('%d.%m.%Y', '%d.%m.%y'):
            try:
                date = dt.datetime.strptime(date_text, fmt).strftime('%d.%m.%Y')
                break
            except ValueError:
                date = None

        if date is None:
            await message.answer('❌ Дата должна быть в формате ДД.ММ.ГГ или ДД.ММ.ГГГГ', reply_markup=kb.close2)
            await state.finish()
            return

        db_date = await catamaran.get_catamaran_by_date(date)
        if db_date:
            text = ''
            for i in db_date:
                text += await kb.info_text(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11])
            await message.answer(
                text=text,
                reply_markup=kb.back_to_search_order,
                parse_mode = 'HTML',
                disable_web_page_preview = True
            )
        else:
            await message.answer('❌ Заказ не найден.', reply_markup=kb.sort_orders)

        await state.finish()
