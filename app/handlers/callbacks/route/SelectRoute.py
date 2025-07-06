from aiogram import types
from app import keyboard
from app.utils.getRouteButton import get_points_a_keyboard


async def select_route(callback: types.CallbackQuery):
    await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                         text='🗺 Выберите маршрут из списка или добавьте новый: ',
                                         reply_markup=get_points_a_keyboard())


def register_select_route_handler(dp):
    dp.register_callback_query_handler(select_route, lambda c: c.data == 'select_route_buttons', state='*')

