import sqlite3


async def add_transfer(order_id, vehicle_type, route_id, persons_count, driver_included, price):
    connection = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = connection.cursor()

    cursor.execute("""
                   INSERT INTO transfer_services (order_id,
                                                  vehicle_type,
                                                  route_id,
                                                  persons_count,
                                                  driver_included,
                                                  price)
                   VALUES (?, ?, ?, ?, ?, ?)
                   """, (order_id, vehicle_type, route_id, persons_count, driver_included, price))

    connection.commit()
    return cursor.lastrowid


async def update_transfer(transfer_id, order_id, vehicle_type, route_id, persons_count, driver_included, price):
    connection = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = connection.cursor()

    cursor.execute("""
                   UPDATE transfer_services
                   SET order_id        = ?,
                       vehicle_type    = ?,
                       route_id        = ?,
                       persons_count   = ?,
                       driver_included = ?,
                       price           = ?
                   WHERE id = ?
                   """, (order_id, vehicle_type, route_id, persons_count, driver_included, price, transfer_id))

    connection.commit()
    connection.close()

    return True

async def delete_transfer_by_id(transfer_id: int):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("DELETE FROM transfer_services WHERE id = ?", (transfer_id,))
    database.commit()
    database.close()


async def get_transfer_quantity(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT persons_count FROM transfer_services WHERE order_id = ?", (order_id,))
    catamaran_row = cursor.fetchone()

    return catamaran_row


async def get_transfer_by_order_id(order_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM transfer_services WHERE order_id = ?", (order_id,))
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
