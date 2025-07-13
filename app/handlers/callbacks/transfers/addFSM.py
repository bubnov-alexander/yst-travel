import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.order import get_order_by_id
from app.database.Models.transfer import add_transfer
from app.utils.getRouteButton import get_points_a_keyboard, get_routes_keyboard_from_point_a


class AddTransferFSM(StatesGroup):
    get_order_id = State()
    count = State()
    price = State()
    vehicle_type = State()
    driver_included = State()
    route_id = State()



def register_add_transfer_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("add_transfer_"))
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

        await callback.message.edit_text(
            f'🔢 Введите количество пассажиров',
            reply_markup=kb.close2,
            parse_mode='HTML'
        )
        await AddTransferFSM.count.set()

    @dp.message_handler(state=AddTransferFSM.count)
    async def save_supboard_quantity(message: types.Message, state: FSMContext):
        if not message.text.isdigit():
            await message.answer("⚠️ Введите корректное число.")
            return

        transfer_count = int(message.text)
        async with state.proxy() as data:
            data['persons_count'] = transfer_count

        await message.answer('💰 Введите стоимость трансфера:', reply_markup=kb.close2)
        await AddTransferFSM.price.set()

    @dp.message_handler(state=AddTransferFSM.price)
    async def save_transfer_price(message: types.Message, state: FSMContext):
        if not re.match(r'^\d+(\.\d{1,2})?$', message.text.strip()):
            await message.answer("⚠️ Введите корректную цену (например: 1000 или 1000.50)")
            return

        async with state.proxy() as data:
            data['price'] = float(message.text.strip())

        await message.answer("🚗 Введите тип транспорта:", reply_markup=kb.close2)
        await AddTransferFSM.vehicle_type.set()

    @dp.message_handler(state=AddTransferFSM.vehicle_type)
    async def save_vehicle_type(message: types.Message, state: FSMContext):
        vehicle_type = message.text.strip()
        async with state.proxy() as data:
            data['vehicle_type'] = vehicle_type

        await message.answer(
            "👨‍✈️ Включён ли водитель? (да / нет):",
            reply_markup=kb.yes_no_kb
        )
        await AddTransferFSM.driver_included.set()

    @dp.message_handler(state=AddTransferFSM.driver_included)
    async def save_driver_included(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()
        if user_input not in ['да', 'нет']:
            await message.answer("⚠️ Ответьте 'да' или 'нет'", reply_markup=kb.yes_no_kb)
            return

        async with state.proxy() as data:
            data['driver_included'] = user_input == 'да'

        await message.answer(
            '🗺 Выберите маршрут из списка:',
            reply_markup=get_points_a_keyboard()
        )
        await AddTransferFSM.route_id.set()

    @dp.callback_query_handler(lambda c: c.data.startswith('select_point_a_'), state=AddTransferFSM.route_id)
    async def handle_point_a_selected(callback: types.CallbackQuery, state: FSMContext):
        point_a = callback.data.replace('select_point_a_', '')
        async with state.proxy() as data:
            data['point_a'] = point_a

        await callback.message.edit_text(
            text=f"📍 Вы выбрали точку А: {point_a}\nТеперь выберите пункт Б:",
            reply_markup=get_routes_keyboard_from_point_a(point_a)
        )

    @dp.callback_query_handler(lambda c: c.data.startswith('select_point_a_'), state=AddTransferFSM.route_id)
    async def handle_point_a_selected(callback: types.CallbackQuery, state: FSMContext):
        point_a = callback.data.replace('select_point_a_', '')
        async with state.proxy() as data:
            data['point_a'] = point_a

        await callback.message.edit_text(
            text=f"📍 Вы выбрали точку А: {point_a}\nТеперь выберите пункт Б:",
            reply_markup=await get_routes_keyboard_from_point_a(point_a)
        )

    @dp.callback_query_handler(lambda c: c.data.startswith('select_route_'), state=AddTransferFSM.route_id)
    async def route_selected(callback: types.CallbackQuery, state: FSMContext):
        try:
            route_id = int(callback.data.replace('select_route_', ''))
        except ValueError:
            return

        async with state.proxy() as data:
            data['route_id'] = route_id

            transfer_id = await add_transfer(
                order_id=data['order_id'],
                vehicle_type=data['vehicle_type'],
                route_id=data['route_id'],
                persons_count=data['persons_count'],
                driver_included=data['driver_included'],
                price=data['price']
            )

        info_text = await kb.info_transfer_text(
            order_id=data['order_id'],
            quantity=data['persons_count'],
            price=data['price'],
            vehicle_type=data['vehicle_type'],
            driver_included=data['driver_included'],
            route_id=data['route_id'],
            transfer_id=transfer_id
        )

        buttons = await kb.service_buttons(data['order_id'])

        await callback.message.answer(
            f'✅ Трансфер успешно добавлен!\n\n{info_text}',
            reply_markup=buttons,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

        await state.finish()