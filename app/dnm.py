import dash
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime

from .components import (
    create_metric_card,
    create_graph_container,
    create_cards_row,
    create_graphs_row,
    create_data_table,
    create_year_selector,
    create_age_group_selector,
    get_chart_color,
    create_export_button
)
from .styles import get_responsive_styles
from .templates import get_dashboard_template
from config import settings
from database.queries import get_dnm_data


def process_dataframe(df):
    """
    Обрабатывает DataFrame для корректного отображения

    Args:
        df: Исходный DataFrame

    Returns:
        pd.DataFrame: Обработанный DataFrame
    """
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Unnamed: 1' in df.columns:
        df = df.drop(columns=['Unnamed: 1'])

    if 'Model \\ Age' in df.columns:
        df = df.rename(columns={'Model \\ Age': 'model'})

    if 'Model' in df.columns:
        df = df.rename(columns={'Model': 'model'})

    # Создаем агрегированные колонки для 0-10Y
    if 'age_0_3' not in df.columns:
        cols_0_3 = [f'age_{y}' for y in range(0, 4)
                    if f'age_{y}' in df.columns]
        if cols_0_3:
            df['age_0_3'] = df[cols_0_3].sum(axis=1)
    if 'age_4_5' not in df.columns:
        cols_4_5 = [f'age_{y}' for y in range(4, 6)
                    if f'age_{y}' in df.columns]
        if cols_4_5:
            df['age_4_5'] = df[cols_4_5].sum(axis=1)
    if 'age_6_10' not in df.columns:
        cols_6_10 = [f'age_{y}' for y in range(6, 11)
                     if f'age_{y}' in df.columns]
        if cols_6_10:
            df['age_6_10'] = df[cols_6_10].sum(axis=1)

    # Создаем агрегированные колонки для 0-5Y (используем age_0_3 и age_4_5)
    if 'age_0_3' not in df.columns:
        cols_0_3 = [f'age_{y}' for y in range(0, 4)
                    if f'age_{y}' in df.columns]
        if cols_0_3:
            df['age_0_3'] = df[cols_0_3].sum(axis=1)
    if 'age_4_5' not in df.columns:
        cols_4_5 = [f'age_{y}' for y in range(4, 6)
                    if f'age_{y}' in df.columns]
        if cols_4_5:
            df['age_4_5'] = df[cols_4_5].sum(axis=1)

    return df


def create_charts(df, age_group='0-10Y'):
    """
    Создает все графики на основе данных

    Args:
        df: DataFrame с данными
        age_group: Выбранная возрастная группа

    Returns:
        dict: Словарь с графиками
    """
    # Исключаем TOTAL из топ-10 графиков (если есть)
    filtered_df = (df[df['model'] != 'TOTAL']
                   if 'model' in df.columns else df)

    # 1. Какая модель больше всего приносит прибыль (RO cost total)
    fig_profit = px.bar(
        filtered_df.sort_values('total_ro_cost', ascending=False).head(10),
        x='model',
        y='total_ro_cost',
        text='total_ro_cost',
    )
    fig_profit.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='inside',
        textfont_size=11
    )
    fig_profit.update_yaxes(tickformat=',d')
    fig_profit.update_layout(
        margin=dict(t=60, b=60, l=60, r=60),
        showlegend=False
    )
    fig_profit.update_traces(marker_color=get_chart_color(0))

    # Определяем колонки в зависимости от возрастной группы
    if age_group == '0-5Y':
        labor_hours_col = 'labor_hours_0_5'
        total_col = 'total_0_5'
        ratio_col = 'ro_ratio_of_uio_5y'
        age_0_3_col = 'age_0_3'
        age_4_5_col = 'age_4_5'
        age_6_10_col = None
    else:
        labor_hours_col = 'labor_hours_0_10'
        total_col = 'total_0_10'
        ratio_col = 'ro_ratio_of_uio_10y'
        age_0_3_col = 'age_0_3'
        age_4_5_col = 'age_4_5'
        age_6_10_col = 'age_6_10'

    # 2. Какая модель наиболее выгодна по работам (нормо-часы)
    fig_mh = px.bar(
        filtered_df.sort_values(labor_hours_col, ascending=False).head(10),
        x='model',
        y=labor_hours_col,
        text=labor_hours_col,
    )
    fig_mh.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='inside',
        textfont_size=11
    )
    fig_mh.update_yaxes(tickformat=",d")
    fig_mh.update_layout(
        margin=dict(t=60, b=60, l=60, r=60),
        showlegend=False
    )
    fig_mh.update_traces(marker_color=get_chart_color(1))

    # 2.1 Среднее количество часов по моделям
    fig_avg_mh = px.bar(
        df.sort_values('aver_labor_hours_per_vhc', ascending=False).head(10),
        x='model',
        y='aver_labor_hours_per_vhc',
        text='aver_labor_hours_per_vhc',
    )
    fig_avg_mh.update_traces(
        texttemplate='%{text:,.1f}',
        textposition='inside',
        textfont_size=11
    )
    fig_avg_mh.update_layout(
        margin=dict(t=60, b=60, l=60, r=60),
        showlegend=False
    )
    fig_avg_mh.update_traces(marker_color=get_chart_color(2))

    # 3. Средний чек по моделям (Average RO cost)
    fig_avg_check = px.bar(
        df.sort_values('avg_ro_cost', ascending=False).head(10),
        x='model',
        y='avg_ro_cost',
        text='avg_ro_cost',
    )
    fig_avg_check.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='inside',
        textfont_size=11
    )
    fig_avg_check.update_yaxes(tickformat=',d')
    fig_avg_check.update_layout(
        margin=dict(t=60, b=60, l=60, r=60),
        showlegend=False
    )
    fig_avg_check.update_traces(marker_color=get_chart_color(3))

    # 4. Ratio – кол-во заказ нарядов / UIO
    fig_ratio = px.bar(
        df.sort_values(ratio_col, ascending=False).head(10),
        x='model',
        y=ratio_col,
        text=ratio_col,
    )
    fig_ratio.update_traces(
        texttemplate='%{text:.2f}',
        textposition='inside',
        textfont_size=11
    )
    fig_ratio.update_layout(
        margin=dict(t=60, b=60, l=60, r=60),
        showlegend=False
    )
    fig_ratio.update_traces(marker_color=get_chart_color(4))

    # 5. Количество заказ-нарядов по годам
    df_ro = df
    if 'model' in df_ro.columns:
        df_ro = df_ro[df_ro['model'] != 'TOTAL']
    if total_col in df_ro.columns:
        df_ro = df_ro.sort_values(total_col, ascending=False)
    df_ro = df_ro.head(10)

    fig_ro_years = go.Figure()

    # Добавляем группы в зависимости от возрастной группы
    if age_group == '0-5Y':
        # Для 0-5Y показываем только 0-3 и 4-5
        fig_ro_years.add_trace(go.Bar(
            x=df_ro['model'],
            y=df_ro[age_0_3_col],
            name='0-3 years',
            marker_color=get_chart_color(0),
            text=df_ro[age_0_3_col],
            textposition='inside',
            textfont=dict(size=11),
        ))
        fig_ro_years.add_trace(go.Bar(
            x=df_ro['model'],
            y=df_ro[age_4_5_col],
            name='4-5 years',
            marker_color=get_chart_color(1),
            text=df_ro[age_4_5_col],
            textposition='inside',
            textfont=dict(size=11),
        ))
    else:
        # Для 0-10Y показываем 0-3, 4-5, 6-10
        fig_ro_years.add_trace(go.Bar(
            x=df_ro['model'],
            y=df_ro[age_0_3_col],
            name='0-3 years',
            marker_color=get_chart_color(0),
            text=df_ro[age_0_3_col],
            textposition='inside',
            textfont=dict(size=11),
        ))
        fig_ro_years.add_trace(go.Bar(
            x=df_ro['model'],
            y=df_ro[age_4_5_col],
            name='4-5 years',
            marker_color=get_chart_color(1),
            text=df_ro[age_4_5_col],
            textposition='inside',
            textfont=dict(size=11),
        ))
        if age_6_10_col and age_6_10_col in df_ro.columns:
            fig_ro_years.add_trace(go.Bar(
                x=df_ro['model'],
                y=df_ro[age_6_10_col],
                name='6-10 years',
                marker_color=get_chart_color(2),
                text=df_ro[age_6_10_col],
                textposition='inside',
                textfont=dict(size=11),
            ))
    fig_ro_years.update_traces(
        texttemplate='%{text:,.0f}'
    )
    fig_ro_years.update_layout(
        barmode='stack',
        xaxis_title='Model',
        yaxis_title='RO Count',
        margin=dict(t=60, b=60, l=60, r=60),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    fig_ro_years.update_yaxes(tickformat=',d')

    return {
        'fig_profit': fig_profit,
        'fig_mh': fig_mh,
        'fig_avg_mh': fig_avg_mh,
        'fig_avg_check': fig_avg_check,
        'fig_ratio': fig_ratio,
        'fig_ro_years': fig_ro_years
    }


def create_table(df, age_group='0-10Y'):
    """
    Создает таблицу данных

    Args:
        df: DataFrame с данными
        age_group: Выбранная возрастная группа

    Returns:
        dash_table.DataTable: Таблица данных
    """
    # Словарь переименований колонок в зависимости от возрастной группы
    if age_group == '0-5Y':
        column_rename = {
            'model': 'Model',
            'uio_5y': 'UIO 5Y',
            'total_0_5': 'RO qty',
            'total_ro_cost': 'Amount',
            'avg_ro_cost': 'CPR',
            'labor_hours_0_5': 'L/H',
            'aver_labor_hours_per_vhc': 'L/H per RO',
            'labor_amount_0_5': 'Labor',
            'avg_ro_labor_cost': 'LPR',
            'parts_amount_0_5': 'Parts',
            'avg_ro_part_cost': 'PPR',
            'age_0': '0Y',
            'age_1': '1Y',
            'age_2': '2Y',
            'age_3': '3Y',
            'age_4': '4Y',
            'age_5': '5Y',
            'age_0_3': '0-3Y',
            'age_4_5': '4-5Y',
            'pct_age_0_3': 'Ratio 0-3Y',
            'pct_age_4_5': 'Ratio 4-5Y',
            'ro_ratio_of_uio_5y': 'RO ratio from UIO 5Y'
        }
    else:
        column_rename = {
            'model': 'Model',
            'uio_10y': 'UIO 10Y',
            'total_0_10': 'RO qty',
            'total_ro_cost': 'Amount',
            'avg_ro_cost': 'CPR',
            'labor_hours_0_10': 'L/H',
            'aver_labor_hours_per_vhc': 'L/H per RO',
            'labor_amount_0_10': 'Labor',
            'avg_ro_labor_cost': 'LPR',
            'parts_amount_0_10': 'Parts',
            'avg_ro_part_cost': 'PPR',
            'age_0': '0Y',
            'age_1': '1Y',
            'age_2': '2Y',
            'age_3': '3Y',
            'age_4': '4Y',
            'age_5': '5Y',
            'age_6': '6Y',
            'age_7': '7Y',
            'age_8': '8Y',
            'age_9': '9Y',
            'age_10': '10Y',
            'age_0_3': '0-3Y',
            'age_4_5': '4-5Y',
            'age_6_10': '6-10Y',
            'pct_age_0_3': 'Ratio 0-3Y',
            'pct_age_4_5': 'Ratio 4-5Y',
            'pct_age_6_10': 'Ratio 6-10Y',
            'ro_ratio_of_uio_10y': 'RO ratio from UIO 10Y'
        }

    # Определяем приоритетные колонки в зависимости от возрастной группы
    if age_group == '0-5Y':
        priority_cols = [
            'model',
            'uio_5y',
            'total_0_5',
            'total_ro_cost',
            'avg_ro_cost',
            'labor_hours_0_5',
            'aver_labor_hours_per_vhc',
            'labor_amount_0_5',
            'avg_ro_labor_cost',
            'parts_amount_0_5',
            'avg_ro_part_cost',
        ]
    else:
        priority_cols = [
            'model',
            'uio_10y',
            'total_0_10',
            'total_ro_cost',
            'avg_ro_cost',
            'labor_hours_0_10',
            'aver_labor_hours_per_vhc',
            'labor_amount_0_10',
            'avg_ro_labor_cost',
            'parts_amount_0_10',
            'avg_ro_part_cost',
        ]
    ordered_cols = (
        [c for c in priority_cols if c in df.columns] +
        [c for c in df.columns if c not in priority_cols]
    )
    columns = []
    for col in ordered_cols:
        # Получаем отображаемое имя колонки
        display_name = column_rename.get(col, col)

        if df[col].dtype.kind in 'fi':
            fmt = {"specifier": ",.1f"} \
                if col == 'aver_labor_hours_per_vhc' else {"specifier": ",.0f"}
            columns.append({
                "name": display_name,
                "id": col,
                "type": "numeric",
                "format": fmt
            })
        else:
            columns.append({"name": display_name, "id": col})

    # Фильтруем строки и сортируем по total_ro_cost
    df_table = df
    total_col = 'total_0_5' if age_group == '0-5Y' else 'total_0_10'
    if total_col in df_table.columns:
        df_table = df_table[df_table[total_col] != 0]
    df_table = (
        df_table.sort_values('total_ro_cost', ascending=False)
        if 'total_ro_cost' in df_table.columns else df_table
    )

    return create_data_table(columns, df_table.to_dict('records'))


def calculate_metrics(df, age_group='0-10Y'):
    """
    Вычисляет суммарные показатели для карт

    Args:
        df: DataFrame с данными
        age_group: Выбранная возрастная группа

    Returns:
        dict: Словарь с метриками
    """
    # Определяем колонки в зависимости от возрастной группы
    if age_group == '0-5Y':
        uio_col = 'uio_5y'
        total_col = 'total_0_5'
        labor_hours_col = 'labor_hours_0_5'
    else:
        uio_col = 'uio_10y'
        total_col = 'total_0_10'
        labor_hours_col = 'labor_hours_0_10'

    total_uio = df[uio_col].sum() if uio_col in df.columns else 0
    total_ro_qty = df[total_col].sum() if total_col in df.columns else 0
    total_cost = (df['total_ro_cost'].sum()
                  if 'total_ro_cost' in df.columns else 0)
    total_labor_hours = (
        df[labor_hours_col].sum()
        if labor_hours_col in df.columns else 0
    )
    avg_ro_cost = (total_cost / total_ro_qty
                   if total_ro_qty > 0 else 0)

    return {
        'total_uio': total_uio,
        'total_ro_qty': total_ro_qty,
        'total_cost': total_cost,
        'total_labor_hours': total_labor_hours,
        'avg_ro_cost': avg_ro_cost
    }


# Определяем доступные годы
current_year = datetime.now().year
# Последние 5 лет + текущий
available_years = list(range(current_year - 5, current_year + 1))

# Layout Dash
app = dash.Dash(__name__)
GRAPH_HEIGHT = 350

# Получаем адаптивные стили
responsive_styles = get_responsive_styles()

# Добавляем CSS для адаптивности
app.index_string = get_dashboard_template()

app.layout = html.Div([
    html.H1('DNM RO DATA by models', style=responsive_styles['title']),

    # Скрытые div для хранения данных
    dcc.Store(id='data-store'),

    # Селекторы и карты в одном блоке
    html.Div([
        # Селекторы года и возрастных групп
        html.Div([
            create_year_selector(available_years, current_year),
            create_age_group_selector()
        ], style={
            'display': 'flex',
            'align-items': 'flex-start',
            'justify-content': 'flex-start',
            'flex-wrap': 'wrap',
            'gap': '20px',
            'marginBottom': '20px',
            'padding': '0 10px'
        }),

        # Карты с суммарными показателями
        html.Div(id='metrics-cards')
    ], style={
        'marginBottom': '40px'
    }),

    # Графики
    html.Div(id='charts-container'),

    # Таблица
    html.H2('Items data by models', style=responsive_styles['section_title']),
    create_export_button(),
    html.Div(id='data-table'),
], style=responsive_styles['main_container'],
    className=responsive_styles['main_container'].get('className', ''))


@callback(
    [Output('data-store', 'data'),
     Output('metrics-cards', 'children'),
     Output('charts-container', 'children'),
     Output('data-table', 'children')],
    [Input('year-selector', 'value'),
     Input('age-group-selector', 'value')]
)
def update_dashboard(selected_year, age_group):
    """
    Обновляет дашборд при изменении года или возрастной группы

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа

    Returns:
        tuple: Данные, карты метрик, графики, таблица
    """
    try:
        # Получаем данные для выбранного года и возрастной группы
        df = get_dnm_data(selected_year, age_group)
        print(f'Данные загружены для года {selected_year} '
              f'и группы {age_group}')
    except Exception as e:
        print(f'Ошибка при загрузке данных из БД для года '
              f'{selected_year} и группы {age_group}: {e}')
        # Fallback на CSV файл в случае ошибки
        df = pd.read_csv('data/aug_25.csv')
        print('Используются данные из CSV файла')

    # Обрабатываем данные
    df = process_dataframe(df)

    # Создаем графики
    charts = create_charts(df, age_group)

    # Создаем таблицу
    table = create_table(df, age_group)

    # Вычисляем метрики
    metrics = calculate_metrics(df, age_group)

    # Создаем карты метрик
    metrics_cards = create_cards_row([
        create_metric_card(f'UIO ({age_group})',
                           f'{metrics["total_uio"]:,.0f}'),
        create_metric_card(f'RO qty ({age_group})',
                           f'{metrics["total_ro_qty"]:,.0f}'),
        create_metric_card(f'Total cost ({age_group})',
                           f'{metrics["total_cost"]:,.0f}'),
        create_metric_card('Total L/H',
                           f'{metrics["total_labor_hours"]:,.0f}'),
        create_metric_card('Average RO cost',
                           f'{metrics["avg_ro_cost"]:,.0f}'),
    ])

    # Создаем контейнеры графиков
    charts_container = html.Div([
        create_graphs_row([
            create_graph_container(
                'Top 10 Models by Total Profit',
                charts['fig_profit'], GRAPH_HEIGHT
            ),
            create_graph_container(
                'Top 10 Models by Total Labor Hours',
                charts['fig_mh'], GRAPH_HEIGHT
            ),
        ]),
        create_graphs_row([
            create_graph_container(
                'Top 10 Models by Average Labor Hours per Car',
                charts['fig_avg_mh'], GRAPH_HEIGHT
            ),
            create_graph_container(
                'Top 10 Models by Average RO Cost',
                charts['fig_avg_check'], GRAPH_HEIGHT
            ),
        ]),
        create_graphs_row([
            create_graph_container(
                'Top 10 Models by Ratio (RO/UIO)',
                charts['fig_ratio'], GRAPH_HEIGHT
            ),
            create_graph_container(
                'RO Count by Age Groups',
                charts['fig_ro_years'], GRAPH_HEIGHT
            ),
        ]),
    ])

    return df.to_dict('records'), metrics_cards, charts_container, table


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


if __name__ == '__main__':
    app.run(
        debug=settings.app.debug,
        host=settings.app.host,
        port=settings.app.port
    )
