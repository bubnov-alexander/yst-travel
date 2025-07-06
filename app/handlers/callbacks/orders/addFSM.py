from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import re
import datetime as dt

from app.database.Models import catamaran
from app import keyboard as kb
from app.database.Models.order import check_availability, add_new_order
from app.utils.getRouteButton import get_points_a_keyboard, get_routes_keyboard_from_point_a
from config import CHAT_ID
from app.utils.logger import logger


class MyFSM(StatesGroup):
    add_date_start = State()
    add_date_end = State()
    add_quantity = State()
    add_time_start = State()
    add_time_end = State()
    add_route = State()
    add_customer_name = State()
    add_phone_number = State()
    add_additional_wishes = State()
    add_prepayment_status = State()


def register_add_order_handlers(dp, bot):
    @dp.callback_query_handler(text='add_order')
    async def add_order(callback: types.CallbackQuery):
        await MyFSM.add_date_start.set()
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='📅 Дата приезда (например: 15.07.2024)',
            reply_markup=kb.close2
        )

    @dp.message_handler(state=MyFSM.add_date_start)
    async def save_date_start(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            try:
                try:
                    data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
                except ValueError:
                    data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')

                await message.answer('📅 Напишите дату выезда (например: 20.07.2024)', reply_markup=kb.close2)
                await MyFSM.next()

            except ValueError:
                await message.answer('❌ Дата приезда должна быть в формате ДД.ММ.ГГ или ДД.ММ.ГГГГ',
                                     reply_markup=kb.close2)

    @dp.message_handler(state=MyFSM.add_date_end)
    async def save_date_end(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            try:
                # Пробуем распарсить дату в двух форматах
                try:
                    data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
                except ValueError:
                    data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')

                # Проверяем доступность ресурсов (с нулями — просто проверка занятости)
                check = await check_availability(
                    data['date_start'],
                    data['date_end'],
                    {
                        'catamarans': 0,
                        'supboards': 0,
                        'transfers': 0
                    }
                )

                if check[0]:
                    remaining = check[1]

                    await message.answer(
                        f'✅ Даты свободны\n'
                        f'Доступно:\n'
                        f'• Катамаранов — {remaining["catamarans"]}\n'
                        f'• Сапбордов — {remaining["supboards"]}\n'
                        f'• Трансферов — {remaining["transfers"]}\n\n'
                        f'🕒 Теперь введите время прибытия в формате ЧЧ:ММ',
                        reply_markup=kb.close2,
                        parse_mode='HTML'
                    )
                    await MyFSM.add_time_start.set()

                else:
                    await message.answer(
                        '❌ Недостаточно свободных ресурсов на выбранные даты\n'
                        f'Свободно: '
                        f'катамаранов — {check[1]["catamarans"]}, '
                        f'Сапбордов — {check[1]["supboards"]}, '
                        f'трансферов — {check[1]["transfers"]}',
                        reply_markup=kb.main,
                        parse_mode='HTML'
                    )
                    await state.finish()

            except Exception as e:
                await message.answer(
                    text=f'❌ Дата выезда должна быть в формате ДД.ММ.ГГ или ДД.ММ.ГГГГ {e}',
                    reply_markup=kb.close2
                )
            except Exception as e:
                await message.answer(
                    '⚠️ Произошла ошибка при проверке доступности',
                    reply_markup=kb.main
                )
                await state.finish()
                logger.error(f"Ошибка в функции save_date_end: {e}")

    @dp.message_handler(state=MyFSM.add_time_start)
    async def save_time_start(message: types.Message, state: FSMContext):
        if not re.match(r'^\d{2}:\d{2}$', message.text.strip()):
            await message.answer('❌ Время должно быть в формате ЧЧ:ММ, например: 16:00', reply_markup=kb.close2)
            return
        async with state.proxy() as data:
            data['time_start'] = message.text
        await message.answer('⏰ Напишите "Время выезда" (например: 14:30)', reply_markup=kb.close2)
        await MyFSM.next()

    @dp.message_handler(state=MyFSM.add_time_end)
    async def save_time_end(message: types.Message, state: FSMContext):
        if not re.match(r'^\d{2}:\d{2}$', message.text.strip()):
            await message.answer('❌ Время должно быть в формате ЧЧ:ММ, например: 16:00', reply_markup=kb.close2)
            return

        async with state.proxy() as data:
            data['time_end'] = message.text.strip()

        await message.answer('🗺 Выберите маршрут из списка или добавьте новый:', reply_markup=get_points_a_keyboard())
        await MyFSM.add_route.set()

    @dp.callback_query_handler(lambda c: c.data.startswith('select_route_'), state=MyFSM.add_route)
    async def route_selected(callback: types.CallbackQuery, state: FSMContext):
        try:
            route_id = int(callback.data.replace('select_route_', ''))
        except:
            return
        async with state.proxy() as data:
            data['route_id'] = route_id

        await callback.message.edit_text("👤 Напиши ФИО заказчика", reply_markup=kb.close2)
        await MyFSM.next()

    @dp.message_handler(state=MyFSM.add_customer_name)
    async def save_customer_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['customer_name'] = message.text
        await message.answer('📞 Напиши "Номер телефона заказчика"', reply_markup=kb.close2)
        await MyFSM.next()

    @dp.callback_query_handler(lambda c: c.data.startswith('select_point_a_'), state=MyFSM.add_route)
    async def handle_point_a_selected(callback: types.CallbackQuery, state: FSMContext):
        point_a = callback.data.replace('select_point_a_', '')
        async with state.proxy() as data:
            data['point_a'] = point_a

        await callback.message.edit_text(
            text=f"📍 Вы выбрали точку А: {point_a}\nТеперь выберите пункт Б:",
            reply_markup=get_routes_keyboard_from_point_a(point_a)
        )

    @dp.callback_query_handler(lambda c: c.data.startswith('select_route_'), state=MyFSM.add_route)
    async def route_selected(callback: types.CallbackQuery, state: FSMContext):
        route_id = int(callback.data.replace('select_route_', ''))
        async with state.proxy() as data:
            data['route_id'] = route_id

        await callback.message.edit_text("👤 Введите ФИО заказчика:", reply_markup=kb.close2)
        await MyFSM.next()

    @dp.message_handler(state=MyFSM.add_phone_number)
    async def save_phone_number(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            try:
                phone = re.sub(r'[^0-9]', '', message.text)

                if len(phone) == 10:
                    whatsapp_link = f"https://wa.me/7{phone}"
                elif len(phone) == 11 and phone[0] in ('7', '8'):
                    whatsapp_link = f"https://wa.me/7{phone[1:]}"
                else:
                    await message.answer('❌ Неверный формат номера. Введите 10 или 11 цифр', reply_markup=kb.close2)
                    return

                data['customer_phone'] = whatsapp_link
                await message.answer('📝 Напиши "Дополнительные пожелания"', reply_markup=kb.close2)
                await MyFSM.next()

            except Exception as e:
                await message.answer('❌ Ошибка обработки номера, попробуйте ещё раз', reply_markup=kb.close2)
                logger.error(f"Phone processing error: {e}")

    @dp.message_handler(state=MyFSM.add_additional_wishes)
    async def save_additional_wishes(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['additional_wishes'] = None if message.text.lower() == 'пропустить' else message.text

            booking_successful = await add_new_order(
                date_arrival=data['date_start'],
                date_departure=data['date_end'],
                time_arrival=data['time_start'],
                time_departure=data['time_end'],
                route_id=data['route_id'],
                customer_name=data['customer_name'],
                phone=data['customer_phone'],
                additional_wishes=data['additional_wishes'],
                prepayment_status=0
            )

            info_text = await kb.info_text(
                order_id=booking_successful,
                date_arrival=data['date_start'],
                date_departure=data['date_end'],
                time_arrival=data['time_start'],
                time_departure=data['time_end'],
                route_id=data['route_id'],
                customer_name=data['customer_name'],
                phone_link=data['customer_phone'],
                additional_wishes=data['additional_wishes'],
                status=False
            )

            if booking_successful:
                buttons = await kb.add_service_buttons(booking_successful)
                await message.answer(
                    text=f'Бронирование успешно добавлено. \n {info_text}',
                    reply_markup=buttons,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                try:
                    await message.bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"Новое бронирование: {info_text}",
                        parse_mode='HTML',
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    logger.error(f'Не удалось отправить сообщение в чат: {e}')
            else:
                await message.answer('Недостаточно катамаранов. Попробуйте выбрать другие даты.', reply_markup=kb.main)

        await state.finish()
