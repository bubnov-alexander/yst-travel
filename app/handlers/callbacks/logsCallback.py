from aiogram import types
import os
from aiogram.types import InputFile


async def send_log_file(callback: types.CallbackQuery):
    logs_file = 'app/storage/logs/bot.log'

    if not os.path.exists(logs_file):
        await callback.answer("Файл логов не найден", show_alert=True)
        return

    file = InputFile(logs_file)
    try:
        await callback.bot.send_document(callback.from_user.id, file)
    except Exception as e:
        await callback.answer("Ошибка при отправке файла", show_alert=True)

def register_callback_query_logs(dp):
    dp.register_callback_query_handler(send_log_file, lambda c: c.data == 'logs')