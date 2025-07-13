import sqlite3, datetime

def get_user_id():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    user_id = cursor.execute("SELECT user_id FROM admin")
    user_ids = [row[0] for row in user_id.fetchall()]

    return user_ids

def get_user_role_from_db(user_id: int) -> str:
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT role FROM admin WHERE telegram_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else "user"