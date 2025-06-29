import sqlite3, datetime

def get_user_id():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    user_id = cursor.execute("SELECT user_id FROM admin")
    user_ids = [row[0] for row in user_id.fetchall()]

    return user_ids