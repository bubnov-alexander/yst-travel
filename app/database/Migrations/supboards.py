import sqlite3


def create_supboard_services_table(cursor: sqlite3.Cursor):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS supboard_services
                   (
                       id              INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       order_id        INTEGER                                  NOT NULL,
                       supboards_count INTEGER                                  NOT NULL,
                       price           INTEGER                                  NOT NULL,

                       FOREIGN KEY (order_id) REFERENCES orders (id)
                   );
                   """)
