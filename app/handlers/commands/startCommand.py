from aiogram import types
from app import keyboard
from app.database.Models import user

async def cmd_start(message: types.Message):
    user_ids = user.get_user_id()
    if message.chat.id in user_ids:
        await message.answer('Приветствую, администратор', reply_markup=keyboard.main)
    else:
        await message.answer('Привет! Добро пожаловать в бота')

def register_handlers_start(dp):
    dp.register_message_handler(cmd_start, commands=['start'])