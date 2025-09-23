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
            /* Базовые стили для адаптивности */
            .metric-card {
                transition: all 0.3s ease;
            }
            .graph-container {
                transition: all 0.3s ease;
            }

            /* Темная тема для выпадающих списков */
            .Select-control {
                background-color: #3a3a3a !important;
                border-color: #4a4a4a !important;
                color: #ffffff !important;
            }
            .Select-value-label {
                color: #ffffff !important;
            }
            .Select-input {
                color: #ffffff !important;
            }
            .Select-menu-outer {
                background-color: #3a3a3a !important;
                border: 1px solid #4a4a4a !important;
            }
            .Select-option {
                background-color: #3a3a3a !important;
                color: #ffffff !important;
            }
            .Select-option:hover {
                background-color: #4a4a4a !important;
            }
            .Select-option.is-selected {
                background-color: #00d4ff !important;
                color: #1a1a1a !important;
            }
            .Select-option.is-focused {
                background-color: #4a4a4a !important;
            }
            .Select-placeholder {
                color: #b0b0b0 !important;
            }
            .Select-arrow {
                border-top-color: #ffffff !important;
            }

            /* Планшеты и маленькие экраны */
            @media (max-width: 1024px) {
                .metric-card {
                    padding: 15px !important;
                    margin: 8px !important;
                }
                .graph-container {
                    margin: 8px !important;
                    padding: 15px !important;
                }
            }

            /* Мобильные устройства */
            @media (max-width: 768px) {
                .dash-graph {
                    width: 100% !important;
                    height: 300px !important;
                }
                .metric-card {
                    margin: 5px !important;
                    padding: 10px !important;
                }
                .graph-container {
                    margin: 5px !important;
                    padding: 10px !important;
                }
                .main-container {
                    padding: 10px !important;
                }
            }

            /* Очень маленькие экраны */
            @media (max-width: 480px) {
                .dash-graph {
                    height: 250px !important;
                }
                .metric-card {
                    padding: 8px !important;
                    margin: 3px !important;
                }
                .graph-container {
                    margin: 3px !important;
                    padding: 8px !important;
                }
                .main-container {
                    padding: 5px !important;
                }
            }

            /* Очень большие экраны */
            @media (min-width: 1400px) {
                .metric-card {
                    padding: 25px !important;
                    margin: 15px !important;
                }
                .graph-container {
                    margin: 15px !important;
                    padding: 25px !important;
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
