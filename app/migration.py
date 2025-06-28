import sqlite3, datetime

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
        additional_wishes TEXT,
        status BOOLEAN DEFAULT 0 NOT NULL
        )""")
    database.commit()

    print("Таблицы успешно созданы")