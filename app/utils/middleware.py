from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery
from aiogram.dispatcher.handler import CancelHandler
from aiogram import types
from app.utils.logger import logger  # Или просто print, если не используешь логгер

class CallbackLoggerMiddleware(BaseMiddleware):
    async def on_pre_process_callback_query(self, callback: CallbackQuery, data: dict):
        logger.info(f'Получен callback: {callback.data}')

class MessageLoggerMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logger.info(f"message От {message.from_user.id}: {message.text}")