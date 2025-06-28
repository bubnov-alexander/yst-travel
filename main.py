from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile
from dotenv import load_dotenv

import os
import datetime as dt
import pytz
import time as tm

from app import exsel
from app import migration
from app.Models import catamaran
from app import keyboard as kb
import datetime as dt

# ============== Setings ==============

tz = pytz.timezone('Asia/Yekaterinburg')

storage = MemoryStorage()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)

CHAT_ID = -1002219421565

async def on_startup(_):
    await migration.db_start()
    TIME = (dt.datetime.now(tz)).strftime('%H:%M:%S')
    DATE = (dt.datetime.now(tz)).strftime('%d.%m')
    print('Бот запущен:', TIME, DATE)

# ============== Commands ==============

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = user.get_user_id()
    for i in user_id:
        if i == message.chat.id:
            await message.answer('Приветствую, администратор', reply_markup=kb.main)
            return

@dp.message_handler(commands=['get_group_id'])
async def get_group_id(message: types.Message):
    await message.answer(message.chat.id)


# ============== Callback_Query ==============

@dp.callback_query_handler(text='view_orders')
async def view_orders(callback: types.CallbackQuery):
    page = 1
    orders = await migration.get_orders()
    total_pages = (len(orders) + 4) // 5 
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]
    
    if orders_page:
        orders_text, markup = await kb.generate_orders_text_and_markup(orders_page, page, total_pages)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=orders_text, reply_markup=markup, parse_mode='Markdown')

@dp.callback_query_handler(lambda callback: callback.data.startswith("prev_page_"))
async def prev_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[2])
    is_sorted = "sorted" in callback.data
    is_month = "month" in callback.data
    month_number = 0

    if is_sorted == True:        
        orders = await migration.sort_date_order()
    elif is_month == True:
        month_number = int(callback.data.split("_")[4])
        orders = await migration.sort_date_order()
        filtered_orders = []
        for order in orders:
            if int(order[5].split('.')[1]) == month_number:
                filtered_orders.append(order)
        orders = filtered_orders
    else:
        orders = await migration.get_orders()


    total_pages = (len(orders) + 4) // 5
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]
    
    if orders_page:
        orders_text, markup = await kb.generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=orders_text, reply_markup=markup, parse_mode='Markdown')

@dp.callback_query_handler(lambda callback: callback.data.startswith("next_page_"))
async def next_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[2])

    is_sorted = "sorted" in callback.data
    is_month = "month" in callback.data
    month_number = 0

    if is_sorted == True:        
        orders = await migration.sort_date_order()
    elif is_month == True:
        month_number = int(callback.data.split("_")[4])
        orders = await migration.sort_date_order()
        filtered_orders = []
        for order in orders:
            print(order[1])
            if int(order[1].split('.')[1]) == month_number:
                filtered_orders.append(order)
        print(filtered_orders)
    else:
        orders = await migration.get_orders()
    
    total_pages = (len(orders) + 4) // 5
    page += 1
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]

    if orders_page:
        orders_text, markup = await kb.generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted, is_month, month_number)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=orders_text, reply_markup=markup, parse_mode='Markdown')

@dp.callback_query_handler(text='sort_date_order')
async def sort_date_order(callback: types.CallbackQuery):
    page = 1
    orders = await migration.sort_date_order()
    total_pages = (len(orders) + 4) // 5  # Calculate total number of pages
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]

    # Используйте функцию для генерации текста и разметки
    orders_text, markup = await kb.generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted=True)

    # Обновите сообщение с новым текстом и разметкой
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=orders_text, reply_markup=markup, parse_mode='Markdown')

@dp.callback_query_handler(text='sort_month_order')
async def sort_month_order(callback: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выберите месяц', reply_markup=kb.months)

@dp.callback_query_handler(text='search_order')
async def search_order(callback: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выбери нужный вариант сортировки', reply_markup=kb.sort_orders)

@dp.callback_query_handler(lambda callback: callback.data.startswith('sort_by_'))
async def sort_by_month(callback: types.CallbackQuery):
    page = 1
    orders = await migration.get_orders()

    month = callback.data.split('_')[2]
    month_number = None

    if month == 'may':
        month_number = 5
    elif month == 'june':
        month_number = 6
    elif month == 'july':
        month_number = 7
    elif month == 'august':
        month_number = 8
    elif month == 'september':
        month_number = 9

    if month_number is not None:
        orders = [order for order in orders if int(order[1].split('.')[1]) == month_number]

        if orders == []:
            await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='В этом месяце нет заказов', reply_markup=kb.main)
        else:
            page = 1
            orders = await migration.sort_date_order()
            orders = [order for order in orders if int(order[1].split('.')[1]) == month_number]
            total_pages = (len(orders) + 4) // 5 
            start_index = (page - 1) * 5
            end_index = start_index + 5
            orders_page = orders[start_index:end_index]

            orders_text, markup = await kb.generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted=False, is_month=True, month_number=month_number)
            await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=orders_text, reply_markup=markup, parse_mode='Markdown')

@dp.callback_query_handler(text='close')
async def close_callback(callback: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Выбери что хочешь сделать', reply_markup=kb.main, parse_mode='Markdown')

@dp.callback_query_handler(text='exsel')
async def send_exsel(callback: types.CallbackQuery):
    db_path = 'data/database.db'
    excel_path = 'data/catamaran_data.xlsx'
    
    exsel.export_sql_to_excel(db_path, excel_path)

    file = InputFile(excel_path)
    await bot.send_document(callback.from_user.id, file)

    os.remove(excel_path)  # Удаляем файл после отправки

# ============== FSM Machne ==============

class my_fsm(StatesGroup):
    add_date_start = State()
    add_date_end = State()
    add_quantity = State()
    add_time_start = State()
    add_route = State()
    add_customer_name = State()
    add_phone_number = State()
    add_price = State()
    add_additional_wishes = State()

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

    delete_order = State()

    search_order = State()

    search_order_by_date = State()

    status_order = State()

    search_free_orders = State()

# ============== Add order ==============

@dp.callback_query_handler(text='add_order')
async def add_order(callback: types.CallbackQuery):
    await my_fsm.add_date_start.set()
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='🟢 Напиши "Дату приезда"', reply_markup=kb.close2)

@dp.message_handler(state=my_fsm.add_date_start)
async def save_date_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            try:
                data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
            except:
                data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')
            await bot.send_message(chat_id=message.chat.id, text='🔴 Напиши "Дату выезда"', reply_markup=kb.close2)
            await my_fsm.next()
        except:
            await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)

@dp.message_handler(state=my_fsm.add_date_end)
async def save_date_end(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        try:
            try:
                data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
            except:
                data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')
            check = await migration.check_availability(data['date_start'], data['date_end'], 1)
            if check[0] == True:
                await bot.send_message(chat_id=message.chat.id, text=f'📈 Напиши "Количество катамаранов" Свободно: {check[1]}', reply_markup=kb.close2)
                await my_fsm.next()
            else:
                await message.answer(f'Недостаточно катамаранов на выбранные даты. Свободных мест: 0', reply_markup=kb.main)
                await state.finish()
        except Exception as e:
            print(e)
            await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)
    
@dp.message_handler(state=my_fsm.add_quantity)
async def save_quantity(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['quantity'] = message.text
        print(data['quantity'])

    check = await migration.check_availability(data['date_start'], data['date_end'], int(data['quantity']))

    if check[0]:
        await bot.send_message(chat_id=message.chat.id, text='⏰️ Напиши "Время приезда"', reply_markup=kb.close2)
        await my_fsm.next()
    else:
        await message.answer(f'Недостаточно катамаранов на выбранные даты. Свободных мест: {check[1]}', reply_markup=kb.main)
        await state.finish()

@dp.message_handler(state=my_fsm.add_time_start)
async def save_time_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time_start'] = message.text
    await bot.send_message(chat_id=message.chat.id, text='🗺 Напиши "Маршрут"', reply_markup=kb.close2)
    await my_fsm.next()


@dp.message_handler(state=my_fsm.add_route)
async def save_route(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['route'] = (message.text)
    await bot.send_message(chat_id=message.chat.id, text='👤 Напиши "Имя заказчика"', reply_markup=kb.close2)
    await my_fsm.next()

@dp.message_handler(state=my_fsm.add_customer_name)
async def save_customer_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['customer_name'] = message.text
    await bot.send_message(chat_id=message.chat.id, text='📞 Напиши "Номер телефона заказчика"', reply_markup=kb.close2)
    await my_fsm.next()

@dp.message_handler(state=my_fsm.add_phone_number)
async def save_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.text
    await bot.send_message(chat_id=message.chat.id, text='💵 Напиши "Цену заказа"', reply_markup=kb.close2)
    await my_fsm.next()

@dp.message_handler(state=my_fsm.add_price)
async def save_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
            data['price'] = message.text
    await bot.send_message(chat_id=message.chat.id, text='📝 Напиши "Дополнительные пожелания"', reply_markup=kb.close3)
    await my_fsm.next()

@dp.message_handler(state=my_fsm.add_additional_wishes)
async def save_additional_wishes(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'пропустить':
            data['additional_wishes'] = ''
        else:
            data['additional_wishes'] = message.text

        # Добавление бронирования
        booking_successful = migration.add_booking(data['date_start'], data['date_end'], data['time_start'], data['route'], data['quantity'], data['customer_name'], data['phone_number'], data['price'], data['additional_wishes'])
        info_text = await kb.info_text(booking_successful, data['date_start'], data['date_end'], data['time_start'], data['route'], data['quantity'], data['customer_name'], data['phone_number'], data['price'], data['additional_wishes'], status = 0)
        if booking_successful:
            await message.answer('Бронирование успешно добавлено.', reply_markup=kb.main)
            await bot.send_message(chat_id=CHAT_ID, text=f"Новое бронирование: {info_text}")
        else:
            await message.answer('Недостаточно катамаранов на выбранные даты. Пожалуйста, выберите другие даты.', reply_markup=kb.main)

    await state.finish()

# ============== Delete order ==============

@dp.callback_query_handler(text='delete_order')
async def delete_order(callback: types.CallbackQuery):
    await my_fsm.delete_order.set()
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Введите ID заказа, который хотите удалить', reply_markup=kb.close2)

@dp.message_handler(state=my_fsm.delete_order)
async def delete_order_by_id(message: types.Message, state: FSMContext):
    order_id = message.text
    order = await migration.get_order_by_id(order_id)
    if order:
        await migration.delete_order(order_id)
        await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} удален', reply_markup=kb.main)
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} не найден', reply_markup=kb.main)
    await state.finish()

# ============== FSM edit_order ==============


@dp.callback_query_handler(text='edit_order')
async def edit_order(callback: types.CallbackQuery):
    await my_fsm.edit_order.set()
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Введите ID заказа, который хотите изменить', reply_markup=kb.close2)

@dp.message_handler(state=my_fsm.edit_order)
async def edit_order_by_id(message: types.Message, state: FSMContext):
    order_id = message.text
    order = await migration.get_order_by_id(order_id)
    if order:
        await my_fsm.edit_date_start.set()
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

        text = await kb.info_text(order_id, data['date_start'], data['date_end'], data['time_start'], data['route'], data['quantity'], data['customer_name'], data['phone_number'], data['price'], data['additional_wishes'], order[10])
        await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=kb.close3)
        await bot.send_message(chat_id=message.chat.id, text='🟢 Напиши "Дату приезда"', reply_markup=kb.close3)
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} не найден', reply_markup=kb.main)
        await state.finish()

@dp.message_handler(state=my_fsm.edit_date_start)
async def edit_date_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'отменить':
            await message.answer('Отменено', reply_markup=kb.main)
            await state.finish()


        elif message.text.lower() == 'пропустить':
            await bot.send_message(chat_id=message.chat.id, text='🔴 Напиши "Дату выезда"', reply_markup=kb.close3)
            await my_fsm.next()
        else:
            try:
                try:
                    data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
                except:
                    data['date_start'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')
                await bot.send_message(chat_id=message.chat.id, text='🔴 Напиши "Дату выезда"', reply_markup=kb.close3)
                await my_fsm.next()
            except:
                await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close3)

@dp.message_handler(state=my_fsm.edit_date_end)
async def edit_date_end(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'отменить':
            await message.answer('Отменено', reply_markup=kb.main)
            await state.finish()

        elif message.text.lower() == 'пропустить':
            await bot.send_message(chat_id=message.chat.id, text='📈 Напиши "Количество катамаранов"', reply_markup=kb.close3)
            await my_fsm.next()
        else:
            try:
                try:
                    data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%y').strftime('%d.%m.%Y')
                except:
                    data['date_end'] = dt.datetime.strptime(message.text, '%d.%m.%Y').strftime('%d.%m.%Y')

                check = await migration.check_availability(data['date_start'], data['date_end'], 1, data['order_id'])
                if check[0] == True:
                    await bot.send_message(chat_id=message.chat.id, text='📈 Напиши "Количество катамаранов"', reply_markup=kb.close3)
                    await my_fsm.next()
                else:
                    await message.answer(f'Недостаточно катамаранов на выбранные даты. Свободных мест: 0', reply_markup=kb.main)
                    await state.finish()
            except Exception as e:
                print(e)
                await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close3)

@dp.message_handler(state=my_fsm.edit_quantity)
async def edit_quantity(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'отменить':
            await message.answer('Отменено', reply_markup=kb.main)
            await state.finish()

        elif message.text.lower() == 'пропустить':
            await bot.send_message(chat_id=message.chat.id, text='⏰️ Напиши "Время приезда"', reply_markup=kb.close3)
            await my_fsm.next()
        else:
            data['quantity'] = message.text

            check = await migration.check_availability(data['date_start'], data['date_end'], int(data['quantity']), data['order_id'])

            if check[0]:
                await bot.send_message(chat_id=message.chat.id, text='⏰️ Напиши "Время приезда"', reply_markup=kb.close3)
                await my_fsm.next()
            else:
                await message.answer(f'Недостаточно катамаранов на выбранные даты. Свободных мест: {check[1]}', reply_markup=kb.main)
                await state.finish()

@dp.message_handler(state=my_fsm.edit_time_start)
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
        await my_fsm.next()

@dp.message_handler(state=my_fsm.edit_route)
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
        await my_fsm.next()

@dp.message_handler(state=my_fsm.edit_customer_name)
async def edit_customer_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'отменить':
            await message.answer('Отменено', reply_markup=kb.main)
            await state.finish()
        elif message.text.lower() == 'пропустить':
            pass
        else:
            data['customer_name'] = message.text
        await bot.send_message(chat_id=message.chat.id, text='📞 Напиши "Номер телефона заказчика"', reply_markup=kb.close3)
        await my_fsm.next()

@dp.message_handler(state=my_fsm.edit_phone_number)
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
        await my_fsm.next()

@dp.message_handler(state=my_fsm.edit_price)
async def edit_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text.lower() == 'отменить':
            await message.answer('Отменено', reply_markup=kb.main)
            await state.finish()
        elif message.text.lower() == 'пропустить':
            await bot.send_message(chat_id=message.chat.id, text='📝 Напиши "Дополнительные пожелания"', reply_markup=kb.close3)
            await my_fsm.next()
        else:
            if message.text != int:
                try:
                    data['price'] = int(message.text)
                except:
                    bot.send_message(chat_id=message.chat.id, text='Цена должна быть числом', reply_markup=kb.close3)
            await bot.send_message(chat_id=message.chat.id, text='📝 Напиши "Дополнительные пожелания"', reply_markup=kb.close3)
            await my_fsm.next()

@dp.message_handler(state=my_fsm.edit_additional_wishes)
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
        text = await kb.info_text(order_id, data['date_start'], data['date_end'], data['time_start'], data['route'], data['quantity'], data['customer_name'], data['phone_number'], data['price'], data['additional_wishes'], status=0)
        await migration.edit_order(data['date_start'], data['date_end'], data['time_start'], data['route'], data['quantity'], data['customer_name'], data['phone_number'], data['price'], data['additional_wishes'], order_id)
        await message.answer('Бронирование успешно изменено.', reply_markup=kb.main)

        await state.finish()

# ============= FSM Search order ==============

@dp.callback_query_handler(text='search_id_order')
async def search_order(callback: types.CallbackQuery):
    await my_fsm.search_order.set()
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Введите ID заказа, который хотите найти', reply_markup=kb.close4)

@dp.message_handler(state=my_fsm.search_order)
async def search_order_by_id(message: types.Message, state: FSMContext):
    if message.text != int or message.text == '':
        try:
            order_id = int(message.text)
        except:
            await bot.send_message(chat_id=message.chat.id, text='ID заказа должен быть числом', reply_markup=kb.main)
            await state.finish()
            
    order = await migration.get_order_by_id(order_id)
    if order:
        text = await kb.info_text(order[0], order[1], order[2], order[3], order[4], order[5], order[6], order[7], order[8], order[9], order[10])
        await bot.send_message(chat_id=message.chat.id, text=text, reply_markup=kb.main)
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} не найден', reply_markup=kb.main)
    await state.finish()

# ============== Search order by date ==============

@dp.callback_query_handler(text='search_date_order')
async def search_date_order(callback: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='🟢 Напиши дату заказа который хочешь найти:', reply_markup=kb.close2)
    await my_fsm.search_order_by_date.set()

@dp.message_handler(state=my_fsm.search_order_by_date)
async def process_order_search(message: types.Message, state: FSMContext):
    date = message.text

    try:
        try:
            date = dt.datetime.strptime(date, '%d.%m.%y').strftime('%d.%m.%Y')  
        except:
            date = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%d.%m.%Y')

        db_date = await migration.get_order_by_date(date)
        if db_date:
            for i in db_date:
                text = await kb.info_text(i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10])
                await message.answer(text, reply_markup=kb.main)
        else:
            await message.answer('Заказ не найден.', reply_markup=kb.sort_orders)
    except Exception as e:
        print(e)
        await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)

    await state.finish()

# ============== Chenge Status ==============

@dp.callback_query_handler(text='status_order')
async def status_order(callback: types.CallbackQuery):
    await my_fsm.status_order.set()
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Введите ID заказа, который хотите изменить', reply_markup=kb.close2)

@dp.message_handler(state=my_fsm.status_order)
async def status_order_by_id(message: types.Message, state: FSMContext):
    order_id = message.text
    order = await migration.get_order_by_id(order_id)
    if order:
        await migration.status_order(order_id)
        await bot.send_message(chat_id=message.chat.id, text=f'Статус заказа с ID {order_id} изменен', reply_markup=kb.main)
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Заказ с ID {order_id} не найден', reply_markup=kb.main)
    await state.finish()

# ============== Search free orders ==============
@dp.callback_query_handler(text='search_free_order')
async def search_free_orders(callback: types.CallbackQuery):
    await my_fsm.search_free_orders.set()
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='🟢 Напиши дату, на которую хочешь найти свободные заказы:', reply_markup=kb.close2)

@dp.message_handler(state=my_fsm.search_free_orders)
async def process_free_orders_search(message: types.Message, state: FSMContext):
    date = message.text

    try:
        try:
            date = dt.datetime.strptime(date, '%d.%m.%y').strftime('%d.%m.%Y')
        except:
            date = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%d.%m.%Y')

        db_date = await migration.get_available_catamarans(date)
        if db_date:
            await message.answer(text= f'Свободных мест на эту дату {db_date}', reply_markup=kb.main)
        else:
            await message.answer('Свободных заказов не найдено.', reply_markup=kb.main)
    except Exception as e:
        print(e)
        await message.answer('Дата должна быть в формате ДД.ММ.ГГ', reply_markup=kb.close2)

    await state.finish()

# ============== FSM close ==============

@dp.callback_query_handler(state="*", text='close_callback')
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Я отменил твой запрос', reply_markup=kb.main)
    await state.finish()

@dp.callback_query_handler(state="*", text='close_callback2')
async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='Я отменил твой запрос', reply_markup=kb.sort_orders)
    await state.finish()

@dp.message_handler(state="*", commands=['cancel'])
async def cancel_handler(message: types.Message, state: FSMContext):
    await message.answer('Я отменил твой запрос', reply_markup=kb.main)
    await state.finish()

# ============== Run ==============

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)