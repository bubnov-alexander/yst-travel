from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.Models import catamaran
from app import keyboard as kb

class DeleteOrderFSM(StatesGroup):
    delete_order = State()


def register_delete_catamaran_handlers(dp, bot):
    @dp.callback_query_handler(text='delete_order')
    async def delete_order(callback: types.CallbackQuery):
        await DeleteOrderFSM.delete_order.set()
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Введите ID заказа, который хотите удалить',
            reply_markup=kb.close2
        )

    @dp.message_handler(state=DeleteOrderFSM.delete_order)
    async def delete_order_by_id(message: types.Message, state: FSMContext):
        order_id = message.text.strip()
        order = await catamaran.get_catamaran_by_id(order_id)
        if order:
            await catamaran.delete_order(order_id)
            await message.answer(f'✅ Заказ с ID {order_id} удален.', reply_markup=kb.main)
        else:
            await message.answer(f'❌ Заказ с ID {order_id} не найден.', reply_markup=kb.main)
        await state.finish()