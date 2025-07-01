import sqlite3

def create_catamaran_orders_table(cursor: sqlite3.Cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catamaran_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            date_arrival DATE NOT NULL,
            time_arrival TIME NOT NULL,
            date_departure DATE NOT NULL,
            time_departure TIME NOT NULL,
            route_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            price INTEGER NOT NULL,
            additional_wishes TEXT,
            prepayment_status BOOLEAN NOT NULL,

            FOREIGN KEY (route_id) REFERENCES routes(id)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION
        )
    """)
