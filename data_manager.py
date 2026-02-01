import pandas as pd
import numpy as np
import os
import config
from sqlalchemy import create_engine, text

# --- ADATBÁZIS KAPCSOLAT INICIALIZÁLÁSA ---
db_engine = None

if hasattr(config, 'DB_URL') and config.DB_URL:
    try:
        # pool_pre_ping=True: Stabilabb kapcsolat, újrapróbálkozik, ha megszakadt
        db_engine = create_engine(config.DB_URL, pool_pre_ping=True)
        print("✅ Adatbázis motor inicializálva.")
    except Exception as e:
        print(f"❌ DB Init Hiba: {e}")

# --- SQL ADATOLVASÁS (MONITORHOZ) ---
def get_latest_sensor_data(limit=100):
    """
    Kiolvassa a legfrissebb 'limit' darab mérést a Neon adatbázisból.
    """
    if db_engine is None:
        print("⚠️ Nincs adatbázis kapcsolat!")
        return pd.DataFrame()

    try:
        # 1. SQL Lekérdezés
        query = text(f"""
            SELECT timestamp as "Ido", co2_ppm as "CO2_ppm"
            FROM sensor_data
            ORDER BY timestamp DESC
            LIMIT {limit}
        """)
        
        with db_engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        if df.empty:
            return df

        # 2. Sorbarendezés időrendben (régi -> új)
        df = df.sort_values(by='Ido')
        
        # 3. IDŐ JAVÍTÁSA
        # - utc=True: Hogy egységes legyen
        df['ParsedTime'] = pd.to_datetime(df['Ido'], utc=True, errors='coerce')
        
        # --- IDŐZÓNA KORREKCIÓ: +1 ÓRA ---
        df['ParsedTime'] = df['ParsedTime'] + pd.Timedelta(hours=1)
        
        # - tz_localize(None): Leszedjük az időzónát a Plotly kompatibilitáshoz
        df['ParsedTime'] = df['ParsedTime'].dt.tz_localize(None)
        
        # Kidobjuk, ami hibás lett
        df = df.dropna(subset=['ParsedTime'])

        if df.empty: return pd.DataFrame()

        # 4. Relatív percek (X tengelyhez)
        start_time = df['ParsedTime'].iloc[0]
        df['Minutes'] = (df['ParsedTime'] - start_time).dt.total_seconds() / 60
            
        return df

    except Exception as e:
        print(f"❌ SQL Olvasási Hiba: {e}")
        return pd.DataFrame()


# --- CSV ADATOLVASÁS (DEMO / UPLOAD MÓDHOZ) ---
def load_and_clean_data(filename):
    """
    CSV fájlok betöltése.
    """
    if not os.path.exists(filename):
        return pd.DataFrame()

    try:
        df = pd.read_csv(filename, sep=None, engine='python', on_bad_lines='skip')
        
        # Oszlopnevek tisztítása
        df.columns = [str(c).strip().replace('ï»¿', '').replace('Idő', 'Ido') for c in df.columns]

        # CO2 keresése
        co2_col = next((c for c in df.columns if 'co2' in c.lower()), None)
        if not co2_col: return pd.DataFrame()
        
        df.rename(columns={co2_col: 'CO2_ppm'}, inplace=True)
        df['CO2_ppm'] = pd.to_numeric(df['CO2_ppm'], errors='coerce')
        df = df.dropna(subset=['CO2_ppm'])

        # Idő kezelése
        if 'Ido' in df.columns:
            df['ParsedTime'] = pd.to_datetime(df['Ido'], errors='coerce')
        else:
            df['ParsedTime'] = pd.NaT

        df = df.dropna(subset=['ParsedTime'])

        # Sorbarendezés és percek
        if not df.empty:
            df = df.sort_values(by='ParsedTime')
            start_t = df['ParsedTime'].iloc[0]
            df['Minutes'] = (df['ParsedTime'] - start_t).dt.total_seconds() / 60
        else:
            df['Minutes'] = pd.Series(np.arange(len(df)))

        return df

    except Exception as e:
        print(f"Fájl Olvasási Hiba: {e}")
        return pd.DataFrame()

# --- KÖZÖS SEGÉDFÜGGVÉNYEK ---
def calculate_kpi(df):
    """KPI számítás (Átlag, Min, Max)."""
    if df.empty or 'CO2_ppm' not in df.columns:
        return {'current': '-', 'avg': '-', 'max': '-', 'min': '-'}
    
    return {
        'current': int(df['CO2_ppm'].iloc[-1]),
        'avg': int(df['CO2_ppm'].mean()),
        'max': int(df['CO2_ppm'].max()),
        'min': int(df['CO2_ppm'].min())
    }

def get_status(value):
    """Státusz szöveg és színkód."""
    if not isinstance(value, (int, float)): return "Nincs adat", "status-neutral"
    
    if value < 800: 
        return "KIVÁLÓ", "status-good"
    if value < 1200: 
        return "ELFOGADHATÓ", "status-warning"
    
    return "VESZÉLYES", "status-danger"