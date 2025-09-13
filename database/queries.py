import os

from database.connection import db_connection


def get_dnm_data(selected_year: int = None, age_group: str = '0-10Y',
                 selected_mobis_code: str = 'All'):
    """
    Получает данные DNM из базы данных используя SQL скрипт

    Args:
        selected_year: Выбранный год для фильтрации данных.
                      Если None, используется текущий год.
        age_group: Выбранная возрастная группа ('0-10Y' или '0-5Y').
        selected_mobis_code: Выбранный код дилера ('All' или конкретный код).

    Returns:
        pd.DataFrame: Данные DNM
    """
    # Определяем имя SQL файла в зависимости от возрастной группы
    if age_group == '0-5Y':
        sql_filename = 'dnm_script_age_0_5.sql'
    else:
        sql_filename = 'dnm_script_age_0_10.sql'

    # Путь к SQL файлу
    sql_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'SQL', sql_filename
    )

    try:
        # Читаем SQL скрипт из файла
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            query = file.read()

        # Если год не указан, используем текущий год
        if selected_year is None:
            from datetime import datetime
            selected_year = datetime.now().year

        # Выполняем запрос с параметрами года и mobis_code
        df = db_connection.execute_query(
            query, {
                'selected_year': selected_year,
                'selected_mobis_code': selected_mobis_code
            }
        )

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f'SQL файл не найден: {sql_file_path}')
    except Exception as e:
        raise Exception(f'Ошибка при получении данных из базы: {e}')


def test_database_connection():
    """
    Тестирует подключение к базе данных

    Returns:
        bool: True если подключение успешно
    """
    return db_connection.test_connection()
