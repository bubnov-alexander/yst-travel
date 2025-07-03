import sqlite3

def create_settings_table(cursor: sqlite3.Cursor):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS settings
                   (
                       id    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       key   TEXT UNIQUE                              NOT NULL,
                       value TEXT                                     NOT NULL
                   );
                   """)