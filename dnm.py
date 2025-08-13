import dash
from dash import dcc, html, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Загрузка данных
# Учитываем, что разделитель в файле может быть необычным (например, ;)
df = pd.read_csv('data.csv')

# Преобразуем числовые столбцы (если нужно)
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Удаляем колонку 'Unnamed: 1', если она есть
if 'Unnamed: 1' in df.columns:
    df = df.drop(columns=['Unnamed: 1'])

# Стандартизируем наименование колонки модели
if 'Model \\ Age' in df.columns:
    df = df.rename(columns={'Model \\ Age': 'model'})
if 'Model' in df.columns:
    df = df.rename(columns={'Model': 'model'})

# Гарантируем агрегированные возрастные группы, если их нет
if 'age_0_3' not in df.columns:
    cols_0_3 = [f'age_{y}' for y in range(0, 4) if f'age_{y}' in df.columns]
    if cols_0_3:
        df['age_0_3'] = df[cols_0_3].sum(axis=1)
if 'age_4_5' not in df.columns:
    cols_4_5 = [f'age_{y}' for y in range(4, 6) if f'age_{y}' in df.columns]
    if cols_4_5:
        df['age_4_5'] = df[cols_4_5].sum(axis=1)
if 'age_6_10' not in df.columns:
    cols_6_10 = [f'age_{y}' for y in range(6, 11) if f'age_{y}' in df.columns]
    if cols_6_10:
        df['age_6_10'] = df[cols_6_10].sum(axis=1)

gray_blue_colors = [
    '#90a4ae',  # blue gray (calm)
    '#a5d6a7',  # soft green
    '#d7ccc8',  # soft brown/gray
    '#b0bec5',  # light blue gray
    '#cfd8dc',  # very light blue gray
]

# Исключаем TOTAL из топ-10 графиков (если есть)
filtered_df = df[df['model'] != 'TOTAL'] if 'model' in df.columns else df

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
fig_profit.update_yaxes(tickformat=",d")
fig_profit.update_layout(
    margin=dict(t=60, b=60, l=60, r=60),
    showlegend=False
)
fig_profit.update_traces(marker_color=gray_blue_colors[0])

# 2. Какая модель наиболее выгодна по работам (нормо-часы)
fig_mh = px.bar(
    filtered_df.sort_values('labor_hours_0_10', ascending=False).head(10),
    x='model',
    y='labor_hours_0_10',
    text='labor_hours_0_10',
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
fig_mh.update_traces(marker_color=gray_blue_colors[1])

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
fig_avg_mh.update_traces(marker_color=gray_blue_colors[2])

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
fig_avg_check.update_yaxes(tickformat=",d")
fig_avg_check.update_layout(
    margin=dict(t=60, b=60, l=60, r=60),
    showlegend=False
)
fig_avg_check.update_traces(marker_color=gray_blue_colors[3])

# 4. Ratio – кол-во заказ нарядов / UIO 10
fig_ratio = px.bar(
    df.sort_values('ro_ratio_of_uio_10y', ascending=False).head(10),
    x='model',
    y='ro_ratio_of_uio_10y',
    text='ro_ratio_of_uio_10y',
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
fig_ratio.update_traces(marker_color=gray_blue_colors[4])

# 5. Количество заказ-нарядов по годам: 0-3 (свежие), 4-5
# (гарантийные), 6-10 (пост гарантийные). Оставляем top-10.
df_ro = df
if 'model' in df_ro.columns:
    df_ro = df_ro[df_ro['model'] != 'TOTAL']
if 'total_0_10' in df_ro.columns:
    df_ro = df_ro.sort_values('total_0_10', ascending=False)
df_ro = df_ro.head(10)

fig_ro_years = go.Figure()
fig_ro_years.add_trace(go.Bar(
    x=df_ro['model'],
    y=df_ro['age_0_3'],
    name='0-3 years',
    marker_color=gray_blue_colors[0],
    text=df_ro['age_0_3'],
    textposition='inside',
    textfont=dict(size=11),
))
fig_ro_years.add_trace(go.Bar(
    x=df_ro['model'],
    y=df_ro['age_4_5'],
    name='4-5 years',
    marker_color=gray_blue_colors[1],
    text=df_ro['age_4_5'],
    textposition='inside',
    textfont=dict(size=11),
))
fig_ro_years.add_trace(go.Bar(
    x=df_ro['model'],
    y=df_ro['age_6_10'],
    name='6-10 years',
    marker_color=gray_blue_colors[2],
    text=df_ro['age_6_10'],
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
fig_ro_years.update_yaxes(tickformat=",d")

# Таблица с уменьшенной шириной колонок
# filtered_df используется только для графиков,
# а table строится по df (где TOTAL есть)
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
    if df[col].dtype.kind in 'fi':
        fmt = {"specifier": ",.1f"} \
            if col == 'aver_labor_hours_per_vhc' else {"specifier": ",.0f"}
        columns.append({
            "name": col,
            "id": col,
            "type": "numeric",
            "format": fmt
        })
    else:
        columns.append({"name": col, "id": col})

# Фильтруем строки, где total_0_10 == 0, и сортируем по total_ro_cost
df_table = df
if 'total_0_10' in df_table.columns:
    df_table = df_table[df_table['total_0_10'] != 0]
df_table = (
    df_table.sort_values('total_ro_cost', ascending=False)
    if 'total_ro_cost' in df_table.columns else df_table
)

table = dash_table.DataTable(
    columns=columns,
    data=df_table.to_dict('records'),  # df_table, а не filtered_df
    style_table={'overflowX': 'auto'},
    style_cell={
        'textAlign': 'center',
        'minWidth': '40px',
        'maxWidth': '90px',
        'whiteSpace': 'normal',
        'padding': '2px',
        'fontSize': '11px',
    },
    style_header={
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
    style_data_conditional=[
        {
            'if': {'column_type': 'numeric'},
            'textAlign': 'center',
        },
    ],
    # page_size=10,  # убираем пагинацию
)

# Layout Dash
app = dash.Dash(__name__)
GRAPH_HEIGHT = 350
app.layout = html.Div([
    html.H1('DNM DATA by models'),
    html.Div([
        html.Div([
            html.H2('Top 10 Models by Total Profit'),
            dcc.Graph(
                figure=fig_profit,
                style={'height': f'{GRAPH_HEIGHT}px'}
                ),
        ], style={'flex': '1', 'margin': '10px'}),
        html.Div([
            html.H2('Top 10 Models by Total Labor Hours'),
            dcc.Graph(figure=fig_mh, style={'height': f'{GRAPH_HEIGHT}px'}),
        ], style={'flex': '1', 'margin': '10px'}),
    ], style={'display': 'flex'}),
    html.Div([
        html.Div([
            html.H2('Top 10 Models by Average Labor Hours per Car'),
            dcc.Graph(
                figure=fig_avg_mh,
                style={'height': f'{GRAPH_HEIGHT}px'}
            ),
        ], style={'flex': '1', 'margin': '10px'}),
        html.Div([
            html.H2('Top 10 Models by Average RO Cost'),
            dcc.Graph(
                figure=fig_avg_check,
                style={'height': f'{GRAPH_HEIGHT}px'}
                ),
        ], style={'flex': '1', 'margin': '10px'}),
    ], style={'display': 'flex'}),
    html.Div([
        html.Div([
            html.H2('Top 10 Models by Ratio (RO/UIO)'),
            dcc.Graph(figure=fig_ratio, style={'height': f'{GRAPH_HEIGHT}px'}),
        ], style={'flex': '1', 'margin': '10px'}),
        html.Div([
            html.H2('RO Count by Age Groups'),
            dcc.Graph(
                figure=fig_ro_years,
                style={'height': f'{GRAPH_HEIGHT}px'}
                ),
        ], style={'flex': '1', 'margin': '10px'}),
    ], style={'display': 'flex'}),
    html.H2('Items data by models'),
    # Таблица без ограничения по высоте и прокрутки
    table,
])


if __name__ == '__main__':
    app.run(debug=False)
