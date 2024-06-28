import sqlite3
from datetime import datetime

# Создание соединения с базой данных
conn = sqlite3.connect('catamaran_booking.db')
cursor = conn.cursor()

# Создание таблицы для бронирований, если она еще не существует
cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_start TEXT NOT NULL,
    date_end TEXT NOT NULL,
    quantity INTEGER NOT NULL
)
""")
conn.commit()

def add_booking(date_start, date_end, quantity):
    check = check_availability(date_start, date_end, quantity)
    if check:
        cursor.execute("INSERT INTO bookings (date_start, date_end, quantity) VALUES (?, ?, ?)", (date_start, date_end, quantity))
        conn.commit()
        return True
    else:
        return False

def check_availability(date_start, date_end, requested_quantity):
    cursor.execute("SELECT date_start, date_end, quantity FROM bookings")
    bookings = cursor.fetchall()
    total_catamarans = 12
    
    requested_start = datetime.strptime(date_start, '%d.%m.%Y')
    requested_end = datetime.strptime(date_end, '%d.%m.%Y')
    
    for booking in bookings:
        booking_start = datetime.strptime(booking[0], '%d.%m.%Y')
        booking_end = datetime.strptime(booking[1], '%d.%m.%Y')
        
        # Проверка на пересечение дат, включая случаи, когда новое бронирование начинается в день окончания другого
        if not (requested_end < booking_start or requested_start > booking_end):
            total_catamarans -= booking[2]
            
    return (total_catamarans >= requested_quantity, total_catamarans)

def get_overbooked_dates(threshold=11):
    cursor.execute("SELECT date_start, date_end, quantity FROM bookings")
    bookings = cursor.fetchall()
    overbooked_dates = []
    
    for booking in bookings:
        if check_availability(booking[0], booking[1], threshold + 1) == False:
            overbooked_dates.append((booking[0], booking[1]))
    
    return overbooked_dates

# Добавление бронирований
print(add_booking('22.07.2024', '26.07.2024', 5))
print(add_booking('25.07.2024', '28.07.2024', 3))  
print(add_booking('27.07.2024', '28.07.2024', 3))

print(add_booking('26.07.2024', '28.07.2024', 2))

# Получение дат с ограниченной доступностью
print(get_overbooked_dates())  # Вернет даты, когда занято 11 или более катамаранов


