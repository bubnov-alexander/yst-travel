from aiogram import types
from app import keyboard
from app.database.Models import catamaran

async def search_order(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text='Выбери нужный вариант сортировки', reply_markup=keyboard.sort_orders)

def register_callback_query_get_sort_buttons_catamaran(dp):
    dp.register_callback_query_handler(search_order, lambda c: c.data == 'search_order')