from aiogram import types
from app import keyboard
from app.utils import exsel
import os
from aiogram.types import InputFile

async def send_excel(callback: types.CallbackQuery):
    db_path = 'app/storage/database.db'
    excel_path = 'app/storage/catamaran_data.xlsx'

    exsel.export_sql_to_excel(db_path, excel_path)

    file = InputFile(excel_path)
    await callback.bot.send_document(callback.from_user.id, file)

    os.remove(excel_path)

def register_callback_query_excel(dp):
    dp.register_callback_query_handler(send_excel, lambda c: c.data == 'excel')