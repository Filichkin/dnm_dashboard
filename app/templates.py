"""
Модуль HTML шаблонов для DNM Dashboard

Минимальный index_string: стартовая тема через data-theme на <html>,
весь дизайн вынесен в assets/dashboard_theme.css (Dash авто-подгрузка).
JetBrains Mono подключается из Google Fonts для числовых колонок.
"""

# HTML шаблон: тема через data-theme, стили — в assets/
DASHBOARD_TEMPLATE = '''<!DOCTYPE html>
<html data-theme="dark">
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>'''


def get_dashboard_template() -> str:
    """
    Возвращает HTML шаблон для дашборда

    Returns:
        str: HTML шаблон с CSS стилями
    """
    return DASHBOARD_TEMPLATE
