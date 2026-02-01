import graf_math
import graf_draw

def get_graph_html(df, mode='demo', is_live=False):
    """
    Fő vezérlő.
    Most már elfogadja az is_live paramétert is a feliratozáshoz.
    """
    # 1. Matek
    processed_data = graf_math.process_data(df, mode=mode)
    
    if processed_data is None:
        return "<div style='text-align:center; padding:50px;'>Nincs elegendő adat.</div>"
    
    # MÓDOSÍTÁS: Beletesszük a csomagba az infót
    processed_data['is_live'] = is_live

    # 2. Rajzolás
    fig = graf_draw.create_figure(processed_data)
    
    return fig.to_html(full_html=False, config={'displayModeBar': False})