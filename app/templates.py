"""
Модуль HTML шаблонов для DNM Dashboard
Содержит HTML шаблоны и CSS стили для адаптивности
"""

# HTML шаблон с CSS для адаптивности
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            @media (max-width: 768px) {
                .dash-graph {
                    width: 100% !important;
                    height: 300px !important;
                }
                .metric-card {
                    min-width: 150px !important;
                    margin: 10px !important;
                }
                .graph-container {
                    min-width: 100% !important;
                    margin: 10px 0 !important;
                }
                .main-container {
                    padding: 10px !important;
                }
            }
            @media (max-width: 480px) {
                .dash-graph {
                    height: 250px !important;
                }
                .metric-card {
                    min-width: 120px !important;
                    padding: 15px !important;
                }
                .main-container {
                    padding: 5px !important;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


def get_dashboard_template() -> str:
    """
    Возвращает HTML шаблон для дашборда

    Returns:
        str: HTML шаблон с CSS стилями
    """
    return DASHBOARD_TEMPLATE
