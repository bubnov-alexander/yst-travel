from aiogram import types

from app import keyboard
from app.database.Models.order import get_orders_with_catamarans_sorted
from app.keyboard import selection_of_sorts


def register_selection_of_sorts_by_date(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("sort_date_"))
    async def search_date_order(callback: types.CallbackQuery):
        data_parts = callback.data.split("_", 2)
        service = data_parts[2]

        orders = await get_orders_with_catamarans_sorted(service)

        if not orders:
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text="Заказы с выбранным сервисом не найдены.",
                reply_markup=keyboard.sort_orders
            )
            return

        page = 1
        total_pages = (len(orders) + 4) // 5
        start_index = (page - 1) * 5
        end_index = start_index + 5
        orders_page = orders[start_index:end_index]

        orders_text, markup = await keyboard.generate_orders_text_and_markup(
            orders_page, page, total_pages, is_sorted=True
        )

        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=orders_text,
            reply_markup=markup,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
