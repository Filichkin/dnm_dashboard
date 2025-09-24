"""
DNM Dashboard - основное приложение Dash
"""
import dash
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from datetime import datetime

from .components import (
    create_year_selector,
    create_age_group_selector,
    create_mobis_code_selector,
    create_holding_selector,
    create_region_selector,
    create_export_button
)
from .functions import (
    process_dataframe,
    create_charts,
    calculate_metrics,
    get_available_years,
    get_current_year,
    load_dashboard_data,
    load_region_data,
    create_metrics_cards,
    create_charts_container,
    create_dealer_display,
    create_holding_display,
    create_region_display
)
from .constants import (
    get_mobis_code_options_by_holding,
    get_mobis_code_options_by_region
)
from config import settings
from .styles import get_responsive_styles
from .templates import get_dashboard_template

# Layout Dash
app = dash.Dash(__name__)

# Получаем адаптивные стили
responsive_styles = get_responsive_styles()

# Добавляем CSS для адаптивности
app.index_string = get_dashboard_template()

# Получаем доступные годы и текущий год
available_years = get_available_years()
current_year = get_current_year()

app.layout = html.Div([
    html.H1('DNM RO DATA', style=responsive_styles['title']),

    # Скрытые div для хранения данных
    dcc.Store(id='data-store'),

    # Селекторы и карты в одном блоке
    html.Div([
        # Селекторы года, возрастных групп, кода дилера, holding, region
        # и отображение дилера и holding
        html.Div([
            create_year_selector(available_years, current_year),
            create_age_group_selector(),
            create_mobis_code_selector(),
            create_holding_selector(),
            create_region_selector(),
            html.Div(id='dealer-name-container'),
            html.Div(id='holding-name-container'),
            html.Div(id='region-name-container')
        ], style={
            'display': 'flex',
            'align-items': 'flex-start',
            'justify-content': 'flex-start',
            'flex-wrap': 'wrap',
            'gap': '20px',
            'marginBottom': '20px',
            'padding': '0 10px'
        }),

        # Карты с суммарными показателями
        html.Div(id='metrics-cards')
    ], style={
        'marginBottom': '40px'
    }),

    # Графики
    html.Div(id='charts-container'),

    # Таблица
    html.H2('Items data by models', style=responsive_styles['section_title']),
    create_export_button(),
    html.Div(id='data-table'),
], style=responsive_styles['main_container'],
    className=responsive_styles['main_container'].get('className', ''))


@callback(
    [Output('data-store', 'data'),
     Output('metrics-cards', 'children'),
     Output('charts-container', 'children'),
     Output('dealer-name-container', 'children'),
     Output('holding-name-container', 'children'),
     Output('region-name-container', 'children')],
    [Input('year-selector', 'value'),
     Input('age-group-selector', 'value'),
     Input('mobis-code-selector', 'value'),
     Input('holding-selector', 'value'),
     Input('region-selector', 'value')]
)
def update_dashboard(selected_year, age_group, selected_mobis_code,
                     selected_holding, selected_region):
    """
    Обновляет дашборд при изменении года, возрастной группы,
    кода дилера, holding или region.

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа
        selected_mobis_code: Выбранный код дилера
        selected_holding: Выбранный holding
        selected_region: Выбранный region

    Returns:
        tuple: Данные, карты метрик, графики, таблица, отображение дилера,
               отображение holding, отображение region
    """
    # Загружаем данные

    # Проверяем, что все параметры не None
    params = [selected_year, age_group, selected_mobis_code,
              selected_holding, selected_region]
    if any(param is None for param in params):
        return [], [], [], [], [], []
    df = load_dashboard_data(selected_year, age_group, selected_mobis_code,
                             selected_holding, selected_region)

    # Обрабатываем данные
    df = process_dataframe(df)

    # Загружаем данные по региону, если выбран конкретный дилер
    region_df = None
    if selected_mobis_code != 'All':
        region_df = load_region_data(selected_year, age_group,
                                     selected_mobis_code)
    # Создаем графики с региональными данными
    charts = create_charts(df, age_group, region_df)

    # Создаем таблицу
    from .functions import create_table
    create_table(df, age_group)

    # Вычисляем метрики
    metrics = calculate_metrics(df, age_group)

    # Создаем карты метрик
    metrics_cards = create_metrics_cards(metrics, age_group)

    # Создаем контейнеры графиков
    charts_container = create_charts_container(charts)

    # Создаем отображение названия дилера
    dealer_display = create_dealer_display(selected_mobis_code)

    # Создаем отображение названия Holding
    holding_display = create_holding_display(selected_holding)

    # Создаем отображение названия Region
    region_display = create_region_display(selected_region)

    return (df.to_dict('records'), metrics_cards, charts_container,
            dealer_display, holding_display, region_display)


@callback(
    [Output('mobis-code-selector', 'options'),
     Output('mobis-code-selector', 'value')],
    [Input('holding-selector', 'value'),
     Input('region-selector', 'value')],
    prevent_initial_call=False
)
def update_mobis_code_options(selected_holding, selected_region):
    """
    Обновляет опции Mobis Code при изменении выбранного Holding или Region.

    Args:
        selected_holding: Выбранный holding
        selected_region: Выбранный region

    Returns:
        tuple: (новые опции, новое значение)
    """
    # Получаем отфильтрованные опции по holding
    holding_options = get_mobis_code_options_by_holding(selected_holding)

    # Получаем отфильтрованные опции по region
    region_options = get_mobis_code_options_by_region(selected_region)

    # Находим пересечение опций
    holding_values = {opt['value'] for opt in holding_options}
    region_values = {opt['value'] for opt in region_options}
    intersection_values = holding_values.intersection(region_values)

    # Создаем финальные опции из пересечения
    new_options = [
        opt for opt in holding_options
        if opt['value'] in intersection_values
    ]

    # Если текущее значение Mobis Code не входит в новые опции,
    # сбрасываем на 'All'
    current_value = 'All'  # По умолчанию всегда 'All'

    # Добавляем отладочную информацию

    return new_options, current_value


@callback(
    Output('data-table', 'children'),
    [Input('year-selector', 'value'),
     Input('age-group-selector', 'value'),
     Input('mobis-code-selector', 'value'),
     Input('holding-selector', 'value'),
     Input('region-selector', 'value')]
)
def update_table(selected_year, age_group, selected_mobis_code,
                 selected_holding, selected_region):
    """
    Обновляет таблицу при изменении параметров

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа
        selected_mobis_code: Выбранный код дилера
        selected_holding: Выбранный holding
        selected_region: Выбранный region

    Returns:
        html.Div: Обновленная таблица
    """
    # По умолчанию скрываем колонки после PPR
    show_all_columns = False

    # Загружаем данные
    df = load_dashboard_data(selected_year, age_group, selected_mobis_code,
                             selected_holding, selected_region)

    # Обрабатываем данные
    df = process_dataframe(df)

    # Создаем таблицу
    from .functions import create_table
    table = create_table(df, age_group, show_all_columns)

    return table


@callback(
    Output('download-csv', 'data'),
    Input('export-csv-button', 'n_clicks'),
    State('data-store', 'data'),
    prevent_initial_call=True
)
def export_to_csv(n_clicks, data):
    """
    Экспортирует данные таблицы в CSV файл

    Args:
        n_clicks: Количество кликов по кнопке
        data: Данные из data-store

    Returns:
        dict: Данные для скачивания CSV файла
    """
    if n_clicks and data:
        # Преобразуем данные обратно в DataFrame
        df = pd.DataFrame(data)

        # Создаем имя файла с текущей датой
        current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'dnm_data_export_{current_date}.csv'

        # Возвращаем данные для скачивания
        return dcc.send_data_frame(df.to_csv, filename, index=False)

    return None


if __name__ == '__main__':
    app.run(
        debug=settings.app.debug,
        host=settings.app.host,
        port=settings.app.port
    )
