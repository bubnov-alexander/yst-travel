import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app import keyboard as kb
from app.database.Models.transfer import get_transfer_by_order_id, update_transfer  # допустим, функция для обновления
from app.utils.getRouteButton import get_routes_keyboard_from_point_a, get_points_a_keyboard


class EditTransferFSM(StatesGroup):
    count = State()
    price = State()
    vehicle_type = State()
    driver_included = State()
    route_id = State()


def register_edit_transfer_handlers(dp):
    @dp.callback_query_handler(lambda c: c.data.startswith("change_transfer_"))
    async def start_edit_transfer(callback: types.CallbackQuery, state: FSMContext):
        order_id = int(callback.data.split("_")[2])
        transfer = await get_transfer_by_order_id(order_id)
        if not transfer:
            await callback.message.answer('⚠️ Не удалось найти трансфер.', reply_markup=kb.main)
            return

        async with state.proxy() as data:
            data['order_id'] = order_id
            data['transfer_id'] = transfer[0]
            data['persons_count'] = transfer[4]
            data['price'] = transfer[6]
            data['vehicle_type'] = transfer[2]
            data['driver_included'] = transfer[5]
            data['route_id'] = transfer[3]

        await callback.message.edit_text(
            text=f"🔢 Текущее количество пассажиров: {transfer[4]}\n"
                 f"Введите новое количество пассажиров или 'пропустить', чтобы оставить прежнее:",
            reply_markup=kb.close2,
            parse_mode='HTML'
        )
        await EditTransferFSM.count.set()

    @dp.message_handler(state=EditTransferFSM.count)
    async def edit_count(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение заказа отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            # переходим к следующему состоянию, не меняя persons_count
            await message.answer('💰 Введите стоимость трансфера или "пропустить":',
                                 reply_markup=kb.close_replay_callback)
            await EditTransferFSM.price.set()
            return

        if not user_input.isdigit():
            await message.answer("⚠️ Введите корректное число или 'пропустить'.")
            return

        async with state.proxy() as data:
            data['persons_count'] = int(user_input)

        await message.answer('💰 Введите стоимость трансфера или "пропустить":', reply_markup=kb.close_replay_callback)
        await EditTransferFSM.price.set()

    @dp.message_handler(state=EditTransferFSM.price)
    async def edit_price(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение заказа отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            await message.answer('🚗 Введите тип транспорта или "пропустить":', reply_markup=kb.close_replay_callback)
            await EditTransferFSM.vehicle_type.set()
            return

        if not re.match(r'^\d+(\.\d{1,2})?$', message.text.strip()):
            await message.answer("⚠️ Введите корректную цену (например: 1000 или 1000.50) или 'пропустить'.")
            return

        async with state.proxy() as data:
            data['price'] = float(message.text.strip())

        await message.answer('🚗 Введите тип транспорта или "пропустить":', reply_markup=kb.close_replay_callback)
        await EditTransferFSM.vehicle_type.set()

    @dp.message_handler(state=EditTransferFSM.vehicle_type)
    async def edit_vehicle_type(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение заказа отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            await message.answer('👨‍✈️ Включён ли водитель? (да / нет) или "пропустить":', reply_markup=kb.yes_no_kb)
            await EditTransferFSM.driver_included.set()
            return

        async with state.proxy() as data:
            data['vehicle_type'] = message.text.strip()

        await message.answer('👨‍✈️ Включён ли водитель? (да / нет) или "пропустить":', reply_markup=kb.yes_no_kb)
        await EditTransferFSM.driver_included.set()

    @dp.message_handler(state=EditTransferFSM.driver_included)
    async def edit_driver_included(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение заказа отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            await message.answer('🗺 Выберите маршрут из списка или "пропустить":',
                                 reply_markup=await get_points_a_keyboard())
            await EditTransferFSM.route_id.set()
            return

        if user_input not in ['да', 'нет']:
            await message.answer("⚠️ Ответьте 'да' или 'нет' или 'пропустить'", reply_markup=kb.yes_no_kb)
            return

        async with state.proxy() as data:
            data['driver_included'] = (user_input == 'да')

        await message.answer('🗺 Выберите маршрут из списка:', reply_markup=get_points_a_keyboard())
        await EditTransferFSM.route_id.set()

    @dp.callback_query_handler(lambda c: c.data.startswith('select_point_a_'), state=EditTransferFSM.route_id)
    async def handle_point_a_selected(callback: types.CallbackQuery, state: FSMContext):
        point_a = callback.data.replace('select_point_a_', '')
        async with state.proxy() as data:
            data['point_a'] = point_a

        await callback.message.edit_text(
            text=f"📍 Вы выбрали точку А: {point_a}\nТеперь выберите пункт Б:",
            reply_markup=get_routes_keyboard_from_point_a(point_a)
        )

    @dp.callback_query_handler(lambda c: c.data.startswith('select_route_'), state=EditTransferFSM.route_id)
    async def route_selected(callback: types.CallbackQuery, state: FSMContext):
        try:
            route_id = int(callback.data.replace('select_route_', ''))
        except ValueError:
            return

        async with state.proxy() as data:
            data['route_id'] = route_id
            # вызываем функцию обновления трансфера
            await update_transfer(
                order_id=data['order_id'],
                transfer_id=data['transfer_id'],
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
            transfer_id=data['transfer_id']
        )

        buttons = await kb.service_buttons(data['order_id'])

        await callback.message.answer(
            f'✅ Трансфер успешно изменён!\n\n{info_text}',
            reply_markup=buttons,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

        await state.finish()
