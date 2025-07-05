import sqlite3

async def get_supboard_by_id(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT supboards_count FROM supboard_services WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()

    return order