from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from app.database.Models.route import get_route_by_id

main = InlineKeyboardMarkup(row_width=3)
main.add(InlineKeyboardButton(text="Добавить заказ", callback_data="add_order"),
         InlineKeyboardButton(text="Просмотр заказов", callback_data="search_order"),
         InlineKeyboardButton(text="Удалить заказ", callback_data="delete_order"),
         InlineKeyboardButton(text="Изменить заказ", callback_data="edit_order"),
         InlineKeyboardButton(text="Поменять статус", callback_data="status_order"))
main.add(InlineKeyboardButton(text='Excel таблица', callback_data='excel'))

back_to_search_order = InlineKeyboardMarkup(row_width=1)
back_to_search_order.add(InlineKeyboardButton(text='🔙Назад', callback_data='search_order'))

sort_orders = InlineKeyboardMarkup(row_width=1)
sort_orders.add(
    InlineKeyboardButton(text="Все заказы", callback_data="view_catamarans"),
        InlineKeyboardButton(text="Сортировка по дате", callback_data="sort_date_order"),
        InlineKeyboardButton(text="Выбор заказав в определённом месяце", callback_data="sort_month_order"),
        InlineKeyboardButton(text="Поиск по ID", callback_data="search_id_order"),
        InlineKeyboardButton(text="Поиск по дате", callback_data="search_date_order"),
        InlineKeyboardButton(text="Свободных мест по дате", callback_data="search_free_order"),
        InlineKeyboardButton(text="🔙Назад", callback_data="close_callback")
    )

months = InlineKeyboardMarkup(row_width=3)
months.add(InlineKeyboardButton(text="Май", callback_data="sort_by_may"),
           InlineKeyboardButton(text="Июнь", callback_data="sort_by_june"),
           InlineKeyboardButton(text="Июль", callback_data="sort_by_july"),
           InlineKeyboardButton(text="Август", callback_data="sort_by_august"),
           InlineKeyboardButton(text="Сентябрь", callback_data="sort_by_september"),
           InlineKeyboardButton(text="🔙Назад", callback_data="search_order"))

close = InlineKeyboardMarkup()
close.add(InlineKeyboardButton(text='🔙Назад', callback_data='close'))

close2 = InlineKeyboardMarkup()
close2.add(InlineKeyboardButton(text='🔙Назад', callback_data='close_callback'))

close3 = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
close3.add(KeyboardButton(text='Отменить'),
           KeyboardButton(text='Пропустить'))

close4 = InlineKeyboardMarkup()
close4.add(InlineKeyboardButton(text='🔙Назад', callback_data='close_callback2'))


async def generate_orders_text_and_markup(orders_page, page, total_pages, is_sorted=False, is_month=False,
                                          month_number=0):
    orders_text = ""
    for order in orders_page:
        route = get_route_by_id(order[5])
        phone = order[8].replace('https://wa.me/', '')

        orders_text += "📝 <b>Информация о заказе</b>\n"
        orders_text += "━━━━━━━━━━━━━━━━━━━━\n\n"
        orders_text += f"📌 <b>ID заказа:</b> {order[0]}\n"
        orders_text += f"⚡️ <b>Дата приезда:</b> {order[1]}\n"
        orders_text += f"⏰️ <b>Время приезда:</b> {order[2]}\n"
        orders_text += f"⚡️ <b>Дата выезда:</b> {order[3]}\n"
        orders_text += f"⏰️ <b>Время выезда:</b> {order[4]}\n"
        orders_text += f"🗺 <b>Маршрут:</b> {route['name']}\n"
        orders_text += f"📈 <b>Количество катамаранов:</b> {order[6]}\n"
        orders_text += f"🤵 <b>ФИО:</b> {order[7]}\n"
        orders_text += f"📞 <b>Телефон:</b><a href='{order[8]}'> +{phone}</a>\n"
        orders_text += f"💰 <b>Цена заказа:</b> {order[9]} ₽\n"

        if order[10] == "" or order[10] is None or order[10] == " " or order[10] == '.':
            orders_text += "\n"
        else:
            orders_text += f"📗 <b>Дополнительные пожелания:</b> {order[10]}\n"
        if order[11]:
            orders_text += "✅ <b>Статус:</b> Подтверждён!\n\n"
        else:
            orders_text += "❌ <b>Статус:</b> Не подтверждён!\n\n"
        orders_text += "━━━━━━━━━━━━━━━━━━━━\n"

    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    if page > 1:
        back_button_data = f"prev_page_{page - 1}" + ("_sorted" if is_sorted else "") + (
            f"_month_{month_number}" if is_month else "")
        buttons.append(InlineKeyboardButton("<< Назад", callback_data=back_button_data))
    if page < total_pages:
        next_button_data = f"next_page_{page}" + ("_sorted" if is_sorted else "") + (
            f"_month_{month_number}" if is_month else "")
        buttons.append(InlineKeyboardButton("Вперед >>", callback_data=next_button_data))
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="sort_month_order"))

    return orders_text, markup


async def info_text(
        order_id: int,
        date_arrival: str,
        time_arrival: str,
        date_departure: str,
        time_departure: str,
        route_id: str,
        quantity: int,
        customer_name: str,
        phone_link: str,
        price: float,
        additional_wishes: str = "",
        status: bool = False
):
    # Форматируем статус
    status_text = "✅ <b>Статус:</b> Подтверждён!" if status else "❌ <b>Статус:</b> Не подтверждён!"

    # Форматируем дополнительные пожелания
    wishes_text = ""
    if additional_wishes and additional_wishes.strip() not in ["", ".", " "]:
        wishes_text = f"📗 <b>Дополнительные пожелания:</b> {additional_wishes}\n"

    # Форматируем телефон с кликабельной ссылкой
    phone = phone_link.replace('https://wa.me/', '')
    route = get_route_by_id(route_id)

    # Собираем полный текст
    return (
        f"📝 <b>Информация о заказе</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 <b>ID заказа:</b> {order_id}\n"
        f"⚡️ <b>Дата приезда:</b> {date_arrival}\n"
        f"⏰️ <b>Время приезда:</b> {time_arrival}\n"
        f"⚡️ <b>Дата выезда:</b> {date_departure}\n"
        f"⏰️ <b>Время выезда:</b> {time_departure}\n"
        f"🗺 <b>Маршрут:</b> {route}\n"
        f"📈 <b>Количество катамаранов:</b> {quantity}\n"
        f"🤵 <b>ФИО:</b> {customer_name}\n"
        f"📞 <b>Телефон:</b><a href='{phone}'> +{phone}</a>\n"
        f"💰 <b>Цена заказа:</b> {price} ₽\n\n"
        f"{wishes_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{status_text}\n\n"
    )
