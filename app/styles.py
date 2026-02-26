"""
Модуль стилей для DNM Dashboard
Содержит все повторяющиеся стили для компонентов интерфейса
"""

# Цветовая палитра для темной темы
COLORS = {
    'primary': '#00d4ff',  # Яркий голубой
    'secondary': '#1a1a1a',  # Очень темный серый
    'background': '#2d2d2d',  # Темно-серый фон
    'card_background': '#3a3a3a',  # Фон карточек
    'text_primary': '#ffffff',  # Белый текст
    'text_secondary': '#00d4ff',  # Голубой текст
    'text_muted': '#b0b0b0',  # Приглушенный текст
    'success': '#00ff88',  # Зеленый для успеха
    'warning': '#ff6b35',  # Оранжевый для предупреждений
    'danger': '#ff4757',  # Красный для ошибок
    'border': '#4a4a4a',  # Границы
}

# Стили для карточек с метриками
CARD_STYLES = {
    'container': {
        'backgroundColor': COLORS['card_background'],
        'padding': '20px',
        'borderRadius': '12px',
        'textAlign': 'center',
        'margin': '10px',
        'flex': '1',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'minHeight': '120px',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center',
        'alignItems': 'center',
        'border': f'1px solid {COLORS["border"]}',
        'className': 'metric-card',
        'transition': 'all 0.3s ease'
    },
    'title': {
        'margin': '0',
        'color': COLORS['text_muted'],
        'fontSize': '1.1em',
        'marginBottom': '10px',
        'fontWeight': '500'
    },
    'value': {
        'margin': '0',
        'color': COLORS['text_primary'],
        'fontSize': '2.5em',
        'fontWeight': 'bold'
    }
}

# Стили для графиков
GRAPH_STYLES = {
    'container': {
        'flex': '1',
        'margin': '10px',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '12px',
        'padding': '20px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)',
        'border': f'1px solid {COLORS["border"]}',
        'className': 'graph-container'
    },
    'graph': {
        'height': '350px',
        'width': '100%'
    }
}

# Стили для секций
SECTION_STYLES = {
    'cards_row': {
        'display': 'flex',
        'marginBottom': '40px',
        'flexWrap': 'nowrap',
        'justifyContent': 'space-between',
        'gap': '10px',
        'alignItems': 'stretch'
    },
    'graphs_row': {
        'display': 'flex',
        'marginBottom': '40px',
        'flexWrap': 'nowrap',
        'justifyContent': 'space-between',
        'gap': '10px',
        'alignItems': 'stretch'
    }
}

# Стили для таблицы
TABLE_STYLES = {
    'table': {
        'overflowX': 'auto',
        'backgroundColor': COLORS['card_background'],
        'borderRadius': '12px',
        'border': f'1px solid {COLORS["border"]}',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.3)'
    },
    'cell': {
        'textAlign': 'center',
        'minWidth': '40px',
        'maxWidth': '90px',
        'whiteSpace': 'normal',
        'padding': '8px',
        'fontSize': '11px',
        'backgroundColor': COLORS['card_background'],
        'color': COLORS['text_primary'],
        'border': f'1px solid {COLORS["border"]}'
    },
    'header': {
        'whiteSpace': 'normal',
        'height': 'auto',
        'lineHeight': '14px',
        'padding': '8px',
        'overflow': 'visible',
        'textOverflow': 'clip',
        'maxWidth': 'none',
        'wordBreak': 'break-word',
        'overflowWrap': 'anywhere',
        'textAlign': 'center',
        'backgroundColor': COLORS['secondary'],
        'color': COLORS['text_primary'],
        'fontWeight': 'bold',
        'border': f'1px solid {COLORS["border"]}'
    },
    'data_conditional': [
        {
            'if': {'column_type': 'numeric'},
            'textAlign': 'center',
        },
    ]
}

# Цвета для графиков (темные тона для лучшей читаемости)
CHART_COLORS = [
    '#3498db',  # Ярко-синий
    '#27ae60',  # Темно-зеленый
    '#e67e22',  # Темно-оранжевый
    '#e74c3c',  # Темно-красный
    '#8e44ad',  # Темно-фиолетовый
    '#f39c12',  # Темно-желтый
    '#c0392b',  # Темно-бордовый
    '#16a085',  # Темно-бирюзовый
    '#9b59b6',  # Темно-пурпурный
    '#3498db',  # Темно-голубой
]

# Адаптивные стили для основного контейнера
RESPONSIVE_STYLES = {
    'main_container': {
        'padding': '20px',
        'maxWidth': '100%',
        'margin': '0 auto',
        'backgroundColor': COLORS['background'],
        'minHeight': '100vh',
        'fontFamily': 'Arial, sans-serif',
        'className': 'main-container'
    },
    'title': {
        'textAlign': 'left',
        'color': COLORS['text_primary'],
        'marginBottom': '30px',
        'fontSize': '2.5em',
        'fontWeight': 'bold'
    },
    'section_title': {
        'textAlign': 'left',
        'color': COLORS['text_primary'],
        'marginBottom': '20px',
        'fontSize': '1.8em',
        'fontWeight': 'bold'
    }
}


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


def get_responsive_styles() -> dict:
    """
    Возвращает адаптивные стили для основного контейнера

    Returns:
        dict: Адаптивные стили
    """
    return RESPONSIVE_STYLES
