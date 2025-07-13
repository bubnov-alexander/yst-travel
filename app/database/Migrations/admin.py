import sqlite3

def create_admin_table(cursor: sqlite3.Cursor):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS admins
                   (
                       id        INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                       user_id   INTEGER UNIQUE                           NOT NULL
                   );
        
                   """)
