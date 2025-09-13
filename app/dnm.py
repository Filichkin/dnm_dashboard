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
    create_export_button
)
from .functions import (
    process_dataframe,
    create_charts,
    create_table,
    calculate_metrics,
    get_available_years,
    get_current_year,
    load_dashboard_data,
    create_metrics_cards,
    create_charts_container,
    create_dealer_display,
    create_holding_display
)
from .constants import get_mobis_code_options_by_holding
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
    html.H1('DNM RO DATA by models', style=responsive_styles['title']),

    # Скрытые div для хранения данных
    dcc.Store(id='data-store'),

    # Селекторы и карты в одном блоке
    html.Div([
        # Селекторы года, возрастных групп, кода дилера, holding
        # и отображение дилера и holding
        html.Div([
            create_year_selector(available_years, current_year),
            create_age_group_selector(),
            create_mobis_code_selector(),
            create_holding_selector(),
            html.Div(id='dealer-name-container'),
            html.Div(id='holding-name-container')
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
     Output('data-table', 'children'),
     Output('dealer-name-container', 'children'),
     Output('holding-name-container', 'children')],
    [Input('year-selector', 'value'),
     Input('age-group-selector', 'value'),
     Input('mobis-code-selector', 'value'),
     Input('holding-selector', 'value')]
)
def update_dashboard(selected_year, age_group, selected_mobis_code,
                     selected_holding):
    """
    Обновляет дашборд при изменении года, возрастной группы,
    кода дилера или holding.

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа
        selected_mobis_code: Выбранный код дилера
        selected_holding: Выбранный holding

    Returns:
        tuple: Данные, карты метрик, графики, таблица, отображение дилера,
               отображение holding
    """
    # Загружаем данные
    df = load_dashboard_data(selected_year, age_group, selected_mobis_code,
                             selected_holding)

    # Обрабатываем данные
    df = process_dataframe(df)

    # Создаем графики
    charts = create_charts(df, age_group)

    # Создаем таблицу
    table = create_table(df, age_group)

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

    return (df.to_dict('records'), metrics_cards, charts_container,
            table, dealer_display, holding_display)


@callback(
    [Output('mobis-code-selector', 'options'),
     Output('mobis-code-selector', 'value')],
    Input('holding-selector', 'value'),
    prevent_initial_call=False
)
def update_mobis_code_options(selected_holding):
    """
    Обновляет опции Mobis Code при изменении выбранного Holding.

    Args:
        selected_holding: Выбранный holding

    Returns:
        tuple: (новые опции, новое значение)
    """
    # Получаем отфильтрованные опции
    new_options = get_mobis_code_options_by_holding(selected_holding)

    # Если текущее значение Mobis Code не входит в новые опции,
    # сбрасываем на 'All'
    current_value = 'All'  # По умолчанию всегда 'All'

    return new_options, current_value


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
