from dash import html, dcc

from .styles import (
    get_card_style, get_graph_style, get_section_style,
    CHART_COLORS
)
from .constants import MOBIS_CODE_OPTIONS, HOLDING_OPTIONS, REGION_OPTIONS


def create_metric_card(title: str, value: str) -> html.Div:
    """
    Создает карточку с метрикой

    Args:
        title: Заголовок карточки
        value: Значение метрики

    Returns:
        html.Div: Компонент карточки
    """
    styles = get_card_style(title, value)

    return html.Div([
        html.H3(title, style=styles['title_style']),
        html.H2(value, style=styles['value_style'])
    ], style=styles['container_style'],
       className=styles['container_style'].get('className', ''))


def create_graph_container(title: str, figure, height: int = 350) -> html.Div:
    """
    Создает контейнер для графика

    Args:
        title: Заголовок графика
        figure: Объект графика Plotly
        height: Высота графика в пикселях

    Returns:
        html.Div: Компонент контейнера графика
    """
    styles = get_graph_style(height)

    return html.Div([
        html.H2(title, style={
            'color': '#ffffff',
            'marginBottom': '15px',
            'fontSize': '1.5em',
            'fontWeight': 'bold'
        }),
        dcc.Graph(figure=figure, style=styles['graph'])
    ], style=styles['container'],
       className=styles['container'].get('className', ''))


def create_cards_row(cards: list) -> html.Div:
    """
    Создает ряд карточек с метриками

    Args:
        cards: Список карточек

    Returns:
        html.Div: Компонент ряда карточек
    """
    return html.Div(cards, style=get_section_style('cards_row'))


def create_graphs_row(graphs: list) -> html.Div:
    """
    Создает ряд графиков

    Args:
        graphs: Список контейнеров графиков

    Returns:
        html.Div: Компонент ряда графиков
    """
    return html.Div(graphs, style=get_section_style('graphs_row'))


def create_data_table(columns: list, data: list,
                      show_all_columns: bool = False) -> html.Div:
    """
    Создает таблицу данных с зеброй, фильтрацией и скрытием колонок

    Args:
        columns: Список колонок
        data: Данные для таблицы
        show_all_columns: Показывать ли все колонки

    Returns:
        html.Div: Компонент таблицы
    """
    print("=== СОЗДАНИЕ DATA_TABLE ===")
    print(f"Количество колонок: {len(columns)}")
    print(f"Количество строк данных: {len(data)}")
    if len(data) > 0:
        print(f"Первые 3 записи: {data[:3] if len(data) >= 3 else data}")
        col_names = [col.get('name', col.get('id', 'unknown'))
                     for col in columns[:5]]
        print(f"Колонки: {col_names}")
    # table_styles = get_table_styles()  # Не используется в HTML таблице

    # Находим индекс колонки PPR для скрытия колонок после неё
    ppr_index = None
    for i, col in enumerate(columns):
        if col.get('name') == 'PPR':
            ppr_index = i
            break

    # Создаем колонки с возможностью скрытия
    table_columns = []
    for i, col in enumerate(columns):
        column_config = {
            'name': col['name'],
            'id': col['id'],
            'type': col.get('type', 'text'),
            'format': col.get('format'),
            'selectable': True,
            'hideable': True
        }

        # Скрываем колонки после PPR
        if ppr_index is not None and i > ppr_index:
            column_config['hidden'] = True

        table_columns.append(column_config)

    # Стили для зебры (чередующиеся строки)
    zebra_styles = []
    for i in range(len(data)):
        if i % 2 == 0:
            zebra_styles.append({
                'if': {'row_index': i},
                'backgroundColor': '#3a3a3a',  # Основной цвет
                'color': '#ffffff'
            })
        else:
            zebra_styles.append({
                'if': {'row_index': i},
                'backgroundColor': '#4a4a4a',  # Альтернативный цвет
                'color': '#ffffff'
            })

    # Объединяем стили зебры с существующими (не используется в HTML таблице)
    # all_conditional_styles = (table_styles['data_conditional'] +
    #                          zebra_styles)

    print(f"Создаем DataTable с {len(data)} строками и "
          f"{len(table_columns)} колонками")

    # Принудительное пересоздание таблицы через изменение структуры
    import time
    import random

    # Создаем уникальный ключ для принудительного обновления
    unique_key = f"table-{int(time.time())}-{random.randint(1000, 9999)}"
    print(f"Уникальный ключ таблицы: {unique_key}")

    # Создаем HTML таблицу вместо DataTable для гарантированного обновления
    print(f"Создаем HTML таблицу с {len(data)} строками")

    # Логика выбора колонок для отображения
    if show_all_columns:
        # Показываем все колонки
        visible_columns = table_columns
        print("Показываем ВСЕ колонки")
    else:
        # Находим индекс колонки PPR для скрытия колонок после неё
        ppr_index = None
        for i, col in enumerate(table_columns):
            if col.get('name') == 'PPR':
                ppr_index = i
                break

        # Показываем все колонки до PPR включительно
        if ppr_index is not None:
            visible_columns = table_columns[:ppr_index + 1]
            print(f"Скрываем колонки после PPR (индекс {ppr_index})")
        else:
            visible_columns = table_columns
            print("PPR колонка не найдена, показываем все колонки")

    print(f"Показываем {len(visible_columns)} колонок из {len(table_columns)}")

    # Создаем заголовок таблицы
    header_style = {'padding': '8px', 'borderBottom': '2px solid #4a4a4a',
                    'backgroundColor': '#2a2a2a', 'color': '#ffffff',
                    'textAlign': 'center'}  # Центрируем заголовки
    header_row = html.Tr([
        html.Th(col['name'], style=header_style)
        for col in visible_columns
    ])

    # Создаем строки данных (первые 20 для демонстрации)
    data_rows = []
    for i, row in enumerate(data[:20]):
        cells = []
        for col in visible_columns:
            value = row.get(col['id'], '')
            col_id = col['id']

            # Форматируем числа с центрированием
            if isinstance(value, (int, float)) and col_id != 'model':
                if col_id == 'aver_labor_hours_per_vhc':
                    value = f"{value:.1f}"  # Убираем символ часов
                elif col_id in ['ro_ratio_of_uio_10y', 'ro_ratio_of_uio_5y']:
                    value = f"{value:.1f}%"  # Проценты
                elif col_id in ['pct_age_0_3', 'pct_age_4_5', 'pct_age_6_10']:
                    value = f"{value:.1f}%"  # Проценты возрастных групп
                else:
                    value = f"{value:,.0f}"  # Обычные числа с разделителями

            # Определяем выравнивание - все по центру
            text_align = 'center'
            cells.append(html.Td(str(value), style={
                'padding': '6px 8px',
                'borderBottom': '1px solid #4a4a4a',
                'backgroundColor': '#3a3a3a' if i % 2 == 0 else '#4a4a4a',
                'color': '#ffffff',
                'textAlign': text_align  # Центрируем числа, левое для модели
            }))
        data_rows.append(html.Tr(cells))

    # Создаем таблицу без кнопки
    result = html.Div([
        html.Table([
            html.Thead(header_row),
            html.Tbody(data_rows)
        ], style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'backgroundColor': '#3a3a3a',
            'color': '#ffffff',
            'fontSize': '12px'
        })
    ], key=unique_key)

    print("=== КОНЕЦ СОЗДАНИЯ DATA_TABLE ===")
    return result


def create_year_selector(available_years: list, current_year: int) -> html.Div:
    """
    Создает выпадающий список для выбора года

    Args:
        available_years: Список доступных годов
        current_year: Текущий выбранный год

    Returns:
        html.Div: Компонент селектора года
    """
    options = [{'label': str(year), 'value': year} for year in available_years]

    return html.Div([
        html.Label('Select Year:',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.2em',
                       'color': '#ffffff'
                   }),
        dcc.Dropdown(
            id='year-selector',
            options=options,
            value=current_year,
            clearable=False,
            style={
                'width': '200px',
                'display': 'inline-block',
                'font-size': '1.1em',
                'backgroundColor': '#3a3a3a',
                'color': '#ffffff'
            },
            optionHeight=40,
            searchable=False
        )
    ], style={
        'margin': '0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def get_chart_color(index: int) -> str:
    """
    Возвращает цвет для графика по индексу

    Args:
        index: Индекс цвета

    Returns:
        str: HEX код цвета
    """
    return CHART_COLORS[index % len(CHART_COLORS)]


def create_age_group_selector() -> html.Div:
    """
    Создает выпадающий список для выбора возрастных групп

    Returns:
        html.Div: Компонент селектора возрастных групп
    """
    options = [
        {'label': '0-10Y', 'value': '0-10Y'},
        {'label': '0-5Y', 'value': '0-5Y'}
    ]

    return html.Div([
        html.Label('Age Group:',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.2em',
                       'color': '#ffffff'
                   }),
        dcc.Dropdown(
            id='age-group-selector',
            options=options,
            value='0-10Y',
            clearable=False,
            style={
                'width': '150px',
                'display': 'inline-block',
                'font-size': '1.1em',
                'backgroundColor': '#3a3a3a',
                'color': '#ffffff'
            },
            optionHeight=40,
            searchable=False
        )
    ], style={
        'margin': '0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def create_mobis_code_selector() -> html.Div:
    """
    Создает выпадающий список для выбора кода дилера (Mobis Code)

    Returns:
        html.Div: Компонент селектора кода дилера
    """
    return html.Div([
        html.Label('Mobis Code:',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.2em',
                       'color': '#ffffff'
                   }),
        dcc.Dropdown(
            id='mobis-code-selector',
            options=MOBIS_CODE_OPTIONS,
            value='All',
            clearable=False,
            style={
                'width': '200px',
                'display': 'inline-block',
                'font-size': '1.1em',
                'backgroundColor': '#3a3a3a',
                'color': '#ffffff'
            },
            optionHeight=40,
            searchable=False
        )
    ], style={
        'margin': '0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def create_holding_selector() -> html.Div:
    """
    Создает выпадающий список для выбора Holding

    Returns:
        html.Div: Компонент селектора Holding
    """
    return html.Div([
        html.Label('Holding:',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.2em',
                       'color': '#ffffff'
                   }),
        dcc.Dropdown(
            id='holding-selector',
            options=HOLDING_OPTIONS,
            value='All',
            clearable=False,
            style={
                'width': '200px',
                'display': 'inline-block',
                'font-size': '1.1em',
                'backgroundColor': '#3a3a3a',
                'color': '#ffffff'
            },
            optionHeight=40,
            searchable=False
        )
    ], style={
        'margin': '0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def create_region_selector() -> html.Div:
    """
    Создает выпадающий список для выбора Region

    Returns:
        html.Div: Компонент селектора Region
    """
    return html.Div([
        html.Label('Region:',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.2em',
                       'color': '#ffffff'
                   }),
        dcc.Dropdown(
            id='region-selector',
            options=REGION_OPTIONS,
            value='All',
            clearable=False,
            style={
                'width': '200px',
                'display': 'inline-block',
                'font-size': '1.1em',
                'backgroundColor': '#3a3a3a',
                'color': '#ffffff'
            },
            optionHeight=40,
            searchable=False
        )
    ], style={
        'margin': '0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def create_dealer_name_display() -> html.Div:
    """
    Создает компонент для отображения названия дилера

    Returns:
        html.Div: Компонент отображения названия дилера
    """
    return html.Div([
        html.Label('Dealer Name: ',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.4em',
                       'color': '#ffffff'
                   }),
        html.Span(id='dealer-name-display',
                  style={
                      'font-size': '1.3em',
                      'color': '#00d4ff',
                      'font-weight': 'normal'
                  })
    ], style={
        'margin': '0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def create_holding_name_display() -> html.Div:
    """
    Создает компонент для отображения названия Holding

    Returns:
        html.Div: Компонент отображения названия Holding
    """
    return html.Div([
        html.Label('Holding Name: ',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.4em',
                       'color': '#ffffff'
                   }),
        html.Span(id='holding-name-display',
                  style={
                      'font-size': '1.3em',
                      'color': '#00d4ff',
                      'font-weight': 'normal'
                  })
    ], style={
        'margin': '0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def create_region_name_display() -> html.Div:
    """
    Создает компонент для отображения названия Region

    Returns:
        html.Div: Компонент отображения названия Region
    """
    return html.Div([
        html.Label('Region Name: ',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.4em',
                       'color': '#ffffff'
                   }),
        html.Span(id='region-name-display',
                  style={
                      'font-size': '1.3em',
                      'color': '#00d4ff',
                      'font-weight': 'normal'
                  })
    ], style={
        'margin': '0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def create_model_filter() -> html.Div:
    """
    Создает фильтр по модели для таблицы

    Returns:
        html.Div: Компонент фильтра по модели
    """
    return html.Div([
        html.Label('Filter by Model:',
                   style={
                       'font-weight': 'bold',
                       'margin-right': '15px',
                       'font-size': '1.2em',
                       'color': '#ffffff'
                   }),
        dcc.Dropdown(
            id='model-filter',
            placeholder='Select model to filter...',
            clearable=True,
            searchable=True,
            style={
                'width': '300px',
                'display': 'inline-block',
                'font-size': '1.1em',
                'backgroundColor': '#3a3a3a',
                'color': '#ffffff'
            },
            optionHeight=40
        )
    ], style={
        'margin': '0 0 20px 0',
        'display': 'flex',
        'align-items': 'center',
        'justify-content': 'flex-start',
        'padding': '10px 20px',
        'backgroundColor': '#3a3a3a',
        'borderRadius': '12px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': '1px solid #4a4a4a'
    })


def create_export_button() -> html.Div:
    """
    Создает кнопку для экспорта данных в CSV

    Returns:
        html.Div: Компонент кнопки экспорта
    """
    return html.Div([
        html.Button(
            'Export to CSV',
            id='export-csv-button',
            n_clicks=0,
            style={
                'backgroundColor': '#00d4ff',
                'color': '#1a1a1a',
                'border': 'none',
                'padding': '12px 24px',
                'borderRadius': '8px',
                'cursor': 'pointer',
                'fontSize': '14px',
                'fontWeight': 'bold',
                'margin': '10px 0',
                'boxShadow': '0 4px 12px rgba(0,212,255,0.3)',
                'transition': 'all 0.3s ease'
            }
        ),
        dcc.Download(id='download-csv')
    ], style={
        'textAlign': 'left',
        'marginBottom': '20px'
    })
