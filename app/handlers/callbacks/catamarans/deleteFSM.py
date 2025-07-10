from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models import catamaran


class DeleteCatamaranFSM(StatesGroup):
    catamaran_id = State()


def register_delete_catamaran_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("delete_catamaran_"))
    async def delete_catamaran(callback: types.CallbackQuery, state: FSMContext):
        catamaran_id = int(callback.data.split("_")[2])
        catamaran_data = await catamaran.get_catamaran_by_order_id(catamaran_id)

        if not catamaran_data:
            await callback.message.edit_text('⚠️ Катамаран не найден.', reply_markup=kb.main)
            return

        await state.update_data(catamaran_id=catamaran_id)
        await DeleteCatamaranFSM.catamaran_id.set()

        buttons = await kb.generate_confirm_buttons('catamaran')

        await callback.message.edit_text(
            f"❓ Вы уверены, что хотите удалить катамаран с ID {catamaran_id}?",
            reply_markup=buttons,
        )

    @dp.callback_query_handler(lambda c: c.data == 'confirm_delete_yes_catamaran',
                               state=DeleteCatamaranFSM.catamaran_id)
    async def process_confirm_delete(callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        catamaran_id = data.get("catamaran_id")

        catamaran_data = await catamaran.get_catamaran_by_order_id(catamaran_id)
        if catamaran_data:
            await catamaran.delete_catamaran(catamaran_id)
            await callback.message.edit_text(f'✅ Катамаран с ID {catamaran_id} удалён.', reply_markup=kb.main)
        else:
            await callback.message.edit_text(f'❌ Катамаран с ID {catamaran_id} не найден.', reply_markup=kb.main)

        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == 'confirm_delete_no_catamaran', state=DeleteCatamaranFSM.catamaran_id)
    async def process_cancel_delete(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("❎ Удаление отменено.", reply_markup=kb.main)
        await state.finish()
