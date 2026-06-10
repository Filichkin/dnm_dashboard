from dash import html, dcc

from .styles import get_graph_style, get_section_style, CHART_COLORS
from .plotly_templates import CONFIG
from .constants import MOBIS_CODE_OPTIONS, HOLDING_OPTIONS, REGION_OPTIONS


# ----------------------------------------------------------------------
# FILTER SELECTORS
# ----------------------------------------------------------------------
def _select_field(label, dropdown_id, options, value,
                  searchable=False, clearable=False,
                  placeholder=None) -> html.Div:
    """Single labelled dropdown rendered as a design-system .field."""
    return html.Div([
        html.Label(label),
        dcc.Dropdown(
            id=dropdown_id,
            options=options,
            value=value,
            clearable=clearable,
            searchable=searchable,
            placeholder=placeholder,
            optionHeight=40,
            className='dash-dropdown',
        ),
    ], className='field')


def create_year_selector(available_years: list,
                         current_year: int) -> html.Div:
    """Создает выпадающий список для выбора года."""
    options = [{'label': str(year), 'value': year}
               for year in available_years]
    return _select_field('Select Year', 'year-selector', options,
                         current_year)


def create_age_group_selector() -> html.Div:
    """Создает выпадающий список для выбора возрастных групп."""
    options = [
        {'label': '0-10Y', 'value': '0-10Y'},
        {'label': '0-5Y', 'value': '0-5Y'},
    ]
    return _select_field('Age Group', 'age-group-selector', options,
                         '0-10Y')


def create_mobis_code_selector() -> html.Div:
    """Создает выпадающий список для выбора кода дилера (Mobis Code)."""
    return _select_field('Mobis Code', 'mobis-code-selector',
                         MOBIS_CODE_OPTIONS, 'All', searchable=True)


def create_holding_selector() -> html.Div:
    """Создает выпадающий список для выбора Holding."""
    return _select_field('Holding', 'holding-selector',
                         HOLDING_OPTIONS, 'All')


def create_region_selector() -> html.Div:
    """Создает выпадающий список для выбора Region."""
    return _select_field('Region', 'region-selector',
                         REGION_OPTIONS, 'All')


# ----------------------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------------------
def create_metric_card(title: str, value: str, unit: str = None,
                       hero: bool = False) -> html.Div:
    """Создает KPI-карточку (.kpi / .kpi.hero для акцентной)."""
    children = [
        html.Div([html.Span(title, className='k-lbl')],
                 className='k-top'),
        html.Div(value, className='k-val num'),
    ]
    if unit:
        children.append(html.Div(unit, className='k-unit'))
    return html.Div(children, className='kpi hero' if hero else 'kpi')


def create_cards_row(cards: list) -> html.Div:
    """Создает grid KPI-карточек (.kpis)."""
    return html.Div(cards, className='kpis')


# ----------------------------------------------------------------------
# CHART CONTAINERS  (restyled fully in a later step)
# ----------------------------------------------------------------------
def create_graph_container(title: str, figure, height: int = 350) -> html.Div:
    """Создает контейнер для графика."""
    styles = get_graph_style(height)
    return html.Div([
        html.H2(title, style={
            'color': 'var(--text)',
            'marginBottom': '15px',
            'fontSize': '1.15em',
            'fontWeight': 'bold',
        }),
        dcc.Graph(figure=figure, style=styles['graph']),
    ], style=styles['container'],
       className=styles['container'].get('className', ''))


def create_graphs_row(graphs: list) -> html.Div:
    """Создает ряд графиков."""
    return html.Div(graphs, style=get_section_style('graphs_row'))


def create_chart_card(figure, title: str, subtitle: str, tag: str,
                      tall: bool = False) -> html.Div:
    """Карточка графика дизайн-системы (.card)."""
    return html.Div([
        html.Div([
            html.Div([
                html.Div(title, className='c-title'),
                html.Div(subtitle, className='c-sub'),
            ]),
            html.Span(tag, className='c-tag'),
        ], className='c-head'),
        dcc.Graph(
            figure=figure,
            config=CONFIG,
            className='plot tall' if tall else 'plot',
            style={'height': '300px' if tall else '248px'},
        ),
    ], className='card')


def get_chart_color(index: int) -> str:
    """Возвращает цвет для графика по индексу."""
    return CHART_COLORS[index % len(CHART_COLORS)]


# ----------------------------------------------------------------------
# DATA TABLE  (restyled fully in a later step)
# ----------------------------------------------------------------------
def create_data_table(columns: list, data: list,
                      show_all_columns: bool = False,
                      title: str = 'Items data by models') -> html.Div:
    """Создает HTML-таблицу данных со скрытием колонок после PPR."""
    # Находим индекс колонки PPR для скрытия колонок после неё
    ppr_index = None
    for i, col in enumerate(columns):
        if col.get('name') == 'PPR':
            ppr_index = i
            break

    table_columns = []
    for i, col in enumerate(columns):
        column_config = {
            'name': col['name'],
            'id': col['id'],
            'type': col.get('type', 'text'),
            'format': col.get('format'),
            'selectable': True,
            'hideable': True,
        }
        if ppr_index is not None and i > ppr_index:
            column_config['hidden'] = True
        table_columns.append(column_config)

    # Логика выбора колонок для отображения
    if show_all_columns:
        visible_columns = table_columns
    else:
        ppr_index = None
        for i, col in enumerate(table_columns):
            if col.get('name') == 'PPR':
                ppr_index = i
                break
        if ppr_index is not None:
            visible_columns = table_columns[:ppr_index + 1]
        else:
            visible_columns = table_columns

    # Заголовок таблицы
    header_row = html.Tr([
        html.Th(col['name']) for col in visible_columns
    ])

    # Строки данных
    data_rows = []
    for row in data:
        cells = []
        for col in visible_columns:
            value = row.get(col['id'], '')
            col_id = col['id']
            if col_id == 'model':
                cells.append(html.Td(html.Span([
                    html.Span(className='mk'),
                    html.Span(str(value)),
                ], className='model-chip')))
                continue
            if isinstance(value, (int, float)):
                if col_id == 'aver_labor_hours_per_vhc':
                    value = f'{value:.1f}'
                elif col_id in ['ro_ratio_of_uio_10y',
                                'ro_ratio_of_uio_5y']:
                    value = f'{value:.1f}%'
                elif col_id in ['pct_age_0_3', 'pct_age_4_5',
                                'pct_age_6_10']:
                    value = f'{value:.1f}%'
                else:
                    value = f'{value:,.0f}'
            cells.append(html.Td(html.Span(str(value), className='num')))
        data_rows.append(html.Tr(cells))

    return html.Div([
        html.Div([
            html.Div(title, className='c-title'),
            create_export_button(),
        ], className='t-head'),
        html.Table([
            html.Thead(header_row),
            html.Tbody(data_rows),
        ]),
    ], className='tablecard')


# ----------------------------------------------------------------------
# NAME DISPLAYS (dealer / holding / region)
# ----------------------------------------------------------------------
def _name_item(label: str) -> html.Div:
    """Один элемент .nameitem: подпись + значение (children[1])."""
    return html.Div([
        html.Span(label, className='nm-lbl'),
        html.Span(className='nm-val'),
    ], className='nameitem')


def create_dealer_name_display() -> html.Div:
    """Компонент для отображения названия дилера."""
    return _name_item('Dealer')


def create_holding_name_display() -> html.Div:
    """Компонент для отображения названия Holding."""
    return _name_item('Holding')


def create_region_name_display() -> html.Div:
    """Компонент для отображения названия Region."""
    return _name_item('Region')


# ----------------------------------------------------------------------
# EXPORT
# ----------------------------------------------------------------------
def create_export_button() -> html.Div:
    """Создает кнопку для экспорта данных в CSV."""
    return html.Div([
        html.Button(
            'Export to CSV',
            id='export-csv-button',
            n_clicks=0,
            className='btn primary',
        ),
        dcc.Download(id='download-csv'),
    ], style={'marginLeft': 'auto'})
