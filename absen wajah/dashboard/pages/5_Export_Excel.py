import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_check import require_login
require_login()

import pandas as pd
from datetime import date
from io import BytesIO
from utils import query

st.set_page_config(page_title="Export Excel", page_icon="", layout="wide")
st.markdown("#  Export Data ke Excel")

st.markdown("### Pilih periode dan filter")

col1, col2 = st.columns(2)
with col1:
    jenis = st.radio("Jenis export", ["Harian", "Bulanan", "Semua"])
with col2:
    if jenis == "Harian":
        tgl = st.date_input("Tanggal", value=date.today())
        tgl_str = tgl.strftime("%Y-%m-%d")
    elif jenis == "Bulanan":
        bulan = st.selectbox("Bulan", list(range(1, 13)), index=date.today().month - 1,
                             format_func=lambda m: ["Januari","Februari","Maret","April","Mei","Juni",
                                                    "Juli","Agustus","September","Oktober","November","Desember"][m-1])
        tahun = st.number_input("Tahun", 2020, 2100, date.today().year)
        prefix = f"{tahun:04d}-{bulan:02d}"
    else:
        pass

# Query
if jenis == "Harian":
    sql = """
        SELECT s.nis AS NIS, s.nama AS Nama, s.kelas AS Kelas,
               k.tanggal AS Tanggal, k.jam_masuk AS "Jam Masuk", k.status AS Status
        FROM kehadiran k JOIN siswa s ON k.nis = s.nis
        WHERE k.tanggal = ?
        ORDER BY s.kelas, s.nama
    """
    df = query(sql, (tgl_str,))
elif jenis == "Bulanan":
    sql = """
        SELECT s.nis AS NIS, s.nama AS Nama, s.kelas AS Kelas,
               k.tanggal AS Tanggal, k.jam_masuk AS "Jam Masuk", k.status AS Status
        FROM kehadiran k JOIN siswa s ON k.nis = s.nis
        WHERE k.tanggal LIKE ?
        ORDER BY k.tanggal, s.kelas, s.nama
    """
    df = query(sql, (f"{prefix}%",))
else:
    sql = """
        SELECT s.nis AS NIS, s.nama AS Nama, s.kelas AS Kelas,
               k.tanggal AS Tanggal, k.jam_masuk AS "Jam Masuk", k.status AS Status
        FROM kehadiran k JOIN siswa s ON k.nis = s.nis
        ORDER BY k.tanggal DESC, s.kelas, s.nama
    """
    df = query(sql)

# Preview
st.markdown("### Preview")
if df.empty:
    st.warning("Tidak ada data untuk periode ini.")
    st.stop()

st.dataframe(df.head(50), use_container_width=True, hide_index=True)
st.caption(f"Total: {len(df)} baris (menampilkan 50 pertama)")

# Download
buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Absensi")
buffer.seek(0)

if jenis == "Harian":
    nama_file = f"absensi_{tgl_str}.xlsx"
elif jenis == "Bulanan":
    nama_file = f"absensi_{prefix}.xlsx"
else:
    nama_file = f"absensi_semua.xlsx"

st.download_button(
    label=" Download Excel",
    data=buffer,
    file_name=nama_file,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)