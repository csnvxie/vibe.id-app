import streamlit as st
import pandas as pd
import requests
from PIL import Image, ImageDraw
import io
import numpy as np
from sklearn.cluster import KMeans
import time

# ==========================================
# 1. SETTING HALAMAN & CONFIG UTAMA
# ==========================================
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

# ==========================================
# 2. DATABASE PRODUK DENGAN VARIASI WARNA LUAS
# ==========================================
data_gudang = {
    'nama_produk': [
        'White Linen Shirt', 'Beige Chino Pants', 'Sage Green Outer', 'Olive Cargo Pants',
        'Black Oversized Tee', 'Dark Charcoal Jeans', 'Oversized Crop Varsity', 'Plated Cargo Skirt',
        'Pastel Pink Cardigan', 'White Tennis Skirt', 'Vintage Corduroy Jacket', 'Retro Baggy Pants',
        'Crimson Red Hoodie', 'Navy Blue Bomber', 'Mustard Yellow Sweater', 'Royal Blue Denim'
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
    ],
    'stok': [15, 10, 7, 12, 20, 14, 9, 11, 8, 12, 6, 13, 7, 5, 6, 10]
}
df_stok = pd.DataFrame(data_gudang)

# ==========================================
# 3. KAMUS WARNA UNIVERSAL (VERSI ANTI-KEPOTONG)
# ==========================================
KAMUS_WARNA = {
    "Putih": (240, 240, 240), 
    "Hitam": (20, 20, 20), 
    "Abu-abu": (128, 128, 128),
    "Merah": (220, 30, 30), 
    "Biru": (30, 30, 220), 
    "Hijau": (30, 150, 30),
    "Kuning": (230, 230, 30), 
    "Krem": (240, 220, 180), 
    "Cokelat": (110, 70, 40),
    "Pink": (240, 130, 180), 
    "Ungu": (130, 30, 180), 
    "Orange": (240, 130, 30)
}

# ==========================================
# 4. FUNGSI DETEKSI AI VISION (YOLOv8)
# ==========================================
def query_ai_vision(image_bytes):
    try:
        API_URL = "https://api-inference.huggingface.co/models/valentinafed/clothing-detector"
        response = requests.post(API_URL, data=image_bytes, timeout=4)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# ==========================================
# 5. FUNGSI DETEKSI WARNA (K-MEANS CLUSTERING)
# ==========================================
def dapatkan_warna_all(pil_image, k=2):
    img = pil_image.resize((50, 50))
    img_np = np.array(img)
    if img_np.shape[2] == 4:
        img_np = img_np[:, :, :3]
    piksel = img_np.reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=3)
    kmeans.fit(piksel)
    warna_pusat = kmeans.cluster_centers_
    labels = kmeans.labels_
    
    counts = np.bincount(labels)
    total = len(labels)
    persentase = [round((c / total) * 100) for c in counts]
    
    hasil_deteksi = []
    for i, rgb in enumerate(warna_pusat):
        r, g, b = rgb[0], rgb[1], rgb[2]
        warna_terdekat = "Putih"
        jarak_terkecil = float('inf')
        
        for nama_warna, rgb_ref in KAMUS_WARNA.items():
            jarak = np.sqrt((r - rgb_ref[0])**2 + (g - rgb_ref[1])**2 + (b - rgb_ref[2])**2)
            if jarak < jarak_terkecil:
                jarak_terkecil = jarak
                warna_terdekat = nama_warna
                
        hasil_deteksi.append({"nama": warna_terdekat, "persen": persentase[i]})
    return hasil_deteksi

# ==========================================
# 6. MENU NAVIGASI UTAMA APPLIKASI
# ==========================================
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle & Hyper-Personalized Recommendation")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli (Visual Search)", "Admin (Dashboard)"])

# ==================== SISI PEMBELI ====================
if menu == "Pembeli (Visual Search)":
    st.header("👤 Langkah 1: Lengkapi Profil Kamu")
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        pilihan_gender = st.selectbox("Pilih Gender Kamu:", ["Pria", "Wanita"])
    with col_input2:
        pilihan_usia = st.selectbox("Pilih Kelompok Usia / Generasi:", ["Gen Z", "Milenial / Gen Z", "Gen Z / Gen Alpha"])

    st.markdown("---")
    st.header("📸 Langkah 2: Upload Foto Inspirasi Gaya")
    file_foto = st.file_uploader("Pilih dan unggah foto pakaian pilihanmu...", type=["jpg", "jpeg", "png"])

    # Inisialisasi Session State Pengaman
    if 'beli_aktif' not in st.session_state: st.session_state.beli_aktif = False
    if 'hasil_rekomendasi' not in st.session_state: st.session_state.hasil_rekomendasi = None
    if 'warna_cari_1' not in st.session_state: st.session_state.warna_cari_1 = ""
    if 'warna_cari_2' not in st.session_state: st.session_state.warna_cari_2 = ""
    if 'persen_1' not in st.session_state: st.session_state.persen_1 = 0
    if 'persen_2' not in st.session_state: st.session_state.persen_2 = 0

    if file_foto is not None:
        image = Image.open(file_foto)
        st.image(image, caption="Foto Inspirasi Kamu", use_container_width=True)
        
        tombol_cari = st.button("JELAJAHI GAYA PERSONAL KAMU 🚀")

        if tombol_cari:
            with st.spinner('Menyelaraskan profil user dengan analisis AI...'):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                hasil_ai = query_ai_vision(img_bytes)
                daftar_warna_riil = dapatkan_warna_all(image, k=2)

            st.session_state.warna_cari_1 = daftar_warna_riil[0]['nama']
            st.session_state.warna_cari_2 = daftar_warna_riil[1]['nama']
            st.session_state.persen_1 = daftar_warna_riil[0]['persen']
            st.session_state.persen_2 = daftar_warna_riil[1]['persen']

            # Filter Logika Database Rekomendasi
            res = df_stok[
                (df_stok['warna'].isin([st.session_state.warna_cari_1, st.session_state.warna_cari_2])) & 
                ((df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')) &
                (df_stok['target_usia'].str.contains(pilihan_usia))
            ]
            
            if res.empty:
                res = df_stok[
                    ((df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')) &
                    (df_stok['target_usia'].str.contains(pilihan_usia))
                ]

            st.session_state.hasil_rekomendasi = res
            st.session_state.beli_aktif = True

        # Tampilkan Output Rekomendasi jika AI sudah dieksekusi
        if st.session_state.beli_aktif:
            st.markdown("#### **🎨 Hasil Analisis Warna Foto Semesta:**")
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                st.info(f"🎨 **Warna Dominan 1:** `{st.session_state.warna_cari_1}` ({st.session_state.persen_1}% Porsi)")
            with c_w2:
                st.info(f"🎨 **Warna Dominan 2:** `{st.session_state.warna_cari_2}` ({st.session_state.persen_2}% Porsi)")

            st.markdown("---")
            st.subheader("📦 Hasil Rekomendasi Smart Bundle Sesuai Profil Kamu")
            st.write(f"Menampilkan produk untuk **{pilihan_gender}**
