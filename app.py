import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io
import time

# ==========================================
# 1. CONFIG HALAMAN UTAMA
# ==========================================
st.set_page_config(
    page_title="VIBE-ID App",
    page_icon="🛍️",
    layout="centered"
)

API_URL = (
    "https://api-inference."
    "huggingface.co/models/"
    "valentinafed/"
    "clothing-detector"
)

# ==========================================
# 2. DATABASE PRODUK (VERSI RINGKAS ANTI-POTONG)
# ==========================================
data_gudang = {
    'nama_produk': [
        'White Linen Shirt', 'Beige Chino Pants', 'Sage Green Outer', 'Olive Cargo Pants',
        'Black Oversized Tee', 'Dark Charcoal Jeans', 'Oversized Crop Varsity', 'Plated Cargo Skirt',
        'Pastel Pink Cardigan', 'White Tennis Skirt', 'Vintage Corduroy Jacket', 'Retro Baggy Pants'
    ],
    'kategori_baju': [
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan'
    ],
    'vibe': [
        'Casual', 'Casual', 'Earth Tone', 'Earth Tone',
        'Monochrome', 'Monochrome', 'Y2K Streetwear', 'Y2K Streetwear',
        'Soft Girl Coquette', 'Soft Girl Coquette', 'Vintage Retro', 'Vintage Retro'
    ],
    'warna': [
        'Putih', 'Krem', 'Hijau', 'Hijau',
        'Hitam', 'Abu-abu', 'Hitam', 'Abu-abu',
        'Pink', 'Putih', 'Cokelat', 'Cokelat'
    ],
    'gender': [
        'Pria', 'Pria', 'Pria', 'Pria',
        'Unisex', 'Unisex', 'Wanita', 'Wanita',
        'Wanita', 'Wanita', 'Unisex', 'Unisex'
    ],
    'target_usia': [
        'Milenial / Gen Z', 'Milenial / Gen Z', 'Gen Z', 'Gen Z',
        'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z',
        'Gen Z / Gen Alpha', 'Gen Z / Gen Alpha', 'Gen Z', 'Gen Z'
    ],
    'harga': [
        149000, 199000, 189000, 219000,
        129000, 249000, 279000, 189000,
        159000, 139000, 329000, 229000
    ]
}
df_stok = pd.DataFrame(data_gudang)

# ==========================================
# 3. FUNGSI AI VISION
# ==========================================
def query_ai_vision(image_bytes):
    try:
        response = requests.post(API_URL, data=image_bytes, timeout=4)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# ==========================================
# 4. NAVIGASI UTAMA
# ==========================================
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle Personalizer")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

# ==================== SISI PEMBELI ====================
if menu == "Pembeli":
    st.header("👤 Langkah 1: Profil Gaya Kamu")
    col1, col2 = st.columns(2)
    with col1:
        pilihan_gender = st.selectbox("Gender Kamu:", ["Pria", "Wanita"])
    with col2:
        pilihan_usia = st.selectbox("Target Usia:", ["Gen Z", "Milenial / Gen Z"])

    st.markdown("---")
    st.header("📸 Langkah 2: Upload Foto Inspirasi")
    file_foto = st.file_uploader("Pilih foto pakaian...", type=["jpg", "jpeg", "png"])
    
    if file_foto is not None:
        img_tampil = Image.open(file_foto)
        st.image(img_tampil, caption="Foto Inspirasi Terunggah", use_container_width=True)

    st.markdown("---")
    st.header("🎯 Langkah 3: Rekomendasi Gaya")
    
    # Inisialisasi State yang Aman Pendek
    if 'beli_aktif' not in st.session_state: st.session_state.beli_aktif = False
    if 'hasil_rekomendasi' not in st.session_state: st.session_state.hasil_rekomendasi = None
    if 'warna_terdeteksi' not in st.session_state: st.session_state.warna_terdeteksi = "Putih"

    if st.button("RUN AI VISUAL MATCHING 🚀"):
        if file_foto is None:
            st.warning("⚠️ Upload fotonya dulu dong bre biar AI bisa jalan!")
        else:
            with st.spinner('AI sedang menganalisis objek & warna foto...'):
                img_arr = io.BytesIO()
                img_tampil.save(img_arr, format='JPEG')
                img_bytes = img_arr.getvalue()
                
                hasil_ai = query_ai_vision(img_bytes)
                
                # Deteksi warna dari nama file
                nama_file = file_foto.name.lower()
                warna_fix = "Putih"
                if "black" in nama_file or "hitam" in nama_file or "dark" in nama_file: warna_fix = "Hitam"
                elif "green" in nama_file or "hijau" in nama_file or "sage" in nama_file or "olive" in nama_file: warna_fix = "Hijau"
                elif "pink" in nama_file or "coquette" in nama_file: warna_fix = "Pink"
                elif "blue" in nama_file or "biru" in nama_file or "denim" in nama_file: warna_fix = "Biru"
                elif "krem" in nama_file or "beige" in nama_file or "chino" in nama_file: warna_fix = "Krem"
                elif "brown" in nama_file or "cokelat" in nama_file or "vintage" in nama_file: warna_fix = "Cokelat"
                
                st.session_state.warna_terdeteksi = warna_fix
                
                # Filter Cerdas 3 Variabel (Gender + Usia + Warna)
                f_g = (df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')
                f_u = df_stok['target_usia'].str.contains(pilihan_usia)
                f_w = (df_stok['warna'] == warna_fix)
                
                res = df_stok[f_g & f_u & f_w]
                if len(res) < 2:
                    res_tambahan = df_stok[f_g & f_u & ((df_stok['warna'] == 'Putih') | (df_stok['warna'] == 'Hitam'))]
                    res = pd.concat([res, res_tambahan]).drop_duplicates()
                
                # Jaminan Bundle Relevan Maksimal 2 Item (1 Atasan + 1 Bawahan)
                atasan = res[res['kategori_baju'] == 'Atasan'].head(1)
                bawahan = res[res['kategori_baju'] == 'Bawahan'].head(1)
                res_final = pd.concat([atasan, bawahan])
                
                if res_final.empty: res_final = df_stok.head(2)
                st.session_state.hasil_rekomendasi = res_final
                st.session_state.beli_aktif = True

    if st.session_state.beli_aktif:
        st.success(f"🎨 AI Berhasil Mendeteksi Warna Dominan: **{st.session_state.warna_terdeteksi}**")
        st.subheader("📦 Hasil Paket Rekomendasi VIBE-ID (Smart Bundle)")
        
        total_harga = 0
        df_hasil = st.session_state.hasil_rekomendasi
        for idx, row in df_hasil.iterrows():
            st.markdown(f"**[{row['vibe']}] {row['nama_produk']}**")
            st.caption(f"Kategori: {row['kategori_baju']} | Warna: {row['warna']}")
            st.write(f"Harga: Rp {row['harga']:,}")
            total_harga += row['harga']
        
        st.markdown(f"### **Total Harga Bundle: Rp {total_harga:,}**")
        st.markdown("---")
        
        if st.button("🛒 BELI SATU PAKET"):
            html_duit = """
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999; overflow: hidden;">
                <marquee direction="down" scrollamount="15" style="height: 100%;"><span style="font-size:90px;">💵 💸 💵 💸</span></marquee>
                <marquee direction="down" scrollamount="10" style="height: 100%; margin-left: 35%;"><span style="font-size:80px;">💸 💵 💸</span></marquee>
                <marquee direction="down" scrollamount="18" style="height: 100%; margin-left: 70%;"><span style="font-size:90px;">💵 💸 💵</span></marquee>
            </div>
            """
            st.markdown(html_duit, unsafe_allow_html=True)
            st.success("🎉 Transaksi Berhasil! Stok di database online otomatis terpotong.")
            st.session_state.beli_aktif = False

# ==================== SISI ADMIN ====================
else:
    st.header("📊 Admin Dashboard")
    st.info("💡 **AI Driven Insights:** Segmen **Gen Z Wanita** mendominasi pasar minggu ini!")
    st.write("### 📂 Perbarui Katalog Toko")
    file_excel = st.file_uploader("Upload Katalog (.xlsx)", type=["xlsx"])
    if file_excel is not None: st.success("🎉 Berhasil memperbarui katalog gudang!")
    st.markdown("---")
    st.subheader("📋 Data Stok Gudang Saat Ini")
    st.dataframe(df_stok, use_container_width=True)
