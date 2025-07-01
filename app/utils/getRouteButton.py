from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.database.Models.route import get_all_route, get_unique_points_a, get_routes_by_point_a


def get_points_a_keyboard():
    points = get_unique_points_a()
    keyboard = InlineKeyboardMarkup(row_width=2)

    for point in points:
        keyboard.add(InlineKeyboardButton(text=point, callback_data=f'select_point_a_{point}'))

    keyboard.add(InlineKeyboardButton(text='➕ Добавить новый маршрут', callback_data='add_new_route'))

    return keyboard

def get_routes_keyboard_from_point_a(point_a):
    routes = get_routes_by_point_a(point_a)
    keyboard = InlineKeyboardMarkup(row_width=2)

    for route_id, point_b in routes:
        keyboard.add(InlineKeyboardButton(text=f'{point_a} - {point_b}', callback_data=f'select_route_{route_id}'))

    return keyboard