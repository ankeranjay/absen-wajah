import streamlit as st

def require_login():
    """Panggil di awal setiap halaman. Kalau belum login, stop."""
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning(" Anda belum login. Silakan login dulu.")
        st.markdown("[ Klik di sini untuk login](/)")
        st.stop()