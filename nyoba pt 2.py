import streamlit as st
import time
import random
import pandas as pd
import numpy as np
import os
import requests
from PIL import Image

# ==========================================
# 1. KONFIGURASI HALAMAN WEB
# ==========================================
st.set_page_config(
    page_title="PVT Test System - Driver Fatigue Assessment",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. STYLING CSS
# ==========================================
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .header-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.12);
    }
    .custom-card {
        background-color: white;
        padding: 24px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 5px solid #1e3c72;
        margin-bottom: 20px;
    }
    [data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700;
        color: #1e3c72;
    }
    </style>
""", unsafe_allow_html=True)

# State Management Initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'rt_data' not in st.session_state:
    st.session_state.rt_data = []

# Fallback Default Values
if 'id_driver' not in st.session_state:
    st.session_state.id_driver = "-"
if 'kategori_driver' not in st.session_state:
    st.session_state.kategori_driver = "-"
if 'sesi_uji' not in st.session_state:
    st.session_state.sesi_uji = "Sebelum Bekerja (Pre-Work)"
if 'mode_tes' not in st.session_state:
    st.session_state.mode_tes = "Tes Utama (5 Menit)"
if 'usia' not in st.session_state:
    st.session_state.usia = 0
if 'masa_kerja' not in st.session_state:
    st.session_state.masa_kerja = 0
if 'jam_tidur' not in st.session_state:
    st.session_state.jam_tidur = 0
if 'menit_tidur' not in st.session_state:
    st.session_state.menit_tidur = 0
if 'durasi_tidur_total' not in st.session_state:
    st.session_state.durasi_tidur_total = 0
if 'kualitas_tidur' not in st.session_state:
    st.session_state.kualitas_tidur = "-"

# ==========================================
# HEADER UTAMA DENGAN LOGO UNIVERSITAS
# ==========================================
col_logo, col_header = st.columns([1, 5])

with col_logo:
    try:
        logo = Image.open("logo_univ.png")
        st.image(logo, width=110)
    except:
        st.info("📌 [Logo Univ]")

with col_header:
    st.markdown("""
        <div class="header-card">
            <h2 style="margin:0; padding:0; color:white;">⚡ PSYCHOMOTOR VIGILANCE TEST (PVT)</h2>
            <p style="margin:4px 0 0 0; opacity:0.9; font-size:15px;">
                Sistem Pengujian Waktu Reaksi & Kesiapan Kerja Pengemudi
            </p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# HALAMAN 1: LOGIN PETUGAS / PENGUJI
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🔐 Otentikasi Akses Penguji")
    st.caption("Silakan masukkan Username dan Password penguji untuk membuka akses pengujian.")
    
    with st.form("login_form"):
        username = st.text_input("👤 Username", placeholder="Masukkan username")
        password = st.text_input("🔑 Password", type="password", placeholder="Masukkan password")
        
        st.write("")
        btn_login = st.form_submit_button("Masuk Ke Sistem ➡️", type="primary", use_container_width=True)
        
        if btn_login:
            if username.strip().lower() == "admin" and password.strip() == "12345":
                st.session_state.logged_in = True
                st.session_state.page = 'form_identitas'
                st.success("✅ Login Berhasil!")
                st.rerun()
            else:
                st.error("❌ Username atau Password salah! (Default -> Username: admin | PW: 12345)")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# HALAMAN 2: IDENTITAS PENGENDARA
# ==========================================
elif st.session_state.page == 'form_identitas':
    col_t, col_l = st.columns([5, 1])
    with col_l:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = 'login'
            st.rerun()

    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("📋 1. Form Identitas & Karakteristik Pengemudi")
    
    with st.form("form_identitas"):
        col1, col2 = st.columns(2)
        with col1:
            id_driver = st.text_input("🆔 ID / Kode Pengemudi", placeholder="Contoh: LOG-001 / BCS-001")
            kategori_driver = st.selectbox("🚛 Kategori Subjek Pengemudi", ["Logistik Industri", "Pasir Proyek", "Lainnya / Umum"])
            sesi_uji = st.radio("⏰ Sesi Pengujian Kerja", ["Sebelum Bekerja (Pre-Work)", "Sesudah Bekerja (Post-Work)"], horizontal=True)
            
        with col2:
            usia = st.number_input("🎂 Usia (Tahun)", min_value=17, max_value=75, value=35)
            masa_kerja = st.number_input("⏱️ Masa Kerja / Pengalaman (Tahun)", min_value=0.0, max_value=50.0, value=3.0, step=0.5)
            mode_tes = st.radio("⏱️ Pilih Durasi Uji PVT", ["Latihan / Trial (1 Menit)", "Tes Utama (5 Menit)"], horizontal=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        btn_next1 = st.form_submit_button("Lanjut ke Evaluasi Tidur ➡️", type="primary", use_container_width=True)
        
        if btn_next1:
            if not id_driver:
                st.error("⚠️ Mohon isi ID Pengemudi terlebih dahulu!")
            else:
                st.session_state.id_driver = id_driver
                st.session_state.kategori_driver = kategori_driver
                st.session_state.sesi_uji = sesi_uji
                st.session_state.usia = usia
                st.session_state.masa_kerja = masa_kerja
                st.session_state.mode_tes = mode_tes
                st.session_state.page = 'form_tidur'
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# HALAMAN 3: EVALUASI DURASI & KUALITAS TIDUR
# ==========================================
elif st.session_state.page == 'form_tidur':
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("🛌 2. Evaluasi Durasi & Kualitas Tidur (24 Jam Terakhir)")
    st.caption("Jawab pertanyaan berikut terkait kondisi tidur Anda sebelum melakukan pekerjaan hari ini.")
    
    tidak_tidur = st.checkbox("❌ Saya Tidak Sempat Tidur Sama Sekali dalam 24 Jam Terakhir")
    st.write("---")
    
    if tidak_tidur:
        st.warning("⚠️ Anda memilih **Tidak Sempat Tidur**. Durasi tidur diatur otomatis ke **0 Jam 0 Menit**.")
        jam_tidur = 0
        menit_tidur = 0
        kualitas_tidur = "Tidak Tidur"
    else:
        st.write("**Berapa lama durasi tidur Anda dalam 24 jam terakhir?**")
        c1, c2 = st.columns(2)
        with c1:
            jam_tidur = st.number_input("Durasi Tidur (Jam)", min_value=0, max_value=24, value=7)
        with c2:
            menit_tidur = st.selectbox("Durasi Tidur (Menit)", [0, 15, 30, 45])
            
        st.write("<br>", unsafe_allow_html=True)
        st.write("**Bagaimana kualitas tidur Anda dalam 24 jam terakhir?**")
        kualitas_tidur = st.select_slider(
            "Pilih Kualitas Tidur:",
            options=["Sangat Tidak Nyenyak", "Tidak Nyenyak", "Cukup / Biasa Saja", "Nyenyak", "Sangat Nyenyak"],
            value="Cukup / Biasa Saja"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Lanjut ke Petunjuk Pengujian ➡️", type="primary", use_container_width=True):
        st.session_state.jam_tidur = jam_tidur
        st.session_state.menit_tidur = menit_tidur
        st.session_state.durasi_tidur_total = round(jam_tidur + (menit_tidur / 60.0), 2)
        st.session_state.kualitas_tidur = kualitas_tidur
        st.session_state.page = 'reminder'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# HALAMAN 4: REMINDER & PETUNJUK TES PVT
# ==========================================
elif st.session_state.page == 'reminder':
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("💡 3. Petunjuk & Instruksi Pengujian PVT")
    
    st.markdown("""
        #### **PETUNJUK PELAKSANAAN TES:**
        1. **FOKUS & RESPON:** 
           * Ketika layar berubah menjadi **MERAH**, segera klik/tap tombol di bawah kotak merah secepat mungkin.
        2. **DURASI & PEREKAMAN:** 
           * Sesuai mode yang dipilih (**1 Menit** untuk Trial atau **5 Menit** untuk Tes Utama).
           * Sistem akan otomatis menghitung berapa kali Anda melakukan respons (*Total Trials*) selama durasi pengujian berlangsung.
    """)
    
    st.write
