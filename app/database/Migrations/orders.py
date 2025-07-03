import sqlite3

def create_orders_table(cursor: sqlite3.Cursor):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS orders
                   (
                       id                INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       date_arrival      DATE                                     NOT NULL,
                       time_arrival      TIME                                     NOT NULL,
                       date_departure    DATE                                     NOT NULL,
                       time_departure    TIME                                     NOT NULL,
                       route_id          INTEGER                                  NOT NULL,
                       customer_name     TEXT                                     NOT NULL,
                       phone             TEXT                                     NOT NULL,
                       prepayment_status BOOLEAN                                  NOT NULL,
                       additional_wishes TEXT,

                       FOREIGN KEY (route_id) REFERENCES routes (id)
                           ON DELETE NO ACTION
                           ON UPDATE NO ACTION
                   );
                   """)