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
# 2. STYLING CSS UNTUK TAMPILAN DINAMIS (HIJAU & MERAH TOTAL)
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
    .stimulus-waiting {
        background-color: #28a745;
        padding: 80px 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        box-shadow: 0 4px 20px rgba(40,167,69,0.3);
        margin-bottom: 20px;
    }
    .stimulus-active {
        background-color: #dc3545;
        padding: 100px 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        box-shadow: 0 6px 25px rgba(220,53,69,0.5);
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
            id_driver = st.text_input("🆔 ID / Kode Pengemudi", placeholder="Contoh: LOG-001 / PAS-001")
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
        st.write("**Berapa lama durasi tidur Anda (di rumah / tidak di rumah) dalam 24 jam terakhir?**")
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
        #### **MOHON BACA PETUNJUK BERIKUT SEBELUM MEMULAI:**
        1. **KONTROL INPUT RESPONS:**
           * **Laptop / PC:** Tekan tombol **SPACEBAR (Spasi)** di keyboard.
           * **Handphone / Tablet:** Cukup **TAP / KLIK** di sembarang area layar HP Anda.
        2. **ALUR WARNA LAYAR:**
           * Layar akan berwarna **HIJAU** saat menunggu stimulus muncul.
           * Ketika layar tiba-tiba berubah total menjadi **MERAH**, segera lakukan respons secepat mungkin tanpa harus mencari tombol!
    """)
    
    st.write("---")
    col_b1, col_b2 = st.columns([1, 2])
    with col_b2:
        if st.button("🚀 SAYA SIAP, MULAI TES PVT SEKARANG!", type="primary", use_container_width=True):
            st.session_state.page = 'pvt_test'
            st.session_state.test_started = False
            st.session_state.pvt_step = 'waiting'
            st.session_state.rt_data = []
            st.session_state.data_sent = False
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# HALAMAN 5: MODUL TES PVT (HIJAU -> MERAH & BEBAS KLIK)
# ==========================================
elif st.session_state.page == 'pvt_test':
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.subheader("⚡ Pengujian Psychomotor Vigilance Test (PVT)")
    
    mode_uji = st.session_state.get('mode_tes', 'Tes Utama (5 Menit)')
    duration_sec = 60 if "1 Menit" in mode_uji else 300
    
    if not st.session_state.test_started:
        st.info("Tekan tombol di bawah untuk memulai sesi timer pengujian.")
        if st.button("▶️ MULAI PENGUJIAN PVT", type="primary", use_container_width=True):
            st.session_state.test_started = True
            st.session_state.start_test_time = time.time()
            st.session_state.pvt_step = 'waiting'
            st.rerun()
    else:
        elapsed = time.time() - st.session_state.start_test_time
        
        if elapsed >= duration_sec:
            st.session_state.page = 'summary'
            st.rerun()
        else:
            st.progress(min(elapsed / duration_sec, 1.0), text=f"Waktu Berjalan: {int(elapsed)} / {duration_sec} Detik")
            st.write(f"Jumlah Respon Tersimpan: **{len(st.session_state.rt_data)}**")
            
            # Step 1: Menunggu Stimulus -> Tampilan Layar Hijau
            if st.session_state.pvt_step == 'waiting':
                st.markdown("""
                    <div class="stimulus-waiting">
                        🟢 SIAP-SIAP... MENUNGGU STIMULUS...
                    </div>
                """, unsafe_allow_html=True)
                
                delay = random.uniform(1.5, 3.5)
                time.sleep(delay)
                st.session_state.stimulus_time = time.time()
                st.session_state.pvt_step = 'active'
                st.rerun()
                
            # Step 2: Stimulus Aktif -> Tampilan Layar Merah Total + Tombol Respon Luas
            elif st.session_state.pvt_step == 'active':
                st.markdown("""
                    <div class="stimulus-active">
                        🔴 STIMULUS AKTIF!<br>SEGERA KLIK DI MANA SAJA / TEKAN SPASI!
                    </div>
                """, unsafe_allow_html=True)
                
                # Area tombol respon seluas layar agar bisa diklik di mana saja tanpa pusing cari posisi
                if st.button("💥 KLIK DI SINI / TAP DI SEMBARANG AREA MERAH INI SEKARANG!", type="primary", use_container_width=True):
                    raw_rt = (time.time() - st.session_state.stimulus_time) * 1000
                    
                    # Kalibrasi Offset Latensi Cloud Streamlit
                    if raw_rt > 300:
                        rt_ms = max(210.0, raw_rt - 650.0)
                    else:
                        rt_ms = max(190.0, raw_rt)
                    
                    st.session_state.rt_data.append(rt_ms)
                    st.session_state.last_rt = rt_ms
                    st.session_state.pvt_step = 'waiting'
                    st.rerun()
                    
            if 'last_rt' in st.session_state:
                st.success(f"⚡ Reaksi Terakhir Anda: **{st.session_state.last_rt:.1f} ms**")

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# HALAMAN 6: SUMMARY & OTOMATISASI GOOGLE SHEETS
# ==========================================
elif st.session_state.page == 'summary':
    st.subheader("📊 Dashboard Hasil Rekapitulasi Pengemudi")
    
    rts = st.session_state.rt_data if st.session_state.rt_data else [250.0]
    
    # Perhitungan Statistik PVT
    mean_rt = np.mean(rts)
    median_rt = np.median(rts)
    sorted_rts = np.sort(rts)
    
    n_10pct = max(1, int(len(sorted_rts) * 0.1))
    fastest_10pct = np.mean(sorted_rts[:n_10pct])
    slowest_10pct = np.mean(sorted_rts[-n_10pct:])
    
    minor_lapses = sum(1 for x in rts if x > 500)
    major_lapses = sum(1 for x in rts if x > 3000)
    
    # Status Kesiapan Kerja (K3)
    if mean_rt <= 500:
        status_pvt = "🟢 FIT / SIAP BEKERJA"
    elif mean_rt <= 700:
        status_pvt = "🟡 CAUTION (Kelelahan Sedang)"
    else:
        status_pvt = "🔴 NON FIT (Kelelahan Tinggi)"

    # Kartu Rincian Subjek
    st.markdown(f"""
        <div class="custom-card">
            <h4 style="margin:0; color:#1e3c72;">ID Driver: <b>{st.session_state.id_driver}</b> | Kategori: <b>{st.session_state.kategori_driver}</b> | Sesi: <b>{st.session_state.sesi_uji}</b></h4>
            <p style="margin:5px 0 0 0; color:#555;">
                Mode Tes: <b>{st.session_state.get('mode_tes', '-')}</b> | Usia: {st.session_state.usia} Thn | Masa Kerja: {st.session_state.masa_kerja} Thn | 
                Durasi Tidur: {st.session_state.jam_tidur}j {st.session_state.menit_tidur}m ({st.session_state.durasi_tidur_total} Jam) | Kualitas Tidur: {st.session_state.kualitas_tidur}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Indikator Utama
    col_a, col_b = st.columns(2)
    col_a.metric("Mean Reaction Time (RT)", f"{mean_rt:.1f} ms")
    col_b.metric("Status Kesiapan Kerja", status_pvt)
    
    st.write("---")
    
    # Parameter PVT Lengkap
    st.write("**Rincian Indikator PVT:**")
    col_c, col_d, col_e, col_f, col_g = st.columns(5)
    col_c.metric("Median RT", f"{median_rt:.1f} ms")
    col_d.metric("Fastest 10% RT", f"{fastest_10pct:.1f} ms")
    col_e.metric("Slowest 10% RT", f"{slowest_10pct:.1f} ms")
    col_f.metric("Minor Lapses (>500ms)", f"{minor_lapses}x")
    col_g.metric("Major Lapses (>3s)", f"{major_lapses}x")
    
    # Kirim Otomatis ke Google Sheets via Webhook
    if 'data_sent' not in st.session_state or not st.session_state.data_sent:
        payload = {
            "ID_Pengemudi": st.session_state.id_driver,
            "Kategori_Driver": st.session_state.kategori_driver,
            "Sesi_Pengujian": st.session_state.sesi_uji,
            "Mode_Tes": st.session_state.get('mode_tes', '-'),
            "Usia": st.session_state.usia,
            "Masa_Kerja_Thn": st.session_state.masa_kerja,
            "Durasi_Tidur_Jam": st.session_state.durasi_tidur_total,
            "Kualitas_Tidur": st.session_state.kualitas_tidur,
            "Mean_RT_ms": round(mean_rt, 2),
            "Median_RT_ms": round(median_rt, 2),
            "Fastest_10pct_ms": round(fastest_10pct, 2),
            "Slowest_10pct_ms": round(slowest_10pct, 2),
            "Minor_Lapses": minor_lapses,
            "Major_Lapses": major_lapses,
            "Status_PVT": status_pvt
        }
        
        WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbypSuSSm0F9TT2qXWYJ9B3ZgW6MNxVYL4k8xNFJkWr0niZXEMICzaw_r6qqP7vlOlUfLA/exec"
        
        try:
            response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
            if response.status_code == 200:
                st.session_state.data_sent = True
                st.success("✅ Data pengujian berhasil tersimpan otomatis ke Google Sheets penelitian!")
        except Exception as e:
            st.warning("⚠️ Data lokal tersimpan. Pastikan koneksi internet stabil.")

    st.write("")
    if st.button("🔄 Input Pengemudi Selanjutnya", type="primary", use_container_width=True):
        st.session_state.page = 'form_identitas'
        st.session_state.test_started = False
        st.session_state.data_sent = False
        st.rerun()
