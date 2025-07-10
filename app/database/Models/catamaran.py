import sqlite3, datetime
from app.utils.logger import logger


async def add_catamaran(order_id, quantity, price):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute(
        """
        INSERT INTO catamaran_services (order_id, quantity, price)
        VALUES (?, ?, ?)
        """, (
            order_id, quantity, price
        )
    )

    database.commit()
    catamaran_id = cursor.lastrowid
    logger.info(f"Катамаран создан: {catamaran_id}")
    return catamaran_id


async def update_catamaran(catamaran_id, quantity, price):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute(
        """
        UPDATE catamaran_services 
        SET quantity = ?, price = ?
        WHERE id = ?
        """, (
            quantity, price, catamaran_id
        )
    )

    database.commit()
    database.close()
    logger.info(f"Катамаран обновлен: {catamaran_id}")
    return catamaran_id


async def get_orders():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran_orders")
    orders = cursor.fetchall()

    return orders


async def delete_catamaran(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("DELETE FROM catamaran_services WHERE id = ?", (order_id,))
    database.commit()
    logger.info("Заказ успешно удален")


async def get_catamaran_quantity(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT quantity FROM catamaran_services WHERE order_id = ?", (order_id,))
    catamaran_row = cursor.fetchone()

    return catamaran_row

async def get_catamaran_price(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT price FROM catamaran_services WHERE order_id = ?", (order_id,))
    catamaran_row = cursor.fetchone()

    return catamaran_row


async def get_catamaran(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran_services WHERE order_id = ?", (order_id,))
    catamaran_row = cursor.fetchone()

    return catamaran_row


async def get_catamaran_by_order_id(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran_services WHERE order_id = ?", (order_id,))
    catamaran_row = cursor.fetchone()

    return catamaran_row


async def sort_date_catamaran():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    # Извлекаем данные без сортировки
    cursor.execute("SELECT * FROM catamaran_orders")
    orders = cursor.fetchall()

    orders_sorted = sorted(orders, key=lambda x: datetime.datetime.strptime(str(x[1]), '%d.%m.%Y')
    if isinstance(x[1], str) else datetime.datetime.now())

    return orders_sorted


async def get_catamaran_by_date(date):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran_orders WHERE date_arrival = ?", (date,))
    orders = cursor.fetchall()

    return orders


async def status_catamaran(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("UPDATE catamaran_orders SET prepayment_status = NOT prepayment_status WHERE id = ?", (order_id,))
    database.commit()

    cursor.execute("SELECT prepayment_status FROM catamaran_orders WHERE id = ?", (order_id,))
    status = cursor.fetchone()

    return status[0]
