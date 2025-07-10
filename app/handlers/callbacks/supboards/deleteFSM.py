from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.supboaed import get_supboard_by_id, delete_supboard_by_id, get_supboard_by_order_id


class DeleteSupboardFSM(StatesGroup):
    supboard_id = State()


def register_delete_supboard_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("delete_supboard_"))
    async def delete_supboard(callback: types.CallbackQuery, state: FSMContext):
        order_id = int(callback.data.split("_")[2])
        supboard_data = await get_supboard_by_order_id(order_id)

        if not supboard_data:
            await callback.message.edit_text("⚠️ SUP-доска не найдена.", reply_markup=kb.main)
            return

        await state.update_data(supboard_id=supboard_data[0])
        await DeleteSupboardFSM.supboard_id.set()

        buttons = await kb.generate_confirm_buttons('supboard')

        await callback.message.edit_text(
            f"❓ Вы уверены, что хотите удалить SUP-доску с ID {supboard_data[0]}?",
            reply_markup=buttons,
        )

    @dp.callback_query_handler(lambda c: c.data == 'confirm_delete_yes_supboard', state=DeleteSupboardFSM.supboard_id)
    async def process_confirm_delete_supboard(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        supboard_id = data.get("supboard_id")

        supboard_data = get_supboard_by_id(supboard_id)
        if supboard_data:
            delete_supboard_by_id(supboard_id)
            await callback.message.edit_text(f'✅ SUP-доска с ID {supboard_id} удалена.', reply_markup=kb.main)
        else:
            await callback.message.edit_text(f'❌ SUP-доска с ID {supboard_id} не найдена.', reply_markup=kb.main)

        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == 'confirm_delete_no_supboard', state=DeleteSupboardFSM.supboard_id)
    async def process_cancel_delete_supboard(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("❎ Удаление SUP-доски отменено.", reply_markup=kb.main)
        await state.finish()
