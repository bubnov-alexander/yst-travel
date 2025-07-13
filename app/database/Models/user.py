import sqlite3


def get_user_id():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    user_id = cursor.execute("SELECT user_id FROM admins")
    user_ids = [row[0] for row in user_id.fetchall()]

    return user_ids


def get_user_role_from_db(user_id: int) -> str:
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT role FROM admins WHERE telegram_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else "user"


def get_users():
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("SELECT id, user_id FROM admins")
    admins = cursor.fetchall()

    database.close()

    return admins


def set_user(user_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id,))
    database.commit()
    database.close()



def delete_user(user_id):
    database = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
    cursor = database.cursor()

    cursor.execute("DELETE FROM admins WHERE id = ?", (user_id,))
    changes = database.total_changes

    database.commit()
    database.close()

    return changes
