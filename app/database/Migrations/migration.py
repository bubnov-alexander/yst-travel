from app.utils.logger import logger
import sqlite3
from app.database.Migrations.catamaran import create_catamaran_table
from app.database.Migrations.admin import create_admin_table

async def db_start():
    try:
        db = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
        cursor = db.cursor()
        logger.info("✅  Подключение к SQLite установлено")

        create_catamaran_table(cursor)
        logger.info("🛶 Таблица catamaran — готова")

        create_admin_table(cursor)
        logger.info("💼 Таблица admin — готова")

        db.commit()
        db.close()
        logger.info("✅  Все миграции выполнены и сохранены")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске миграций: {e}")
