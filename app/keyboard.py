from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import requests
import json
import time
import datetime as dt
import os


main = InlineKeyboardMarkup(row_width=3)
main.add(InlineKeyboardButton(text = "Добавить заказ", callback_data = "add_order"),
        InlineKeyboardButton(text = "Просмотр заказов", callback_data = "view_catamarans"),
        InlineKeyboardButton(text = "Удалить заказ", callback_data = "delete_order"),
        InlineKeyboardButton(text = "Изменить заказ", callback_data = "edit_order"),
        InlineKeyboardButton(text = "Поиск заказов", callback_data = "search_order"),
        InlineKeyboardButton(text = "Поменять статус", callback_data = "status_order"))
main.add(InlineKeyboardButton(text = 'Excel таблица', callback_data = 'exsel'))

sort_orders = InlineKeyboardMarkup(row_width=1)
# sort_orders.add(InlineKeyboardButton(text = "По месяцам", callback_data = "sort_by_month"),
#         
#         InlineKeyboardButton(text = "По количеству катамаранов", callback_data = "sort_by_quantity"),
#         InlineKeyboardButton(text = "По цене", callback_data = "sort_by_price"),
#         InlineKeyboardButton(text = "По имени заказчика", callback_data = "sort_by_name"),
#         InlineKeyboardButton(text = "По номеру телефона", callback_data = "sort_by_phone"),
#         InlineKeyboardButton(text = "По ID заказа", callback_data = "sort_by_id"),)

sort_orders.add(InlineKeyboardButton(text = "Сортировка по дате", callback_data = "sort_date_order"),
        InlineKeyboardButton(text = "Выбор заказав в определённом месяце", callback_data = "sort_month_order"),
        InlineKeyboardButton(text = "Поиск по ID", callback_data = "search_id_order"),
        InlineKeyboardButton(text = "Поиск по дате", callback_data = "search_date_order"),
        InlineKeyboardButton(text = "Свободных мест по дате", callback_data = "search_free_order"),
        InlineKeyboardButton(text = "🔙Назад", callback_data = "close_callback"))

months = InlineKeyboardMarkup(row_width=3)
months.add(InlineKeyboardButton(text = "Май", callback_data = "sort_by_may"),
        InlineKeyboardButton(text = "Июнь", callback_data = "sort_by_june"),
        InlineKeyboardButton(text = "Июль", callback_data = "sort_by_july"),
        InlineKeyboardButton(text = "Август", callback_data = "sort_by_august"),
        InlineKeyboardButton(text = "Сентябрь", callback_data = "sort_by_september"),
        InlineKeyboardButton(text = "🔙Назад", callback_data = "search_order"))

close = InlineKeyboardMarkup()
close.add(InlineKeyboardButton(text = '🔙Назад', callback_data = 'close'))


close2 = InlineKeyboardMarkup()
close2.add(InlineKeyboardButton(text = '🔙Назад', callback_data = 'close_callback'))

close3 = ReplyKeyboardMarkup( resize_keyboard=True, one_time_keyboard=True)
close3.add(KeyboardButton(text='Отменить'),
        KeyboardButton(text='Пропустить'))

close4 = InlineKeyboardMarkup()
close4.add(InlineKeyboardButton(text = '🔙Назад', callback_data = 'close_callback2'))

async def generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted=False, is_month=False, month_number=0):
        orders_text = ""
        for order in orders_page:
                orders_text += "📝 **Информация о заказе**\n"
                orders_text += "━━━━━━━━━━━━━━━━━━━━\n\n"
                orders_text += f"📌**ID заказа:** {str(order[0])}\n"
                orders_text += f"⚡️**Дата приезда:** {str(order[1])}\n"
                orders_text += f"⚡️**Дата выезда:** {str(order[2])}\n"
                orders_text += f"⏰️**Время приезда:** {str(order[3])}\n"
                orders_text += f"🗺**Маршрут:** {str(order[4])}\n"
                orders_text += f"📈**Количество катамаранов:** {str(order[5])}\n"
                orders_text += f"🤵**Имя:** {str(order[6])}\n"
                orders_text += f"📞 **Номер телефона:** {str(order[7])}\n"
                orders_text += f"💰**Цена заказа:** {str(order[8])}\n"
                if order[9] == "" or order[9] == None or order[9] == " " or order[9] == '.': 
                        orders_text += "\n"
                else:
                        orders_text += f"📗 **Дополнительные пожелания:** {str(order[9])}\n"
                orders_text += "━━━━━━━━━━━━━━━━━━━━\n"
                if order[10] == True:
                        orders_text += "✅ **Статус:** Подтверждён!\n\n"
                else:
                        orders_text += "❌ **Статус:** Не подтверждён!\n\n"

        markup = InlineKeyboardMarkup(row_width=2)
        buttons = []
        if page > 1:
                back_button_data = f"prev_page_{page-1}" + ("_sorted" if is_sorted else "") + (f"_month_{month_number}" if is_month else "")
                buttons.append(InlineKeyboardButton("<< Назад", callback_data=back_button_data))
        if page < total_pages:
                next_button_data = f"next_page_{page}" + ("_sorted" if is_sorted else "") + (f"_month_{month_number}" if is_month else "")
                buttons.append(InlineKeyboardButton("Вперед >>", callback_data=next_button_data))
        markup.add(*buttons)
        markup.add(InlineKeyboardButton("Меню", callback_data="search_order"))

        return orders_text, markup

async def info_text(date_id, date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes, status):
        if status == True:
                last_status = "✅ Статус: Подтверждён!"
        else:
                last_status = "❌ Статус: Не подтверждён!"

        if additional_wishes == "" or additional_wishes == None or additional_wishes == " " or additional_wishes == '.':
                last_wishes = "\n"
        else:
                last_wishes = f"\n📗 Дополнительные пожелания: {additional_wishes}\n"

        return (f'📝 Информация о заказе\n'
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f'📌ID заказа: {date_id}\n'
                f'⚡️ Дата начала заказа: {date_start}\n'
                f'⚡️ Дата конца заказа: {date_end}\n'
                f'⏰️ Время приезда: {time_start}\n'
                f'🗺 Маршрут: {route}\n'
                f'📈 Количество катамаранов: {quantity}\n'
                f'🤵 Имя заказчика: {customer_name}\n'
                f'📞 Номер телефона: {phone_number}\n\n'
                
                f'💰 Цена заказа: {price}р\n\n'

                f'{last_wishes}\n'
                f'━━━━━━━━━━━━━━━━━━━━\n'
                f'{last_status}\n\n')