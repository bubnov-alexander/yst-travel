import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.order import get_order_by_id, check_availability
from app.database.Models.supboaed import get_supboard_by_order_id, update_supboard


class EditSupboardFSM(StatesGroup):
    edit_quantity = State()
    edit_price = State()


def register_edit_supboard_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("change_supboard_"))
    async def edit_supboard(callback: types.CallbackQuery, state: FSMContext):
        order_id = int(callback.data.split("_")[2])
        supboard_data = await get_supboard_by_order_id(order_id)

        if not supboard_data:
            await callback.message.edit_text('⚠️ SUP-доски не найдены.', reply_markup=kb.main)
            return

        order = await get_order_by_id(order_id)

        async with state.proxy() as data:
            data['supboard_id'] = supboard_data[0]
            data['order_id'] = order_id
            data['current_quantity'] = supboard_data[2]
            data['current_price'] = supboard_data[3]
            data['date_start'] = order[1]
            data['date_end'] = order[3]

        await callback.message.answer(
            text=f'📦 Текущее количество SUP-досок: <b>{supboard_data[2]}</b>\n'
                 '🔢 Введите новое количество или "Пропустить":',
            reply_markup=kb.close_replay_callback,
            parse_mode='HTML'
        )
        await EditSupboardFSM.edit_quantity.set()

    @dp.message_handler(state=EditSupboardFSM.edit_quantity)
    async def process_quantity(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение отменено.', reply_markup=kb.main)
            await state.finish()
            return

        async with state.proxy() as data:
            if user_input == 'пропустить':
                data['new_quantity'] = data['current_quantity']
                await message.answer(
                    f'💰 Текущая цена: <b>{data["current_price"]}</b>\n'
                    'Введите новую цену или "Пропустить":',
                    reply_markup=kb.close_replay_callback,
                    parse_mode='HTML'
                )
                await EditSupboardFSM.edit_price.set()
                return

            if not user_input.isdigit():
                await message.answer('⚠️ Введите число, "Пропустить" или "Отменить"')
                return

            new_quantity = int(user_input)
            if new_quantity == data['current_quantity']:
                data['new_quantity'] = data['current_quantity']
                await message.answer(
                    f'💰 Текущая цена: <b>{data["current_price"]}</b>\n'
                    'Введите новую цену или "Пропустить":',
                    reply_markup=kb.close_replay_callback,
                    parse_mode='HTML'
                )
                await EditSupboardFSM.edit_price.set()
                return

            diff = new_quantity
            remaining = await check_availability(
                date_start=data['date_start'],
                date_end=data['date_end'],
                requested={'catamarans': 0, 'transfers': 0, 'supboards': diff},
                order_id=data['order_id']
            )

            if not remaining[0]:
                await message.answer(
                    f'❌ Недостаточно SUP-досок! Доступно: <b>{remaining[1]["supboards"]}</b>\n'
                    'Попробуйте другое количество:',
                    reply_markup=kb.close_replay_callback,
                    parse_mode='HTML'
                )
                return

            data['new_quantity'] = new_quantity
            await message.answer(
                f'💰 Текущая цена: <b>{data["current_price"]}</b>\n'
                'Введите новую цену или "Пропустить":',
                reply_markup=kb.close_replay_callback,
                parse_mode='HTML'
            )
            await EditSupboardFSM.next()

    @dp.message_handler(state=EditSupboardFSM.edit_price)
    async def process_price(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение отменено.', reply_markup=kb.main)
            await state.finish()
            return

        async with state.proxy() as data:
            if user_input == 'пропустить':
                new_price = data['current_price']
            else:
                if not re.match(r'^\d+(\.\d{1,2})?$', user_input):
                    await message.answer('⚠️ Введите корректную цену (например: 1000.50)')
                    return
                new_price = user_input

            update_supboard(
                supboard_id=data['supboard_id'],
                quantity=data['new_quantity'],
                price=new_price
            )

            info_text = await kb.info_supboard_text(  # Не забудь реализовать
                order_id=data['order_id'],
                price=new_price,
                quantity=data['new_quantity'],
                supboard_id=data['supboard_id']
            )

            buttons = await kb.service_buttons(data['order_id'])

            await message.answer(
                f'✅ SUP-доски обновлены!\n\n{info_text}',
                reply_markup=buttons,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            await state.finish()
