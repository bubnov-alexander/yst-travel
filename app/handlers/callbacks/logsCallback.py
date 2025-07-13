from aiogram import types
import os
from aiogram.types import InputFile

async def send_excel(callback: types.CallbackQuery):
    logs_file = 'app/storage/logs/bot.log'

    file = InputFile(logs_file)
    await callback.bot.send_document(callback.from_user.id, file)

    os.remove(logs_file)

def register_callback_query_logs(dp):
    dp.register_callback_query_handler(send_excel, lambda c: c.data == 'logs')