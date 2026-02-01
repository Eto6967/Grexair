import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# --- SZÍNEK ---
COLORS = {
    'bg': 'rgba(0,0,0,0)', 
    'raw': 'rgba(59, 130, 246, 0.25)',
    'trend': '#3b82f6',
    'trend_fill': 'rgba(59, 130, 246, 0.05)', 
    'speed': '#8b5cf6',
    'speed_fill': 'rgba(139, 92, 246, 0.05)',
    'accel': '#d946ef',
    'accel_fill': 'rgba(217, 70, 239, 0.05)',
    'grid': 'rgba(255, 255, 255, 0.06)', 
    'text_muted': '#737373',
    'text_main': '#d4d4d4',
    'max_color': '#ef4444', 
    'min_color': '#10b981', 
    'badge_bg': 'rgba(40, 40, 40, 0.85)', 
    'badge_border': 'rgba(255, 255, 255, 0.1)',
    'zone_good': 'rgba(16, 185, 129, 0.02)',
    'zone_warn': 'rgba(245, 158, 11, 0.02)',
    'zone_bad': 'rgba(239, 68, 68, 0.02)'
}

def add_labels(fig, stats, row_idx):
    """ Min/Max címkék a grafikonon """
    if not stats: return

    def add_marker(stat, color_text, label, ay):
        fig.add_trace(go.Scatter(
            x=[stat['x']], y=[stat['y']], 
            mode='markers',
            marker=dict(color=color_text, size=6, line=dict(width=1, color='rgba(255,255,255,0.5)')),
            showlegend=False, hoverinfo='skip'
        ), row=row_idx, col=1)

        fig.add_annotation(
            x=stat['x'], y=stat['y'],
            text=f"<span style='color:{COLORS['text_muted']}'>{label}</span> <span style='color:{color_text}; font-weight:bold;'>{stat['text']}</span>",
            showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=COLORS['text_muted'], ax=0, ay=ay,
            font=dict(size=11, family="Inter"), bgcolor=COLORS['badge_bg'], bordercolor=COLORS['badge_border'], borderwidth=1, borderpad=4, opacity=1, row=row_idx, col=1
        )

    add_marker(stats['max'], COLORS['max_color'], "MAX", -40)
    add_marker(stats['min'], COLORS['min_color'], "MIN", 40)

def create_figure(data):
    if not data: return go.Figure()

    # --- HOVER (Egérrávitel) SZÖVEG ---
    hover_text_list = None
    if 'date_labels' in data and data['date_labels'] and len(data['date_labels']) > 0:
        hover_text_list = [d.replace('<br>', ' ') for d in data['date_labels']]
    
    def get_hovertemplate(unit):
        if hover_text_list:
            return "<b>%{y:.1f} " + unit + "</b><br>%{customdata}<extra></extra>"
        else:
            return "<b>%{y:.1f} " + unit + "</b><br>%{x:.1f} perc<extra></extra>"

    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.08, # Kicsit növeltem a távolságot a feliratok miatt
        row_heights=[0.50, 0.20, 0.15, 0.15],
        subplot_titles=("", "", "", "")
    )

    # --- 1. SOR: CO2 ---
    fig.add_hrect(y0=0, y1=1000, fillcolor=COLORS['zone_good'], layer="below", line_width=0, row=1, col=1)
    fig.add_hrect(y0=1000, y1=1500, fillcolor=COLORS['zone_warn'], layer="below", line_width=0, row=1, col=1)
    fig.add_hrect(y0=1500, y1=5000, fillcolor=COLORS['zone_bad'], layer="below", line_width=0, row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data['x'], y=data['y_raw'],
        name="Nyers mérés",
        mode='lines', line=dict(color=COLORS['raw'], width=1),
        opacity=0.6, showlegend=True,
        customdata=hover_text_list if hover_text_list else data['x'],
        hovertemplate=get_hovertemplate("ppm")
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data['x'], y=data['y_smooth'], 
        name="Trend",
        mode='lines', line=dict(color=COLORS['trend'], width=2), 
        fill='tozeroy', fillcolor=COLORS['trend_fill'], showlegend=True,
        customdata=hover_text_list if hover_text_list else data['x'],
        hovertemplate=get_hovertemplate("ppm")
    ), row=1, col=1)
    
    add_labels(fig, data['stats']['co2'], 1)

    # --- ÉLŐ JELZÉS ---
    if data.get('is_live', False):
        try:
            last_x = data['x'].iloc[-1]
            last_y_raw = data['y_raw'].iloc[-1]
            
            live_text = f"🔴 ÉLŐ: <b>{int(last_y_raw)}</b> ppm"
            if 'date_labels' in data and data['date_labels'] and len(data['date_labels']) > 0:
                last_date = data['date_labels'][-1].replace('<br>', ' ')
                live_text += f"<br><span style='font-size:10px; font-weight:normal; opacity:0.9'>{last_date}</span>"

            fig.add_trace(go.Scatter(
                x=[last_x], y=[last_y_raw],
                mode='markers',
                marker=dict(color='#ef4444', size=8, line=dict(color='white', width=1.5)),
                showlegend=False, hoverinfo='skip'
            ), row=1, col=1)

            fig.add_annotation(
                x=last_x, y=last_y_raw,
                text=live_text,
                showarrow=True, arrowhead=0, arrowwidth=1, ax=0, ay=-60,
                bgcolor="rgba(239, 68, 68, 0.15)", bordercolor="#ef4444", borderwidth=1, borderpad=6,
                font=dict(size=12, color="#ef4444", family="Inter", weight="bold"),
                row=1, col=1
            )
        except Exception: pass

    fig.add_annotation(text="CO₂ Koncentráció", xref="paper", yref="paper", x=0.01, y=0.98, showarrow=False, font=dict(size=12, color=COLORS['text_main'], weight="bold"), row=1, col=1)

    # --- 2. SOR ---
    fig.add_trace(go.Scatter(
        x=data['x'], y=data['speed'], name="Sebesség",
        mode='lines', line=dict(color=COLORS['speed'], width=1.5),
        fill='tozeroy', fillcolor=COLORS['speed_fill'], showlegend=False,
        customdata=hover_text_list if hover_text_list else data['x'],
        hovertemplate=get_hovertemplate("ppm/perc")
    ), row=2, col=1)
    add_labels(fig, data['stats']['speed'], 2)
    fig.add_annotation(text="Változás sebessége", xref="paper", yref="paper", x=0.01, y=0.95, showarrow=False, font=dict(size=11, color=COLORS['text_muted']), row=2, col=1)

    # --- 3. SOR ---
    fig.add_trace(go.Scatter(
        x=data['x'], y=data['accel'], name="Gyorsulás",
        mode='lines', line=dict(color=COLORS['accel'], width=1.5),
        fill='tozeroy', fillcolor=COLORS['accel_fill'], showlegend=False,
        customdata=hover_text_list if hover_text_list else data['x'],
        hovertemplate=get_hovertemplate("ppm/perc²")
    ), row=3, col=1)
    add_labels(fig, data['stats']['accel'], 3)
    fig.add_annotation(text="Folyamat dinamikája", xref="paper", yref="paper", x=0.01, y=0.95, showarrow=False, font=dict(size=11, color=COLORS['text_muted']), row=3, col=1)

    # --- 4. SOR ---
    lbls = [f"{v:.1f} perc" for v in data['time_stats']]
    fig.add_trace(go.Bar(
        y=['JÓ', 'FIGYELEM', 'KRITIKUS'], x=data['time_stats'], orientation='h',
        marker_color=['#10b981', '#f59e0b', '#ef4444'],
        text=lbls, textposition='auto',
        textfont=dict(color='white', size=11, family="Inter"), showlegend=False,
        hoverinfo='skip'
    ), row=4, col=1)

    # --- LAYOUT ---
    fig.update_layout(
        height=1000, 
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=COLORS['text_muted'])),
        margin=dict(t=60, b=30, l=40, r=40),
        font=dict(family="Inter, sans-serif", size=11, color=COLORS['text_muted']),
        hovermode="x unified", 
        hoverlabel=dict(bgcolor="#171717", bordercolor="#333", font_size=12)
    )

    axis_config = dict(
        showgrid=True, gridcolor=COLORS['grid'], gridwidth=1,
        zeroline=False, showline=False,
        tickfont=dict(color=COLORS['text_muted']),
    )
    fig.update_yaxes(**axis_config)

    # --- TENGELY FELIRATOK KEZELÉSE ---
    # Beállítjuk a formátumot (Dátum vagy Szám)
    if 'date_labels' in data and data['date_labels'] and len(data['date_labels']) > 0:
        total_points = len(data['x'])
        num_ticks = 6
        if total_points > num_ticks:
            tick_indices = np.linspace(0, total_points - 1, num_ticks, dtype=int)
            tick_vals = [data['x'].iloc[i] for i in tick_indices]
            tick_text = [data['date_labels'][i] for i in tick_indices]
        else:
            tick_vals = data['x']
            tick_text = data['date_labels']

        fig.update_xaxes(
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_text,
            **axis_config
        )
    elif data.get('use_date_axis', False):
        fig.update_xaxes(type='date', tickformat="%H:%M", **axis_config)
    else:
        fig.update_xaxes(**axis_config)

    # --- KÉRÉS: MINDEN GRAFIKONON JELENJEN MEG A FELIRAT ---
    x_title = "Eltelt idő (perc)" if not ('date_labels' in data and data['date_labels']) else ""
    
    # Végigmegyünk mind a 4 soron és kényszerítjük a megjelenítést
    for r in [1, 2, 3, 4]:
        # A 'showticklabels=True' biztosítja, hogy a shared_xaxes ellenére is látsszon
        # Az x_title-t csak a legalsóra (4) tesszük ki, hogy ne legyen túl sok szövegismétlés,
        # de a számok/dátumok (tick-ek) mindegyiken ott lesznek.
        title = x_title if r == 4 else ""
        fig.update_xaxes(showticklabels=True, title_text=title, row=r, col=1)

    return fig