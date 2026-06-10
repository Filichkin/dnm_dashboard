"""
Функции для обработки данных и создания компонентов DNM Dashboard
"""
import pandas as pd
from datetime import datetime
from dash import html
from loguru import logger

from .components import (
    create_metric_card,
    create_cards_row,
    create_chart_card,
    create_data_table,
    create_dealer_name_display,
    create_holding_name_display,
    create_region_name_display
)
from .plotly_templates import build_dashboard_figures
from .constants import (
    get_dealer_name,
    get_holding_name,
    get_region_name,
    get_holding_by_mobis_code,
    get_region_by_mobis_code,
    get_mobis_codes_by_holding
)
from database.queries import (
    get_dnm_data,
)


def format_number_k_m(value):
    """
    Форматирует число в формат K/M (тысячи/миллионы)

    Args:
        value: Числовое значение для форматирования

    Returns:
        str: Отформатированная строка (например, 100K, 270M)
    """
    if pd.isna(value) or value == 0:
        return '0'

    abs_value = abs(value)

    if abs_value >= 1_000_000:
        formatted = f"{value / 1_000_000:.0f}M"
    elif abs_value >= 1_000:
        formatted = f"{value / 1_000:.0f}K"
    else:
        formatted = f"{value:.0f}"

    return formatted


def process_dataframe(df):
    """
    Обрабатывает DataFrame для корректного отображения

    Args:
        df: Исходный DataFrame

    Returns:
        pd.DataFrame: Обработанный DataFrame
    """
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Unnamed: 1' in df.columns:
        df = df.drop(columns=['Unnamed: 1'])

    if 'Model \\ Age' in df.columns:
        df = df.rename(columns={'Model \\ Age': 'model'})

    if 'Model' in df.columns:
        df = df.rename(columns={'Model': 'model'})

    # Создаем агрегированные колонки для 0-10Y
    if 'age_0_3' not in df.columns:
        cols_0_3 = [f'age_{y}' for y in range(0, 4)
                    if f'age_{y}' in df.columns]
        if cols_0_3:
            df['age_0_3'] = df[cols_0_3].sum(axis=1)
    if 'age_4_5' not in df.columns:
        cols_4_5 = [f'age_{y}' for y in range(4, 6)
                    if f'age_{y}' in df.columns]
        if cols_4_5:
            df['age_4_5'] = df[cols_4_5].sum(axis=1)
    if 'age_6_10' not in df.columns:
        cols_6_10 = [f'age_{y}' for y in range(6, 11)
                     if f'age_{y}' in df.columns]
        if cols_6_10:
            df['age_6_10'] = df[cols_6_10].sum(axis=1)

    # Создаем агрегированные колонки для 0-5Y (используем age_0_3 и age_4_5)
    if 'age_0_3' not in df.columns:
        cols_0_3 = [f'age_{y}' for y in range(0, 4)
                    if f'age_{y}' in df.columns]
        if cols_0_3:
            df['age_0_3'] = df[cols_0_3].sum(axis=1)
    if 'age_4_5' not in df.columns:
        cols_4_5 = [f'age_{y}' for y in range(4, 6)
                    if f'age_{y}' in df.columns]
        if cols_4_5:
            df['age_4_5'] = df[cols_4_5].sum(axis=1)

    return df


def create_charts(df, age_group='0-10Y', region_df=None, theme='dark'):
    """Создаёт все 6 тематизированных графиков.

    Делегирует построение в
    plotly_templates.build_dashboard_figures, который применяет
    дизайн-систему (ранжированная прозрачность, значения над
    столбцами, оверлей Region Average, stacked age-groups с линией
    AVG UIO) и поддерживает тёмную и светлую темы.
    """
    return build_dashboard_figures(df, age_group, region_df, theme)


def create_table(df, age_group='0-10Y', show_all_columns=False):
    """
    Создает таблицу данных с фильтрацией, зеброй и скрытием колонок

    Args:
        df: DataFrame с данными
        age_group: Выбранная возрастная группа

    Returns:
        dash_table.DataTable: Таблица данных
    """
    # Словарь переименований колонок в зависимости от возрастной группы
    if age_group == '0-5Y':
        column_rename = {
            'model': 'Model',
            # 'uio': 'UIO',
            'uio_5y': 'UIO 5Y',
            'avg_uio_5y': 'AVG_UIO 5Y',
            'total_0_5': 'RO qty',
            'total_ro_cost': 'Amount',
            'avg_ro_cost': 'CPR',
            'labor_hours_0_5': 'L/H',
            'aver_labor_hours_per_vhc': 'L/H per RO',
            'labor_amount_0_5': 'Labor',
            'avg_ro_labor_cost': 'LPR',
            'parts_amount_0_5': 'Parts',
            'avg_ro_part_cost': 'PPR',
            'age_0': '0Y',
            'age_1': '1Y',
            'age_2': '2Y',
            'age_3': '3Y',
            'age_4': '4Y',
            'age_5': '5Y',
            'age_0_3': '0-3Y',
            'age_4_5': '4-5Y',
            'pct_age_0_3': 'Ratio 0-3Y',
            'pct_age_4_5': 'Ratio 4-5Y',
            'ro_ratio_of_uio_5y': 'RO ratio from UIO 5Y'
        }
    else:
        column_rename = {
            'model': 'Model',
            # 'uio': 'UIO',
            'uio_10y': 'UIO 10Y',
            'avg_uio_10y': 'AVG_UIO 10Y',
            'total_0_10': 'RO qty',
            'total_ro_cost': 'Amount',
            'avg_ro_cost': 'CPR',
            'labor_hours_0_10': 'L/H',
            'aver_labor_hours_per_vhc': 'L/H per RO',
            'labor_amount_0_10': 'Labor',
            'avg_ro_labor_cost': 'LPR',
            'parts_amount_0_10': 'Parts',
            'avg_ro_part_cost': 'PPR',
            'age_0': '0Y',
            'age_1': '1Y',
            'age_2': '2Y',
            'age_3': '3Y',
            'age_4': '4Y',
            'age_5': '5Y',
            'age_6': '6Y',
            'age_7': '7Y',
            'age_8': '8Y',
            'age_9': '9Y',
            'age_10': '10Y',
            'age_0_3': '0-3Y',
            'age_4_5': '4-5Y',
            'age_6_10': '6-10Y',
            'pct_age_0_3': 'Ratio 0-3Y',
            'pct_age_4_5': 'Ratio 4-5Y',
            'pct_age_6_10': 'Ratio 6-10Y',
            'ro_ratio_of_uio_10y': 'RO ratio from UIO 10Y'
        }

    # Определяем приоритетные колонки в зависимости от возрастной группы
    if age_group == '0-5Y':
        priority_cols = [
            'model',
            'uio',
            'uio_5y',
            'avg_uio_5y',
            'total_0_5',
            'total_ro_cost',
            'avg_ro_cost',
            'labor_hours_0_5',
            'aver_labor_hours_per_vhc',
            'labor_amount_0_5',
            'avg_ro_labor_cost',
            'parts_amount_0_5',
            'avg_ro_part_cost',
        ]
    else:
        priority_cols = [
            'model',
            'uio',
            'uio_10y',
            'avg_uio_10y',
            'total_0_10',
            'total_ro_cost',
            'avg_ro_cost',
            'labor_hours_0_10',
            'aver_labor_hours_per_vhc',
            'labor_amount_0_10',
            'avg_ro_labor_cost',
            'parts_amount_0_10',
            'avg_ro_part_cost',
        ]
    ordered_cols = (
        [c for c in priority_cols if c in df.columns] +
        [c for c in df.columns if c not in priority_cols]
    )
    columns = []
    for col in ordered_cols:
        # Получаем отображаемое имя колонки
        display_name = column_rename.get(col, col)

        if df[col].dtype.kind in 'fi':
            fmt = {'specifier': ',.1f'} \
                if col == 'aver_labor_hours_per_vhc' else {'specifier': ',.0f'}
            columns.append({
                'name': display_name,
                'id': col,
                'type': 'numeric',
                'format': fmt
            })
        else:
            columns.append({'name': display_name, 'id': col})

    # Фильтруем строки и сортируем по total_ro_cost
    df_table = df.copy()
    total_col = 'total_0_5' if age_group == '0-5Y' else 'total_0_10'

    # Фильтруем строки с валидными данными
    if total_col in df_table.columns:
        df_table = df_table[df_table[total_col] > 0]

    # Убираем строки с пустыми или нулевыми значениями в ключевых колонках
    if 'total_ro_cost' in df_table.columns:
        df_table = df_table[df_table['total_ro_cost'] > 0]

    # Сортируем по total_ro_cost
    if 'total_ro_cost' in df_table.columns:
        df_table = df_table.sort_values('total_ro_cost', ascending=False)

    result = create_data_table(columns, df_table.to_dict('records'),
                               show_all_columns)
    return result


def calculate_metrics(df, age_group='0-10Y'):
    """
    Вычисляет суммарные показатели для карт

    Args:
        df: DataFrame с данными
        age_group: Выбранная возрастная группа

    Returns:
        dict: Словарь с метриками
    """
    # Определяем колонки в зависимости от возрастной группы
    if age_group == '0-5Y':
        total_col = 'total_0_5'
        labor_hours_col = 'labor_hours_0_5'
    else:
        total_col = 'total_0_10'
        labor_hours_col = 'labor_hours_0_10'

    # Используем новую колонку uio, если она есть, иначе fallback
    if 'uio' in df.columns:
        total_uio = df['uio'].sum()
    elif age_group == '0-5Y' and 'uio_5y' in df.columns:
        total_uio = df['uio_5y'].sum()
    elif (age_group == '0-10Y' and
          'uio_10y' in df.columns):
        total_uio = df['uio_10y'].sum()
    else:
        total_uio = 0
    total_ro_qty = df[total_col].sum() if total_col in df.columns else 0
    total_cost = (df['total_ro_cost'].sum()
                  if 'total_ro_cost' in df.columns else 0)
    total_labor_hours = (
        df[labor_hours_col].sum()
        if labor_hours_col in df.columns else 0
    )
    avg_ro_cost = (total_cost / total_ro_qty
                   if total_ro_qty > 0 else 0)

    return {
        'total_uio': total_uio,
        'total_ro_qty': total_ro_qty,
        'total_cost': total_cost,
        'total_labor_hours': total_labor_hours,
        'avg_ro_cost': avg_ro_cost
    }


def get_available_years():
    """
    Получает список доступных годов

    Returns:
        list: Список годов
    """
    current_year = datetime.now().year
    # Последние 5 лет + текущий
    return list(range(current_year - 5, current_year + 1))


def get_current_year():
    """
    Получает текущий год

    Returns:
        int: Текущий год
    """
    return datetime.now().year


def load_dashboard_data(selected_year, age_group, selected_mobis_code,
                        selected_holding, selected_region='All'):
    """
    Загружает данные для дашборда с автоматическим определением региона

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа
        selected_mobis_code: Выбранный код дилера
        selected_holding: Выбранный holding
        selected_region: Выбранный region

    Returns:
        pd.DataFrame: DataFrame с данными
    """
    # НОВАЯ ЛОГИКА: Автоматически определяем регион по mobis_code
    if selected_mobis_code != 'All':
        # Определяем регион по выбранному дилеру
        auto_region = get_region_by_mobis_code(selected_mobis_code)
        if auto_region:
            selected_region = auto_region
            logger.info(f'Автоматически определен регион: {auto_region} '
                        f'для дилера {selected_mobis_code}')
        else:
            selected_region = 'All'
            logger.warning(f'Не удалось определить регион для дилера '
                           f'{selected_mobis_code}')
    else:
        # Если выбран 'All' дилеров, используем выбранный пользователем регион
        # (если он был выбран, иначе 'All')
        if selected_region is None or selected_region == '':
            selected_region = 'All'

    # Проверяем совместимость выбранного Mobis Code с Holding
    if (selected_holding != 'All' and
        selected_mobis_code != 'All' and
        selected_mobis_code not in get_mobis_codes_by_holding(
            selected_holding)):
        # Если выбранный Mobis Code не соответствует Holding,
        # используем 'All' для Mobis Code
        selected_mobis_code = 'All'

    try:
        # Получаем данные для выбранного года, возрастной группы,
        # кода дилера, holding и автоматически определенного region
        df = get_dnm_data(selected_year, age_group, selected_mobis_code,
                          selected_holding, selected_region)
    except Exception:
        # Fallback на CSV файл в случае ошибки
        if selected_year == 2024:
            # Используем июль 2025 как 2024
            df = pd.read_csv('data/jul_25.csv')
        else:
            # Используем август 2025 как 2025
            df = pd.read_csv('data/aug_25.csv')

        # Добавляем пустую колонку UIO для fallback данных
        df['uio'] = 0

    return df


def load_region_data(selected_year, age_group, selected_mobis_code):
    """
    Загружает данные по региону выбранного дилера (НОВАЯ ЛОГИКА)

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа
        selected_mobis_code: Выбранный код дилера

    Returns:
        pd.DataFrame: Данные по региону
    """
    try:
        # Определяем регион по mobis_code
        region = get_region_by_mobis_code(selected_mobis_code)
        if not region:
            logger.warning(f'Не удалось определить регион для дилера '
                           f'{selected_mobis_code}')
            return pd.DataFrame()

        logger.info(f'Получаем данные по региону {region} для дилера '
                    f'{selected_mobis_code}')

        # Получаем данные по региону с использованием нового скрипта
        df = get_dnm_data(
            selected_year=selected_year,
            age_group=age_group,
            selected_mobis_code='All',  # Все дилеры в регионе
            selected_holding='All',    # Все холдинги в регионе
            selected_region=region,     # Конкретный регион
            group_by_region=True  # Используем скрипт с группировкой по региону
        )
        return df
    except Exception as e:
        logger.error(f'Ошибка при получении данных по региону: {e}')
        return pd.DataFrame()


def create_metrics_cards(metrics, age_group):
    """
    Создает карты с метриками

    Args:
        metrics: Словарь с метриками
        age_group: Выбранная возрастная группа

    Returns:
        html.Div: Компонент с картами метрик
    """
    return create_cards_row([
        create_metric_card(f'UIO ({age_group})',
                           f'{metrics["total_uio"]:,.0f}',
                           unit='units in operation'),
        create_metric_card(f'RO qty ({age_group})',
                           f'{metrics["total_ro_qty"]:,.0f}',
                           unit='repair orders'),
        create_metric_card(f'Total cost ({age_group})',
                           f'{metrics["total_cost"]:,.0f}',
                           unit='RUB', hero=True),
        create_metric_card('Total L/H',
                           f'{metrics["total_labor_hours"]:,.0f}',
                           unit='labor hours'),
        create_metric_card('Average RO cost',
                           f'{metrics["avg_ro_cost"]:,.0f}',
                           unit='RUB per RO'),
    ])


def create_charts_container(charts):
    """
    Создает контейнер с графиками

    Args:
        charts: Словарь с графиками

    Returns:
        html.Div: Компонент с графиками
    """
    return html.Div([
        create_chart_card(charts['fig_profit'], 'Total Profit',
                          'by model · amount', 'Amount'),
        create_chart_card(charts['fig_mh'], 'Total Labor Hours',
                          'by model · L/H', 'L/H'),
        create_chart_card(charts['fig_avg_mh'], 'Avg Labor Hours / Car',
                          'by model · L/H per RO', 'L/H·RO'),
        create_chart_card(charts['fig_avg_check'], 'Average RO Cost',
                          'by model · CPR', 'CPR'),
        create_chart_card(charts['fig_ratio'], 'Ratio RO / UIO',
                          'by model · %', 'Ratio'),
        create_chart_card(charts['fig_ro_years'], 'RO Count by Age Groups',
                          '0-3y / 4-5y · vs AVG UIO', 'Mix', tall=True),
    ], className='charts')


def create_dealer_display(selected_mobis_code):
    """
    Создает компонент отображения названия дилера, holding и region

    Args:
        selected_mobis_code: Выбранный код дилера

    Returns:
        html.Div: Компонент отображения дилера с дополнительной информацией
    """
    dealer_name = get_dealer_name(selected_mobis_code)
    holding = get_holding_by_mobis_code(selected_mobis_code)
    region = get_region_by_mobis_code(selected_mobis_code)

    # Создаем основной контейнер
    if not dealer_name:
        return html.Div()

    # Создаем отображение дилера
    dealer_display = create_dealer_name_display()
    dealer_display.children[1].children = dealer_name

    # Создаем отображение holding
    holding_display = create_holding_name_display()
    holding_display.children[1].children = holding if holding else 'No holding'

    # Создаем отображение region
    region_display = create_region_name_display()
    region_display.children[1].children = region if region else 'No region'

    # Объединяем все компоненты в горизонтальную линию
    return html.Div([
        dealer_display,
        holding_display,
        region_display
    ], className='namebar')


def create_holding_display(selected_holding):
    """
    Создает компонент отображения названия Holding

    Args:
        selected_holding: Выбранный holding

    Returns:
        html.Div: Компонент отображения Holding
    """
    holding_name = get_holding_name(selected_holding)
    holding_display = (create_holding_name_display()
                       if holding_name else html.Div())

    # Обновляем текст названия Holding
    if holding_name:
        holding_display.children[1].children = holding_name

    return holding_display


def create_region_display(selected_region):
    """
    Создает компонент отображения названия Region

    Args:
        selected_region: Выбранный region

    Returns:
        html.Div: Компонент отображения Region
    """
    region_name = get_region_name(selected_region)
    region_display = (create_region_name_display()
                      if region_name else html.Div())

    # Обновляем текст названия Region
    if region_name:
        region_display.children[1].children = region_name

    return region_display
