import streamlit as st
import os
from datetime import datetime, date
from utils import check_login, query, get_pengaturan

# ==== CARI LOGO OTOMATIS ====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(BASE_DIR, "assets")

def cari_logo():
    if not os.path.exists(LOGO_DIR):
        return None
    for nama in os.listdir(LOGO_DIR):
        if nama.lower().startswith("logo."):
            return os.path.join(LOGO_DIR, nama)
    return None

LOGO_PATH = cari_logo()

# ==== KONFIGURASI HALAMAN ====
st.set_page_config(
    page_title="Dashboard Absensi - MAN 11 Jakarta Selatan",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==== TEMA CERAH HIJAU-EMAS ====
st.markdown("""
<style>
    /* Background utama cerah */
    .stApp {
        background: linear-gradient(180deg, #f0f7f2 0%, #ffffff 100%);
    }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #2d7a4a 0%, #4a9d68 100%);
        padding: 20px 28px;
        border-radius: 12px;
        margin-bottom: 22px;
        border-left: 6px solid #e6c757;
        box-shadow: 0 4px 14px rgba(45, 122, 74, 0.18);
    }
    .main-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.3px;
    }
    .main-header p {
        color: #f5f0d8;
        margin: 6px 0 0 0;
        font-size: 13px;
    }

    /* Kartu metric */
    div[data-testid="stMetric"] {
        background: #ffffff;
        padding: 18px 20px;
        border-radius: 10px;
        border-left: 5px solid #2d7a4a;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
    }
    div[data-testid="stMetric"] label {
        color: #4a6b58 !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #1a4d2e !important;
        font-weight: 700;
    }

    /* Tombol */
    .stButton>button {
        background: linear-gradient(135deg, #2d7a4a 0%, #4a9d68 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 22px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4a9d68 0%, #2d7a4a 100%);
        color: #e6c757;
        box-shadow: 0 4px 12px rgba(45, 122, 74, 0.3);
    }

    /* Sidebar cerah */
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #eaf6ee 0%, #ffffff 100%);
        border-right: 1px solid #d4e6d9;
    }
    div[data-testid="stSidebar"] * {
        color: #1a4d2e !important;
    }
    div[data-testid="stSidebar"] a {
        color: #2d7a4a !important;
        font-weight: 500;
    }
    div[data-testid="stSidebar"] a:hover {
        background-color: rgba(45, 122, 74, 0.08) !important;
        border-radius: 6px;
    }
    div[data-testid="stSidebar"] hr {
        border-color: #c8e0cf;
    }

    /* Judul h1/h2/h3 */
    h1, h2, h3 {
        color: #1a4d2e !important;
    }

    /* Tabel */
    div[data-testid="stDataFrame"] {
        border: 1px solid #d4e6d9;
        border-radius: 8px;
        overflow: hidden;
    }

    /* Divider */
    hr {
        border-color: #d4e6d9;
    }
</style>
""", unsafe_allow_html=True)

# ==== LOGIN ====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        # Logo di tengah
        if LOGO_PATH:
            logo_col1, logo_col2, logo_col3 = st.columns([1, 1, 1])
            with logo_col2:
                st.image(LOGO_PATH, use_container_width=True)
        else:
            st.warning("Logo tidak ditemukan di folder assets/")

        st.markdown("""
        <div style='text-align: center; margin-top: 10px;'>
            <h1 style='color: #1a4d2e; margin-bottom: 0; font-size: 28px;'>Dashboard Absensi</h1>
            <p style='color: #4a6b58; margin-top: 6px; font-size: 15px;'>MAN 11 Jakarta Selatan</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Masukkan username")
            password = st.text_input("Password", type="password", placeholder="Masukkan password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Username atau password salah")

    st.stop()

# ==== HEADER (setelah login) ====
col_logo, col_title = st.columns([1, 8])
with col_logo:
    if LOGO_PATH:
        st.image(LOGO_PATH, width=80)
with col_title:
    st.markdown(f"""
    <div class="main-header">
        <h1>Dashboard Absensi Wajah</h1>
        <p>MAN 11 Jakarta Selatan · {datetime.now().strftime('%A, %d %B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

# ==== SIDEBAR ====
with st.sidebar:
    if LOGO_PATH:
        logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
        with logo_col2:
            st.image(LOGO_PATH, use_container_width=True)
    st.markdown("### Pengguna")
    st.markdown(f"**{st.session_state.get('username', 'Admin')}**")
    st.markdown("---")
    st.markdown("### Statistik")

    total = query("SELECT COUNT(*) AS n FROM siswa WHERE aktif=1").iloc[0]["n"]
    st.metric("Total Siswa Aktif", total)

    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==== KONTEN UTAMA ====
st.markdown("## Selamat Datang")
st.markdown("""
Pilih menu di **sidebar kiri** untuk navigasi:

- **Rekap Hari Ini** — Kehadiran hari ini
- **Rekap Bulanan** — Rekap per bulan
- **Siswa Terlambat** — Daftar siswa yang sering terlambat
- **Koreksi Absen** — Edit / tambah absen manual
- **Export Excel** — Download data absensi
""")

st.markdown("---")

# ==== METRIK ====
today = date.today().strftime("%Y-%m-%d")

total = query("SELECT COUNT(*) AS n FROM siswa WHERE aktif=1").iloc[0]["n"]
hadir = query("SELECT COUNT(*) AS n FROM kehadiran WHERE tanggal=? AND status='Hadir'", (today,)).iloc[0]["n"]
terlambat = query("SELECT COUNT(*) AS n FROM kehadiran WHERE tanggal=? AND status='Terlambat'", (today,)).iloc[0]["n"]
alpa = total - hadir - terlambat

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Siswa", total)
with col2:
    st.metric("Hadir", hadir, delta=f"{hadir/total*100:.1f}%" if total else "0%")
with col3:
    st.metric("Terlambat", terlambat)
with col4:
    st.metric("Belum Absen", alpa)