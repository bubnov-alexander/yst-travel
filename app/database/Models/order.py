import sqlite3
import datetime
import logging

from app.database.Models.catamaran import get_order_by_id
from app.database.Models.supboaed import get_supboard_by_id

logger = logging.getLogger(__name__)

TOTAL_CATAMARANS = 16
TOTAL_SUPBOARDS = 20
TOTAL_TRANSFER_VEHICLES = 5


async def check_availability(date_start, date_end, requested, order_id=None):
    """
    Проверяет доступность ресурсов:
    :param date_start: дата начала в формате 'дд.мм.гггг'
    :param date_end: дата окончания в формате 'дд.мм.гггг'
    :param requested: dict с ключами catamarans, supboards, transfers
    :param order_id: если редактируется заказ — исключить его из проверок
    :return: (можно_забронировать, минимальное_оставшееся_значение_по_каждому_ресурсу)
    """
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    requested_start = datetime.datetime.strptime(date_start, '%d.%m.%Y')
    requested_end = datetime.datetime.strptime(date_end, '%d.%m.%Y') + datetime.timedelta(days=1)

    availability = {
        'catamarans': {},
        'supboards': {},
        'transfers': {}
    }

    for single_date in (requested_start + datetime.timedelta(n) for n in range((requested_end - requested_start).days)):
        availability['catamarans'][single_date] = TOTAL_CATAMARANS
        availability['supboards'][single_date] = TOTAL_SUPBOARDS
        availability['transfers'][single_date] = TOTAL_TRANSFER_VEHICLES

    # Получаем все заказы
    all_orders = get_all_order()

    for order in all_orders:
        o_id, arrival, departure = order
        if order_id and o_id == order_id:
            continue

        order_start = datetime.datetime.strptime(arrival, '%Y-%m-%d')
        order_end = datetime.datetime.strptime(departure, '%Y-%m-%d') + datetime.timedelta(days=1)

        catamaran_row = get_order_by_id(o_id)
        catamaran_q = catamaran_row[0] if catamaran_row else 0

        supboard_row = get_supboard_by_id(o_id)
        supboard_q = supboard_row[0] if supboard_row else 0

        cursor.execute("SELECT COUNT(*) FROM transfer_services WHERE order_id = ?", (o_id,))
        transfer_count = cursor.fetchone()[0]

        for single_date in (order_start + datetime.timedelta(n) for n in range((order_end - order_start).days)):
            if single_date in availability['catamarans']:
                availability['catamarans'][single_date] -= catamaran_q
                availability['supboards'][single_date] -= supboard_q
                availability['transfers'][single_date] -= transfer_count

    can_book = all(
        availability['catamarans'][d] >= requested.get('catamarans', 0) and
        availability['supboards'][d] >= requested.get('supboards', 0) and
        availability['transfers'][d] >= requested.get('transfers', 0)
        for d in availability['catamarans']
    )

    remaining = {
        'catamarans': min(availability['catamarans'].values()),
        'supboards': min(availability['supboards'].values()),
        'transfers': min(availability['transfers'].values())
    }

    database.close()
    return can_book, remaining


def get_all_order():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT id, date_arrival, date_departure FROM orders")
    result = cursor.fetchall()
    database.close()
    return result

import sqlite3


async def add_new_order(
    date_arrival,
    date_departure,
    time_arrival,
    time_departure,
    route_id,
    customer_name,
    phone,
    additional_wishes,
    prepayment_status
):
    try:
        conn = sqlite3.connect('app/storage/database.db')
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO orders (
                date_arrival, date_departure,
                time_arrival, time_departure,
                route_id, customer_name, phone,
                prepayment_status, additional_wishes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_arrival, date_departure,
            time_arrival, time_departure,
            route_id, customer_name, phone,
            prepayment_status, additional_wishes
        ))

        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return order_id

    except Exception as e:
        logger.error("[add_order] Ошибка при добавлении заказа: ", e)
        return False