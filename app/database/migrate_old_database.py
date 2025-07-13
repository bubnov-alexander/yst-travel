import sqlite3

def migrate_catamaran_data(old_db_path: str, new_db_path: str, default_route_id: int = 1):
    old_conn = sqlite3.connect(old_db_path)
    new_conn = sqlite3.connect(new_db_path)

    old_cursor = old_conn.cursor()
    new_cursor = new_conn.cursor()

    # Получаем данные из старой таблицы
    old_cursor.execute("SELECT * FROM catamaran")
    rows = old_cursor.fetchall()

    for row in rows:
        (
            _id,
            date_start,
            date_end,
            time_start,
            _route,
            quantity,
            customer_name,
            phone_number,
            price_text,
            additional_wishes,
            status
        ) = row

        try:
            price = int(''.join(filter(str.isdigit, str(price_text))))
        except:
            price = 0

        new_cursor.execute("""
            INSERT INTO orders (
                date_arrival,
                time_arrival,
                date_departure,
                time_departure,
                route_id,
                customer_name,
                phone,
                prepayment_status,
                additional_wishes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_start,
            time_start,
            date_end,
            time_start,
            default_route_id,
            customer_name,
            phone_number,
            int(status),
            additional_wishes
        ))

        order_id = new_cursor.lastrowid

        new_cursor.execute("""
            INSERT INTO catamaran_services (
                order_id,
                quantity,
                price
            ) VALUES (?, ?, ?)
        """, (order_id, quantity, price))

    new_conn.commit()
    print(f"[✓] Успешно перенесено {len(rows)} заказов.")

    old_conn.close()
    new_conn.close()

migrate_catamaran_data("app/storage/old_database.db", "app/storage/database.db", default_route_id=1)
