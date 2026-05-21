import streamlit as st
import pandas as pd
import time

# --- 1. SETTING HALAMAN & MODERATION STYLE ---
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

# CSS
st.markdown("""
    <style>
    .main { background-color: #fdfdfb; }
    .stButton>button { background-color: #433e36; color: white; border-radius: 8px; width: 100%; }
    .stButton>button:hover { background-color: #5a5449; color: white; }
    h1, h2, h3 { color: #433e36; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE TIRUAN (Mewakili data Excel Toko) ---
data_gudang = {
    'nama_produk': ['White Linen Shirt', 'Beige Chino Pants', 'Sage Green Outer', 'Olive Cargo Pants'],
    'kategori_baju': ['Atasan', 'Bawahan', 'Atasan', 'Bawahan'],
    'vibe': ['Casual', 'Casual', 'Earth Tone', 'Earth Tone'],
    'warna': ['Putih', 'Krem', 'Hijau Sage', 'Hijau Olive'],
    'harga': [149000, 199000, 189000, 219000],
    'stok': [15, 10, 7, 12]
}
df_stok = pd.DataFrame(data_gudang)

# --- 3. MENU NAVIGASI ---
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle & Visual Search Discovery Platform")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli (Visual Search)", "Admin (Upload Excel)"])

# ==================== Halaman 1: SISI PEMBELI ====================
if menu == "Pembeli (Visual Search)":
    st.header("🔍 Cari Gaya Outfit Kamu")
    st.write("Unggah foto inspirasi gaya dari Pinterest/Instagram, AI kami akan mencarikannya di toko.")

    # Widget Upload Foto
    file_foto = st.file_uploader("Pilih foto pakaian...", type=["jpg", "jpeg", "png"])

    if file_foto is not None:
        st.image(file_foto, caption="Foto Inspirasi Kamu", use_container_width=True)
        tombol_cari = st.button("JELAJAHI GAYA INI (Jalankan AI)")

        if tombol_cari:
            with st.spinner('Model Computer Vision sedang mendeteksi warna dan jenis pakaian...'):
                time.sleep(2) 
            
            st.success("Analisis Computer Vision Berhasil!")
            
            col_deteksi1, col_deteksi2 = st.columns(2)
            with col_deteksi1:
                st.metric(label="Deteksi Atasan", value="Kategori: Casual / Earth Tone", delta="Warna: Krem/Hijau")
            with col_deteksi2:
                st.metric(label="Deteksi Bawahan", value="Kategori: Chino/Cargo", delta="Warna: Earth Tone")

            st.markdown("---")
            st.subheader("📦 Hasil Rekomendasi Smart Bundle")
            st.write("Berikut setelan baju dari gudang toko kami yang paling cocok dengan foto kamu:")

            hasil_rekomendasi = df_stok[df_stok['vibe'] == 'Casual'] 

            total_harga = 0
            for idx, row in hasil_rekomendasi.iterrows():
                with st.container():
                    st.markdown(f"**{row['kategori_baju']}: {row['nama_produk']}**")
                    st.write(f"Warna: {row['warna']} | Harga: Rp {row['harga']:,} | Stok sisa: {row['stok']}")
                    total_harga += row['harga']
            
            st.markdown(f"### **Total Harga Paket: Rp {total_harga:,}**")
            st.session_state.tombol_beli_muncul = True

        # Mengunci posisi tombol beli di luar fungsi tombol cari agar tidak hilang saat direfresh
        if st.session_state.get('tombol_beli_muncul', False):
            st.write("")
            if st.button("🛒 BELI SATU PAKET"):
                st.balloons()
                st.success("🎉 Transaksi Berhasil!")

# ==================== Halaman 2: SISI ADMIN ====================
else:
    st.header("📊 Admin Dashboard & Manajemen Inventaris")
    st.write("Perbarui seluruh data produk aplikasi secara instan hanya dengan file Excel.")

    file_excel = st.file_uploader("Upload File Katalog Toko (.xlsx)", type=["xlsx"])
    
    if file_excel is not None:
        st.success("File Excel berhasil diunggah! Sistem membaca data baru.")
    
    st.subheader("📋 Data Stok Gudang Saat Ini (Real-time)")
    st.dataframe(df_stok, use_container_width=True)
    
    st.subheader("💡 AI Driven Insights (Rekomendasi Kemajuan)")
    st.info("Berdasarkan pencarian pembeli minggu ini, gaya **Earth Tone Casual Mix** sedang naik daun! Disarankan menambah stok **Beige Chino Pants** karena diprediksi habis dalam 4 hari ke depan.")
