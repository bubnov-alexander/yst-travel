import sqlite3, datetime
from app.utils.logger import logger


async def add_order(
        date_arrival, date_departure, time_arrival, time_departure,
        route_id, quantity, customer_name, phone, price,
        additional_wishes, prepayment_status
):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("""
                   INSERT INTO catamaran_orders (date_arrival, date_departure, time_arrival, time_departure,
                                                 route_id, quantity, customer_name, phone, price,
                                                 additional_wishes, prepayment_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   """, (
                       date_arrival, date_departure, time_arrival, time_departure,
                       route_id, quantity, customer_name, phone, price,
                       additional_wishes, prepayment_status
                   ))

    database.commit()
    order_id = cursor.lastrowid
    logger.info(f"Заказ создан: {order_id}")
    return order_id


async def get_orders():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran_orders")
    orders = cursor.fetchall()

    return orders


async def delete_order(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("DELETE FROM catamaran_orders WHERE id = ?", (order_id,))
    database.commit()
    logger.info("Заказ успешно удален")


async def edit_order(
        date_arrival, date_departure, time_arrival, time_departure,
        route_id, quantity, customer_name, phone, price,
        additional_wishes, prepayment_status, order_id
):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("""
                   UPDATE catamaran_orders
                   SET date_arrival      = ?,
                       date_departure    = ?,
                       time_arrival      = ?,
                       time_departure    = ?,
                       route_id          = ?,
                       quantity          = ?,
                       customer_name     = ?,
                       phone             = ?,
                       price             = ?,
                       additional_wishes = ?,
                       prepayment_status = ?
                   WHERE id = ?
                   """, (
                       date_arrival, date_departure, time_arrival, time_departure,
                       route_id, quantity, customer_name, phone, price,
                       additional_wishes, prepayment_status, order_id
                   ))

    database.commit()
    database.close()

    logger.info(f"📝 Заказ успешно изменён (ID: {order_id})")


async def get_order_by_id(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran_orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()

    return order


async def check_availability(date_start, date_end, requested_quantity, order_id=None):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT date_arrival, date_departure, quantity, id FROM catamaran_orders")
    bookings = cursor.fetchall()

    total_catamarans = 16

    requested_start = datetime.datetime.strptime(date_start, '%d.%m.%Y')
    requested_end = datetime.datetime.strptime(date_end, '%d.%m.%Y') + datetime.timedelta(days=1)

    # Исключаем текущий заказ при редактировании
    if order_id:
        cursor.execute("SELECT date_arrival, date_departure, quantity, id FROM catamaran_orders WHERE id = ?",
                       (order_id,))
        order = cursor.fetchone()
        if order:
            try:
                bookings.remove(order)
            except ValueError:
                logger.warning(f"Order with id={order_id} not found in bookings list.")

    availability = {}

    for single_date in (requested_start + datetime.timedelta(n) for n in range((requested_end - requested_start).days)):
        availability[single_date] = total_catamarans

    for booking in bookings:
        booking_start = datetime.datetime.strptime(booking[0], '%d.%m.%Y')
        booking_end = datetime.datetime.strptime(booking[1], '%d.%m.%Y') + datetime.timedelta(days=1)

        for single_date in (booking_start + datetime.timedelta(n) for n in range((booking_end - booking_start).days)):
            if single_date in availability:
                availability[single_date] -= booking[2]

    can_book = all(availability[date] >= requested_quantity for date in availability)
    remaining_catamarans = min(availability[date] for date in availability)

    database.close()

    return can_book, remaining_catamarans


async def get_available_catamarans(date):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT date_arrival, date_departure, quantity FROM catamaran_orders")
    bookings = cursor.fetchall()

    total_catamarans = 16
    requested_date = datetime.datetime.strptime(date, '%d.%m.%Y')

    availability = total_catamarans

    for booking in bookings:
        booking_start = datetime.datetime.strptime(booking[0], '%d.%m.%Y')
        booking_end = datetime.datetime.strptime(booking[1], '%d.%m.%Y') + datetime.timedelta(days=1)

        if booking_start <= requested_date < booking_end:
            availability -= booking[2]

    database.close()

    return availability


async def sort_date_order():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    # Извлекаем данные без сортировки
    cursor.execute("SELECT * FROM catamaran_orders")
    orders = cursor.fetchall()

    orders_sorted = sorted(orders, key=lambda x: datetime.datetime.strptime(str(x[1]), '%d.%m.%Y')
    if isinstance(x[1],str) else datetime.datetime.now())

    return orders_sorted


async def get_order_by_date(date):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran_orders WHERE date_arrival = ?", (date,))
    orders = cursor.fetchall()

    return orders


async def status_order(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("UPDATE catamaran_orders SET prepayment_status = NOT prepayment_status WHERE id = ?", (order_id,))
    database.commit()

    cursor.execute("SELECT prepayment_status FROM catamaran_orders WHERE id = ?", (order_id,))
    status = cursor.fetchone()

    return status[0]
