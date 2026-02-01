import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- SZÍNPALETTA (Sötét Téma) ---
COLORS = {
    'bg': 'rgba(0,0,0,0)', # Átlátszó háttér
    'text': '#cfd8dc',
    'grid': '#3a3a3a',
    'raw': '#5DADE2',
    'trend': '#23a6d5',   
    'speed': '#1f77b4',   
    'accel': '#9467bd',   
    'max': '#ff5252',     
    'min': '#69f0ae',    
}

def create_base_figure(x_label_bottom, mode):
    """Létrehozza az üres, 4 soros vásznat."""
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.08, 
        row_heights=[0.4, 0.2, 0.2, 0.2],
        subplot_titles=(
            "1. CO₂ koncentráció (ppm)", 
            "2. Változás sebessége", 
            "3. Gyorsulás", 
            "4. Időmérleg"
        )
    )
    return fig

def add_trace_with_markers(fig, x_vals, y_vals, row, name, color, stats=None, show_fill=False):
    """Hozzáad egy görbét, opcionálisan Min/Max jelölőkkel."""
    fill_arg = 'tozeroy' if show_fill else None
    
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals, name=name,
        line=dict(color=color, width=2),
        fill=fill_arg
    ), row=row, col=1)

    if stats:
        # MAX jelölő
        fig.add_annotation(
            x=x_vals[stats['max_idx']], y=stats['max_val'],
            text="MAX", showarrow=True, arrowhead=2, ay=-30,
            font=dict(color=COLORS['max']), bordercolor=COLORS['max'],
            row=row, col=1
        )
        # MIN jelölő
        fig.add_annotation(
            x=x_vals[stats['min_idx']], y=stats['min_val'],
            text="MIN", showarrow=True, arrowhead=2, ay=30,
            font=dict(color=COLORS['min']), bordercolor=COLORS['min'],
            row=row, col=1
        )

def create_bar_chart(fig, values):
    """Létrehozza az alsó sávdiagramot."""
    fig.add_trace(go.Bar(
        y=['JÓ', 'KÖZEPES', 'ROSSZ'],
        x=values,
        orientation='h',
        marker_color=['#66cc99', '#f0ad4e', '#d9534f'],
        text=[f"{v:.1f} perc" for v in values], 
        textposition='auto'
    ), row=4, col=1)

def apply_layout(fig, mode):
    """Beállítja a végső formázást."""
    fig.update_layout(
        height=1400,
        template='plotly_dark',
        paper_bgcolor=COLORS['bg'],
        plot_bgcolor=COLORS['bg'],
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    # JAVÍTÁS: Ha nem Demo mód (hanem Monitor), akkor DÁTUM tengely
    if mode != 'demo':
        fig.update_xaxes(type='date')
        fig.update_xaxes(tickformat="%H:%M:%S") # Csak óra:perc:mp

    return fig