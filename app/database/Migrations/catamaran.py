import sqlite3

def create_catamaran_orders_table(cursor: sqlite3.Cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catamaran_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL,
            price INTEGER NOT NULL
        )
    """)
