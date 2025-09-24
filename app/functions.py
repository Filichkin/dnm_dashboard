"""
Функции для обработки данных и создания компонентов DNM Dashboard
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from datetime import datetime
from dash import html

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
    get_mobis_codes_by_holding,
    get_mobis_codes_by_region,
    GRAPH_HEIGHT
)
from database.queries import (
    get_dnm_data, get_dnm_data_by_region, get_region_by_mobis_code
)


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
    fig_profit = px.bar(
        filtered_df.sort_values('total_ro_cost', ascending=False).head(10),
        x='model',
        y='total_ro_cost',
        text='total_ro_cost',
    )
    
    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = filtered_df.sort_values('total_ro_cost', ascending=False).head(10)['model'].tolist()
        region_filtered = region_df[region_df['model'].isin(top_10_models)]
        
        if not region_filtered.empty:
            fig_profit.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered['total_ro_cost'],
                mode='markers',
                name='Region Average',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='circle',
                    line=dict(width=2, color='white')
                ),
                yaxis='y2'
            ))
    
    # Обновляем только bar traces (основные данные дилера)
    fig_profit.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='inside',
        textfont_size=11,
        textfont_color='white',
        selector=dict(type='bar')
    )
    fig_profit.update_yaxes(
        tickformat=',d',
        title='Amount',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
        showgrid=False
    )
    
    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_profit.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=12, family='Arial', color='white'),
                tickfont=dict(color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            )
        )
    fig_profit.update_xaxes(
        title='Model',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
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
    
    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = filtered_df.sort_values(labor_hours_col, ascending=False).head(10)['model'].tolist()
        region_filtered = region_df[region_df['model'].isin(top_10_models)]
        
        if not region_filtered.empty:
            fig_mh.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered[labor_hours_col],
                mode='markers',
                name='Region Average',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='circle',
                    line=dict(width=2, color='white')
                ),
                yaxis='y2'
            ))
    
    # Обновляем только bar traces (основные данные дилера)
    fig_mh.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='inside',
        textfont_size=11,
        textfont_color='white',
        selector=dict(type='bar')
    )
    fig_mh.update_yaxes(
        tickformat=',d',
        title='L/H',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
        showgrid=False
    )
    
    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_mh.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=12, family='Arial', color='white'),
                tickfont=dict(color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            )
        )
    fig_mh.update_xaxes(
        title='Model',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
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
    fig_mh.update_traces(marker_color=get_chart_color(1))

    # 2.1 Среднее количество часов по моделям
    fig_avg_mh = px.bar(
        df.sort_values('aver_labor_hours_per_vhc', ascending=False).head(10),
        x='model',
        y='aver_labor_hours_per_vhc',
        text='aver_labor_hours_per_vhc',
    )
    
    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = df.sort_values('aver_labor_hours_per_vhc', ascending=False).head(10)['model'].tolist()
        region_filtered = region_df[region_df['model'].isin(top_10_models)]
        
        if not region_filtered.empty:
            fig_avg_mh.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered['aver_labor_hours_per_vhc'],
                mode='markers',
                name='Region Average',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='circle',
                    line=dict(width=2, color='white')
                ),
                yaxis='y2'
            ))
    
    # Обновляем только bar traces (основные данные дилера)
    fig_avg_mh.update_traces(
        texttemplate='%{text:,.1f}',
        textposition='inside',
        textfont_size=11,
        textfont_color='white',
        selector=dict(type='bar')
    )
    fig_avg_mh.update_yaxes(
        title='L/H per RO',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
        showgrid=False
    )
    
    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_avg_mh.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=12, family='Arial', color='white'),
                tickfont=dict(color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            )
        )
    fig_avg_mh.update_xaxes(
        title='Model',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
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
    fig_avg_mh.update_traces(marker_color=get_chart_color(2))

    # 3. Средний чек по моделям (Average RO cost)
    fig_avg_check = px.bar(
        df.sort_values('avg_ro_cost', ascending=False).head(10),
        x='model',
        y='avg_ro_cost',
        text='avg_ro_cost',
    )
    
    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = df.sort_values('avg_ro_cost', ascending=False).head(10)['model'].tolist()
        region_filtered = region_df[region_df['model'].isin(top_10_models)]
        
        if not region_filtered.empty:
            fig_avg_check.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered['avg_ro_cost'],
                mode='markers',
                name='Region Average',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='circle',
                    line=dict(width=2, color='white')
                ),
                yaxis='y2'
            ))
    
    # Обновляем только bar traces (основные данные дилера)
    fig_avg_check.update_traces(
        texttemplate='%{text:,.0f}',
        textposition='inside',
        textfont_size=11,
        textfont_color='white',
        selector=dict(type='bar')
    )
    fig_avg_check.update_yaxes(
        tickformat=',d',
        title='CPR',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
        showgrid=False
    )
    
    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_avg_check.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=12, family='Arial', color='white'),
                tickfont=dict(color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            )
        )
    fig_avg_check.update_xaxes(
        title='Model',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
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
    fig_avg_check.update_traces(marker_color=get_chart_color(3))

    # 4. Ratio – кол-во заказ нарядов / UIO
    fig_ratio = px.bar(
        df.sort_values(ratio_col, ascending=False).head(10),
        x='model',
        y=ratio_col,
        text=ratio_col,
    )
    
    # Добавляем трассу с региональными данными, если они есть
    if region_df is not None and not region_df.empty:
        # Берем только модели из топ 10 основного дилера
        top_10_models = df.sort_values(ratio_col, ascending=False).head(10)['model'].tolist()
        region_filtered = region_df[region_df['model'].isin(top_10_models)]
        
        if not region_filtered.empty:
            fig_ratio.add_trace(go.Scatter(
                x=region_filtered['model'],
                y=region_filtered[ratio_col],
                mode='markers',
                name='Region Average',
                marker=dict(
                    color='red',
                    size=12,
                    symbol='circle',
                    line=dict(width=2, color='white')
                ),
                yaxis='y2'
            ))
    
    # Обновляем только bar traces (основные данные дилера)
    fig_ratio.update_traces(
        texttemplate='%{text:.2f}',
        textposition='inside',
        textfont_size=11,
        textfont_color='white',
        selector=dict(type='bar')
    )

    # Определяем название для оси Y в зависимости от возрастной группы
    ratio_title = ('RO ratio from UIO 5Y' if age_group == '0-5Y'
                   else 'RO ratio from UIO 10Y')

    fig_ratio.update_yaxes(
        title=ratio_title,
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
        showgrid=False
    )
    
    # Добавляем вспомогательную ось Y для региональных данных
    if region_df is not None and not region_df.empty:
        fig_ratio.update_layout(
            yaxis2=dict(
                title='Region Average',
                title_font=dict(size=12, family='Arial', color='white'),
                tickfont=dict(color='white'),
                overlaying='y',
                side='right',
                showgrid=False
            )
        )
    fig_ratio.update_xaxes(
        title='Model',
        title_font=dict(size=14, family='Arial', color='white'),
        tickfont=dict(color='white'),
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
        texttemplate='%{text:,.0f}',
        textfont_color='white',
        textfont_size=11
    )
    fig_ro_years.update_layout(
        barmode='stack',
        xaxis_title='Model',
        yaxis_title='RO qty',
        margin=dict(t=60, b=60, l=60, r=60),
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
            title_font=dict(size=14, family='Arial', color='white'),
            tickfont=dict(color='white'),
            showgrid=False,
            tickangle=-45
        ),
        yaxis=dict(
            title_font=dict(size=14, family='Arial', color='white'),
            tickfont=dict(color='white'),
            showgrid=False
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


def create_table(df, age_group='0-10Y', show_all_columns=False):
    """
    Создает таблицу данных с фильтрацией, зеброй и скрытием колонок

    Args:
        df: DataFrame с данными
        age_group: Выбранная возрастная группа

    Returns:
        dash_table.DataTable: Таблица данных
    """
    print("=== СОЗДАНИЕ ТАБЛИЦЫ ===")
    print(f"create_table: получено {len(df)} строк для возрастной группы "
          f"{age_group}")
    if len(df) > 0:
        models = (df['model'].head(3).tolist()
                  if 'model' in df.columns else 'Нет колонки model')
        print(f"Первые 3 модели в таблице: {models}")
        print(f"Колонки таблицы: {list(df.columns)[:5]}...")
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

    print(f"create_table: создаем таблицу с {len(df_table)} строками и "
          f"{len(columns)} колонками")
    if len(df_table) > 0:
        models_final = (df_table['model'].head(3).tolist()
                        if 'model' in df_table.columns
                        else 'Нет колонки model')
        print(f"Первые 3 модели в финальной таблице: {models_final}")
    result = create_data_table(columns, df_table.to_dict('records'),
                               show_all_columns)
    print(f"create_table: таблица создана, тип: {type(result)}")
    print("=== КОНЕЦ СОЗДАНИЯ ТАБЛИЦЫ ===")
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
    Загружает данные для дашборда

    Args:
        selected_year: Выбранный год
        age_group: Выбранная возрастная группа
        selected_mobis_code: Выбранный код дилера
        selected_holding: Выбранный holding
        selected_region: Выбранный region

    Returns:
        pd.DataFrame: DataFrame с данными
    """
    # Проверяем совместимость выбранного Mobis Code с Holding
    if (selected_holding != 'All' and
        selected_mobis_code != 'All' and
        selected_mobis_code not in get_mobis_codes_by_holding(
            selected_holding)):
        # Если выбранный Mobis Code не соответствует Holding,
        # используем 'All' для Mobis Code
        selected_mobis_code = 'All'
        print('Выбранный Mobis Code не соответствует Holding. '
              'Используется "All" для Mobis Code.')

    # Проверяем совместимость выбранного Mobis Code с Region
    if (selected_region != 'All' and
        selected_mobis_code != 'All' and
        selected_mobis_code not in get_mobis_codes_by_region(
            selected_region)):
        # Если выбранный Mobis Code не соответствует Region,
        # используем 'All' для Mobis Code
        selected_mobis_code = 'All'
        print('Выбранный Mobis Code не соответствует Region. '
              'Используется "All" для Mobis Code.')

    try:
        # Получаем данные для выбранного года, возрастной группы,
        # кода дилера, holding и region
        print("=== ЗАГРУЗКА ИЗ БД ===")
        print(f"Параметры: год={selected_year}, группа={age_group}, "
              f"mobis_code={selected_mobis_code}, holding={selected_holding}, "
              f"region={selected_region}")
        df = get_dnm_data(selected_year, age_group, selected_mobis_code,
                          selected_holding, selected_region)
        print(f'Данные загружены из БД для года {selected_year}, '
              f'группы {age_group}, кода дилера {selected_mobis_code}, '
              f'holding {selected_holding} и region {selected_region}')
        print(f"Размер данных из БД: {len(df)} строк")
        if len(df) > 0:
            models_db = (df['model'].head(3).tolist()
                         if 'model' in df.columns else 'Нет колонки model')
            print(f"Первые 3 модели из БД: {models_db}")
    except Exception as e:
        print(f'Ошибка при загрузке данных из БД для года '
              f'{selected_year}, группы {age_group}, кода дилера '
              f'{selected_mobis_code} и holding {selected_holding}: {e}')
        # Fallback на CSV файл в случае ошибки
        if selected_year == 2024:
            # Используем июль 2025 как 2024
            df = pd.read_csv('data/jul_25.csv')
            print('Используются данные из CSV файла jul_25.csv (как 2024 год)')
        else:
            # Используем август 2025 как 2025
            df = pd.read_csv('data/aug_25.csv')
            print('Используются данные из CSV файла aug_25.csv (как 2025 год)')

    return df


def load_region_data(selected_year, age_group, selected_mobis_code):
    """
    Загружает данные по региону выбранного дилера

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
        print(f"Регион для mobis_code {selected_mobis_code}: {region}")
        
        if not region:
            print("Регион не найден, возвращаем пустой DataFrame")
            return pd.DataFrame()
        
        # Получаем данные по региону
        df = get_dnm_data_by_region(
            selected_year=selected_year,
            age_group=age_group,
            selected_region=region
        )
        print(f"Загружено {len(df)} строк данных по региону {region}")
        return df
    except Exception as e:
        print(f"Ошибка при загрузке данных по региону: {e}")
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
    Создает компонент отображения названия дилера

    Args:
        selected_mobis_code: Выбранный код дилера

    Returns:
        html.Div: Компонент отображения дилера
    """
    dealer_name = get_dealer_name(selected_mobis_code)
    dealer_display = (create_dealer_name_display()
                      if dealer_name else html.Div())

    # Обновляем текст названия дилера
    if dealer_name:
        dealer_display.children[1].children = dealer_name

    return dealer_display


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
