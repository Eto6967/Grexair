import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

def prepare_data(df, window_size=15):
    """Elvégzi a simítást és a deriváltak számítását."""
    if df is None or df.empty:
        return df

    # 1. Simítás (Trend)
    # Ha nincs elég adat, nem simítunk, csak másolunk
    effective_window = min(window_size, len(df))
    if effective_window % 2 == 0: effective_window -= 1 # Páratlannak kell lennie

    if len(df) > 5 and effective_window > 3:
        df['CO2_smooth'] = savgol_filter(df['CO2_ppm'], effective_window, 2)
    else:
        df['CO2_smooth'] = df['CO2_ppm']

    # 2. Sebesség (1. derivált)
    df['speed'] = np.gradient(df['CO2_smooth'], df['Minutes'])
    
    # 3. Gyorsulás (2. derivált)
    df['accel'] = np.gradient(df['speed'], df['Minutes'])

    return df

def get_stats(series):
    """Megkeresi a Min, Max indexeket és értékeket."""
    if series is None or series.empty:
        return None
        
    idx_min = series.idxmin()
    idx_max = series.idxmax()
    
    return {
        'min_idx': idx_min,
        'min_val': series.loc[idx_min],
        'max_idx': idx_max,
        'max_val': series.loc[idx_max]
    }

def get_time_balance(df):
    """Kiszámolja, mennyi időt töltöttünk a zónákban."""
    if df is None or df.empty:
        return [0, 0, 0]

    # Időkülönbségek (dt)
    dt = np.diff(df['Minutes'], prepend=df['Minutes'].iloc[0])
    # Ha minden 0 (pl. hiba), akkor egységnyi
    if np.sum(dt) == 0: dt = np.ones(len(df))

    vals = df['CO2_smooth'].values
    
    time_good = np.sum(dt[vals < 1000])
    time_medium = np.sum(dt[(vals >= 1000) & (vals < 1500)])
    time_bad = np.sum(dt[vals >= 1500])
    
    return [time_good, time_medium, time_bad]