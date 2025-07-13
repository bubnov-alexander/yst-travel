import sqlite3


async def set_value_in_settings(setting_key, value):
    conn = sqlite3.connect("app/storage/database.db")
    cursor = conn.cursor()

    cursor.execute("""
                   INSERT INTO settings (key, value)
                   VALUES (?, ?)
                   ON CONFLICT(key) DO UPDATE SET value = excluded.value
                   """, (setting_key, value))

    conn.commit()
    conn.close()

def get_service_counts():
    conn = sqlite3.connect("app/storage/database.db")
    cursor = conn.cursor()

    keys = ("database_supboard", "database_transfer", "database_catamaran")
    cursor.execute(
        f"SELECT key, value FROM settings WHERE key IN ({','.join('?' for _ in keys)})",
        keys
    )

    results = dict(cursor.fetchall())
    conn.close()

    return {
        "supboard": results.get("database_supboard", "0"),
        "transfer": results.get("database_transfer", "0"),
        "catamaran": results.get("database_catamaran", "0")
    }