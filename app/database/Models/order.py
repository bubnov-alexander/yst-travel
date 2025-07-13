import datetime
import logging
import sqlite3

from app.database.Models.catamaran import get_catamaran_quantity
from app.database.Models.settings import get_service_counts
from app.database.Models.supboaed import get_supboard_quantity

logger = logging.getLogger(__name__)


async def check_availability(date_start, date_end, requested, order_id=None):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    requested_start = datetime.datetime.strptime(date_start, '%d.%m.%Y')
    requested_end = datetime.datetime.strptime(date_end, '%d.%m.%Y')

    days_count = (requested_end - requested_start).days + 1

    availability = {
        'catamarans': {},
        'supboards': {},
        'transfers': {}
    }

    counts = get_service_counts()

    TOTAL_CATAMARANS = int(counts["catamaran"])
    TOTAL_SUPBOARDS = int(counts["supboard"])
    TOTAL_TRANSFER_VEHICLES = int(counts["transfer"])

    for single_date in (requested_start + datetime.timedelta(n) for n in range(days_count)):
        availability['catamarans'][single_date] = TOTAL_CATAMARANS
        availability['supboards'][single_date] = TOTAL_SUPBOARDS
        availability['transfers'][single_date] = TOTAL_TRANSFER_VEHICLES

    all_orders = get_all_order()

    for order in all_orders:
        o_id, arrival, departure = order
        if order_id and o_id == order_id:
            continue

        order_start = datetime.datetime.strptime(arrival, '%d.%m.%Y')
        order_end = datetime.datetime.strptime(departure, '%d.%m.%Y')

        order_days_count = (order_end - order_start).days + 1

        catamaran_row = await get_catamaran_quantity(o_id)
        catamaran_q = catamaran_row[0] if catamaran_row else 0

        supboard_row = await get_supboard_quantity(o_id)
        supboard_q = supboard_row[0] if supboard_row else 0

        cursor.execute("SELECT COUNT(*) FROM transfer_services WHERE order_id = ?", (o_id,))
        transfer_count = cursor.fetchone()[0]

        order_days_count = (order_end - order_start).days + 1

        for single_date in (order_start + datetime.timedelta(n) for n in range(order_days_count)):
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
        'catamarans': min(availability['catamarans'].values()) if availability['catamarans'] else 0,
        'supboards': min(availability['supboards'].values()) if availability['supboards'] else 0,
        'transfers': min(availability['transfers'].values()) if availability['transfers'] else 0,
    }

    if all(value == 0 for value in remaining.values()):
        database.close()
        return False, remaining

    database.close()
    return can_book, remaining


def get_all_order():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT id, date_arrival, date_departure FROM orders")
    result = cursor.fetchall()
    database.close()
    return result


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
                       INSERT INTO orders (date_arrival, date_departure,
                                           time_arrival, time_departure,
                                           route_id, customer_name, phone,
                                           prepayment_status, additional_wishes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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


async def edit_order(
        date_arrival, date_departure, time_arrival, time_departure,
        route_id, customer_name, phone,
        additional_wishes, prepayment_status, order_id
):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("""
                   UPDATE orders
                   SET date_arrival      = ?,
                       date_departure    = ?,
                       time_arrival      = ?,
                       time_departure    = ?,
                       route_id          = ?,
                       customer_name     = ?,
                       phone             = ?,
                       additional_wishes = ?,
                       prepayment_status = ?
                   WHERE id = ?
                   """, (
                       date_arrival, date_departure, time_arrival, time_departure,
                       route_id, customer_name, phone,
                       additional_wishes, prepayment_status, order_id
                   ))

    database.commit()
    database.close()

    logger.info(f"📝 Заказ успешно изменён (ID: {order_id})")


async def get_order_by_id(order_id: int):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    database.close()

    return order


async def delete_order_by_id(transfer_id: int):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("DELETE FROM orders WHERE id = ?", (transfer_id,))
    database.commit()
    database.close()


def change_status_order(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("UPDATE orders SET prepayment_status = NOT prepayment_status WHERE id = ?", (order_id,))
    database.commit()

    cursor.execute("SELECT prepayment_status FROM orders WHERE id = ?", (order_id,))
    status = cursor.fetchone()

    return status[0]


async def get_orders():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    return orders


async def get_order_by_date(date):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM orders WHERE date_arrival = ?", (date,))
    orders = cursor.fetchall()

    return orders


async def sort_date_orders():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    orders_sorted = sorted(orders, key=lambda x: datetime.datetime.strptime(str(x[1]), '%d.%m.%Y')
    if isinstance(x[1], str) else datetime.datetime.now())

    return orders_sorted


async def get_orders_with_catamarans_sorted(service):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()

    orders_with_catamarans = []

    for order in orders:
        order_id = order[0]
        date_start = order[1]

        cursor.execute(f"SELECT * FROM {service} WHERE order_id = ?", (order_id,))
        catamaran_row = cursor.fetchone()

        if catamaran_row and catamaran_row[0] > 0:
            orders_with_catamarans.append(order)

    # Сортируем по дате начала
    orders_sorted = sorted(
        orders_with_catamarans,
        key=lambda x: datetime.datetime.strptime(x[1], '%d.%m.%Y') if isinstance(x[1], str) else datetime.datetime.min
    )

    database.close()
    return orders_sorted
