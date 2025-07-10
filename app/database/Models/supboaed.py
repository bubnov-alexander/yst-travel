import sqlite3

async def get_supboard_quantity(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT supboards_count FROM supboard_services WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()

    return order

async def get_supboard_price(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT price FROM supboard_services WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()

    return order


def get_supboard_by_id(supboard_id: int):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM supboard_services WHERE id = ?", (supboard_id,))
    result = cursor.fetchone()

    database.close()
    return result


def delete_supboard_by_id(supboard_id: int):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("DELETE FROM supboard_services WHERE id = ?", (supboard_id,))
    database.commit()
    database.close()


async def get_supboard_by_order_id(order_id: int):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM supboard_services WHERE order_id = ?", (order_id,))
    result = cursor.fetchone()

    database.close()
    return result


async def add_supboard(order_id: int, quantity: int, price: float):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute(
        "INSERT INTO supboard_services (order_id, supboards_count, price) VALUES (?, ?, ?)",
        (order_id, quantity, price)
    )
    database.commit()

    cursor.execute("SELECT last_insert_rowid()")
    row_id = cursor.fetchone()[0]

    database.close()
    return row_id

def update_supboard(supboard_id: int, quantity: int, price: float):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute(
        "UPDATE supboard_services SET supboards_count = ?, price = ? WHERE id = ?",
        (quantity, price, supboard_id)
    )
    database.commit()

    cursor.execute("SELECT last_insert_rowid()")
    row_id = cursor.fetchone()[0]

    database.close()
    return row_id


