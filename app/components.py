from dash import html, dcc, dash_table

from .styles import (
    get_card_style, get_graph_style, get_section_style,
    get_table_styles, CHART_COLORS
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


def create_data_table(columns: list, data: list) -> dash_table.DataTable:
    """
    Создает таблицу данных

    Args:
        columns: Список колонок
        data: Данные для таблицы

    Returns:
        dash_table.DataTable: Компонент таблицы
    """
    table_styles = get_table_styles()

    return dash_table.DataTable(
        columns=columns,
        data=data,
        style_table=table_styles['table'],
        style_cell=table_styles['cell'],
        style_header=table_styles['header'],
        style_data_conditional=table_styles['data_conditional'],
    )


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
