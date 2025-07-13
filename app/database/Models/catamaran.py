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
