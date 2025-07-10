import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.order import check_availability, get_order_by_id
from app.database.Models.supboaed import get_supboard_by_order_id, add_supboard


class AddSupboardFSM(StatesGroup):
    get_order_id = State()
    supboards_count = State()
    price = State()


def register_add_supboard_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("add_supboard_"))
    async def add_supboard_handler(callback: types.CallbackQuery, state: FSMContext):
        order_id = int(callback.data.split("_")[2])
        order = await get_order_by_id(order_id)

        if not order:
            await callback.message.answer('⚠️ Не удалось найти заказ.', reply_markup=kb.main)
            return

        async with state.proxy() as data:
            data['order_id'] = order_id
            data['date_start'] = order[1]
            data['date_end'] = order[3]

        supboard_data = await get_supboard_by_order_id(order_id)
        current_quantity = supboard_data[2] if supboard_data else 0

        remaining = await check_availability(
            date_start=order[1],
            date_end=order[3],
            requested={
                'catamarans': 0,
                'transfers': 0,
                'supboards': current_quantity,
            },
            order_id=order_id
        )

        if remaining[0]:
            await callback.message.edit_text(
                f'✅ Даты свободны!\n'
                f'📦 Доступно:\n• SUP-досок — <b>{remaining[1]["supboards"]}</b>\n\n'
                f'🔢 Введите количество SUP-досок, которое нужно добавить:',
                reply_markup=kb.close2,
                parse_mode='HTML'
            )
            await AddSupboardFSM.supboards_count.set()
        else:
            await callback.message.answer(
                f'❌ Недостаточно SUP-досок в наличии.\n'
                f'📦 Доступно: <b>{remaining[1]["supboards"]}</b>',
                reply_markup=kb.main,
                parse_mode='HTML'
            )
            await state.finish()

    @dp.message_handler(state=AddSupboardFSM.supboards_count)
    async def save_supboard_quantity(message: types.Message, state: FSMContext):
        if not message.text.isdigit():
            await message.answer("⚠️ Введите корректное число.")
            return

        supboards_count = int(message.text)
        async with state.proxy() as data:
            data['supboards_count'] = supboards_count

            remaining = await check_availability(
                date_start=data['date_start'],
                date_end=data['date_end'],
                requested={
                    'catamarans': 0,
                    'transfers': 0,
                    'supboards': supboards_count
                },
                order_id=data['order_id']
            )

        if remaining[0]:
            await message.answer('💰 Введите стоимость SUP-досок:', reply_markup=kb.close2)
            await AddSupboardFSM.next()
        else:
            await message.answer(
                f'❌ Недостаточно SUP-досок в наличии.\n'
                f'📦 Доступно: <b>{remaining[1]["supboards"]}</b>',
                reply_markup=kb.main,
                parse_mode='HTML'
            )
            await state.finish()

    @dp.message_handler(state=AddSupboardFSM.price)
    async def save_supboard_price(message: types.Message, state: FSMContext):
        if not re.match(r'^\d+(\.\d{1,2})?$', message.text):
            await message.answer("⚠️ Введите корректную цену (например: 1000 или 1000.50)")
            return

        async with state.proxy() as data:
            data['price'] = message.text

            supboard_id = await add_supboard(
                order_id=data['order_id'],
                quantity=data['supboards_count'],
                price=data['price']
            )

        info_text = await kb.info_supboard_text(  # нужно реализовать аналогично `info_catamaran_text`
            order_id=data['order_id'],
            quantity=data['supboards_count'],
            price=data['price'],
            supboard_id=supboard_id
        )

        buttons = await kb.service_buttons(data['order_id'])

        await message.answer(
            f'✅ SUP-доски успешно добавлены!\n\n{info_text}',
            reply_markup=buttons,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

        await state.finish()
