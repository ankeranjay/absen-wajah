import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_check import require_login
require_login()

import pandas as pd
from datetime import date, datetime
from utils import query

st.set_page_config(page_title="Rekap Hari Ini", page_icon="", layout="wide")
st.markdown("#  Rekap Kehadiran Hari Ini")

tanggal = st.date_input("Pilih tanggal", value=date.today())
tgl_str = tanggal.strftime("%Y-%m-%d")

# Ringkasan
total = query("SELECT COUNT(*) AS n FROM siswa WHERE aktif=1").iloc[0]["n"]
hadir = query("SELECT COUNT(*) AS n FROM kehadiran WHERE tanggal=? AND status='Hadir'", (tgl_str,)).iloc[0]["n"]
terlambat = query("SELECT COUNT(*) AS n FROM kehadiran WHERE tanggal=? AND status='Terlambat'", (tgl_str,)).iloc[0]["n"]
alpa = total - hadir - terlambat

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Siswa", total)
col2.metric(" Hadir", hadir)
col3.metric(" Terlambat", terlambat)
col4.metric(" Belum Absen", alpa)

st.markdown("---")

# Rekap per kelas
st.subheader(" Rekap Per Kelas")
df_kelas = query("""
    SELECT s.kelas,
           COUNT(DISTINCT s.nis) AS total,
           COUNT(CASE WHEN k.status='Hadir' THEN 1 END) AS hadir,
           COUNT(CASE WHEN k.status='Terlambat' THEN 1 END) AS terlambat
    FROM siswa s
    LEFT JOIN kehadiran k ON s.nis = k.nis AND k.tanggal = ?
    WHERE s.aktif = 1
    GROUP BY s.kelas
    ORDER BY s.kelas
""", (tgl_str,))

if not df_kelas.empty:
    df_kelas["belum_absen"] = df_kelas["total"] - df_kelas["hadir"] - df_kelas["terlambat"]
    df_kelas["kehadiran_%"] = ((df_kelas["hadir"] + df_kelas["terlambat"]) / df_kelas["total"] * 100).round(1)
    st.dataframe(df_kelas, use_container_width=True, hide_index=True)
else:
    st.info("Belum ada data kelas.")

st.markdown("---")

# Detail absen
st.subheader(" Detail Absensi")
df_detail = query("""
    SELECT s.nis AS NIS, s.nama AS Nama, s.kelas AS Kelas,
           k.jam_masuk AS "Jam Masuk", k.status AS Status
    FROM kehadiran k
    JOIN siswa s ON k.nis = s.nis
    WHERE k.tanggal = ?
    ORDER BY s.kelas, s.nama
""", (tgl_str,))

if not df_detail.empty:
    filter_kelas = st.selectbox("Filter kelas", ["Semua"] + sorted(df_detail["Kelas"].unique().tolist()))
    if filter_kelas != "Semua":
        df_detail = df_detail[df_detail["Kelas"] == filter_kelas]

    st.dataframe(df_detail, use_container_width=True, hide_index=True)
    st.caption(f"Total: {len(df_detail)} baris")
else:
    st.warning("Belum ada absensi pada tanggal ini.")

st.markdown("---")

# Siswa belum absen
st.subheader(" Siswa Belum Absen")
df_belum = query("""
    SELECT s.nis AS NIS, s.nama AS Nama, s.kelas AS Kelas
    FROM siswa s
    LEFT JOIN kehadiran k ON s.nis = k.nis AND k.tanggal = ?
    WHERE s.aktif = 1 AND k.id IS NULL
    ORDER BY s.kelas, s.nama
""", (tgl_str,))

if not df_belum.empty:
    st.dataframe(df_belum, use_container_width=True, hide_index=True)
    st.caption(f"Total: {len(df_belum)} siswa belum absen")
else:
    st.success(" Semua siswa sudah absen!")