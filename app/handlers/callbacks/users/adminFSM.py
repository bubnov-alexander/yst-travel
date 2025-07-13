from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard
from app.database.Models.user import set_user, delete_user


class AdminFSM(StatesGroup):
    waiting_for_user_id_to_add = State()
    waiting_for_user_id_to_remove = State()


def register_handle_add_admin(dp):
    @dp.callback_query_handler(lambda c: c.data == "add_admin")
    async def handle_add_admin(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text="🔹 Отправь ID пользователя или пересылай сообщение от него.",
            reply_markup=keyboard.close2
        )
        await AdminFSM.waiting_for_user_id_to_add.set()

    @dp.message_handler(state=AdminFSM.waiting_for_user_id_to_add, content_types=types.ContentTypes.ANY)
    async def process_add_admin(message: types.Message, state: FSMContext):
        if message.forward_from:
            user_id = message.forward_from.id
            username = message.forward_from.username

        else:
            try:
                user_id = int(message.text.strip())
                username = None
            except ValueError:
                await message.reply(
                    text=(
                        "❗ Не удалось определить ID пользователя. Возможно, он запретил пересылку с указанием аккаунта."
                        "\n\nПожалуйста, введите его Telegram ID вручную или попросите отправить любое сообщение боту."
                    ),
                    reply_markup=keyboard.close2
                )
                return

        set_user(
            user_id=user_id
        )

        await message.reply(
            text=f"✅ Пользователь с ID {user_id} добавлен в администраторы.",
            reply_markup=keyboard.main
        )
        await state.finish()


def register_handle_delete_admin(dp):
    @dp.callback_query_handler(lambda c: c.data == "remove_admin")
    async def handle_remove_admin(callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(
            text="🔸 Введи ID администратора, которого нужно удалить.",
            reply_markup=keyboard.close2
        )
        await AdminFSM.waiting_for_user_id_to_remove.set()

    @dp.message_handler(state=AdminFSM.waiting_for_user_id_to_remove)
    async def process_remove_admin(message: types.Message, state: FSMContext):
        try:
            user_id = int(message.text.strip())
        except ValueError:
            await message.reply(
                text="❌ Неверный формат ID. Попробуй ещё раз.",
                reply_markup=keyboard.close2
            )
            return

        changes = delete_user(
            user_id=user_id,
        )

        if changes:
            await message.reply(
                text=f"🗑 Администратор с ID {user_id} удалён.",
                reply_markup=keyboard.main
            )
            await state.finish()
        else:
            await message.reply("⚠️ Администратор с таким ID не найден.")
            return
