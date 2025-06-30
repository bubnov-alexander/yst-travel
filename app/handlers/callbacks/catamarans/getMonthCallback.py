from aiogram import types
from app import keyboard


async def sort_month_order(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text='Выберите месяц', reply_markup=keyboard.months)

def register_callback_query_get_month_catamarans(dp):
    dp.register_callback_query_handler(sort_month_order, lambda c: c.data == 'sort_month_order')