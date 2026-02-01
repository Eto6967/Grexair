import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from datetime import datetime, timedelta
import config

def clean_columns(df):
    if df is None: return None
    df.columns = [str(c).strip().replace('ï»¿', '').replace('Idő', 'Ido') for c in df.columns]
    return df

def get_series_stats(series, x_axis, unit="", date_source=None):
    """
    Min/Max kereső. A pozíciót (x_axis) és a feliratot (date_source) külön kezeli.
    """
    if series is None or len(series) == 0: return None
    
    vals = series.values if isinstance(series, pd.Series) else series
    if len(vals) == 0 or np.all(np.isnan(vals)): return None

    idx_min = np.nanargmin(vals)
    idx_max = np.nanargmax(vals)
    
    val_min = vals[idx_min]
    val_max = vals[idx_max]
    
    # Pozíció (szám)
    if isinstance(x_axis, pd.Series):
        x_min = x_axis.iloc[idx_min]
        x_max = x_axis.iloc[idx_max]
    else:
        x_min = x_axis[idx_min]
        x_max = x_axis[idx_max]

    txt_min = f"{val_min:.1f} {unit}"
    txt_max = f"{val_max:.1f} {unit}"

    # Dátum felirat keresése
    ts_min = None
    ts_max = None

    if date_source is not None:
        if isinstance(date_source, pd.Series):
            ts_min = date_source.iloc[idx_min]
            ts_max = date_source.iloc[idx_max]
        else:
            ts_min = date_source[idx_min]
            ts_max = date_source[idx_max]
    elif isinstance(x_min, (pd.Timestamp, datetime)):
        ts_min = x_min
        ts_max = x_max

    def format_date_label(txt, ts):
        if ts is not None and not pd.isna(ts):
            try:
                date_str = ts.strftime("%Y.%m.%d %H:%M")
                return txt + f"<br><span style='font-size:10px; font-weight:normal; opacity:0.8'>{date_str}</span>"
            except:
                pass
        return txt

    txt_min = format_date_label(txt_min, ts_min)
    txt_max = format_date_label(txt_max, ts_max)

    return {
        'min': {'x': x_min, 'y': val_min, 'text': txt_min},
        'max': {'x': x_max, 'y': val_max, 'text': txt_max}
    }

def process_data(df, mode='demo'):
    if df is None or df.empty: return None

    df = clean_columns(df)
    co2_col = 'CO2_ppm'
    if co2_col not in df.columns: return None

    df[co2_col] = pd.to_numeric(df[co2_col], errors='coerce')
    df = df.dropna(subset=[co2_col])

    # Időoszlop
    if 'ParsedTime' not in df.columns:
        if 'Ido' in df.columns:
            df['ParsedTime'] = pd.to_datetime(df['Ido'], errors='coerce')
        else:
            df['ParsedTime'] = pd.NaT

    # Mindig kiszámoljuk az egyenletes perceket (ez a TRÜKK a stabil grafikonhoz)
    if df['ParsedTime'].notna().any():
        df = df.sort_values(by='ParsedTime')
        start_t = df['ParsedTime'].iloc[0]
        minutes = (df['ParsedTime'] - start_t).dt.total_seconds() / 60
    else:
        minutes = pd.Series(np.arange(len(df)))

    # Tengely beállítása:
    # Mindig 'minutes' (számok) lesz a tengely, hogy ne torzuljon a görbe.
    x_axis = minutes
    use_date_axis = False # Kikapcsoljuk az automatikus dátumozást

    if len(df) == 0: return None

    # Dátumok előkészítése feliratnak
    date_source = df['ParsedTime'] if df['ParsedTime'].notna().any() else None

    # Ezt a listát küldjük át a rajzolónak az X tengely felirataihoz
    date_labels = []
    if date_source is not None:
        try:
            # Sortörés (<br>) hogy kiférjen
            date_labels = date_source.dt.strftime('%Y.%m.%d<br>%H:%M').tolist()
        except:
            date_labels = []

    # Matek
    window = min(config.WINDOW_SIZE, len(df))
    if window % 2 == 0: window -= 1
    
    vals = df[co2_col].values
    if window > 3:
        smooth = savgol_filter(vals, window, 2)
    else:
        smooth = vals
    
    speed = np.gradient(smooth, minutes)
    accel = np.gradient(speed, minutes)

    diffs = np.diff(minutes, prepend=minutes.iloc[0])
    if np.sum(diffs) == 0: diffs = np.ones(len(minutes))
    
    time_stats = [
        np.sum(diffs[smooth < 1000]),
        np.sum(diffs[(smooth >= 1000) & (smooth < 1500)]),
        np.sum(diffs[smooth >= 1500])
    ]

    stats = {
        'co2': get_series_stats(df[co2_col], x_axis, "ppm", date_source=date_source),
        'speed': get_series_stats(speed, x_axis, "ppm/perc", date_source=date_source),
        'accel': get_series_stats(accel, x_axis, "ppm/perc²", date_source=date_source)
    }

    return {
        'x': x_axis,
        'y_raw': df[co2_col],
        'y_smooth': smooth,
        'speed': speed,
        'accel': accel,
        'time_stats': time_stats,
        'use_date_axis': use_date_axis,
        'stats': stats,
        'date_labels': date_labels # <--- Itt adjuk át a dátumokat!
    }