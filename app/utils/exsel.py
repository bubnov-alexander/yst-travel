import sqlite3
from openpyxl import Workbook

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
import sqlite3


def export_sql_to_excel(db_path, excel_path):
    # Подключаемся к базе данных
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Выполняем запрос для извлечения всех данных из таблицы
    cursor.execute("SELECT * FROM catamaran_orders")
    rows = cursor.fetchall()

    # Получаем имена столбцов
    cursor.execute("PRAGMA table_info(catamaran_orders)")
    columns = [column[1] for column in cursor.fetchall()]

    # Создаем новый рабочий файл Excel
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Catamaran Data"

    # Записываем имена столбцов в первую строку
    for col_num, column_name in enumerate(columns, 1):
        sheet.cell(row=1, column=col_num, value=column_name)

    # Записываем данные в таблицу
    for row_num, row_data in enumerate(rows, 2):
        for col_num, cell_data in enumerate(row_data, 1):
            sheet.cell(row=row_num, column=col_num, value=cell_data)

    # Автоматическая настройка ширины столбцов
    for col_num, column_title in enumerate(columns, 1):
        max_length = len(str(column_title))
        for row in sheet.iter_rows(min_row=2, min_col=col_num, max_col=col_num):
            for cell in row:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
        adjusted_width = max_length + 2  # Добавляем небольшой отступ
        col_letter = get_column_letter(col_num)
        sheet.column_dimensions[col_letter].width = adjusted_width

    # Сохраняем файл Excel
    workbook.save(excel_path)

    # Закрываем соединение с базой данных
    conn.close()


