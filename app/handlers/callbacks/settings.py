from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.settings import set_value_in_settings
from app.database.Models.user import get_users


class ChangeSettingState(StatesGroup):
    waiting_for_value = State()


def register_settings_handlers(dp):
    @dp.callback_query_handler(text='settings')
    async def search_date_order(callback: types.CallbackQuery):
        await callback.bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Выбери действие', reply_markup=kb.settings_buttons)

    @dp.callback_query_handler(lambda c: c.data.startswith("change_") and c.data.endswith("_services"))
    async def ask_for_setting_value(callback: types.CallbackQuery, state: FSMContext):
        setting_key = callback.data.replace("change_", "").replace("_services", "")  # supboard, transfer, catamaran
        setting_map = {
            "supboard": "SUP-бордов",
            "transfer": "транспортных средств",
            "catamaran": "катамаранов"
        }

        await state.update_data(setting_key=setting_key)

        await callback.message.edit_text(
            f"Введите количество {setting_map.get(setting_key, 'единиц')}, доступных в наличии:"
        )
        await ChangeSettingState.waiting_for_value.set()

    @dp.message_handler(state=ChangeSettingState.waiting_for_value)
    async def save_setting_value(message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        setting_key = user_data.get("setting_key")

        if not message.text.isdigit():
            await message.reply("Пожалуйста, введите число.")
            return

        value = message.text

        await set_value_in_settings(
            setting_key=setting_key,
            value=value
        )

        await message.reply(
            text=f"Количество {setting_key} успешно обновлено на {value}.",
            reply_markup=kb.main
        )
        await state.finish()

    @dp.callback_query_handler(lambda c: c.data == "change_database_admin")
    async def change_admin_menu(callback: types.CallbackQuery):

        admins = get_users()

        if admins:
            text = "👤 Список администраторов:\n"
            for admin_id, username in admins:
                text += f"• {username or '(без username)'} — <code>{admin_id}</code>\n"
        else:
            text = "Нет добавленных администраторов."


        await callback.message.edit_text(text, reply_markup=kb.admin_settings, parse_mode="HTML")
