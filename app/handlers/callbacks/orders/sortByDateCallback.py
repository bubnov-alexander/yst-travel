from aiogram import types

from app import keyboard
from app.database.Models.order import get_orders, sort_date_orders


async def sort_date_catamaran(callback: types.CallbackQuery):
    page = 1
    orders = await sort_date_orders()
    total_pages = (len(orders) + 4) // 5
    start_index = (page - 1) * 5
    end_index = start_index + 5
    orders_page = orders[start_index:end_index]

    orders_text, markup = await keyboard.generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted=True)

    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=orders_text,
        reply_markup=markup,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


async def sort_by_month(callback: types.CallbackQuery):
    orders = await get_orders()

    month_name = callback.data.split('_')[2]
    month_number = None

    if month_name == 'may':
        month_number = 5
    elif month_name == 'june':
        month_number = 6
    elif month_name == 'july':
        month_number = 7
    elif month_name == 'august':
        month_number = 8
    elif month_name == 'september':
        month_number = 9

    if month_number is not None:
        filtered_orders = []

        for order in orders:
            date_arrival = order[1]
            month = int(date_arrival.split('.')[1])

            if month == month_number:
                filtered_orders.append(order)

        orders = filtered_orders

        if not orders:
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=f'В {month_name} нет заказов',
                reply_markup=keyboard.months
            )
        else:
            page = 1
            orders = await sort_date_orders()
            orders = [order for order in orders if int(order[1].split('.')[1]) == month_number]
            total_pages = (len(orders) + 4) // 5
            start_index = (page - 1) * 5
            end_index = start_index + 5
            orders_page = orders[start_index:end_index]

            orders_text, markup = await keyboard.generate_orders_text_and_markup(orders_page, page, total_pages,
                                                                                 is_sorted=False, is_month=True,
                                                                                 month_number=month_number)
            await callback.bot.edit_message_text(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                text=orders_text,
                reply_markup=markup,
                parse_mode='HTML',
                disable_web_page_preview=True
            )


def register_callback_query_sort_by_month_catamaran(dp):
    dp.register_callback_query_handler(sort_by_month, lambda c: c.data.startswith('sort_by_'))


def register_callback_query_sort_by_date_catamaran(dp):
    dp.register_callback_query_handler(sort_date_catamaran, lambda c: c.data == 'sort_date_order')
