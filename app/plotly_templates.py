"""
plotly_templates.py — themed Plotly figures for the DNM RO dashboard.

Single source of truth for chart styling, mirroring the CSS design
system (assets/dashboard_theme.css) 1:1 in both dark and light themes.
Pure Plotly + Dash compatible (no extra deps).

Token values in THEMES are kept identical to the CSS custom properties —
if a color changes in the CSS, change it here too.
"""

import pandas as pd
import plotly.graph_objects as go


# ----------------------------------------------------------------------
# THEME TOKENS  (kept identical to dashboard_theme.css)
# ----------------------------------------------------------------------
ACCENT_2 = '#16AFC0'      # secondary accent — AVG UIO line / region dots

THEMES = {
    'dark': {
        'accent': '#BFC2BF',
        'paper': 'rgba(0,0,0,0)',
        'plot': 'rgba(0,0,0,0)',
        'font': '#9fb3c2',
        'axis': '#7d92a4',
        'grid': 'rgba(255,255,255,0.07)',
        'text': '#eef4f8',
        'surface': '#0c2230',
        'border': 'rgba(255,255,255,0.16)',
    },
    'light': {
        'accent': '#05141f',
        'paper': 'rgba(0,0,0,0)',
        'plot': 'rgba(0,0,0,0)',
        'font': '#48586a',
        'axis': '#9aa6b1',
        'grid': 'rgba(5,20,31,0.08)',
        'text': '#05141f',
        'surface': '#ffffff',
        'border': 'rgba(5,20,31,0.18)',
    },
}

FONT_STACK = 'KiaSignature, "Helvetica Neue", Arial, sans-serif'
MONO_STACK = 'JetBrains Mono, ui-monospace, monospace'

CONFIG = {'responsive': True, 'displayModeBar': False}


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------
def _hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ramp(hex_color, n):
    """Ranked accent: bar #1 solid -> last bar faded (1.0 -> 0.38)."""
    r, g, b = _hex2rgb(hex_color)
    out = []
    for i in range(n):
        a = 1 - (i / max(n - 1, 1)) * 0.62
        out.append(f'rgba({r},{g},{b},{a:.3f})')
    return out


def _abbr(v):
    """Compact money/qty label: 121M, 1.5K, etc."""
    if pd.isna(v):
        return ''
    a = abs(v)
    if a >= 1e6:
        s = f'{v / 1e6:.0f}M' if a >= 1e7 else f'{v / 1e6:.1f}M'
    elif a >= 1e3:
        s = f'{v / 1e3:.0f}K' if a >= 1e4 else f'{v / 1e3:.1f}K'
    else:
        s = f'{v:g}'
    return s.replace('.0M', 'M').replace('.0K', 'K')


def _fmt(kind, v):
    if pd.isna(v):
        return ''
    if kind == 'abbr':
        return _abbr(v)
    if kind == 'float1':
        return f'{v:.1f}'
    if kind == 'float2':
        return f'{v:.2f}'
    if kind == 'pct1':
        return f'{v:.1f}%'
    if kind == 'pct2':
        return f'{v:.2f}%'
    return f'{v:,.0f}'


def base_layout(theme, **extra):
    tok = THEMES[theme]
    lay = dict(
        paper_bgcolor=tok['paper'],
        plot_bgcolor=tok['plot'],
        font=dict(family=FONT_STACK, size=12, color=tok['font']),
        margin=dict(l=8, r=14, t=14, b=44),
        bargap=0.42,
        showlegend=False,
        hoverlabel=dict(
            bgcolor=tok['surface'],
            bordercolor=tok['border'],
            font=dict(family=MONO_STACK, size=12, color=tok['text']),
        ),
        xaxis=dict(
            tickfont=dict(size=11, color=tok['axis']),
            showgrid=False, zeroline=False, fixedrange=True,
            automargin=True, showline=False, tickangle=-45,
        ),
        yaxis=dict(
            visible=False, showgrid=False, zeroline=False,
            fixedrange=True,
        ),
    )
    lay.update(extra)
    return lay


# ----------------------------------------------------------------------
# CHART BUILDERS
# ----------------------------------------------------------------------
def ranked_bar(df, value_key, value_fmt='abbr', top=10, theme='dark',
               currency=None, region_df=None, region_key=None,
               region_label='Region Average'):
    """Vertical ranked bar with opacity ramp and labels above bars.

    Optionally overlays a Region Average scatter on a secondary axis.
    `df` is a pandas DataFrame; `value_key`/`region_key` are columns.
    """
    tok = THEMES[theme]
    region_key = region_key or value_key

    data = df[df['model'] != 'TOTAL'] if 'model' in df.columns else df
    data = data.sort_values(value_key, ascending=False).head(top)

    x = data['model'].tolist()
    y = data[value_key].tolist()
    labels = [_fmt(value_fmt, v) for v in y]
    if currency:
        hover = [f'{v:,.0f} {currency}' if pd.notna(v) else ''
                 for v in y]
    elif value_fmt in ('pct1', 'pct2'):
        hover = [f'{v:.2f}%' if pd.notna(v) else '' for v in y]
    else:
        hover = [f'{v:,.0f}' if pd.notna(v) else '' for v in y]

    fig = go.Figure(go.Bar(
        x=x, y=y,
        marker=dict(
            color=ramp(tok['accent'], len(y)),
            cornerradius=5, line=dict(width=0),
        ),
        text=labels, textposition='outside', cliponaxis=False,
        textfont=dict(family=MONO_STACK, size=10.5, color=tok['font']),
        customdata=hover,
        hovertemplate='<b>%{x}</b><br>%{customdata}<extra></extra>',
    ))

    lay = base_layout(theme)
    valid_y = [v for v in y if pd.notna(v)] or [1]
    lay['yaxis']['range'] = [0, max(valid_y) * 1.18]

    # Region Average overlay (secondary axis)
    if (region_df is not None and not region_df.empty
            and region_key in region_df.columns):
        reg = region_df[region_df['model'].isin(x)]
        if not reg.empty:
            hov = (
                '<b>%{x}</b><br>%{y:,.0f} · '
                + region_label + '<extra></extra>'
            )
            fig.add_trace(go.Scatter(
                x=reg['model'].tolist(),
                y=reg[region_key].tolist(),
                mode='markers', name=region_label, yaxis='y2',
                marker=dict(
                    size=9, symbol='circle', color=ACCENT_2,
                    line=dict(width=1.5, color=tok['surface']),
                ),
                hovertemplate=hov,
            ))
            lay['showlegend'] = True
            lay['legend'] = dict(
                orientation='h', y=1.12, x=1, xanchor='right',
                font=dict(size=10.5, color=tok['font']),
                bgcolor='rgba(0,0,0,0)',
            )
            lay['yaxis2'] = dict(
                overlaying='y', side='right', showgrid=False,
                zeroline=False, fixedrange=True,
                tickfont=dict(size=10, color=tok['axis']),
                tickformat='~s',
            )

    fig.update_layout(lay)
    return fig


def age_groups(df, age_group='0-10Y', theme='dark'):
    """Stacked RO by age band (0-3y / 4-5y [/ 6-10y]) + AVG UIO
    spline on a secondary axis."""
    tok = THEMES[theme]
    r, g, b = _hex2rgb(tok['accent'])

    total_col = 'total_0_5' if age_group == '0-5Y' else 'total_0_10'
    avg_uio_col = 'avg_uio_5y' if age_group == '0-5Y' else 'avg_uio_10y'

    data = df[df['model'] != 'TOTAL'] if 'model' in df.columns else df
    sort_col = total_col if total_col in data.columns else 'age_0_3'
    if sort_col in data.columns:
        data = data.sort_values(sort_col, ascending=False)
    data = data.head(10)
    order = data['model'].tolist()

    bands = [
        ('age_0_3', '0-3 years', 0.92),
        ('age_4_5', '4-5 years', 0.55),
    ]
    if age_group != '0-5Y':
        bands.append(('age_6_10', '6-10 years', 0.32))

    traces = []
    for col, name, alpha in bands:
        if col not in data.columns:
            continue
        hov = '%{x} · ' + name + '<br>%{y:,} RO<extra></extra>'
        traces.append(go.Bar(
            name=name, x=order, y=data[col].tolist(),
            marker=dict(
                color=f'rgba({r},{g},{b},{alpha})', cornerradius=3,
            ),
            hovertemplate=hov,
        ))

    if avg_uio_col in data.columns:
        uio_vals = data[avg_uio_col].tolist()
        uio_text = [_abbr(v) for v in uio_vals]
        traces.append(go.Scatter(
            name='AVG UIO', x=order, y=uio_vals,
            mode='lines+markers+text', yaxis='y2',
            line=dict(color=ACCENT_2, width=2.5, shape='spline'),
            marker=dict(size=6, color=ACCENT_2),
            text=uio_text, textposition='middle right',
            textfont=dict(family=MONO_STACK, size=10, color=ACCENT_2),
            hovertemplate='%{x} · AVG UIO<br>%{y:,}<extra></extra>',
        ))

    lay = base_layout(
        theme, barmode='stack',
        margin=dict(l=8, r=42, t=30, b=44), showlegend=True,
        legend=dict(
            orientation='h', y=1.16, x=0,
            font=dict(size=11, color=tok['font']),
            bgcolor='rgba(0,0,0,0)',
        ),
        yaxis=dict(
            visible=False, showgrid=False, zeroline=False,
            fixedrange=True,
        ),
        yaxis2=dict(
            overlaying='y', side='right', showgrid=False,
            zeroline=False, fixedrange=True,
            tickfont=dict(size=10, color=tok['axis']),
            tickformat='~s',
        ),
    )
    fig = go.Figure(traces)
    fig.update_layout(lay)
    return fig


# ----------------------------------------------------------------------
# DISPATCHER  — returns the 6 figures the layout expects
# ----------------------------------------------------------------------
def build_dashboard_figures(df, age_group='0-10Y', region_df=None,
                            theme='dark'):
    """Build all six themed figures from a processed DataFrame.

    Returns a dict with the keys consumed by create_charts_container:
    fig_profit, fig_mh, fig_avg_mh, fig_avg_check, fig_ratio,
    fig_ro_years.
    """
    if age_group == '0-5Y':
        lh_col = 'labor_hours_0_5'
        ratio_col = 'ro_ratio_of_avg_uio_5y'
    else:
        lh_col = 'labor_hours_0_10'
        ratio_col = 'ro_ratio_of_uio_10y'

    df = df.copy()

    # Derive the 0-5Y ratio against AVG UIO if not present
    if age_group == '0-5Y' and ratio_col not in df.columns:
        if 'avg_uio_5y' in df.columns and 'total_0_5' in df.columns:
            df[ratio_col] = df.apply(
                lambda row: (
                    round(100 * row['total_0_5'] / row['avg_uio_5y'], 2)
                    if row['avg_uio_5y'] > 0 else 0
                ),
                axis=1,
            )
        else:
            ratio_col = 'ro_ratio_of_uio_5y'

    if (region_df is not None and not region_df.empty
            and age_group == '0-5Y'
            and ratio_col == 'ro_ratio_of_avg_uio_5y'
            and ratio_col not in region_df.columns
            and 'avg_uio_5y' in region_df.columns
            and 'total_0_5' in region_df.columns):
        region_df = region_df.copy()
        region_df[ratio_col] = region_df.apply(
            lambda row: (
                round(100 * row['total_0_5'] / row['avg_uio_5y'], 2)
                if row['avg_uio_5y'] > 0 else 0
            ),
            axis=1,
        )

    return {
        'fig_profit': ranked_bar(
            df, 'total_ro_cost', value_fmt='abbr', theme=theme,
            currency='RUB', region_df=region_df),
        'fig_mh': ranked_bar(
            df, lh_col, value_fmt='abbr', theme=theme,
            region_df=region_df),
        'fig_avg_mh': ranked_bar(
            df, 'aver_labor_hours_per_vhc', value_fmt='float1',
            theme=theme, region_df=region_df),
        'fig_avg_check': ranked_bar(
            df, 'avg_ro_cost', value_fmt='abbr', theme=theme,
            currency='RUB', region_df=region_df),
        'fig_ratio': ranked_bar(
            df, ratio_col, value_fmt='pct1', theme=theme,
            region_df=region_df),
        'fig_ro_years': age_groups(
            df, age_group=age_group, theme=theme),
    }
