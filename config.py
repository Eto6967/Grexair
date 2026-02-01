import os

# --- FÁJLOK ---
# A Demo módhoz megmarad a CSV, de a SENSOR.CSV már nem kell, 
# mert az adatbázisból olvassuk az élő adatokat.
FILE_DEMO = 'DATA.CSV'

# --- ADATBÁZIS KAPCSOLAT (ÚJ RÉSZ) ---
# A Renderen a rendszer a környezeti változókból (Environment Variable) olvassa ki.
# Ha nem találja (pl. a saját gépeden futtatod), akkor ezt a beégetett címet használja fallback-ként.
DB_URL = os.environ.get('DB_URL', "postgresql://neondb_owner:npg_XOSHJid94uCK@ep-delicate-smoke-agrpz918-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")

# --- GRAFIKON BEÁLLÍTÁSOK ---
WINDOW_SIZE = 15   # Simítás mértéke (maradt a régiben is)
MAX_POINTS = 2000  # Maximum pontok száma (teljesítmény optimalizálás)
