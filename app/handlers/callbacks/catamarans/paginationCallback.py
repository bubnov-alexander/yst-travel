from aiogram import types
from app import keyboard
from app.database.Models import catamaran

async def prev_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[2])
    is_sorted = "sorted" in callback.data
    is_month = "month" in callback.data

    if is_sorted:
        orders = await catamaran.sort_date_order()
    elif is_month:
        month_number = int(callback.data.split("_")[4])
        orders = await catamaran.sort_date_order()
        filtered_orders = []
        for order in orders:
            if int(order[5].split('.')[1]) == month_number:
                filtered_orders.append(order)
        orders = filtered_orders
    else:
        orders = await catamaran.get_orders()

    total_pages = (len(orders) + 4) // 5
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]

    if orders_page:
        orders_text, markup = await keyboard.generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted)
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text=orders_text, reply_markup=markup, parse_mode='Markdown')


async def next_page(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[2])

    is_sorted = "sorted" in callback.data
    is_month = "month" in callback.data
    month_number = 0

    if is_sorted:
        orders = await catamaran.sort_date_order()
    elif is_month:
        month_number = int(callback.data.split("_")[4])
        orders = await catamaran.sort_date_order()
        filtered_orders = []
        for order in orders:
            print(order[1])
            if int(order[1].split('.')[1]) == month_number:
                filtered_orders.append(order)
        print(filtered_orders)
    else:
        orders = await catamaran.get_orders()

    total_pages = (len(orders) + 4) // 5
    page += 1
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]

    if orders_page:
        orders_text, markup = await keyboard.generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted,
                                                                       is_month, month_number)
        await callback.bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                    text=orders_text, reply_markup=markup, parse_mode='Markdown')

def register_callback_query_view_next_page_catamarans(dp):
    dp.register_callback_query_handler(next_page, lambda c: c.data.startswith('next_page_'))

def register_callback_query_view_back_page_catamarans(dp):
    dp.register_callback_query_handler(prev_page, lambda c: c.data.startswith('prev_page_'))