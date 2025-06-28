import sqlite3, datetime

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

def add_booking(date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes, status=0):
    # Преобразуем даты и время в объекты datetime
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()
    cursor.execute("INSERT INTO catamaran (date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (date_start, date_end, time_start, route, quantity, customer_name, phone_number, price, additional_wishes, status))
    database.commit()
    
    order_id = cursor.lastrowid
    return order_id

async def check_availability(date_start, date_end, requested_quantity, order_id=None):
    # Подключение к базе данных
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()
    
    # Извлечение всех бронирований
    cursor.execute("SELECT date_start, date_end, quantity FROM catamaran")
    bookings = cursor.fetchall()
    total_catamarans = 16
    
    requested_start = datetime.datetime.strptime(date_start, '%d.%m.%Y')
    requested_end = datetime.datetime.strptime(date_end, '%d.%m.%Y') + datetime.timedelta(days=1)

    if order_id:
        cursor.execute("SELECT date_start, date_end, quantity FROM catamaran WHERE id = ?", (order_id,))
        order = cursor.fetchone()
        if order:
            bookings.remove(order)
    
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
    
    return can_book, remaining_catamarans

async def get_available_catamarans(date):
    # Подключение к базе данных
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()
    
    # Извлечение всех бронирований
    cursor.execute("SELECT date_start, date_end, quantity FROM catamaran")
    bookings = cursor.fetchall()
    total_catamarans = 16
    
    requested_date = datetime.datetime.strptime(date, '%d.%m.%Y')
    
    availability = total_catamarans
    for booking in bookings:
        booking_start = datetime.datetime.strptime(booking[0], '%d.%m.%Y')
        booking_end = datetime.datetime.strptime(booking[1], '%d.%m.%Y') + datetime.timedelta(days=1)
        
        if booking_start <= requested_date < booking_end:
            availability -= booking[2]
    
    return availability

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

async def status_order(order_id):
    database = sqlite3.connect('data/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("UPDATE catamaran SET status = NOT status WHERE id = ?", (order_id,))
    database.commit()

    cursor.execute("SELECT status FROM catamaran WHERE id = ?", (order_id,))
    status = cursor.fetchone()

    return status[0]