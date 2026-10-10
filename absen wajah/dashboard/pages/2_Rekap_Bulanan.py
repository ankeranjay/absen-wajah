import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_check import require_login
require_login()

import pandas as pd
from datetime import date
from utils import query, hari_indo

st.set_page_config(page_title="Rekap Bulanan", page_icon="", layout="wide")
st.markdown("#  Rekap Bulanan")

col1, col2 = st.columns(2)
with col1:
    bulan = st.selectbox("Bulan", list(range(1, 13)), index=date.today().month - 1,
                         format_func=lambda m: ["Januari","Februari","Maret","April","Mei","Juni",
                                                "Juli","Agustus","September","Oktober","November","Desember"][m-1])
with col2:
    tahun = st.number_input("Tahun", min_value=2020, max_value=2100, value=date.today().year)

prefix = f"{tahun:04d}-{bulan:02d}"

# Ringkasan bulan
total_hari = query("""
    SELECT COUNT(DISTINCT tanggal) AS n FROM kehadiran
    WHERE tanggal LIKE ?
""", (f"{prefix}%",)).iloc[0]["n"]

st.metric("Hari dengan Absensi", total_hari)

st.markdown("---")

# Rekap per siswa
st.subheader(" Rekap Per Siswa")
df = query("""
    SELECT s.nis AS NIS, s.nama AS Nama, s.kelas AS Kelas,
           COUNT(CASE WHEN k.status='Hadir' THEN 1 END) AS Hadir,
           COUNT(CASE WHEN k.status='Terlambat' THEN 1 END) AS Terlambat,
           COUNT(CASE WHEN k.status='Izin' THEN 1 END) AS Izin,
           COUNT(CASE WHEN k.status='Sakit' THEN 1 END) AS Sakit
    FROM siswa s
    LEFT JOIN kehadiran k ON s.nis = k.nis AND k.tanggal LIKE ?
    WHERE s.aktif = 1
    GROUP BY s.nis
    ORDER BY s.kelas, s.nama
""", (f"{prefix}%",))

if not df.empty:
    filter_kelas = st.selectbox("Filter kelas", ["Semua"] + sorted(df["Kelas"].unique().tolist()))
    if filter_kelas != "Semua":
        df = df[df["Kelas"] == filter_kelas]

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Total: {len(df)} siswa")
else:
    st.warning("Belum ada data bulan ini.")