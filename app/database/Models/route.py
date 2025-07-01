import sqlite3, datetime


def get_route_by_id(route_id):
    with sqlite3.connect('app/storage/database.db') as database:
        cursor = database.cursor()
        cursor.execute("SELECT id, point_a, point_b FROM routes WHERE id = ?", (route_id,))
        route = cursor.fetchone()

    if route:
        return {'id': route[0], 'name': f"{route[1]} - {route[2]}"}
    else:
        return None


def get_all_route():
    database = sqlite3.connect('app/storage/database.db')
    cursor = database.cursor()

    cursor.execute("SELECT * FROM routes")
    rotes = cursor.fetchall()
    database.close()
    return rotes


def add_new_route(point_a, point_b):
    database = sqlite3.connect('app/storage/database.db')
    cursor = database.cursor()

    cursor.execute(
        "SELECT id FROM routes WHERE point_a = ? AND point_b = ?",
        (point_a, point_b)
    )
    existing = cursor.fetchone()
    if existing:
        route_id = existing[0]
    else:
        cursor.execute("INSERT INTO routes (point_a, point_b) VALUES (?, ?)", (point_a, point_b))
        database.commit()
        route_id = cursor.lastrowid

    database.close()

    return route_id


def get_unique_points_a():
    database = sqlite3.connect('app/storage/database.db')
    cursor = database.cursor()
    cursor.execute("SELECT DISTINCT point_a FROM routes")
    points = [row[0] for row in cursor.fetchall()]
    database.close()
    return points


def get_routes_by_point_a(point_a):
    database = sqlite3.connect('app/storage/database.db')
    cursor = database.cursor()
    cursor.execute("SELECT id, point_b FROM routes WHERE point_a = ?", (point_a,))
    routes = cursor.fetchall()
    database.close()
    return routes
