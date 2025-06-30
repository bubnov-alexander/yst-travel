from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import datetime as dt

from app.database.Models import catamaran
from app import keyboard as kb

class EditOrderFSM(StatesGroup):
    edit_order = State()
    edit_date_start = State()
    edit_date_end = State()
    edit_quantity = State()
    edit_time_start = State()
    edit_route = State()
    edit_customer_name = State()
    edit_phone_number = State()
    edit_price = State()
    edit_additional_wishes = State()

def register_edit_catamaran_handlers(dp, bot):
    @dp.callback_query_handler(text='edit_order')
    async def edit_order(callback: types.CallbackQuery):
        await EditOrderFSM.edit_order.set()
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text='Введите ID заказа, который хотите изменить', reply_markup=kb.close2)

    @dp.message_handler(state=EditOrderFSM.edit_order)
    async def edit_order_by_id(message: types.Message, state: FSMContext):
        order_id = message.text
        order = await catamaran.get_order_by_id(order_id)
        if order:
            await EditOrderFSM.edit_date_start.set()
            await state.update_data(order_id=order_id)

            async with state.proxy() as data:
                # Save the order details in the state
                data['order_id'] = order_id
                data['date_start'] = order[1]
                data['date_end'] = order[2]
                data['time_start'] = order[3]
                data['route'] = order[4]
                data['quantity'] = order[5]
                data['customer_name'] = order[6]
                data['phone_number'] = order[7]
                data['price'] = order[8]
                data['additional_wishes'] = order[9]

            text = await kb.info_text(order_id, data['date_start'], data['date_end'], data['time_start'], data['route'],
                                      data['quantity'], data['customer_name'], data['phone_number'], data['price'],
                                      data['additional_wishes'], order[10])
            await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=kb.close3)
            await bot.send_message(chat_id=message.chat.id, text='🟢 Напиши "Дату приезда"', reply_markup=kb.close3)
        else:
            await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} не найден',
                                   reply_markup=kb.main)
            await state.finish()

    @dp.message_handler(state=EditOrderFSM.edit_date_start)
    async def edit_date_start(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()


            elif message.text.lower() == 'пропустить':
                await bot.send_message(chat_id=message.chat.id, text='🔴 Напиши "Дату выезда"', reply_markup=kb.close3)
                await EditOrderFSM.next()
            else:
                try:
                    try:
                        data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
                    except:
                        data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')
                    await bot.send_message(chat_id=message.chat.id, text='🔴 Напиши "Дату выезда"',
                                           reply_markup=kb.close3)
                    await EditOrderFSM.next()
                except:
                    await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close3)

    @dp.message_handler(state=EditOrderFSM.edit_date_end)
    async def edit_date_end(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()

            elif message.text.lower() == 'пропустить':
                await bot.send_message(chat_id=message.chat.id, text='📈 Напиши "Количество катамаранов"',
                                       reply_markup=kb.close3)
                await EditOrderFSM.next()
            else:
                try:
                    try:
                        data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
                    except:
                        data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')

                    check = await catamaran.check_availability(data['date_start'], data['date_end'], 1,
                                                               data['order_id'])
                    if check[0] == True:
                        await bot.send_message(chat_id=message.chat.id, text='📈 Напиши "Количество катамаранов"',
                                               reply_markup=kb.close3)
                        await EditOrderFSM.next()
                    else:
                        await message.answer(f'Недостаточно катамаранов на выбранные даты. Свободных мест: 0',
                                             reply_markup=kb.main)
                        await state.finish()
                except Exception as e:
                    print(e)
                    await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close3)

    @dp.message_handler(state=EditOrderFSM.edit_quantity)
    async def edit_quantity(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()

            elif message.text.lower() == 'пропустить':
                await bot.send_message(chat_id=message.chat.id, text='⏰️ Напиши "Время приезда"',
                                       reply_markup=kb.close3)
                await EditOrderFSM.next()
            else:
                data['quantity'] = message.text

                check = await catamaran.check_availability(data['date_start'], data['date_end'], int(data['quantity']),
                                                           data['order_id'])

                if check[0]:
                    await bot.send_message(chat_id=message.chat.id, text='⏰️ Напиши "Время приезда"',
                                           reply_markup=kb.close3)
                    await EditOrderFSM.next()
                else:
                    await message.answer(f'Недостаточно катамаранов на выбранные даты. Свободных мест: {check[1]}',
                                         reply_markup=kb.main)
                    await state.finish()

    @dp.message_handler(state=EditOrderFSM.edit_time_start)
    async def edit_time_start(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
            elif message.text.lower() == 'пропустить':
                pass
            else:
                data['time_start'] = message.text

            await bot.send_message(chat_id=message.chat.id, text='🗺 Напиши "Маршрут"', reply_markup=kb.close3)
            await EditOrderFSM.next()

    @dp.message_handler(state=EditOrderFSM.edit_route)
    async def edit_route(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
            elif message.text.lower() == 'пропустить':
                pass
            else:
                data['route'] = (message.text)
            await bot.send_message(chat_id=message.chat.id, text='👤 Напиши "Имя заказчика"', reply_markup=kb.close3)
            await EditOrderFSM.next()

    @dp.message_handler(state=EditOrderFSM.edit_customer_name)
    async def edit_customer_name(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
            elif message.text.lower() == 'пропустить':
                pass
            else:
                data['customer_name'] = message.text
            await bot.send_message(chat_id=message.chat.id, text='📞 Напиши "Номер телефона заказчика"',
                                   reply_markup=kb.close3)
            await EditOrderFSM.next()

    @dp.message_handler(state=EditOrderFSM.edit_phone_number)
    async def edit_phone_number(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
            elif message.text.lower() == 'пропустить':
                pass
            else:
                data['phone_number'] = message.text
            await bot.send_message(chat_id=message.chat.id, text='💵 Напиши "Цену заказа"', reply_markup=kb.close3)
            await EditOrderFSM.next()

    @dp.message_handler(state=EditOrderFSM.edit_price)
    async def edit_price(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
            elif message.text.lower() == 'пропустить':
                await bot.send_message(chat_id=message.chat.id, text='📝 Напиши "Дополнительные пожелания"',
                                       reply_markup=kb.close3)
                await EditOrderFSM.next()
            else:
                if message.text != int:
                    try:
                        data['price'] = int(message.text)
                    except:
                        await bot.send_message(chat_id=message.chat.id, text='Цена должна быть числом',
                                               reply_markup=kb.close3)
                await bot.send_message(chat_id=message.chat.id, text='📝 Напиши "Дополнительные пожелания"',
                                       reply_markup=kb.close3)
                await EditOrderFSM.next()

    @dp.message_handler(state=EditOrderFSM.edit_additional_wishes)
    async def edit_additional_wishes(message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            if message.text.lower() == 'отменить':
                await message.answer('Отменено', reply_markup=kb.main)
                await state.finish()
            elif message.text.lower() == 'пропустить':
                pass
            else:
                data['additional_wishes'] = message.text

            # Изменение заказа
            order_id = data['order_id']
            text = await kb.info_text(order_id, data['date_start'], data['date_end'], data['time_start'], data['route'],
                                      data['quantity'], data['customer_name'], data['phone_number'], data['price'],
                                      data['additional_wishes'], status=0)
            await catamaran.edit_order(data['date_start'], data['date_end'], data['time_start'], data['route'],
                                       data['quantity'], data['customer_name'], data['phone_number'], data['price'],
                                       data['additional_wishes'], order_id)
            await message.answer('Бронирование успешно изменено.', reply_markup=kb.main)

            await state.finish()