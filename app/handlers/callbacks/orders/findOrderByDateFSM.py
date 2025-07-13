import datetime as dt

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.order import get_order_by_date
from app.database.Models.route import get_route_by_id


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
            return

        db_date = await get_order_by_date(date)
        if db_date:
            text = ''
            for order in db_date:
                route = get_route_by_id(order[5])

                text += await kb.info_order_text(
                    order_id=order[0],
                    date_arrival=order[1],
                    time_arrival=order[2],
                    date_departure=order[3],
                    time_departure=order[4],
                    route_id=route,
                    customer_name=order[6],
                    phone_link=order[7],
                    additional_wishes=order[9],
                    status=order[8])

            buttons = await kb.generate_buttons_for_search('search_date_order')

            await message.answer(
                text=text,
                reply_markup=buttons,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
        else:
            await message.answer('❌ Заказ не найден.', reply_markup=kb.sort_orders)

        await state.finish()
