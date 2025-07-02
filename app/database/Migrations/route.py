import sqlite3
import itertools

from app.utils.logger import logger


def create_routes_table(cursor: sqlite3.Cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
            point_a TEXT NOT NULL,
            point_b TEXT NOT NULL
        )
    """)


def seed_routes():
    points = ['Усть-Утка', 'Ёква', 'Сулём', 'Харёнки', 'Верхняя Ослянка']

    database = sqlite3.connect('app/storage/database.db')
    cursor = database.cursor()

    create_routes_table(cursor)

    pairs = list(itertools.permutations(points, 2))  # Все возможные маршруты, где A != B

    for point_a, point_b in pairs:
        try:
            # Проверяем, существует ли уже такой маршрут
            cursor.execute(
                "SELECT 1 FROM routes WHERE point_a = ? AND point_b = ?",
                (point_a, point_b)
            )
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(
                    "INSERT INTO routes (point_a, point_b) VALUES (?, ?)",
                    (point_a, point_b)
                )
        except Exception as e:
            logger.error(f"Ошибка при добавлении маршрута {point_a} - {point_b}: {e}")

    database.commit()
    database.close()
    logger.info("🚢 Все маршруты успешно обработаны")
