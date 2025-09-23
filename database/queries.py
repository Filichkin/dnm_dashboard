import os

from database.connection import db_connection


def get_dnm_data(
    selected_year: int = None,
    age_group: str = '0-10Y',
    selected_mobis_code: str = 'All',
    selected_holding: str = 'All',
    selected_region: str = 'All',
    group_by_region: bool = False
):
    """
    Получает данные DNM из базы данных используя SQL скрипт

    Args:
        selected_year: Выбранный год для фильтрации данных.
                      Если None, используется текущий год.
        age_group: Выбранная возрастная группа ('0-10Y' или '0-5Y').
        selected_mobis_code: Выбранный код дилера ('All' или конкретный код).
        selected_holding: Выбранный holding ('All' или конкретный holding).
        selected_region: Выбранный регион ('All' или конкретный регион).
        group_by_region: Если True, группирует данные по регионам.

    Returns:
        pd.DataFrame: Данные DNM
    """
    # Определяем имя SQL файла в зависимости от возрастной группы и группировки
    if group_by_region:
        if age_group == '0-5Y':
            sql_filename = 'dnm_script_age_0_5_by_region.sql'
        else:
            sql_filename = 'dnm_script_age_0_10_by_region.sql'
    else:
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

        # Выполняем запрос с параметрами
        if group_by_region:
            # Для запросов с группировкой по регионам нужны только год и регион
            df = db_connection.execute_query(
                query, {
                    'selected_year': selected_year,
                    'selected_region': selected_region
                }
            )
        else:
            # Для обычных запросов нужны все параметры
            df = db_connection.execute_query(
                query, {
                    'selected_year': selected_year,
                    'selected_mobis_code': selected_mobis_code,
                    'selected_holding': selected_holding,
                    'selected_region': selected_region
                }
            )

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f'SQL файл не найден: {sql_file_path}')
    except Exception as e:
        raise Exception(f'Ошибка при получении данных из базы: {e}')


def get_dealers_data():
    """
    Получает данные дилеров из таблицы dealers_data

    Returns:
        pd.DataFrame: Данные дилеров с колонками mobis_code, dealer_name,
                      holding, region
    """
    query = """
    SELECT mobis_code, dealer_name, holding, region
    FROM public.dealers_data
    WHERE mobis_code IS NOT NULL
    ORDER BY mobis_code
    """
    return db_connection.execute_query(query)


def get_regions():
    """
    Получает список уникальных регионов из таблицы dealers_data

    Returns:
        list: Список уникальных регионов
    """
    query = """
    SELECT DISTINCT region
    FROM public.dealers_data
    WHERE region IS NOT NULL AND region != ''
    ORDER BY region
    """
    df = db_connection.execute_query(query)
    return df['region'].tolist()


def get_region_by_mobis_code(mobis_code):
    """
    Получает region по mobis_code из таблицы dealers_data

    Args:
        mobis_code: Код дилера

    Returns:
        str: Название региона или пустая строка
    """
    if mobis_code == 'All' or not mobis_code:
        return ''

    query = """
    SELECT region
    FROM public.dealers_data
    WHERE mobis_code = %(mobis_code)s
    """

    df = db_connection.execute_query(
        query, {'mobis_code': mobis_code}
    )
    if not df.empty:
        return df['region'].iloc[0] if df['region'].iloc[0] else ''
    return ''


def get_mobis_codes_by_region(region):
    """
    Получает список mobis_code для указанного региона

    Args:
        region: Название региона

    Returns:
        list: Список mobis_code
    """
    if region == 'All':
        query = """
        SELECT mobis_code
        FROM public.dealers_data
        WHERE mobis_code IS NOT NULL
        ORDER BY mobis_code
        """
    else:
        query = """
        SELECT mobis_code
        FROM public.dealers_data
        WHERE region = %(region)s AND mobis_code IS NOT NULL
        ORDER BY mobis_code
        """

    df = db_connection.execute_query(query, {'region': region})
    return df['mobis_code'].tolist()


def get_dnm_data_by_region(
    selected_year: int = None,
    age_group: str = '0-10Y',
    selected_mobis_code: str = 'All',
    selected_holding: str = 'All',
    selected_region: str = 'All'
):
    """
    Получает данные DNM с группировкой по регионам из базы данных

    Args:
        selected_year: Выбранный год для фильтрации данных.
                      Если None, используется текущий год.
        age_group: Выбранная возрастная группа ('0-10Y' или '0-5Y').
        selected_mobis_code: Выбранный код дилера ('All' или конкретный код).
        selected_holding: Выбранный holding ('All' или конкретный holding).
        selected_region: Выбранный регион ('All' или конкретный регион).

    Returns:
        pd.DataFrame: Данные DNM сгруппированные по регионам
    """
    return get_dnm_data(
        selected_year=selected_year,
        age_group=age_group,
        selected_mobis_code=selected_mobis_code,
        selected_holding=selected_holding,
        selected_region=selected_region,
        group_by_region=True
    )


def test_database_connection():
    """
    Тестирует подключение к базе данных

    Returns:
        bool: True если подключение успешно
    """
    return db_connection.test_connection()
