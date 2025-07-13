from aiogram import types

from app.keyboard import selection_of_sorts


def register_get_buttons_selection_of_sorts(dp):
    @dp.callback_query_handler(text='selection_of_sorts')
    async def search_date_order(callback: types.CallbackQuery):
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Выбери действие', reply_markup=selection_of_sorts)
