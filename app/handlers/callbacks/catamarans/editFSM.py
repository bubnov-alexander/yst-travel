from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import re
import datetime as dt

from app.database.Models import catamaran
from app import keyboard as kb
from app.database.Models.catamaran import get_order_by_id
from app.database.Models.route import get_route_by_id
from app.utils.getRouteButton import get_points_a_keyboard, get_routes_keyboard_from_point_a
from app.utils.logger import logger


class EditOrderFSM(StatesGroup):
    edit_order = State()
    edit_date_arrival = State()
    edit_time_arrival = State()
    edit_date_departure = State()
    edit_time_departure = State()
    edit_quantity = State()
    edit_route = State()
    edit_customer_name = State()
    edit_phone = State()
    edit_price = State()
    edit_additional_wishes = State()

def register_edit_catamaran_handlers(dp, bot):
    @dp.callback_query_handler(text='edit_order')
    async def edit_order(callback: types.CallbackQuery):
        await EditOrderFSM.edit_order.set()
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='Введите ID заказа, который хотите изменить',
            reply_markup=kb.close2
        )

    @dp.message_handler(state=EditOrderFSM.edit_order)
    async def edit_order_by_id(message: types.Message, state: FSMContext):
        order_id = message.text.strip()

        if not order_id.isdigit():
            await message.answer("❌ ID заказа должен быть числом.", reply_markup=kb.main)
            await state.finish()
            return

        order = await catamaran.get_order_by_id(int(order_id))

        if order:
            await EditOrderFSM.edit_date_arrival.set()
            await state.update_data(order_id=order_id)

            async with state.proxy() as data:
                data['order_id'] = order_id
                data['date_arrival'] = order[1]
                data['time_arrival'] = order[2]
                data['date_departure'] = order[3]
                data['time_departure'] = order[4]
                data['route_id'] = order[5]
                data['quantity'] = order[6]
                data['customer_name'] = order[7]
                data['phone'] = order[8]
                data['price'] = order[9]
                data['additional_wishes'] = order[10]
                data['prepayment_status'] = order[11]

            route = get_route_by_id(order[5])
            route_name = route['name'] if route else '❓ Неизвестно'

            text = await kb.info_text(
                order_id=order[0],
                date_arrival=order[1],
                time_arrival=order[2],
                date_departure=order[3],
                time_departure=order[4],
                route_id=route_name,
                quantity=order[6],
                customer_name=order[7],
                phone_link=order[8],
                price=order[9],
                additional_wishes=order[10],
                status=order[11]
            )

            await bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=kb.close3,
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            await bot.send_message(
                chat_id=message.chat.id,
                text='📅 Дата приезда (например: 15.07.2024):',
                reply_markup=kb.close3,
                parse_mode='HTML'
            )
        else:
            await message.answer(f'❌ Заказ с ID <b>{order_id}</b> не найден.', reply_markup=kb.main, parse_mode='HTML')
            await state.finish()

    @dp.message_handler(state=EditOrderFSM.edit_date_arrival)
    async def save_edit_date_arrival(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение заказа отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            await message.answer('📅 Напишите дату выезда (например: 20.07.2024)', reply_markup=kb.close3)
            await EditOrderFSM.edit_date_departure.set()
            return

        try:
            try:
                parsed_date = dt.datetime.strptime(message.text, '%d.%m.%y')
            except ValueError:
                parsed_date = dt.datetime.strptime(message.text, '%d.%m.%Y')

            formatted_date = parsed_date.strftime('%d.%m.%Y')

            async with state.proxy() as data:
                data['date_arrival'] = formatted_date

            await message.answer('📅 Напишите дату выезда (например: 20.07.2024)', reply_markup=kb.close3)
            await EditOrderFSM.edit_date_departure.set()

        except ValueError:
            await message.answer('❌ Неверный формат. Введите дату в формате ДД.ММ.ГГ или ДД.ММ.ГГГГ',
                                 reply_markup=kb.close3)

    @dp.message_handler(state=EditOrderFSM.edit_date_departure)
    async def save_edit_date_departure(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение заказа отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            await message.answer('📈 Напишите количество катамаранов:', reply_markup=kb.close3)
            await EditOrderFSM.edit_quantity.set()
            return

        async with state.proxy() as data:
            try:
                try:
                    parsed_date = dt.datetime.strptime(message.text, '%d.%m.%y')
                except ValueError:
                    parsed_date = dt.datetime.strptime(message.text, '%d.%m.%Y')

                formatted_date = parsed_date.strftime('%d.%m.%Y')
                data['date_departure'] = formatted_date

                check = await catamaran.check_availability(
                    data['date_arrival'],
                    data['date_departure'],
                    1,
                    data['order_id']
                )

                if check[0]:
                    await message.answer(
                        f'📈 Напишите количество катамаранов\nСвободно: {check[1]}',
                        reply_markup=kb.close3
                    )
                    await EditOrderFSM.edit_quantity.set()
                else:
                    await message.answer(
                        f'❌ Недостаточно катамаранов на выбранные даты.\nСвободно: {check[1]}',
                        reply_markup=kb.main
                    )
                    await state.finish()

            except ValueError:
                await message.answer(
                    '❌ Неверный формат. Введите дату в формате ДД.ММ.ГГ или ДД.ММ.ГГГГ',
                    reply_markup=kb.close3
                )
            except Exception as e:
                logger.error(f"Ошибка в save_edit_date_departure: {e}")
                await message.answer(
                    '⚠️ Произошла ошибка при проверке дат. Попробуйте позже.',
                    reply_markup=kb.main
                )
                await state.finish()

    @dp.message_handler(state=EditOrderFSM.edit_quantity)
    async def save_edit_quantity(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение заказа отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            await message.answer('⏰ Напишите <b>время приезда</b> (например: 14:30)', reply_markup=kb.close3,
                                 parse_mode='HTML')
            await EditOrderFSM.edit_time_arrival.set()
            return

        async with state.proxy() as data:
            try:
                quantity = int(message.text)
                if quantity <= 0:
                    await message.answer('❌ Количество должно быть больше 0', reply_markup=kb.close3)
                    return

                data['quantity'] = quantity

                check = await catamaran.check_availability(
                    data['date_arrival'],
                    data['date_departure'],
                    quantity,
                    data['order_id']
                )

                if check[0]:
                    await message.answer('⏰ Напишите <b>время приезда</b> (например: 14:30)', reply_markup=kb.close3,
                                         parse_mode='HTML')
                    await EditOrderFSM.edit_time_arrival.set()
                else:
                    await message.answer(
                        f'❌ Недостаточно катамаранов на выбранные даты.\nСвободно: {check[1]}',
                        reply_markup=kb.main
                    )
                    await state.finish()

            except ValueError:
                await message.answer(
                    '❌ Введите корректное число (например: 2)',
                    reply_markup=kb.close3
                )
            except Exception as e:
                logger.error(f"Ошибка в save_edit_quantity: {e}")
                await message.answer(
                    '⚠️ Произошла ошибка при проверке количества',
                    reply_markup=kb.main
                )
                await state.finish()

    @dp.message_handler(state=EditOrderFSM.edit_time_arrival)
    async def save_edit_time_start(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            await message.answer('⏰ Напишите <b>время выезда</b> (например: 14:30)', reply_markup=kb.close3,
                                 parse_mode='HTML')
            await EditOrderFSM.edit_time_departure.set()
            return

        if not re.match(r'^\d{2}:\d{2}$', message.text.strip()):
            await message.answer('❌ Время должно быть в формате ЧЧ:ММ, например: 16:00', reply_markup=kb.close3)
            return

        async with state.proxy() as data:
            data['time_arrival'] = message.text.strip()

        await message.answer('⏰ Напишите <b>время выезда</b> (например: 14:30)', reply_markup=kb.close3,
                             parse_mode='HTML')
        await EditOrderFSM.edit_time_departure.set()

    @dp.message_handler(state=EditOrderFSM.edit_time_departure)
    async def save_edit_time_end(message: types.Message, state: FSMContext):
        user_input = message.text.strip().lower()

        if user_input == 'отменить':
            await message.answer('❌ Изменение отменено.', reply_markup=kb.main)
            await state.finish()
            return

        if user_input == 'пропустить':
            await message.answer('🗺 Выберите маршрут из списка или добавьте новый:',
                                 reply_markup=get_points_a_keyboard())
            await EditOrderFSM.edit_route.set()
            return

        if not re.match(r'^\d{2}:\d{2}$', message.text.strip()):
            await message.answer('❌ Время должно быть в формате ЧЧ:ММ, например: 16:00', reply_markup=kb.close3)
            return

        async with state.proxy() as data:
            data['time_departure'] = message.text.strip()

        await message.answer('🗺 Выберите маршрут из списка или добавьте новый:', reply_markup=get_points_a_keyboard())
        await EditOrderFSM.edit_route.set()

    @dp.callback_query_handler(lambda c: c.data.startswith('select_point_a_'), state=EditOrderFSM.edit_route)
    async def handle_point_a_selected(callback: types.CallbackQuery, state: FSMContext):
        point_a = callback.data.replace('select_point_a_', '')
        async with state.proxy() as data:
            data['point_a'] = point_a

        await callback.message.edit_text(
            f"📍 Вы выбрали точку А: {point_a}\nТеперь выберите пункт Б:",
            reply_markup=get_routes_keyboard_from_point_a(point_a)
        )

    @dp.callback_query_handler(lambda c: c.data.startswith('select_route_'), state=EditOrderFSM.edit_route)
    async def handle_route_selected(callback: types.CallbackQuery, state: FSMContext):
        route_id = int(callback.data.replace('select_route_', ''))
        async with state.proxy() as data:
            data['route_id'] = route_id

        await callback.message.edit_text("👤 Напиши ФИО заказчика")
        await callback.answer()
        await EditOrderFSM.edit_customer_name.set()

    @dp.message_handler(state=EditOrderFSM.edit_route)
    async def edit_route(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
                return
            elif message.text.lower() == 'пропустить':
                await message.answer('👤 Напиши ФИО заказчика', reply_markup=kb.close3)
                await EditOrderFSM.edit_customer_name.set()
                return
            else:
                data['route'] = message.text

        await message.answer('👤 Напиши ФИО заказчика', reply_markup=kb.close3)
        await EditOrderFSM.edit_customer_name.set()

    @dp.message_handler(state=EditOrderFSM.edit_customer_name)
    async def edit_customer_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
                return
            elif message.text.lower() == 'пропустить':
                await message.answer('📞 Напиши "Номер телефона заказчика"', reply_markup=kb.close3)
                await EditOrderFSM.edit_phone.set()
                return
            else:
                data['customer_name'] = message.text
        await message.answer('📞 Напиши "Номер телефона заказчика"', reply_markup=kb.close3)
        await EditOrderFSM.edit_phone.set()

    @dp.message_handler(state=EditOrderFSM.edit_phone)
    async def edit_phone_number(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            try:
                if message.text.lower() == 'отменить':
                    await message.answer('Отменено', reply_markup=kb.main)
                    await state.finish()
                    return
                elif message.text.lower() == 'пропустить':
                    await message.answer('💵 Напиши "Цену заказа"', reply_markup=kb.close3)
                    await EditOrderFSM.edit_price.set()
                    return
                else:
                    phone = re.sub(r'[^0-9]', '', message.text)

                    if len(phone) == 10:
                        whatsapp_link = f"https://wa.me/7{phone}"
                    elif len(phone) == 11 and phone[0] in ('7', '8'):
                        whatsapp_link = f"https://wa.me/7{phone[1:]}"
                    else:
                        await message.answer('❌ Неверный формат номера. Введите 10 или 11 цифр', reply_markup=kb.close3)
                        return

                    data['phone'] = whatsapp_link
                    await message.answer('💵 Напиши "Цену заказа"', reply_markup=kb.close3)
                    await EditOrderFSM.edit_price.set()

            except Exception as e:
                await message.answer('❌ Ошибка обработки номера, попробуйте ещё раз', reply_markup=kb.close3)
                logger.error(f"Phone processing error (edit): {e}")

    @dp.message_handler(state=EditOrderFSM.edit_price)
    async def edit_price(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
                return
            elif message.text.lower() == 'пропустить':
                await message.answer('📝 Напиши "Дополнительные пожелания"', reply_markup=kb.close3)
                await EditOrderFSM.edit_additional_wishes.set()
                return
            else:
                data['price'] = message.text
        await message.answer('📝 Напиши "Дополнительные пожелания"', reply_markup=kb.close3)
        await EditOrderFSM.edit_additional_wishes.set()

    @dp.message_handler(state=EditOrderFSM.edit_additional_wishes)
    async def edit_additional_wishes(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('❌ Отменено', reply_markup=kb.main)
                await state.finish()
                return

            if message.text.lower() != 'пропустить':
                data['additional_wishes'] = message.text
            else:
                data['additional_wishes'] = data.get('additional_wishes', '')

            try:
                order_id = data['order_id']
                text = await kb.info_text(
                    order_id=order_id,
                    date_arrival=data['date_arrival'],
                    date_departure=data['date_departure'],
                    time_arrival=data['time_arrival'],
                    time_departure=data['time_departure'],
                    route_id=data['route_id'],
                    quantity=data['quantity'],
                    customer_name=data['customer_name'],
                    phone_link=data['phone'],
                    price=data['price'],
                    additional_wishes=data['additional_wishes'],
                    status=data['prepayment_status']
                )

                await catamaran.edit_order(
                    date_arrival=data['date_arrival'],
                    date_departure=data['date_departure'],
                    time_arrival=data['time_arrival'],
                    time_departure=data['time_departure'],
                    route_id=data['route_id'],
                    quantity=data['quantity'],
                    customer_name=data['customer_name'],
                    phone=data['phone'],
                    price=data['price'],
                    additional_wishes=data['additional_wishes'],
                    prepayment_status=data['prepayment_status'],
                    order_id=order_id,
                )

                await message.answer(
                    text=f"✅ Бронирование успешно изменено. \n\n {text}",
                    reply_markup=kb.main,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )

            except Exception as e:
                await message.answer('⚠️ Произошла ошибка при сохранении изменений.', reply_markup=kb.main)
                logger.error(f'Ошибка в edit_additional_wishes: {e}')

            await state.finish()