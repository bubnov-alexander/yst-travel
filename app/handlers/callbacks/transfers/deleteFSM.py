from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.transfer import get_transfer_by_order_id, delete_transfer_by_id


class DeleteTransferFSM(StatesGroup):
    transfer_id = State()


def register_delete_transfer_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("delete_transfer_"))
    async def delete_transfer(callback: types.CallbackQuery, state: FSMContext):
        order_id = int(callback.data.split("_")[2])
        transfer_data = await get_transfer_by_order_id(order_id)

        if not transfer_data:
            await callback.message.edit_text("⚠️ Трансфер не найден.", reply_markup=kb.main)
            return

        await state.update_data(transfer_id=transfer_data[0])
        await DeleteTransferFSM.transfer_id.set()

        buttons = await kb.generate_confirm_buttons('transfer')

        await callback.message.edit_text(
            f"❓ Вы уверены, что хотите удалить трансфер с ID {transfer_data[0]}?",
            reply_markup=buttons,
        )

    @dp.callback_query_handler(lambda c: c.data == 'confirm_delete_yes_transfer', state=DeleteTransferFSM.transfer_id)
    async def process_confirm_delete_transfer(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        transfer_id = data.get("transfer_id")

        await delete_transfer_by_id(transfer_id)
        await callback.message.edit_text("❎ Удаление трансфера выполнено.", reply_markup=kb.main)
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == 'confirm_delete_no_transfer', state=DeleteTransferFSM.transfer_id)
    async def process_cancel_delete_transfer(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("❎ Удаление трансфера отменено.", reply_markup=kb.main)
        await state.finish()
