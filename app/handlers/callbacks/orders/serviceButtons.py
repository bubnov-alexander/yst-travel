from aiogram import types
from app import keyboard


from aiogram import types
from app import keyboard




async def catamaran_service_callback(callback: types.CallbackQuery):
    order_id = callback.data.split('_')[2]
    buttons = await keyboard.catamarans_buttons(order_id)
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text='Выбери действие',
        reply_markup=buttons
    )


async def supboard_service_callback(callback: types.CallbackQuery):
    order_id = callback.data.split('_')[2]
    buttons = await keyboard.supboards_buttons(order_id)
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text='Выбери действие',
        reply_markup=buttons
    )


async def transfer_service_callback(callback: types.CallbackQuery):
    order_id = callback.data.split('_')[2]
    buttons = await keyboard.transfer_buttons(order_id)
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text='Выбери действие',
        reply_markup=buttons
    )



def register_catamaran_callback(dp):
    dp.register_callback_query_handler(catamaran_service_callback,
                                       lambda c: c.data.startswith('catamaran_buttons_'))


def register_supboard_callback(dp):
    dp.register_callback_query_handler(supboard_service_callback,
                                       lambda c: c.data.startswith('supboard_buttons_'))


def register_transfer_callback(dp):
    dp.register_callback_query_handler(transfer_service_callback,
                                       lambda c: c.data.startswith('transfer_buttons_'))

