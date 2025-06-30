from app import keyboard

from aiogram import types
from aiogram.dispatcher import FSMContext

async def close_callback(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                text='Выбери что хочешь сделать', reply_markup=keyboard.main, parse_mode='Markdown')

def register_callback_query_close_button(dp):
    dp.register_callback_query_handler(close_callback, lambda c: c.data == 'close')


def register_callback_close_handlers(dp, bot):
    @dp.callback_query_handler(state="*", text='close_callback')
    async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Я отменил твой запрос', reply_markup=keyboard.main)
        await state.finish()


    @dp.callback_query_handler(state="*", text='close_callback2')
    async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Я отменил твой запрос', reply_markup=keyboard.sort_orders)
        await state.finish()


    @dp.message_handler(state="*", commands=['cancel'])
    async def cancel_handler(message: types.Message, state: FSMContext):
        await message.answer('Я отменил твой запрос', reply_markup=keyboard.main)
        await state.finish()
