from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from app.database.Models.catamaran import get_catamaran_quantity, get_catamaran_price
from app.database.Models.route import get_route_by_id
from app.database.Models.supboaed import get_supboard_quantity, get_supboard_price
from app.database.Models.transfer import get_transfer_quantity, get_transfer_price, get_transfer_route_id

main = InlineKeyboardMarkup(row_width=3)
main.add(InlineKeyboardButton(text="Добавить заказ", callback_data="add_order"),
         InlineKeyboardButton(text="Просмотр заказов", callback_data="search_order"),
         InlineKeyboardButton(text="Изменить заказ", callback_data="edit_order"),
         InlineKeyboardButton(text="Поменять статус", callback_data="status_order"))
main.add(InlineKeyboardButton(text='Excel таблица', callback_data='excel'))
main.add(InlineKeyboardButton(text='⚙ Настройки', callback_data='settings'))

sort_orders = InlineKeyboardMarkup(row_width=1)
sort_orders.add(
    InlineKeyboardButton(text="Все заказы", callback_data="view_catamarans"),
    InlineKeyboardButton(text="Сортировка по дате", callback_data="selection_of_sorts"),
    InlineKeyboardButton(text="Выбор заказав в определённом месяце", callback_data="sort_month_order"),
    InlineKeyboardButton(text="Поиск по ID", callback_data="search_id_order"),
    InlineKeyboardButton(text="Поиск по дате", callback_data="search_date_order"),
    InlineKeyboardButton(text="Свободных мест по дате", callback_data="search_free_order"),
    InlineKeyboardButton(text="🔙Назад", callback_data="close_callback")
)

admin_settings = InlineKeyboardMarkup(row_width=2)
admin_settings.add(
    InlineKeyboardButton("➕ Добавить", callback_data="add_admin"),
    InlineKeyboardButton("➖ Удалить", callback_data="remove_admin"),
    InlineKeyboardButton("🔙 Назад", callback_data="settings")
)

settings_buttons = InlineKeyboardMarkup(row_width=2)
settings_buttons.add(
    InlineKeyboardButton(text="🏄 Услуги SUP-бордов", callback_data="change_database_supboard_services"),
    InlineKeyboardButton(text="🚐 Услуги трансфера", callback_data="change_database_transfer_services"),
    InlineKeyboardButton(text="⛵ Услуги катамаранов", callback_data="change_database_catamaran_services"),
    InlineKeyboardButton(text="👤 Управление администраторами", callback_data="change_database_admin"),
    InlineKeyboardButton(text="🔙 Назад", callback_data="close_callback")
)

yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

selection_of_sorts = InlineKeyboardMarkup(row_width=1)
selection_of_sorts.add(
    InlineKeyboardButton(text="Всех заказов", callback_data="sort_date_order"),
    InlineKeyboardButton(text="Катамараны", callback_data="sort_date_catamaran_services"),
    InlineKeyboardButton(text="Трансферы", callback_data="sort_date_transfer_services"),
    InlineKeyboardButton(text="СапБорды", callback_data="sort_date_supboard_services"),
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

close_replay_callback = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
close_replay_callback.add(KeyboardButton(text='Отменить'),
                          KeyboardButton(text='Пропустить'))


async def generate_buttons_for_search(callback_data):
    back_to_search_order = InlineKeyboardMarkup(row_width=1)
    back_to_search_order.add(InlineKeyboardButton(text='Повторить поиск', callback_data=f'{callback_data}'))
    back_to_search_order.add(InlineKeyboardButton(text='🔙Назад', callback_data='search_order'))

    return back_to_search_order


async def generate_confirm_buttons(entity_type: str):
    confirm_delete = InlineKeyboardMarkup()
    confirm_delete.add(
        InlineKeyboardButton(text='✅ Да', callback_data=f'confirm_delete_yes_{entity_type}'),
        InlineKeyboardButton(text='❌ Нет', callback_data=f'confirm_delete_no_{entity_type}')
    )
    return confirm_delete


close4 = InlineKeyboardMarkup()
close4.add(InlineKeyboardButton(text='🔙Назад', callback_data='close_callback2'))


async def generate_orders_text_and_markup(
        orders_page, page, total_pages, is_sorted=False, is_month=False, month_number=0
):
    orders_text = ""
    for order in orders_page:
        route = get_route_by_id(order[5])

        single_order_text = await info_order_text(
            order_id=order[0],
            date_arrival=order[1],
            time_arrival=order[2],
            date_departure=order[3],
            time_departure=order[4],
            route_id=route,
            customer_name=order[6],
            phone_link=order[7],
            additional_wishes=order[9],
            status=order[8]
        )

        orders_text += single_order_text

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
    markup.add(InlineKeyboardButton("🔙 Назад", callback_data="search_order"))

    return orders_text, markup


async def info_order_text(
        order_id: int,
        date_arrival: str,
        time_arrival: str,
        date_departure: str,
        time_departure: str,
        route_id,
        customer_name: str,
        phone_link: str,
        additional_wishes: str = "",
        status: bool = False
):
    status_text = "✅ <b>Аванс:</b> Внесён!" if status else "❌ <b>Аванс:</b> Не внесён!"

    phone = phone_link.replace('https://wa.me/', '')

    wishes_clean = (additional_wishes or "").strip().lower()
    wishes_text = ""
    if wishes_clean not in ["", ".", " ", "0", "нету", "none"]:
        wishes_text = f"📗 <b>Дополнительные пожелания:</b> {additional_wishes}\n"

    # Получение количества услуг
    catamarans = (await get_catamaran_quantity(order_id) or [0])[0]
    transfers = (await get_transfer_quantity(order_id) or [0])[0]
    supboards = (await get_supboard_quantity(order_id) or [0])[0]

    # Получение цен
    catamarans_price = (await get_catamaran_price(order_id) or [0])[0]
    transfers_price = (await get_transfer_price(order_id) or [0])[0]
    supboards_price = (await get_supboard_price(order_id) or [0])[0]

    price = catamarans_price + transfers_price + supboards_price

    # Получение маршрута трансфера
    transfer_route_id = (await get_transfer_route_id(order_id) or ['Маршрута нету'])[0]
    try:
        route_transfer = await get_route_by_id(transfer_route_id)
    except:
        route_transfer = {'name': 'Маршрута нету'}

    # Формирование блока услуг
    services_parts = []
    if catamarans > 0:
        services_parts.append(f"🛶 <b>Катамаранов:</b> {catamarans}")
    if transfers > 0:
        services_parts.append(f"🚐 <b>Трансферов:</b> {transfers}")
    if supboards > 0:
        services_parts.append(f"🏄 <b>Сапбордов:</b> {supboards}")
    if price > 0:
        services_parts.append(f"💰 <b>Цена:</b> {price}₽")

    services_text = ""
    if services_parts:
        services_text = "\n" + "\n".join(services_parts) + "\n"

    # Собираем финальный текст
    return (
        f"📝 <b>Информация о заказе</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 <b>ID заказа:</b> {order_id}\n"
        f"⚡️ <b>Дата приезда:</b> {date_arrival}\n"
        f"⏰️ <b>Время приезда:</b> {time_arrival}\n"
        f"⚡️ <b>Дата выезда:</b> {date_departure}\n"
        f"⏰️ <b>Время выезда:</b> {time_departure}\n"
        f"🗺 <b>Маршрут:</b> {route_id['name']}\n"
        f"🗺 <b>Маршрут для трансфера:</b> {route_transfer['name']}\n"
        f"🤵 <b>ФИО:</b> {customer_name}\n"
        f"📞 <b>Телефон:</b> <a href='https://wa.me/{phone}'>+{phone}</a>\n"
        f"{wishes_text}"
        f"{services_text}"
        f"{status_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
    )


async def info_catamaran_text(
        order_id: int,
        price,
        quantity,
        catamaran_id
):
    return (
        f"📝 <b>Информация о катамаранах в заказе {order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 <b>ID заказа:</b> {catamaran_id}\n"
        f"🚤 <b>Количество катамаранов:</b> {quantity}\n"
        f"💸 <b>Цена:</b> {price}\n"
    )


async def info_supboard_text(
        order_id: int,
        price,
        quantity,
        supboard_id
):
    return (
        f"📝 <b>Информация о SUP-бордов в заказе {order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 <b>ID заказа:</b> {supboard_id}\n"
        f"🚤 <b>Количество SUP-бордов:</b> {quantity}\n"
        f"💸 <b>Цена:</b> {price}\n"
    )


async def info_transfer_text(
        order_id: int,
        price,
        quantity,
        vehicle_type,
        driver_included,
        route_id,
        transfer_id
):
    return (
        f"📝 <b>Информация о трансфере в заказе {order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 <b>ID трансфера:</b> {transfer_id}\n"
        f"🚗 <b>Тип транспорта:</b> {vehicle_type}\n"
        f"👥 <b>Количество пассажиров:</b> {quantity}\n"
        f"💸 <b>Цена:</b> {price}\n"
        f"🧭 <b>ID маршрута:</b> {route_id}\n"
        f"👨‍✈️ <b>Водитель включён:</b> {'Да' if driver_included else 'Нет'}\n"
    )


async def service_buttons(order_id: int):
    add_service = InlineKeyboardMarkup(row_width=3)
    add_service.add(InlineKeyboardButton(text="Трансфер", callback_data=f"transfer_buttons_{order_id}"),
                    InlineKeyboardButton(text="СапБорды", callback_data=f"supboard_buttons_{order_id}"),
                    InlineKeyboardButton(text="Катамараны", callback_data=f"catamaran_buttons_{order_id}"),
                    InlineKeyboardButton(text="Удалить заказ", callback_data=f"delete_order_{order_id}"),
                    InlineKeyboardButton(text="Изменить заказ", callback_data=f"change_order_{order_id}"))
    add_service.add(InlineKeyboardButton(text='🔙 Назад', callback_data='close'))

    return add_service


async def catamarans_buttons(order_id: int):
    catamarans = InlineKeyboardMarkup(row_width=3)
    catamarans.add(InlineKeyboardButton(text="Добавить", callback_data=f'add_catamaran_{order_id}'),
                   InlineKeyboardButton(text="Изменить", callback_data=f'change_catamaran_{order_id}'),
                   InlineKeyboardButton(text="Удалить", callback_data=f'delete_catamaran_{order_id}'))

    catamarans.add(InlineKeyboardButton(text='🔙 Назад', callback_data='close'))

    return catamarans


async def supboards_buttons(order_id: int):
    supboards = InlineKeyboardMarkup(row_width=3)
    supboards.add(InlineKeyboardButton(text="Добавить", callback_data=f'add_supboard_{order_id}'),
                  InlineKeyboardButton(text="Изменить", callback_data=f'change_supboard_{order_id}'),
                  InlineKeyboardButton(text="Удалить", callback_data=f'delete_supboard_{order_id}'))

    supboards.add(InlineKeyboardButton(text='🔙 Назад', callback_data='close'))

    return supboards


async def transfer_buttons(order_id: int):
    transfer = InlineKeyboardMarkup(row_width=3)
    transfer.add(InlineKeyboardButton(text="Добавить", callback_data=f'add_transfer_{order_id}'),
                 InlineKeyboardButton(text="Изменить", callback_data=f'change_transfer_{order_id}'),
                 InlineKeyboardButton(text="Удалить", callback_data=f'delete_transfer_{order_id}'))

    transfer.add(InlineKeyboardButton(text='🔙 Назад', callback_data='close'))

    return transfer
