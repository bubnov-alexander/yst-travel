import datetime as dt

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.order import check_availability


class SearchFreeOrders(StatesGroup):
    search_free_orders = State()


def register_search_free_catamaran_handlers(dp, bot):
    @dp.callback_query_handler(text='search_free_order')
    async def search_free_orders(callback: types.CallbackQuery):
        await SearchFreeOrders.search_free_orders.set()
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='🟢 Напиши дату, на которую хочешь найти свободные заказы:',
                                    reply_markup=kb.close2)

    @dp.message_handler(state=SearchFreeOrders.search_free_orders)
    async def process_free_orders_search(message: types.Message, state: FSMContext):
        user_input = message.text

        try:
            try:
                parsed_date = dt.datetime.strptime(user_input, '%d.%m.%y').strftime('%d.%m.%Y')
            except ValueError:
                parsed_date = dt.datetime.strptime(user_input, '%d.%m.%Y').strftime('%d.%m.%Y')

            requested = {
                'catamarans': 0,
                'supboards': 0,
                'transfers': 0
            }

            can_book, remaining = await check_availability(
                date_start=parsed_date,
                date_end=parsed_date,
                requested=requested
            )

            response = f"📅 Доступность на {parsed_date}:\n"
            response += f"— Катамараны: {remaining['catamarans']} свободно\n"
            response += f"— SUP-доски: {remaining['supboards']} свободно\n"
            response += f"— Трансферы: {remaining['transfers']} доступно\n"

            await message.answer(response, reply_markup=kb.main)

        except Exception as e:
            await message.answer('❌ Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)
            return

        await state.finish()
