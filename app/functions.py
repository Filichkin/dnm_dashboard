"""
Функции для обработки данных и создания компонентов DNM Dashboard
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
from dash import html
from loguru import logger

from .components import (
    create_metric_card,
    create_graph_container,
    create_cards_row,
    create_graphs_row,
    create_data_table,
    create_dealer_name_display,
    create_holding_name_display,
    create_region_name_display,
    get_chart_color
)
from .constants import (
    get_dealer_name,
    get_holding_name,
    get_region_name,
    get_holding_by_mobis_code,
    get_region_by_mobis_code,
    get_mobis_codes_by_holding,
    GRAPH_HEIGHT
)
from database.queries import (
    get_dnm_data,
)


def format_number_k_m(value):
    """
    Форматирует число в формат K/M (тысячи/миллионы)

    Args:
        value: Числовое значение для форматирования

    Returns:
        str: Отформатированная строка (например, 100K, 270M)
    """
    if pd.isna(value) or value == 0:
        return '0'

    abs_value = abs(value)

    if abs_value >= 1_000_000:
        formatted = f"{value / 1_000_000:.0f}M"
    elif abs_value >= 1_000:
        formatted = f"{value / 1_000:.0f}K"
    else:
        formatted = f"{value:.0f}"

    return formatted


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


def create_charts(df, age_group='0-10Y', region_df=None):
    """
    Создает все графики на основе данных

    Args:
        df: DataFrame с данными
        age_group: Выбранная возрастная группа
        region_df: DataFrame с данными по региону (опционально)

    Returns:
        dict: Словарь с графиками
    """
    # Исключаем TOTAL из топ-10 графиков (если есть)
    filtered_df = (df[df['model'] != 'TOTAL']
                   if 'model' in df.columns else df)

    # 1. Какая модель больше всего приносит прибыль (RO cost total)
    # Подготавливаем данные для отображения с форматированием K/M
    profit_data = (
        filtered_df.sort_values(
            'total_ro_cost',
            ascending=False
            ).head(10)
        )
    profit_data = profit_data.copy()
    profit_data['total_ro_cost_formatted'] = (
        profit_data['total_ro_cost'].apply(format_number_k_m))

    fig_profit = px.bar(
        profit_data,
        x='model',
        y='total_ro_cost',
        text='total_ro_cost_formatted',
        color_discrete_sequence=['#1f77b4']
    )

    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = (
            filtered_df.sort_values(
                'total_ro_cost',
                ascending=False
                ).head(10)['model'].tolist()
            )
        region_filtered = region_df[region_df['model'].isin(top_10_models)]

        if not region_filtered.empty:
            fig_profit.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered['total_ro_cost'],
                mode='markers',
                name='Region Average',
                yaxis='y2',
                marker=dict(size=8, symbol='circle',
                            line=dict(width=1, color='white'))
            ))

            # Жёстко задаём цвет именно последнему (scatter) трэйсу
            sc = fig_profit.data[-1]

            # 1) на всякий случай отключаем любую цветовую ось/палитру
            sc.marker.coloraxis = None
            fig_profit.update_layout(coloraxis=None)

            # 2) задаём собственный цвет (как массив — ничего не перетрёт)
            sc.marker.color = ['#00ff88'] * len(region_filtered)

            # 3) обводка — как хотели
            sc.marker.line.color = '#00ff88'
            sc.marker.line.width = 1
            sc.marker.symbol = 'circle'

    # ЖЁСТКО зафиксировать цвета по типам трейсов
    fig_profit.update_traces(marker=dict(color='#1f77b4'),
                             selector=dict(type='bar'), overwrite=True)

    # Обновляем только bar traces (основные данные дилера)
    fig_profit.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        textfont_size=15,
        textfont_color='white',
        marker_line_width=0,
        selector=dict(type='bar')
    )
    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_profit.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=14, family='Arial', color='white'),
                tickfont=dict(size=14, color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            ),
            colorway=None  # отключаем автопалитру
        )

    fig_profit.update_yaxes(
        tickformat=',d',
        title='Amount',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False
    )

    fig_profit.update_xaxes(
        title='Model',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False,
        tickangle=-45
    )
    fig_profit.update_layout(
        margin=dict(t=80, b=60, l=60, r=60),
        showlegend=True,
        plot_bgcolor='#3a3a3a',
        paper_bgcolor='#3a3a3a',
        font=dict(color='white'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='white')
        )
    )
    fig_profit.update_traces(marker_color=get_chart_color(0),
                             selector=dict(type='bar'))

    # Определяем колонки в зависимости от возрастной группы
    if age_group == '0-5Y':
        labor_hours_col = 'labor_hours_0_5'
        total_col = 'total_0_5'
        age_0_3_col = 'age_0_3'
        age_4_5_col = 'age_4_5'
        age_6_10_col = None
        # Создаем новую колонку с ratio на основе avg_uio_5y для графика
        if 'avg_uio_5y' in df.columns and 'total_0_5' in df.columns:
            df = df.copy()
            df['ro_ratio_of_avg_uio_5y'] = (
                df.apply(
                    lambda row: (
                        round(100 * row['total_0_5'] / row['avg_uio_5y'], 2)
                        if row['avg_uio_5y'] > 0 else 0
                    ),
                    axis=1
                )
            )
            ratio_col = 'ro_ratio_of_avg_uio_5y'
            # Обновляем filtered_df после создания новой колонки
            filtered_df = (df[df['model'] != 'TOTAL']
                           if 'model' in df.columns else df)
            # Также обновляем region_df, если он есть
            if region_df is not None and not region_df.empty:
                if ('avg_uio_5y' in region_df.columns and
                        'total_0_5' in region_df.columns):
                    region_df = region_df.copy()
                    region_df['ro_ratio_of_avg_uio_5y'] = (
                        region_df.apply(
                            lambda row: (
                                round(100 * row['total_0_5'] /
                                      row['avg_uio_5y'], 2)
                                if row['avg_uio_5y'] > 0 else 0
                            ),
                            axis=1
                        )
                    )
        else:
            # Fallback на старую колонку, если avg_uio_5y не найдена
            ratio_col = 'ro_ratio_of_uio_5y'
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
        color_discrete_sequence=['#1f77b4']
    )

    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = (
            filtered_df.sort_values(
                labor_hours_col,
                ascending=False
                ).head(10)['model'].tolist()
            )
        region_filtered = region_df[region_df['model'].isin(top_10_models)]

        if not region_filtered.empty:
            fig_mh.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered[labor_hours_col],
                mode='markers',
                name='Region Average',
                yaxis='y2',
                marker=dict(size=8, symbol='circle',
                            line=dict(width=1, color='white'))
            ))

            # Жёстко задаём цвет именно последнему (scatter) трэйсу
            sc = fig_mh.data[-1]

            # 1) на всякий случай отключаем любую цветовую ось/палитру
            sc.marker.coloraxis = None
            fig_mh.update_layout(coloraxis=None)

            # 2) задаём собственный цвет (как массив — ничего не перетрёт)
            sc.marker.color = ['#00ff88'] * len(region_filtered)

            # 3) обводка — как хотели
            sc.marker.line.color = '#00ff88'
            sc.marker.line.width = 1
            sc.marker.symbol = 'circle'

    # ЖЁСТКО зафиксировать цвета по типам трейсов
    fig_mh.update_traces(marker=dict(color='#1f77b4'),
                         selector=dict(type='bar'), overwrite=True)

    # Обновляем только bar traces (основные данные дилера)
    fig_mh.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        textfont_size=15,
        textfont_color='white',
        marker_line_width=0,
        selector=dict(type='bar')
    )
    fig_mh.update_yaxes(
        tickformat=',d',
        title='L/H',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False
    )

    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_mh.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=14, family='Arial', color='white'),
                tickfont=dict(size=14, color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            ),
            colorway=None  # отключаем автопалитру
        )
    fig_mh.update_xaxes(
        title='Model',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False,
        tickangle=-45
    )
    fig_mh.update_layout(
        margin=dict(t=80, b=60, l=60, r=60),
        showlegend=True,
        plot_bgcolor='#3a3a3a',
        paper_bgcolor='#3a3a3a',
        font=dict(color='white'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='white')
        )
    )
    fig_mh.update_traces(marker_color=get_chart_color(1),
                         selector=dict(type='bar'))

    # 2.1 Среднее количество часов по моделям
    fig_avg_mh = px.bar(
        df.sort_values('aver_labor_hours_per_vhc', ascending=False).head(10),
        x='model',
        y='aver_labor_hours_per_vhc',
        text='aver_labor_hours_per_vhc',
        color_discrete_sequence=['#1f77b4']
    )

    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = (
            df.sort_values(
                'aver_labor_hours_per_vhc',
                ascending=False
                ).head(10)['model'].tolist()
            )
        region_filtered = region_df[region_df['model'].isin(top_10_models)]

        if not region_filtered.empty:
            fig_avg_mh.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered['aver_labor_hours_per_vhc'],
                mode='markers',
                name='Region Average',
                yaxis='y2',
                marker=dict(size=8, symbol='circle',
                            line=dict(width=1, color='white'))
            ))

            # Жёстко задаём цвет именно последнему (scatter) трэйсу
            sc = fig_avg_mh.data[-1]

            # 1) на всякий случай отключаем любую цветовую ось/палитру
            sc.marker.coloraxis = None
            fig_avg_mh.update_layout(coloraxis=None)

            # 2) задаём собственный цвет (как массив — ничего не перетрёт)
            sc.marker.color = ['#00ff88'] * len(region_filtered)

            # 3) обводка — как хотели
            sc.marker.line.color = '#00ff88'
            sc.marker.line.width = 1
            sc.marker.symbol = 'circle'

    # ЖЁСТКО зафиксировать цвета по типам трейсов
    fig_avg_mh.update_traces(marker=dict(color='#1f77b4'),
                             selector=dict(type='bar'), overwrite=True)

    # Обновляем только bar traces (основные данные дилера)
    fig_avg_mh.update_traces(
        texttemplate='%{text:,.1f}',
        textposition='outside',
        textfont_size=15,
        textfont_color='white',
        marker_line_width=0,
        selector=dict(type='bar')
    )
    fig_avg_mh.update_yaxes(
        title='L/H per RO',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False
    )

    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_avg_mh.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=14, family='Arial', color='white'),
                tickfont=dict(size=14, color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            ),
            colorway=None  # отключаем автопалитру
        )
    fig_avg_mh.update_xaxes(
        title='Model',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False,
        tickangle=-45
    )
    fig_avg_mh.update_layout(
        margin=dict(t=80, b=60, l=60, r=60),
        showlegend=True,
        plot_bgcolor='#3a3a3a',
        paper_bgcolor='#3a3a3a',
        font=dict(color='white'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='white')
        )
    )
    fig_avg_mh.update_traces(marker_color=get_chart_color(2),
                             selector=dict(type='bar'))

    # 3. Средний чек по моделям (Average RO cost)
    fig_avg_check = px.bar(
        df.sort_values('avg_ro_cost', ascending=False).head(10),
        x='model',
        y='avg_ro_cost',
        text='avg_ro_cost',
        color_discrete_sequence=['#1f77b4']
    )

    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = (
            df.sort_values(
                'avg_ro_cost',
                ascending=False
                ).head(10)['model'].tolist()
            )
        region_filtered = region_df[region_df['model'].isin(top_10_models)]

        if not region_filtered.empty:
            fig_avg_check.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered['avg_ro_cost'],
                mode='markers',
                name='Region Average',
                yaxis='y2',
                marker=dict(size=8, symbol='circle',
                            line=dict(width=1, color='white'))
            ))

            # Жёстко задаём цвет именно последнему (scatter) трэйсу
            sc = fig_avg_check.data[-1]

            # 1) на всякий случай отключаем любую цветовую ось/палитру
            sc.marker.coloraxis = None
            fig_avg_check.update_layout(coloraxis=None)

            # 2) задаём собственный цвет (как массив — ничего не перетрёт)
            sc.marker.color = ['#00ff88'] * len(region_filtered)

            # 3) обводка — как хотели
            sc.marker.line.color = '#00ff88'
            sc.marker.line.width = 1
            sc.marker.symbol = 'circle'

    # ЖЁСТКО зафиксировать цвета по типам трейсов
    fig_avg_check.update_traces(marker=dict(color='#1f77b4'),
                                selector=dict(type='bar'), overwrite=True)

    # Обновляем только bar traces (основные данные дилера)
    fig_avg_check.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='outside',
        textfont_size=15,
        textfont_color='white',
        marker_line_width=0,
        selector=dict(type='bar')
    )
    fig_avg_check.update_yaxes(
        tickformat=',d',
        title='CPR',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False
    )

    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_avg_check.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=14, family='Arial', color='white'),
                tickfont=dict(size=14, color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            ),
            colorway=None  # отключаем автопалитру
        )
    fig_avg_check.update_xaxes(
        title='Model',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False,
        tickangle=-45
    )
    fig_avg_check.update_layout(
        margin=dict(t=80, b=60, l=60, r=60),
        showlegend=True,
        plot_bgcolor='#3a3a3a',
        paper_bgcolor='#3a3a3a',
        font=dict(color='white'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='white')
        )
    )
    fig_avg_check.update_traces(marker_color=get_chart_color(3),
                                selector=dict(type='bar'))

    # 4. Ratio – кол-во заказ нарядов / UIO
    # Используем filtered_df для исключения TOTAL
    if ratio_col in filtered_df.columns:
        ratio_data = (
            filtered_df.sort_values(
                ratio_col,
                ascending=False
            ).head(10))
    elif ratio_col in df.columns:
        ratio_data = df.sort_values(ratio_col, ascending=False).head(10)
    else:
        # Fallback на старую колонку
        if age_group == '0-5Y':
            ratio_col = 'ro_ratio_of_uio_5y'
        else:
            ratio_col = 'ro_ratio_of_uio_10y'
        ratio_data = df.sort_values(ratio_col, ascending=False).head(10)
    fig_ratio = px.bar(
        ratio_data,
        x='model',
        y=ratio_col,
        text=ratio_col,
        color_discrete_sequence=['#1f77b4']
    )

    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        if ratio_col in ratio_data.columns:
            top_10_models = ratio_data['model'].tolist()
        else:
            top_10_models = (
                df.sort_values(
                    ratio_col,
                    ascending=False
                ).head(10)['model'].tolist())
        region_filtered = region_df[region_df['model'].isin(top_10_models)]

        if not region_filtered.empty:
            fig_ratio.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered[ratio_col],
                mode='markers',
                name='Region Average',
                yaxis='y2',
                marker=dict(size=8, symbol='circle',
                            line=dict(width=1, color='white'))
            ))

            # Жёстко задаём цвет именно последнему (scatter) трэйсу
            sc = fig_ratio.data[-1]

            # 1) на всякий случай отключаем любую цветовую ось/палитру
            sc.marker.coloraxis = None
            fig_ratio.update_layout(coloraxis=None)

            # 2) задаём собственный цвет (как массив — ничего не перетрёт)
            sc.marker.color = ['#00ff88'] * len(region_filtered)

            # 3) обводка — как хотели
            sc.marker.line.color = '#00ff88'
            sc.marker.line.width = 1
            sc.marker.symbol = 'circle'

    # ЖЁСТКО зафиксировать цвета по типам трейсов
    fig_ratio.update_traces(marker=dict(color='#1f77b4'),
                            selector=dict(type='bar'), overwrite=True)

    # Обновляем только bar traces (основные данные дилера)
    fig_ratio.update_traces(
        texttemplate='%{text:.2f}',
        textposition='outside',
        textfont_size=15,
        textfont_color='white',
        marker_line_width=0,
        selector=dict(type='bar')
    )

    # Определяем название для оси Y в зависимости от возрастной группы
    ratio_title = ('RO ratio from AVG_UIO 5Y' if age_group == '0-5Y'
                   else 'RO ratio from UIO 10Y')

    fig_ratio.update_yaxes(
        title=ratio_title,
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False
    )

    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_ratio.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=14, family='Arial', color='white'),
                tickfont=dict(size=14, color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            ),
            colorway=None  # отключаем автопалитру
        )
    fig_ratio.update_xaxes(
        title='Model',
        title_font=dict(size=16, family='Arial', color='white'),
        tickfont=dict(size=14, color='white'),
        showgrid=False,
        tickangle=-45
    )
    fig_ratio.update_layout(
        margin=dict(t=80, b=60, l=60, r=60),
        showlegend=True,
        plot_bgcolor='#3a3a3a',
        paper_bgcolor='#3a3a3a',
        font=dict(color='white'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='white')
        )
    )
    fig_ratio.update_traces(marker_color=get_chart_color(4),
                            selector=dict(type='bar'))

    # 5. Количество заказ-нарядов по годам с UIO как отдельным сегментом
    df_ro = df
    if 'model' in df_ro.columns:
        df_ro = df_ro[df_ro['model'] != 'TOTAL']
    if total_col in df_ro.columns:
        df_ro = df_ro.sort_values(total_col, ascending=False)
    df_ro = df_ro.head(10)

    fig_ro_years = go.Figure()

    # Определяем колонку AVG_UIO в зависимости от возрастной группы
    avg_uio_col = 'avg_uio_5y' if age_group == '0-5Y' else 'avg_uio_10y'

    # Подготавливаем данные для графика
    if age_group == '0-5Y':
        # Для 0-5Y показываем 0-3, 4-5 и AVG_UIO линией
        if avg_uio_col in df_ro.columns:
            text_uio = df_ro.apply(
                lambda row: (
                    f"{int(row[avg_uio_col]):,}"
                    if (pd.notna(row[avg_uio_col]) and
                        row[avg_uio_col] > 0) else ""
                ),
                axis=1
            )
            fig_ro_years.add_trace(go.Scatter(
                x=df_ro['model'],
                y=df_ro[avg_uio_col],
                name=f'AVG_UIO ({age_group})',
                mode='lines+markers+text',
                line=dict(color=get_chart_color(4), width=3),
                marker=dict(size=12, color=get_chart_color(4), opacity=0),
                text=text_uio,
                textposition='bottom left',
                textfont=dict(size=13, color='white'),
                hovertemplate='%{x}<br>AVG_UIO: %{y:,.0f}<extra></extra>',
                yaxis='y2'
            ))
        # Текст для 4-5 years: показываем только количество RO
        text_4_5 = df_ro.apply(
            lambda row: (
                f"{int(row[age_4_5_col]):,}"
                if pd.notna(row[age_4_5_col]) else ""
            ),
            axis=1
        )
        fig_ro_years.add_trace(go.Bar(
            x=df_ro['model'],
            y=df_ro[age_4_5_col],
            name='4-5 years',
            marker_color=get_chart_color(1),
            marker_line_width=0,
            text=text_4_5,
            textposition='outside',
            textfont=dict(size=15, color='white'),
            hovertemplate='%{x}<br>4-5 years: %{y:,.0f}<extra></extra>'
        ))
        # Текст для 0-3 years: показываем только количество RO
        text_0_3 = df_ro.apply(
            lambda row: (
                f"{int(row[age_0_3_col]):,}"
                if pd.notna(row[age_0_3_col]) else ""
            ),
            axis=1
        )
        fig_ro_years.add_trace(go.Bar(
            x=df_ro['model'],
            y=df_ro[age_0_3_col],
            name='0-3 years',
            marker_color=get_chart_color(0),
            marker_line_width=0,
            text=text_0_3,
            textposition='outside',
            textfont=dict(size=15, color='white'),
            hovertemplate='%{x}<br>0-3 years: %{y:,.0f}<extra></extra>'
        ))

    else:
        # Для 0-10Y показываем 0-3, 4-5, 6-10 и AVG_UIO линией
        if avg_uio_col in df_ro.columns:
            text_uio = df_ro.apply(
                lambda row: (
                    f"{int(row[avg_uio_col]):,}"
                    if (pd.notna(row[avg_uio_col]) and
                        row[avg_uio_col] > 0) else ""
                ),
                axis=1
            )
            fig_ro_years.add_trace(go.Scatter(
                x=df_ro['model'],
                y=df_ro[avg_uio_col],
                name=f'AVG_UIO ({age_group})',
                mode='lines+markers+text',
                line=dict(color=get_chart_color(4), width=3),
                marker=dict(size=12, color=get_chart_color(4), opacity=0),
                text=text_uio,
                textposition='bottom left',
                textfont=dict(size=13, color='white'),
                hovertemplate='%{x}<br>AVG_UIO: %{y:,.0f}<extra></extra>',
                yaxis='y2'
            ))

        # Текст для 4-5 years
        text_4_5 = df_ro.apply(
            lambda row: (
                f"{int(row[age_4_5_col]):,}"
                if pd.notna(row[age_4_5_col]) else ""
            ),
            axis=1
        )
        fig_ro_years.add_trace(go.Bar(
            x=df_ro['model'],
            y=df_ro[age_4_5_col],
            name='4-5 years',
            marker_color=get_chart_color(1),
            marker_line_width=0,
            text=text_4_5,
            textposition='outside',
            textfont=dict(size=15, color='white'),
            hovertemplate='%{x}<br>4-5 years: %{y:,.0f}<extra></extra>'
        ))

        # Текст для 6-10 years
        if age_6_10_col and age_6_10_col in df_ro.columns:
            text_6_10 = df_ro.apply(
                lambda row: (
                    f"{int(row[age_6_10_col]):,}"
                    if pd.notna(row[age_6_10_col]) else ""
                ),
                axis=1
            )
            fig_ro_years.add_trace(go.Bar(
                x=df_ro['model'],
                y=df_ro[age_6_10_col],
                name='6-10 years',
                marker_color=get_chart_color(2),
                marker_line_width=0,
                text=text_6_10,
                textposition='outside',
                textfont=dict(size=15, color='white'),
                hovertemplate='%{x}<br>6-10 years: %{y:,.0f}<extra></extra>'
            ))
        # Текст для 0-3 years
        text_0_3 = df_ro.apply(
            lambda row: (
                f"{int(row[age_0_3_col]):,}"
                if pd.notna(row[age_0_3_col]) else ""
            ),
            axis=1
        )
        fig_ro_years.add_trace(go.Bar(
            x=df_ro['model'],
            y=df_ro[age_0_3_col],
            name='0-3 years',
            marker_color=get_chart_color(0),
            marker_line_width=0,
            text=text_0_3,
            textposition='outside',
            textfont=dict(size=15, color='white'),
            hovertemplate='%{x}<br>0-3 years: %{y:,.0f}<extra></extra>'
        ))

    # Вычисляем диапазон правой оси — сдвигаем "0" ниже оси X,
    # чтобы оно не накладывалось на "0" левой оси
    if avg_uio_col in df_ro.columns and not df_ro[avg_uio_col].empty:
        max_uio_val = df_ro[avg_uio_col].max()
        yaxis2_range = [max_uio_val * 0.001, max_uio_val * 1.2]
    else:
        yaxis2_range = None

    fig_ro_years.update_layout(
        barmode='group',
        xaxis_title='Model',
        margin=dict(t=60, b=60, l=60, r=80),
        plot_bgcolor='#3a3a3a',
        paper_bgcolor='#3a3a3a',
        font=dict(color='white'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(color='white')
        ),
        xaxis=dict(
            title_font=dict(size=16, family='Arial', color='white'),
            tickfont=dict(size=14, color='white'),
            showgrid=False,
            tickangle=-45
        ),
        yaxis=dict(
            title='RO qty',
            title_font=dict(size=16, family='Arial', color='white'),
            tickfont=dict(size=14, color='white'),
            showgrid=False,
            tickformat=',d'
        ),
        yaxis2=dict(
            title='AVG UIO',
            title_font=dict(size=16, family='Arial', color='white'),
            tickfont=dict(size=14, color='white'),
            showgrid=False,
            tickformat=',d',
            overlaying='y',
            side='right',
            range=yaxis2_range
        )
    )

    return {
        'fig_profit': fig_profit,
        'fig_mh': fig_mh,
        'fig_avg_mh': fig_avg_mh,
        'fig_avg_check': fig_avg_check,
        'fig_ratio': fig_ratio,
        'fig_ro_years': fig_ro_years
    }


def create_table(df, age_group='0-10Y', show_all_columns=False):
    """
    Создает таблицу данных с фильтрацией, зеброй и скрытием колонок

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
            # 'uio': 'UIO',
            'uio_5y': 'UIO 5Y',
            'avg_uio_5y': 'AVG_UIO 5Y',
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
            # 'uio': 'UIO',
            'uio_10y': 'UIO 10Y',
            'avg_uio_10y': 'AVG_UIO 10Y',
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
            'uio',
            'uio_5y',
            'avg_uio_5y',
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
            'uio',
            'uio_10y',
            'avg_uio_10y',
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
            fmt = {'specifier': ',.1f'} \
                if col == 'aver_labor_hours_per_vhc' else {'specifier': ',.0f'}
            columns.append({
                'name': display_name,
                'id': col,
                'type': 'numeric',
                'format': fmt
            })
        else:
            columns.append({'name': display_name, 'id': col})

    # Фильтруем строки и сортируем по total_ro_cost
    df_table = df.copy()
    total_col = 'total_0_5' if age_group == '0-5Y' else 'total_0_10'

    # Фильтруем строки с валидными данными
    if total_col in df_table.columns:
        df_table = df_table[df_table[total_col] > 0]

    # Убираем строки с пустыми или нулевыми значениями в ключевых колонках
    if 'total_ro_cost' in df_table.columns:
        df_table = df_table[df_table['total_ro_cost'] > 0]

    # Сортируем по total_ro_cost
    if 'total_ro_cost' in df_table.columns:
        df_table = df_table.sort_values('total_ro_cost', ascending=False)

    result = create_data_table(columns, df_table.to_dict('records'),
                               show_all_columns)
    return result


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
        total_col = 'total_0_5'
        labor_hours_col = 'labor_hours_0_5'
    else:
        total_col = 'total_0_10'
        labor_hours_col = 'labor_hours_0_10'

    # Используем новую колонку uio, если она есть, иначе fallback
    if 'uio' in df.columns:
        total_uio = df['uio'].sum()
    elif age_group == '0-5Y' and 'uio_5y' in df.columns:
        total_uio = df['uio_5y'].sum()
    elif (age_group == '0-10Y' and
          'uio_10y' in df.columns):
        total_uio = df['uio_10y'].sum()
    else:
        total_uio = 0
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


def get_available_years():
    """
    Получает список доступных годов

    Returns:
        list: Список годов
    """
    current_year = datetime.now().year
    # Последние 5 лет + текущий
    return list(range(current_year - 5, current_year + 1))


def get_current_year():
    """
    Получает текущий год

    Returns:
        int: Текущий год
    """
    return datetime.now().year


def load_dashboard_data(selected_year, age_group, selected_mobis_code,
                        selected_holding, selected_region='All'):
    """
    Загружает данные для дашборда с автоматическим определением региона

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа
        selected_mobis_code: Выбранный код дилера
        selected_holding: Выбранный holding
        selected_region: Выбранный region

    Returns:
        pd.DataFrame: DataFrame с данными
    """
    # НОВАЯ ЛОГИКА: Автоматически определяем регион по mobis_code
    if selected_mobis_code != 'All':
        # Определяем регион по выбранному дилеру
        auto_region = get_region_by_mobis_code(selected_mobis_code)
        if auto_region:
            selected_region = auto_region
            logger.info(f'Автоматически определен регион: {auto_region} '
                        f'для дилера {selected_mobis_code}')
        else:
            selected_region = 'All'
            logger.warning(f'Не удалось определить регион для дилера '
                           f'{selected_mobis_code}')
    else:
        # Если выбран 'All' дилеров, используем выбранный пользователем регион
        # (если он был выбран, иначе 'All')
        if selected_region is None or selected_region == '':
            selected_region = 'All'

    # Проверяем совместимость выбранного Mobis Code с Holding
    if (selected_holding != 'All' and
        selected_mobis_code != 'All' and
        selected_mobis_code not in get_mobis_codes_by_holding(
            selected_holding)):
        # Если выбранный Mobis Code не соответствует Holding,
        # используем 'All' для Mobis Code
        selected_mobis_code = 'All'

    try:
        # Получаем данные для выбранного года, возрастной группы,
        # кода дилера, holding и автоматически определенного region
        df = get_dnm_data(selected_year, age_group, selected_mobis_code,
                          selected_holding, selected_region)
    except Exception:
        # Fallback на CSV файл в случае ошибки
        if selected_year == 2024:
            # Используем июль 2025 как 2024
            df = pd.read_csv('data/jul_25.csv')
        else:
            # Используем август 2025 как 2025
            df = pd.read_csv('data/aug_25.csv')

        # Добавляем пустую колонку UIO для fallback данных
        df['uio'] = 0

    return df


def load_region_data(selected_year, age_group, selected_mobis_code):
    """
    Загружает данные по региону выбранного дилера (НОВАЯ ЛОГИКА)

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа
        selected_mobis_code: Выбранный код дилера

    Returns:
        pd.DataFrame: Данные по региону
    """
    try:
        # Определяем регион по mobis_code
        region = get_region_by_mobis_code(selected_mobis_code)
        if not region:
            logger.warning(f'Не удалось определить регион для дилера '
                           f'{selected_mobis_code}')
            return pd.DataFrame()

        logger.info(f'Получаем данные по региону {region} для дилера '
                    f'{selected_mobis_code}')

        # Получаем данные по региону с использованием нового скрипта
        df = get_dnm_data(
            selected_year=selected_year,
            age_group=age_group,
            selected_mobis_code='All',  # Все дилеры в регионе
            selected_holding='All',    # Все холдинги в регионе
            selected_region=region,     # Конкретный регион
            group_by_region=True  # Используем скрипт с группировкой по региону
        )
        return df
    except Exception as e:
        logger.error(f'Ошибка при получении данных по региону: {e}')
        return pd.DataFrame()


def create_metrics_cards(metrics, age_group):
    """
    Создает карты с метриками

    Args:
        metrics: Словарь с метриками
        age_group: Выбранная возрастная группа

    Returns:
        html.Div: Компонент с картами метрик
    """
    return create_cards_row([
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


def create_charts_container(charts):
    """
    Создает контейнер с графиками

    Args:
        charts: Словарь с графиками

    Returns:
        html.Div: Компонент с графиками
    """
    return html.Div([
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


def create_dealer_display(selected_mobis_code):
    """
    Создает компонент отображения названия дилера, holding и region

    Args:
        selected_mobis_code: Выбранный код дилера

    Returns:
        html.Div: Компонент отображения дилера с дополнительной информацией
    """
    dealer_name = get_dealer_name(selected_mobis_code)
    holding = get_holding_by_mobis_code(selected_mobis_code)
    region = get_region_by_mobis_code(selected_mobis_code)

    # Создаем основной контейнер
    if not dealer_name:
        return html.Div()

    # Создаем отображение дилера
    dealer_display = create_dealer_name_display()
    dealer_display.children[1].children = dealer_name

    # Создаем отображение holding
    holding_display = create_holding_name_display()
    holding_display.children[1].children = holding if holding else 'No holding'

    # Создаем отображение region
    region_display = create_region_name_display()
    region_display.children[1].children = region if region else 'No region'

    # Объединяем все компоненты в горизонтальную линию
    return html.Div([
        dealer_display,
        holding_display,
        region_display
    ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '20px',
              'alignItems': 'center'})


def create_holding_display(selected_holding):
    """
    Создает компонент отображения названия Holding

    Args:
        selected_holding: Выбранный holding

    Returns:
        html.Div: Компонент отображения Holding
    """
    holding_name = get_holding_name(selected_holding)
    holding_display = (create_holding_name_display()
                       if holding_name else html.Div())

    # Обновляем текст названия Holding
    if holding_name:
        holding_display.children[1].children = holding_name

    return holding_display


def create_region_display(selected_region):
    """
    Создает компонент отображения названия Region

    Args:
        selected_region: Выбранный region

    Returns:
        html.Div: Компонент отображения Region
    """
    region_name = get_region_name(selected_region)
    region_display = (create_region_name_display()
                      if region_name else html.Div())

    # Обновляем текст названия Region
    if region_name:
        region_display.children[1].children = region_name

    return region_display
