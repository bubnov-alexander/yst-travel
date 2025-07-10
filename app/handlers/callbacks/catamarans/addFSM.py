import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models import catamaran
from app.database.Models.catamaran import get_catamaran_by_order_id
from app.database.Models.order import check_availability, get_order_by_id


class MyFSM(StatesGroup):
    get_order_id = State()
    quantity = State()
    price = State()


def register_add_catamaran_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("add_catamaran_"))
    async def add_catamaran(callback: types.CallbackQuery, state: FSMContext):
        order_id = int(callback.data.split("_")[2])
        order = await get_order_by_id(order_id)

        if not order:
            await callback.message.answer('⚠️ Не удалось найти заказ.', reply_markup=kb.main)
            return

        async with state.proxy() as data:
            data['order_id'] = order_id
            data['date_start'] = order[1]
            data['date_end'] = order[3]

        catamarans = await get_catamaran_by_order_id(order_id=order_id)
        current_quantity = catamarans[2] if catamarans else 0

        remaining = await check_availability(
            date_start=order[1],
            date_end=order[3],
            requested={
                'catamarans': current_quantity,
                'transfers': 0,
                'supboards': 0
            },
            order_id=order_id
        )

        print(remaining, current_quantity)

        await callback.message.edit_text(
            f'✅ Даты свободны!\n'
            f'📦 Доступно:\n• Катамаранов — <b>{remaining[1]["catamarans"]}</b>\n\n'
            f'🔢 Введите количество катамаранов, которое нужно добавить:',
            reply_markup=kb.close2,
            parse_mode='HTML'
        )

        await MyFSM.quantity.set()

    @dp.message_handler(state=MyFSM.quantity)
    async def save_quantity(message: types.Message, state: FSMContext):
        if not message.text.isdigit():
            await message.answer('⚠️ Пожалуйста, введите число.')
            return

        quantity = int(message.text)

        async with state.proxy() as data:
            data['quantity'] = quantity
            remaining = await check_availability(
                date_start=data['date_start'],
                date_end=data['date_end'],
                requested={
                    'catamarans': quantity,
                    'transfers': 0,
                    'supboards': 0
                },
                order_id=data['order_id']

            )

        if remaining[0]:
            await message.answer('💰 Введите стоимость катамаранов:', reply_markup=kb.close2)
            await MyFSM.next()
        else:
            await message.answer(
                f'❌ Недостаточно катамаранов в наличии.\n'
                f'📦 Доступно: <b>{remaining[1]["catamarans"]}</b>',
                reply_markup=kb.main,
                parse_mode='HTML'
            )
            await state.finish()

    @dp.message_handler(state=MyFSM.price)
    async def save_price(message: types.Message, state: FSMContext):
        if not re.match(r'^\d+(\.\d{1,2})?$', message.text):
            await message.answer('⚠️ Введите корректную цену (например: 1500 или 1500.50)')
            return

        async with state.proxy() as data:
            data['price'] = message.text

            catamaran_id = await catamaran.add_catamaran(
                order_id=data['order_id'],
                price=data['price'],
                quantity=data['quantity']
            )

        info_text = await kb.info_catamaran_text(
            order_id=data['order_id'],
            price=data['price'],
            quantity=data['quantity'],
            catamaran_id=catamaran_id
        )

        buttons = await kb.service_buttons(data['order_id'])

        await message.answer(
            f'✅ Катамараны успешно добавлены!\n\n{info_text}',
            reply_markup=buttons,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

        await state.finish()
