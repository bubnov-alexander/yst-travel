import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models import catamaran
from app.database.Models.order import check_availability, get_order_by_id


class EditCatamaranFSM(StatesGroup):
    edit_quantity = State()
    edit_price = State()


def register_edit_catamaran_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("change_catamaran_"))
    async def edit_catamaran(callback: types.CallbackQuery, state: FSMContext):
        order_id = int(callback.data.split("_")[2])
        catamaran_data = await catamaran.get_catamaran_by_order_id(order_id)

        if not catamaran_data:
            await callback.message.edit_text('⚠️ Катамаран не найден.', reply_markup=kb.main)
            return

        order = await get_order_by_id(order_id)

        async with state.proxy() as data:
            data['catamaran_id'] = catamaran_data[0]
            data['order_id'] = order_id
            data['current_quantity'] = catamaran_data[2]
            data['current_price'] = catamaran_data[3]
            data['date_start'] = order[1]
            data['date_end'] = order[3]

        await callback.message.answer(
            text=f'📦 Текущее количество: <b>{catamaran_data[2]}</b>\n'
                 '🔢 Введите новое количество или "Пропустить":',
            reply_markup=kb.close_replay_callback,
            parse_mode='HTML'
        )
        await EditCatamaranFSM.edit_quantity.set()

    @dp.message_handler(state=EditCatamaranFSM.edit_quantity)
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
                await EditCatamaranFSM.edit_price.set()
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
                await EditCatamaranFSM.edit_price.set()
                return

            diff = new_quantity
            remaining = await check_availability(
                date_start=data['date_start'],
                date_end=data['date_end'],
                requested={'catamarans': diff, 'transfers': 0, 'supboards': 0},
                order_id=data['order_id']
            )

            if not remaining[0]:
                await message.answer(
                    f'❌ Недостаточно катамаранов! Доступно: <b>{remaining[1]["catamarans"]}</b>\n'
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
            await EditCatamaranFSM.next()

    @dp.message_handler(state=EditCatamaranFSM.edit_price)
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
                    await message.answer('⚠️ Введите корректную цену (например: 1500.50)')
                    return
                new_price = user_input

            # Обновляем данные в БД
            await catamaran.update_catamaran(
                catamaran_id=data['catamaran_id'],
                quantity=data['new_quantity'],
                price=new_price
            )

            info_text = await kb.info_catamaran_text(
                order_id=data['order_id'],
                price=new_price,
                quantity=data['new_quantity'],
                catamaran_id=data['catamaran_id']
            )

            buttons = await kb.service_buttons(data['order_id'])

            await message.answer(
                f'✅ Катамаран обновлен!\n\n{info_text}',
                reply_markup=buttons,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            await state.finish()
