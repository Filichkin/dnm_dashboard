"""
Модуль стилей для DNM Dashboard
Содержит все повторяющиеся стили для компонентов интерфейса
"""

# Цветовая палитра
COLORS = {
    'primary': '#3498db',
    'secondary': '#2c3e50',
    'background': '#ecf0f1',
    'text_primary': '#2c3e50',
    'text_secondary': '#3498db',
}

# Стили для карточек с метриками
CARD_STYLES = {
    'container': {
        'backgroundColor': COLORS['background'],
        'padding': '25px',
        'borderRadius': '10px',
        'textAlign': 'center',
        'margin': '10px',
        'flex': '1',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'minHeight': '120px',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center'
    },
    'title': {
        'margin': '0',
        'color': COLORS['text_primary'],
        'fontSize': '1.3em',
        'marginBottom': '15px'
    },
    'value': {
        'margin': '0',
        'color': COLORS['text_secondary'],
        'fontSize': '2.2em',
        'fontWeight': 'normal'
    }
}

# Стили для графиков
GRAPH_STYLES = {
    'container': {
        'flex': '1',
        'margin': '10px'
    },
    'graph': {
        'height': '350px'
    }
}

# Стили для секций
SECTION_STYLES = {
    'cards_row': {
        'display': 'flex',
        'marginBottom': '30px'
    },
    'graphs_row': {
        'display': 'flex'
    }
}

# Стили для таблицы
TABLE_STYLES = {
    'table': {
        'overflowX': 'auto'
    },
    'cell': {
        'textAlign': 'center',
        'minWidth': '40px',
        'maxWidth': '90px',
        'whiteSpace': 'normal',
        'padding': '2px',
        'fontSize': '11px',
    },
    'header': {
        'whiteSpace': 'normal',
        'height': 'auto',
        'lineHeight': '14px',
        'padding': '2px',
        'overflow': 'visible',
        'textOverflow': 'clip',
        'maxWidth': 'none',
        'wordBreak': 'break-word',
        'overflowWrap': 'anywhere',
        'textAlign': 'center',
    },
    'data_conditional': [
        {
            'if': {'column_type': 'numeric'},
            'textAlign': 'center',
        },
    ]
}

# Цвета для графиков
CHART_COLORS = [
    '#90a4ae',  # blue gray (calm)
    '#a5d6a7',  # soft green
    '#d7ccc8',  # soft brown/gray
    '#b0bec5',  # light blue gray
    '#cfd8dc',  # very light blue gray
]


def get_card_style(title: str, value: str) -> dict:
    """
    Возвращает стили для карточки с метрикой

    Args:
        title: Заголовок карточки
        value: Значение метрики

    Returns:
        dict: Стили для компонента карточки
    """
    return {
        'title': title,
        'value': value,
        'title_style': CARD_STYLES['title'],
        'value_style': CARD_STYLES['value'],
        'container_style': CARD_STYLES['container']
    }


def get_graph_style(height: int = 350) -> dict:
    """
    Возвращает стили для графика

    Args:
        height: Высота графика в пикселях

    Returns:
        dict: Стили для графика
    """
    return {
        'container': GRAPH_STYLES['container'],
        'graph': {**GRAPH_STYLES['graph'], 'height': f'{height}px'}
    }


def get_section_style(section_type: str) -> dict:
    """
    Возвращает стили для секции

    Args:
        section_type: Тип секции ('cards_row' или 'graphs_row')

    Returns:
        dict: Стили для секции
    """
    return SECTION_STYLES.get(section_type, {})


def get_table_styles() -> dict:
    """
    Возвращает все стили для таблицы

    Returns:
        dict: Стили для таблицы
    """
    return TABLE_STYLES
