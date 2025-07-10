import sqlite3, datetime
from app.utils.logger import logger

async def get_transfer_quantity(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT persons_count FROM transfer_services WHERE order_id = ?", (order_id,))
    catamaran_row = cursor.fetchone()

    return catamaran_row

async def get_transfer_price(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT price FROM transfer_services WHERE order_id = ?", (order_id,))
    catamaran_row = cursor.fetchone()

    return catamaran_row

async def get_transfer_route_id(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT route_id FROM transfer_services WHERE order_id = ?", (order_id,))
    catamaran_row = cursor.fetchone()

    return catamaran_row