import sqlite3

def create_catamaran_table(cursor: sqlite3.Cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catamaran (
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
        )
    """)
