import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

# Создаем подключение к базе данных
conn = sqlite3.connect('data/database.db')
cursor = conn.cursor()

# Создаем таблицу (если она еще не существует)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS catamaran (
        id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        phone_number TEXT NOT NULL,
        price TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        date_start DATETIME NOT NULL,
        date_end DATETIME NOT NULL
    )
''')

# Генератор случайных данных
fake = Faker()

# Функция для генерации случайной даты
def random_date(start, end):
    return start + timedelta(
        days=random.randint(0, (end - start).days))  # Максимальная разница в днях - разница между start и end

# Период времени для случайных дат
start_date = datetime(2024, 5, 1).date()
end_date = datetime(2024, 9, 1).date()

print(f'Генерация и вставка записей в базу данных... ({start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")})')

# Генерация и вставка множества записей
num_records = 10  # Количество записей для вставки

for _ in range(num_records):
    customer_name = fake.name()
    phone_number = fake.phone_number()
    price = random.randint(100, 10000)
    quantity = random.randint(1, 10)
    date_start = random_date(start_date, end_date)
    # Генерация случайной даты окончания
    date_end = random_date(date_start, min(date_start + timedelta(days=8), end_date))  # Максимальная разница в днях - 8

    cursor.execute('''
        INSERT INTO catamaran (customer_name, phone_number, price, quantity, date_start, date_end)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (customer_name, phone_number, price, quantity, date_start.strftime("%d.%m.%Y"), date_end.strftime("%d.%m.%Y")))

    # Получаем месяц из даты начала и выводим его
    month = date_start.strftime("%B")
    print(f'Сгенерирована запись с датой начала в месяце {month}')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print(f'{num_records} записей успешно добавлено в базу данных.')
