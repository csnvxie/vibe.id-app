import streamlit as st
import pandas as pd
from PIL import Image
import io
import time

# ==========================================
# 1. SETTING HALAMAN & CONFIG UTAMA
# ==========================================
st.set_page_config(
    page_title="VIBE-ID App",
    page_icon="🛍️",
    layout="centered"
)

# ==========================================
# 2. DATABASE PRODUK (VERSI ULTRA AMAN)
# ==========================================
data_gudang = {
    'nama_produk': [
        'White Linen Shirt', 'Beige Chino Pants', 
        'Sage Green Outer', 'Olive Cargo Pants',
        'Black Oversized Tee', 'Dark Charcoal Jeans', 
        'Oversized Crop Varsity', 'Plated Cargo Skirt',
        'Pastel Pink Cardigan', 'White Tennis Skirt', 
        'Vintage Corduroy Jacket', 'Retro Baggy Pants',
        'Crimson Red Hoodie', 'Navy Blue Bomber', 
        'Mustard Yellow Sweater', 'Royal Blue Denim'
    ],
    'kategori_baju': [
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Atasan', 'Atasan', 'Bawahan'
    ],
    'vibe': [
        'Casual', 'Casual', 'Earth Tone', 'Earth Tone',
        'Monochrome', 'Monochrome', 'Y2K Streetwear', 'Y2K Streetwear',
        'Soft Girl Coquette', 'Soft Girl Coquette', 'Vintage Retro', 'Vintage Retro',
        'Bold Streetwear', 'Sporty', 'Indie Aesthetic', 'Casual'
    ],
    'warna': [
        'Putih', 'Krem', 'Hijau', 'Hijau',
        'Hitam', 'Abu-abu', 'Hitam', 'Abu-abu',
        'Pink', 'Putih', 'Cokelat', 'Cokelat',
        'Merah', 'Biru', 'Kuning', 'Biru'
    ],
    'gender': [
        'Pria', 'Pria', 'Pria', 'Pria',
        'Unisex', 'Unisex', 'Wanita', 'Wanita',
        'Wanita', 'Wanita', 'Unisex', 'Unisex',
        'Unisex', 'Pria', 'Unisex', 'Unisex'
    ],
    'target_usia': [
        'Milenial / Gen Z', 'Milenial / Gen Z', 'Gen Z', 'Gen Z',
        'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z',
        'Gen Z / Gen Alpha', 'Gen Z / Gen Alpha', 'Gen Z', 'Gen Z',
        'Gen Z', 'Milenial / Gen Z', 'Gen Z', 'Milenial / Gen Z'
    ],
    'harga': [
        149000, 199000, 189000, 219000,
        129000, 249000, 279000, 189000,
        159000, 139000, 329000, 229000,
        259000, 299000, 179000, 219000
    ]
}
df_stok = pd.DataFrame(data_gudang)

# ==========================================
# 3. MENU NAVIGASI UTAMA APLIKASI
# ==========================================
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle Personalizer")

menu = st.sidebar.radio(
    "Pilih Hak Akses:", 
    ["Pembeli", "Admin"]
)

# ==================== SISI PEMBELI ====================
if menu == "Pembeli":
    st.header("👤 Langkah 1: Profil Gaya Kamu")
    col1, col2 = st.columns(2)
    with col1:
        pilihan_gender = st.selectbox(
            "Gender Kamu:", 
            ["Pria", "Wanita"]
        )
    with col2:
        pilihan_usia = st.selectbox(
            "Target Usia:", 
            ["Gen Z", "Milenial / Gen Z"]
        )

    st.markdown("---")
    
    # FITUR UPLOAD FOTO SUDAH KEMBALI DI SINI BRE!
    st.header("📸 Langkah 2: Upload Foto Inspirasi")
    file_foto = st.file_uploader(
        "Pilih foto pakaian...", 
        type=["jpg", "jpeg", "png"]
    )
    
    if file_foto is not None:
        img_tampil = Image.open(file_foto)
        st.image(
            img_tampil, 
            caption="Foto Inspirasi Terunggah", 
            use_container_width=True
        )

    st.markdown("---")
    st.header("🎯 Langkah 3: Rekomendasi Gaya")
    
    if 'beli_aktif' not in st.session_state: 
        st.session_state.beli_aktif = False
    if 'hasil_rekomendasi' not in st.session_state:
