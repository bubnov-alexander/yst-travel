from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import datetime as dt

from app.database.Models import catamaran
from app import keyboard as kb
from config import CHAT_ID
from app.utils.logger import logger


class MyFSM(StatesGroup):
    add_date_start = State()
    add_date_end = State()
    add_quantity = State()
    add_time_start = State()
    add_route = State()
    add_customer_name = State()
    add_phone_number = State()
    add_price = State()
    add_additional_wishes = State()


def register_add_catamaran_handlers(dp, bot):
    @dp.callback_query_handler(text='add_order')
    async def add_order(callback: types.CallbackQuery):
        await MyFSM.add_date_start.set()
        await bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='🟢 Напиши "Дату приезда"',
            reply_markup=kb.close2
        )

    @dp.message_handler(state=MyFSM.add_date_start)
    async def save_date_start(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            try:
                try:
                    data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
                except:
                    data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')
                await message.answer('🔴 Напиши "Дату выезда"', reply_markup=kb.close2)
                await MyFSM.next()
            except:
                await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)

    @dp.message_handler(state=MyFSM.add_date_end)
    async def save_date_end(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            try:
                try:
                    data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
                except:
                    data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')
                check = await catamaran.check_availability(data['date_start'], data['date_end'], 1)
                if check[0]:
                    await message.answer(f'📈 Напиши "Количество катамаранов" Свободно: {check[1]}', reply_markup=kb.close2)
                    await MyFSM.next()
                else:
                    await message.answer('Недостаточно катамаранов на выбранные даты. Свободных мест: 0', reply_markup=kb.main)
                    await state.finish()
            except:
                await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)

    @dp.message_handler(state=MyFSM.add_quantity)
    async def save_quantity(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['quantity'] = message.text
            check = await catamaran.check_availability(data['date_start'], data['date_end'], int(data['quantity']))
            if check[0]:
                await message.answer('⏰️ Напиши "Время приезда"', reply_markup=kb.close2)
                await MyFSM.next()
            else:
                await message.answer(f'Недостаточно катамаранов. Свободно: {check[1]}', reply_markup=kb.main)
                await state.finish()

    @dp.message_handler(state=MyFSM.add_time_start)
    async def save_time_start(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['time_start'] = message.text
        await message.answer('🗺 Напиши "Маршрут"', reply_markup=kb.close2)
        await MyFSM.next()

    @dp.message_handler(state=MyFSM.add_route)
    async def save_route(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['route'] = message.text
        await message.answer('👤 Напиши "Имя заказчика"', reply_markup=kb.close2)
        await MyFSM.next()

    @dp.message_handler(state=MyFSM.add_customer_name)
    async def save_customer_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['customer_name'] = message.text
        await message.answer('📞 Напиши "Номер телефона заказчика"', reply_markup=kb.close2)
        await MyFSM.next()

    @dp.message_handler(state=MyFSM.add_phone_number)
    async def save_phone_number(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['phone_number'] = message.text
        await message.answer('💵 Напиши "Цену заказа"', reply_markup=kb.close2)
        await MyFSM.next()

    @dp.message_handler(state=MyFSM.add_price)
    async def save_price(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['price'] = message.text
        await message.answer('📝 Напиши "Дополнительные пожелания"', reply_markup=kb.close3)
        await MyFSM.next()

    @dp.message_handler(state=MyFSM.add_additional_wishes)
    async def save_additional_wishes(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['additional_wishes'] = '' if message.text.lower() == 'пропустить' else message.text
            booking_successful = catamaran.add_booking(
                data['date_start'], data['date_end'], data['time_start'], data['route'],
                data['quantity'], data['customer_name'], data['phone_number'],
                data['price'], data['additional_wishes']
            )
            info_text = await kb.info_text(
                booking_successful, data['date_start'], data['date_end'], data['time_start'],
                data['route'], data['quantity'], data['customer_name'], data['phone_number'],
                data['price'], data['additional_wishes'], status=0
            )
            if booking_successful:
                await message.answer('Бронирование успешно добавлено.', reply_markup=kb.main)
                try:
                    await message.bot.send_message(chat_id=CHAT_ID, text=f"Новое бронирование: {info_text}")
                except:
                    logger.error(f'Не удалось отправить сообщение в чат')
            else:
                await message.answer('Недостаточно катамаранов. Попробуйте выбрать другие даты.', reply_markup=kb.main)
        await state.finish()
