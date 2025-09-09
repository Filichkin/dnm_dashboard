"""
Модуль компонентов для DNM Dashboard
Содержит переиспользуемые компоненты интерфейса
"""

from dash import html, dcc, dash_table
from .styles import (
    get_card_style, get_graph_style, get_section_style,
    get_table_styles, CHART_COLORS
)


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
    ], style=styles['container_style'])


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
        html.H2(title),
        dcc.Graph(figure=figure, style=styles['graph'])
    ], style=styles['container'])


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


def get_chart_color(index: int) -> str:
    """
    Возвращает цвет для графика по индексу

    Args:
        index: Индекс цвета

    Returns:
        str: HEX код цвета
    """
    return CHART_COLORS[index % len(CHART_COLORS)]
