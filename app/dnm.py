"""
DNM Dashboard - основное приложение Dash
"""
import dash
from dash import (
    html, dcc, callback, Input, Output, State, clientside_callback
)
import pandas as pd
from datetime import datetime

# Инициализация логирования
from .logging_config import logger

from .components import (
    create_year_selector,
    create_age_group_selector,
    create_mobis_code_selector,
    create_holding_selector,
    create_region_selector
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
from .templates import get_dashboard_template

# Layout Dash (кнопка экспорта рендерится внутри динамической таблицы,
# поэтому разрешаем колбэки на компоненты вне стартового layout)
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Добавляем CSS для адаптивности
app.index_string = get_dashboard_template()

# Получаем доступные годы и текущий год
available_years = get_available_years()
current_year = get_current_year()

app.layout = html.Div([
    # ---- header: brand + theme toggle ----
    html.Header(className='top', children=[
        html.Div(className='top-inner', children=[
            html.Div(className='brand', children=[
                html.Div(className='mark'),
                html.Div([
                    html.H1(id='dashboard-title'),
                    html.Div(
                        'After-sales performance — repair orders',
                        className='sub'
                    ),
                ]),
            ]),
            html.Div(className='spacer'),
            dcc.RadioItems(
                id='theme', className='seg',
                options=[{'label': 'Light', 'value': 'light'},
                         {'label': 'Dark', 'value': 'dark'}],
                value='dark', inline=True
            ),
        ])
    ]),

    # ---- body ----
    html.Div([
        # Скрытые div для хранения данных
        dcc.Store(id='data-store'),

        # Селекторы и карты в одном блоке
        html.Div([
            # Фильтр-бар (.filters)
            html.Div([
                create_year_selector(available_years, current_year),
                create_age_group_selector(),
                create_mobis_code_selector(),
                create_holding_selector(),
                create_region_selector(),
            ], className='filters'),

            # Отображение дилера / holding / region (.namebar)
            html.Div([
                html.Div(id='dealer-name-container'),
                html.Div(id='holding-name-container'),
                html.Div(id='region-name-container'),
            ], className='namebar', style={'marginBottom': '20px'}),

            # Карты с суммарными показателями
            html.Div(id='metrics-cards')
        ], style={
            'marginBottom': '40px'
        }),

        # Графики
        html.Div(id='charts-container'),

        # Таблица (заголовок и экспорт внутри карточки .tablecard)
        html.Div(id='data-table'),
    ], className='wrap'),

    # hidden sink for the clientside theme toggle
    html.Div(id='_theme_sink', style={'display': 'none'}),
])


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
     Input('region-selector', 'value'),
     Input('theme', 'value')]
)
def update_dashboard(selected_year, age_group, selected_mobis_code,
                     selected_holding, selected_region, theme):
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
    logger.info(
        f'Обновляем дашборд: год={selected_year}, группа={age_group}, '
        f'дилер={selected_mobis_code}, холдинг={selected_holding}, '
        f'регион={selected_region}'
    )

    # Проверяем, что все параметры не None
    params = [selected_year, age_group, selected_mobis_code,
              selected_holding, selected_region]
    if any(param is None for param in params):
        logger.warning(
            'Некоторые параметры не заданы, возвращаем пустые данные'
        )
        return [], [], [], [], [], []

    try:
        df = load_dashboard_data(selected_year, age_group, selected_mobis_code,
                                 selected_holding, selected_region)
        logger.info(f'Данные дашборда загружены: {len(df)} строк')
    except Exception as e:
        logger.error(f'Ошибка при загрузке данных дашборда: {e}')
        return [], [], [], [], [], []

    # Обрабатываем данные
    logger.info('Обрабатываем данные дашборда')
    df = process_dataframe(df)

    # Загружаем данные по региону, если выбран конкретный дилер
    region_df = None
    if selected_mobis_code != 'All':
        logger.info('Загружаем данные по региону')
        region_df = load_region_data(selected_year, age_group,
                                     selected_mobis_code)

    # Создаем графики с региональными данными
    logger.info('Создаем графики')
    charts = create_charts(df, age_group, region_df, theme)

    # Вычисляем метрики
    logger.info('Вычисляем метрики')
    metrics = calculate_metrics(df, age_group)

    # Создаем карты метрик
    metrics_cards = create_metrics_cards(metrics, age_group)

    # Создаем контейнеры графиков
    charts_container = create_charts_container(charts)

    # Создаем отображение названия дилера (включает holding и region)
    dealer_display = create_dealer_display(selected_mobis_code)

    # Создаем отображение названия Holding (только если не выбран дилер)
    holding_display = (create_holding_display(selected_holding)
                       if selected_mobis_code == 'All'
                       else html.Div())

    # Создаем отображение названия Region (только если не выбран дилер)
    region_display = (create_region_display(selected_region)
                      if selected_mobis_code == 'All'
                      else html.Div())

    logger.success('Дашборд успешно обновлен')
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


@callback(
    Output('dashboard-title', 'children'),
    Input('year-selector', 'value')
)
def update_title(selected_year):
    return f'{selected_year} DNM commercial RO data analysis'


# ---- flip data-theme on <html> so the CSS variables switch ----
clientside_callback(
    "function(t){"
    "document.documentElement.setAttribute('data-theme', t);"
    "return '';}",
    Output('_theme_sink', 'children'),
    Input('theme', 'value')
)


if __name__ == '__main__':
    logger.info(
        f'Запускаем DNM Dashboard на {settings.app.host}:{settings.app.port}'
    )
    logger.info(f'Режим отладки: {settings.app.debug}')

    app.run(
        debug=settings.app.debug,
        host=settings.app.host,
        port=settings.app.port,
        use_reloader=True
    )
