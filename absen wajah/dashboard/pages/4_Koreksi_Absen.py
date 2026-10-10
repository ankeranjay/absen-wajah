import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth_check import require_login
require_login()

import pandas as pd
from datetime import date
from utils import query, execute

st.set_page_config(page_title="Koreksi Absen", page_icon="", layout="wide")
st.markdown("# Koreksi & Absen Manual")

tab1, tab2, tab3 = st.tabs([" Tambah Absen Manual", " Edit Absen", " Hapus Absen"])

# ==== TAB 1: TAMBAH ====
with tab1:
    st.subheader("Tambah Absen Manual")
    st.caption("Untuk siswa yang sakit/izin atau tidak sempat lewat kiosk.")

    df_siswa = query("SELECT nis, nama, kelas FROM siswa WHERE aktif=1 ORDER BY kelas, nama")

    with st.form("tambah_absen"):
        col1, col2 = st.columns(2)
        with col1:
            pilihan = st.selectbox(
                "Pilih siswa",
                options=df_siswa["nis"].tolist(),
                format_func=lambda nis: f"{nis} - {df_siswa[df_siswa['nis']==nis]['nama'].values[0]} ({df_siswa[df_siswa['nis']==nis]['kelas'].values[0]})"
            )
        with col2:
            tanggal = st.date_input("Tanggal", value=date.today())

        col3, col4 = st.columns(2)
        with col3:
            status = st.selectbox("Status", ["Hadir", "Terlambat", "Izin", "Sakit", "Alpa"])
        with col4:
            jam = st.text_input("Jam masuk (HH:MM:SS)", value="07:00:00")

        submit = st.form_submit_button(" Simpan", use_container_width=True)

        if submit:
            tgl_str = tanggal.strftime("%Y-%m-%d")
            # Cek sudah ada
            ada = query("SELECT id FROM kehadiran WHERE nis=? AND tanggal=?", (pilihan, tgl_str))
            if not ada.empty:
                st.error(f" Siswa ini sudah absen pada {tgl_str}. Gunakan tab Edit.")
            else:
                execute("""
                    INSERT INTO kehadiran (nis, tanggal, jam_masuk, status)
                    VALUES (?, ?, ?, ?)
                """, (pilihan, tgl_str, jam, status))
                st.success(f" Absen ditambahkan: {pilihan} · {tgl_str} · {status}")
                st.rerun()

# ==== TAB 2: EDIT ====
with tab2:
    st.subheader("Edit Absen")
    tanggal_filter = st.date_input("Filter tanggal", value=date.today(), key="edit_tgl")
    tgl_str = tanggal_filter.strftime("%Y-%m-%d")

    df = query("""
        SELECT k.id, s.nis, s.nama, s.kelas, k.jam_masuk, k.status
        FROM kehadiran k JOIN siswa s ON k.nis = s.nis
        WHERE k.tanggal = ?
        ORDER BY s.kelas, s.nama
    """, (tgl_str,))

    if df.empty:
        st.info(f"Tidak ada absen pada {tgl_str}.")
    else:
        df["label"] = df["nis"] + " - " + df["nama"] + " (" + df["kelas"] + ")"
        pilihan_id = st.selectbox("Pilih absen yang diedit", df["id"].tolist(),
                                  format_func=lambda i: df[df["id"]==i]["label"].values[0])

        row = df[df["id"] == pilihan_id].iloc[0]

        with st.form("edit_absen"):
            col1, col2 = st.columns(2)
            with col1:
                jam_baru = st.text_input("Jam masuk", value=row["jam_masuk"] or "")
            with col2:
                status_baru = st.selectbox(
                    "Status",
                    ["Hadir", "Terlambat", "Izin", "Sakit", "Alpa"],
                    index=["Hadir", "Terlambat", "Izin", "Sakit", "Alpa"].index(row["status"]) if row["status"] in ["Hadir","Terlambat","Izin","Sakit","Alpa"] else 0
                )
            submit = st.form_submit_button(" Update", use_container_width=True)

            if submit:
                execute("UPDATE kehadiran SET jam_masuk=?, status=? WHERE id=?",
                        (jam_baru, status_baru, pilihan_id))
                st.success(" Absen diperbarui")
                st.rerun()

# ==== TAB 3: HAPUS ====
with tab3:
    st.subheader("Hapus Absen")
    tanggal_hapus = st.date_input("Filter tanggal", value=date.today(), key="hapus_tgl")
    tgl_str = tanggal_hapus.strftime("%Y-%m-%d")

    df_hapus = query("""
        SELECT k.id, s.nis, s.nama, s.kelas, k.jam_masuk, k.status
        FROM kehadiran k JOIN siswa s ON k.nis = s.nis
        WHERE k.tanggal = ?
        ORDER BY s.kelas, s.nama
    """, (tgl_str,))

    if df_hapus.empty:
        st.info("Tidak ada data.")
    else:
        df_hapus["label"] = df_hapus["nis"] + " - " + df_hapus["nama"] + " (" + df_hapus["kelas"] + ")"
        pilihan_hapus = st.selectbox("Pilih yang dihapus", df_hapus["id"].tolist(),
                                     format_func=lambda i: df_hapus[df_hapus["id"]==i]["label"].values[0],
                                     key="pilih_hapus")
        st.warning(" Data yang dihapus tidak bisa dikembalikan!")
        if st.button(" Hapus", type="primary"):
            execute("DELETE FROM kehadiran WHERE id=?", (pilihan_hapus,))
            st.success(" Absen dihapus")
            st.rerun()