import sqlite3, datetime, pytz

# tz = pytz.timezone('Asia/Yekaterinburg')
# TIME = (datetime.datetime.now(tz)).strftime('%H:%M:%S')
# DATE = (datetime.datetime.now(tz)).strftime('%d.%m')

# ============== Create tables ==============

async def db_start():
    database = sqlite3.connect(
        'data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()
    print("Подключен к SQLite3")

    cursor.execute("""CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        user_id INTEGER UNIQUE NOT NULL,
        user_name TEXT NOT NULL
        )""")
    database.commit()

    cursor.execute("""CREATE TABLE IF NOT EXISTS catamaran(
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        date_start DATETIME NOT NULL,
        date_end DATETIME NOT NULL,
        time_start TEXT NOT NULL,
        route TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        price TEXT NOT NULL,
        additional_wishes TEXT
        )""")
    database.commit()

    print("Таблицы успешно созданы")

def get_user_id(user_id):
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT id FROM admin WHERE user_name = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        return None
    
async def add_order(date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes):
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("INSERT INTO catamaran (date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes)),
    database.commit()

    order_id = cursor.lastrowid
    print("Заказ успешно добавлен")
    return order_id

async def get_orders():
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran")
    orders = cursor.fetchall()

    return orders

async def delete_order(order_id):
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("DELETE FROM catamaran WHERE id = ?", (order_id,))
    database.commit()
    print("Заказ успешно удален")

async def edit_order(date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes, order_id):
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("UPDATE catamaran SET date_start = ?, date_end = ?, time_start = ?, route = ?, quantity = ?, customer_name = ?, phone_number = ?, price = ?, additional_wishes = ? WHERE id = ?", (date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes, order_id))
    database.commit()
    print("Заказ успешно изменен")

async def get_order_by_id(order_id):
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran WHERE id = ?", (order_id,))
    order = cursor.fetchone()

    return order

def add_booking(date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes):
    # Преобразуем даты и время в объекты datetime
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()
    cursor.execute("INSERT INTO catamaran (date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes))
    database.commit()
    
    order_id = cursor.lastrowid
    return order_id

async def check_availability(date_start, date_end, requested_quantity, order_id=None):
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT date_start, date_end, quantity FROM catamaran")
    bookings = cursor.fetchall()
    total_catamarans = 12
    
    requested_start = datetime.datetime.strptime(date_start, '%d.%m.%Y')
    requested_end = datetime.datetime.strptime(date_end, '%d.%m.%Y')
    
    if order_id:
        cursor.execute("SELECT date_start, date_end, quantity FROM catamaran WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if order:
            bookings.remove(order)

    for booking in bookings:
        booking_start = datetime.datetime.strptime(booking[0], '%d.%m.%Y')
        booking_end = datetime.datetime.strptime(booking[1], '%d.%m.%Y')
        
        # Измененная проверка на пересечение дат
        if not (requested_end <= booking_start or requested_start >= booking_end):
            total_catamarans -= booking[2]
    
    return (total_catamarans >= requested_quantity), total_catamarans

async def sort_date_order():
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    # Извлекаем данные без сортировки
    cursor.execute("SELECT * FROM catamaran")
    orders = cursor.fetchall()

    # Преобразуем строки дат в объекты datetime и сортируем
    orders_sorted = sorted(orders, key=lambda x: datetime.datetime.strptime(str(x[1]), '%d.%m.%Y') if isinstance(x[1], str) else datetime.datetime.now())

    return orders_sorted

async def get_order_by_date(date):
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT * FROM catamaran WHERE date_start = ?", (date,))
    orders = cursor.fetchall()

    return orders