from aiogram import types
from app import keyboard
from app.database.Models import catamaran

async def sort_date_catamaran(callback: types.CallbackQuery):
    page = 1
    orders = await catamaran.sort_date_order()
    total_pages = (len(orders) + 4) // 5
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]

    # Используйте функцию для генерации текста и разметки
    orders_text, markup = await keyboard.generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted=True)

    # Обновите сообщение с новым текстом и разметкой
    await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text=orders_text, reply_markup=markup, parse_mode='Markdown')

def register_callback_query_sort_by_date_catamaran(dp):
    dp.register_callback_query_handler(sort_date_catamaran, lambda c: c.data == 'sort_date_order')
