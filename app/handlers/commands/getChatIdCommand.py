from aiogram import types

async def get_group_id(message: types.Message):
    await message.answer(message.chat.id)

def register_handlers_get_group_id(dp):
    dp.register_message_handler(get_group_id, commands=['get_group_id'])