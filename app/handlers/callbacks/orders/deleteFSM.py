from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.order import get_order_by_id, delete_order_by_id


class DeleteOrderFSM(StatesGroup):
    order_id = State()


def register_delete_order_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("delete_order_"))
    async def delete_order(callback: types.CallbackQuery, state: FSMContext):
        order_id = int(callback.data.split("_")[2])
        order_data = await get_order_by_id(order_id)

        if not order_data:
            await callback.message.edit_text("⚠️ Заказ не найден.", reply_markup=kb.main)
            return

        await state.update_data(order_id=order_id)
        await DeleteOrderFSM.order_id.set()

        buttons = await kb.generate_confirm_buttons('order')

        await callback.message.edit_text(
            f"❓ Вы уверены, что хотите удалить заказ с ID {order_id}?",
            reply_markup=buttons,
        )

    @dp.callback_query_handler(lambda c: c.data == 'confirm_delete_yes_order', state=DeleteOrderFSM.order_id)
    async def process_confirm_delete_order(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        order_id = data.get("order_id")

        await delete_order_by_id(order_id)
        await callback.message.edit_text("✅ Заказ успешно удалён.", reply_markup=kb.main)
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == 'confirm_delete_no_order', state=DeleteOrderFSM.order_id)
    async def process_cancel_delete_order(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("❎ Удаление заказа отменено.", reply_markup=kb.main)
        await state.finish()
