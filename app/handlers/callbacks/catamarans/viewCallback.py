from aiogram import types
from app import keyboard
from app.database.Models import catamaran


async def view_catamarans(callback: types.CallbackQuery):
    page = 1
    orders = await catamaran.get_orders()
    total_pages = (len(orders) + 4) // 5
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]

    if orders_page:
        orders_text, markup = await keyboard.generate_orders_text_and_markup(
            orders_page=orders_page,
            page=page,
            total_pages=total_pages
        )
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=orders_text,
            reply_markup=markup,
            parse_mode='Markdown'
        )


def register_callback_query_view_catamarans(dp):
    dp.register_callback_query_handler(view_catamarans, lambda c: c.data == 'view_catamarans')
