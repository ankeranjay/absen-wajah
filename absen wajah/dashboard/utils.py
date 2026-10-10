import sqlite3
import pandas as pd
import os
from datetime import datetime

# Path absolut ke database (biar bisa dijalankan dari mana saja)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "absensi.db")

USERNAME = "MANSE"
PASSWORD = "m4ns311j4ka7t4s31at4n"

def check_login(username, password):
    return username == USERNAME and password == PASSWORD

def get_conn():
    return sqlite3.connect(DB_PATH)

def query(sql, params=()):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

def execute(sql, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(sql, params)
    conn.commit()
    conn.close()

def get_pengaturan(key):
    conn = get_conn()
    row = conn.execute("SELECT value FROM pengaturan WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else None

def set_pengaturan(key, value):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO pengaturan (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()

def hari_indo(tgl_str):
    """Ubah 2026-10-10 -> 'Sabtu, 10 Oktober 2026'"""
    hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    bulan = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
             "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    d = datetime.strptime(tgl_str, "%Y-%m-%d")
    return f"{hari[d.weekday()]}, {d.day} {bulan[d.month]} {d.year}"