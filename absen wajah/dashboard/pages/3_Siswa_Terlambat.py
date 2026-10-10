import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_check import require_login
require_login()

from datetime import date
from utils import query

st.set_page_config(page_title="Siswa Terlambat", page_icon="", layout="wide")
st.markdown("#  Siswa Sering Terlambat")

col1, col2 = st.columns(2)
with col1:
    bulan = st.selectbox("Bulan", list(range(1, 13)), index=date.today().month - 1,
                         format_func=lambda m: ["Januari","Februari","Maret","April","Mei","Juni",
                                                "Juli","Agustus","September","Oktober","November","Desember"][m-1])
with col2:
    tahun = st.number_input("Tahun", min_value=2020, max_value=2100, value=date.today().year)

prefix = f"{tahun:04d}-{bulan:02d}"

df = query("""
    SELECT s.nis AS NIS, s.nama AS Nama, s.kelas AS Kelas,
           COUNT(*) AS "Jumlah Terlambat"
    FROM kehadiran k
    JOIN siswa s ON k.nis = s.nis
    WHERE k.status = 'Terlambat' AND k.tanggal LIKE ?
    GROUP BY s.nis
    HAVING COUNT(*) > 0
    ORDER BY COUNT(*) DESC
""", (f"{prefix}%",))

if not df.empty:
    st.warning(f" Ditemukan {len(df)} siswa dengan keterlambatan bulan ini")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.success(" Tidak ada siswa terlambat bulan ini. Mantap!")

st.markdown("---")
st.markdown("###  Grafik 10 Siswa Terlambat Terbanyak")
if not df.empty:
    top10 = df.head(10)
    st.bar_chart(top10.set_index("Nama")["Jumlah Terlambat"])