from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.Models import catamaran
from app import keyboard as kb
from app.database.Models.route import get_route_by_id


class FindOrderById(StatesGroup):
    search_order = State()

def register_find_order_by_id_handlers(dp, bot):
    @dp.callback_query_handler(text='search_id_order')
    async def search_order(callback: types.CallbackQuery):
        await FindOrderById.search_order.set()
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Введите ID заказа, который хотите найти',
            reply_markup=kb.close4)


    @dp.message_handler(state=FindOrderById.search_order)
    async def search_order_by_id(message: types.Message, state: FSMContext):
        try:
            order_id = int(message.text)
        except ValueError:
            await message.answer('❌ ID заказа должен быть числом', reply_markup=kb.main)
            return

        order = await catamaran.get_catamaran_quantity(order_id)

        if order:
            route = get_route_by_id(order[5])
            phone = order[8].replace('https://wa.me/', '')

            text = "📝 <b>Информация о заказе</b>\n"
            text += "━━━━━━━━━━━━━━━━━━━━\n\n"
            text += f"📌 <b>ID заказа:</b> {order[0]}\n"
            text += f"⚡️ <b>Дата приезда:</b> {order[1]}\n"
            text += f"⏰️ <b>Время приезда:</b> {order[2]}\n"
            text += f"⚡️ <b>Дата выезда:</b> {order[3]}\n"
            text += f"⏰️ <b>Время выезда:</b> {order[4]}\n"
            text += f"🗺 <b>Маршрут:</b> {route['name']}\n"
            text += f"📈 <b>Количество катамаранов:</b> {order[6]}\n"
            text += f"🤵 <b>ФИО:</b> {order[7]}\n"
            text += f"📞 <b>Телефон:</b> <a href='{order[8]}'>+{phone}</a>\n"
            text += f"💰 <b>Цена заказа:</b> {order[9]} ₽\n"

            if order[10] and order[10].strip() not in ["", ".", " "]:
                text += f"📗 <b>Дополнительные пожелания:</b> {order[10]}\n"

            if order[11]:
                text += "✅ <b>Статус:</b> Подтверждён!\n"
            else:
                text += "❌ <b>Статус:</b> Не подтверждён!\n"

            text += "\n━━━━━━━━━━━━━━━━━━━━"

            await message.answer(
                text=text,
                reply_markup=kb.back_to_search_order,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
        else:
            await message.answer(f'❌ Заказ с ID <b>{order_id}</b> не найден', reply_markup=kb.main)

        await state.finish()
