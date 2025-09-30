import os
from functools import lru_cache

from loguru import logger
from database.connection import db_connection


@lru_cache(maxsize=10)
def load_sql_file(sql_filename: str) -> str:
    """
    Загружает SQL файл из директории SQL с кэшированием в памяти

    Args:
        sql_filename: Имя SQL файла

    Returns:
        str: Содержимое SQL файла

    Note:
        Результаты кэшируются в памяти для ускорения повторных загрузок
    """
    sql_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'SQL', sql_filename
    )

    logger.debug(f'Загружаем SQL файл: {sql_file_path}')

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            query = file.read()
        logger.debug(f'SQL файл успешно загружен: {sql_filename}')
        return query
    except FileNotFoundError:
        logger.error(f'SQL файл не найден: {sql_file_path}')
        raise FileNotFoundError(f'SQL файл не найден: {sql_file_path}')


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

    try:
        logger.info(
            f'Загружаем данные DNM: год={selected_year}, группа={age_group}, '
            f'дилер={selected_mobis_code}, холдинг={selected_holding}, '
            f'регион={selected_region}, '
            f'группировка_по_региону={group_by_region}'
        )

        # Читаем SQL скрипт из кэша (или из файла при первой загрузке)
        query = load_sql_file(sql_filename)

        # Если год не указан, используем текущий год
        if selected_year is None:
            from datetime import datetime
            selected_year = datetime.now().year
            logger.info(f'Год не указан, используем текущий: {selected_year}')

        # Выполняем запрос с параметрами
        params = {
            'selected_year': selected_year,
            'selected_mobis_code': selected_mobis_code,
            'selected_holding': selected_holding,
            'selected_region': selected_region
        }

        if group_by_region:
            logger.info('Выполняем запрос с группировкой по регионам')
        else:
            logger.info('Выполняем обычный запрос')

        df = db_connection.execute_query(query, params)
        logger.success(f'Данные DNM успешно загружены: {len(df)} строк')
        return df

    except FileNotFoundError:
        logger.error(f'SQL файл не найден: {sql_filename}')
        raise
    except Exception as e:
        logger.error(f'Ошибка при получении данных из базы: {e}')
        raise


def get_dealers_data():
    """
    Получает данные дилеров из таблицы dealers_data

    Returns:
        pd.DataFrame: Данные дилеров с колонками mobis_code, dealer_name,
                      holding, region
    """
    logger.info('Загружаем данные дилеров')
    query = """
    SELECT mobis_code, dealer_name, holding, region
    FROM public.dealers_data
    WHERE mobis_code IS NOT NULL
    ORDER BY mobis_code
    """
    df = db_connection.execute_query(query)
    logger.success(f'Данные дилеров загружены: {len(df)} записей')
    return df


def get_regions():
    """
    Получает список уникальных регионов из таблицы dealers_data

    Returns:
        list: Список уникальных регионов
    """
    logger.info('Загружаем список регионов')
    query = """
    SELECT DISTINCT region
    FROM public.dealers_data
    WHERE region IS NOT NULL AND region != ''
    ORDER BY region
    """
    df = db_connection.execute_query(query)
    regions = df['region'].tolist()
    logger.success(f'Список регионов загружен: {len(regions)} регионов')
    return regions


def get_region_by_mobis_code(mobis_code):
    """
    Получает region по mobis_code из таблицы dealers_data

    Args:
        mobis_code: Код дилера

    Returns:
        str: Название региона или пустая строка
    """
    if mobis_code == 'All' or not mobis_code:
        logger.debug(
            'Код дилера не указан или равен All, возвращаем пустую строку'
        )
        return ''

    logger.info(f'Получаем регион для дилера: {mobis_code}')
    query = """
    SELECT region
    FROM public.dealers_data
    WHERE mobis_code = %(mobis_code)s
    """

    df = db_connection.execute_query(
        query, {'mobis_code': mobis_code}
    )
    if not df.empty:
        region = df['region'].iloc[0] if df['region'].iloc[0] else ''
        logger.success(f'Регион найден: {region}')
        return region
    logger.warning(f'Регион для дилера {mobis_code} не найден')
    return ''


def get_mobis_codes_by_region(region):
    """
    Получает список mobis_code для указанного региона

    Args:
        region: Название региона

    Returns:
        list: Список mobis_code
    """
    logger.info(f'Получаем коды дилеров для региона: {region}')

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
    codes = df['mobis_code'].tolist()
    logger.success(
        f'Коды дилеров загружены: {len(codes)} кодов для региона {region}'
    )
    return codes


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
    logger.info('Тестируем подключение к базе данных')
    result = db_connection.test_connection()
    if result:
        logger.success('Тест подключения к базе данных прошел успешно')
    else:
        logger.error('Тест подключения к базе данных не прошел')
    return result
