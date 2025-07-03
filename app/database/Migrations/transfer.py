import sqlite3

def create_transfer_service(cursor: sqlite3.Cursor):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS transfer_services
                   (
                       id                INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       order_id          INTEGER                                  NOT NULL,
                       vehicle_type      TEXT                                     NOT NULL,
                       route_id          INTEGER                                  NOT NULL,
                       persons_count     INTEGER                                  NOT NULL,
                       driver_included   BOOLEAN                                  NOT NULL,
                       price             INTEGER                                  NOT NULL,

                       FOREIGN KEY (order_id) REFERENCES orders (id),
                       FOREIGN KEY (route_id) REFERENCES routes (id)
                   );

                   """)