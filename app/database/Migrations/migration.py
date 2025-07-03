from app.database.Migrations.route import create_routes_table, seed_routes
from app.database.Migrations.settings import create_settings_table
from app.database.Migrations.supboards import create_supboard_services_table
from app.database.Migrations.transfer import create_transfer_service
from app.utils.logger import logger
import sqlite3
from app.database.Migrations.catamaran import create_catamaran_orders_table
from app.database.Migrations.orders import create_orders_table
from app.database.Migrations.admin import create_admin_table

async def db_start():
    try:
        db = sqlite3.connect('app/storage/database.db', check_same_thread=False, timeout=7)
        cursor = db.cursor()
        logger.info("✅  Подключение к SQLite установлено")

        seed_routes()
        logger.info("🚢 Таблица route — готова ")

        create_orders_table(cursor)
        logger.info("🛶 Таблица orders — готова")

        create_catamaran_orders_table(cursor)
        logger.info("🛶 Таблица catamaran — готова")

        create_supboard_services_table(cursor)
        logger.info("🛶 Таблица supboard — готова")

        create_transfer_service(cursor)
        logger.info("Таблица transfer — готова")

        create_settings_table(cursor)
        logger.info("🛶 Таблица settings — готова")

        create_admin_table(cursor)
        logger.info("💼 Таблица admin — готова")

        db.commit()
        db.close()
        logger.info("✅  Все миграции выполнены и сохранены")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске миграций: {e}")
