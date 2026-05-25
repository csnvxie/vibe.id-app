import streamlit as st
import pandas as pd
import requests
from PIL import Image
import io
import numpy as np
from sklearn.cluster import KMeans
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
# 2. DATABASE PRODUK (VERSI ULTRA PENDEK)
# ==========================================
data_gudang = {
    'nama_produk': [
        'White Linen Shirt', 
        'Beige Chino Pants', 
        'Sage Green Outer', 
        'Olive Cargo Pants',
        'Black Oversized Tee', 
        'Dark Charcoal Jeans', 
        'Oversized Crop Varsity', 
        'Plated Cargo Skirt',
        'Pastel Pink Cardigan', 
        'White Tennis Skirt', 
        'Vintage Corduroy Jacket', 
        'Retro Baggy Pants',
        'Crimson Red Hoodie', 
        'Navy Blue Bomber', 
        'Mustard Yellow Sweater', 
        'Royal Blue Denim'
    ],
    'kategori_baju': [
        'Atasan', 'Bawahan', 
        'Atasan', 'Bawahan', 
        'Atasan', 'Bawahan', 
        'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 
        'Atasan', 'Bawahan', 
        'Atasan', 'Atasan', 
        'Atasan', 'Bawahan'
    ],
    'vibe': [
        'Casual', 'Casual', 
        'Earth Tone', 'Earth Tone', 
        'Monochrome', 'Monochrome', 
        'Y2K Streetwear', 'Y2K Streetwear',
        'Soft Girl Coquette', 
        'Soft Girl Coquette', 
        'Vintage Retro', 'Vintage Retro', 
        'Bold Streetwear', 'Sporty', 
        'Indie Aesthetic', 'Casual'
    ],
    'warna': [
        'Putih', 'Krem', 
        'Hijau', 'Hijau', 
        'Hitam', 'Abu-abu', 
        'Hitam', 'Abu-abu',
        'Pink', 'Putih', 
        'Cokelat', 'Cokelat', 
        'Merah', 'Biru', 
        'Kuning', 'Biru'
    ],
    'gender': [
        'Pria', 'Pria', 
        'Pria', 'Pria', 
        'Unisex', 'Unisex', 
        'Wanita', 'Wanita',
        'Wanita', 'Wanita', 
        'Unisex', 'Unisex', 
        'Unisex', 'Pria', 
        'Unisex', 'Unisex'
    ],
    'target_usia': [
        'Milenial / Gen Z', 
        'Milenial / Gen Z', 
        'Gen Z', 'Gen Z', 
        'Gen Z', 'Gen Z', 
        'Gen Z', 'Gen Z',
        'Gen Z / Gen Alpha', 
        'Gen Z / Gen Alpha', 
        'Gen Z', 'Gen Z', 
        'Gen Z', 'Milenial / Gen Z', 
        'Gen Z', 'Milenial / Gen Z'
    ],
    'harga': [
        149000, 199000, 
        189000, 219000, 
        129000, 249000, 
        279000, 189000,
        159000, 139000, 
        329000, 229000, 
        259000, 299000, 
        179000, 219000
    ],
    'stok': [
        15, 10, 7, 12, 
        20, 14, 9, 11, 
        8, 12, 6, 13, 
        7, 5, 6, 10
    ]
}
df_stok = pd.DataFrame(data_gudang)

# ==========================================
# 3. KAMUS WARNA UNIVERSAL
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
# 4. FUNGSI DETEKSI AI VISION
# ==========================================
def query_ai_vision(image_bytes):
    try:
        API_URL = (
            "https://api-inference."
            "huggingface.co/models/"
            "valentinafed/"
            "clothing-detector"
        )
        response = requests.post(
            API_URL, 
            data=image_bytes, 
            timeout=4
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# ==========================================
# 5. FUNGSI DETEKSI WARNA (VERSI VERTIKAL)
# ==========================================
def dapatkan_warna_all(pil_image, k=2):
    img = pil_image.resize((50, 50))
    img_np = np.array(img)
    if img_np.shape[2] == 4:
        img_np = img_np[:, :, :3]
    piksel = img_np.reshape(-1, 3)
    
    kmeans = KMeans(
        n_clusters=k, 
        random_state=42, 
        n_init=3
    )
    kmeans.fit(piksel)
    warna_pusat = kmeans.cluster_centers_
    labels = kmeans.labels_
    
    counts = np.bincount(labels)
    total = len(labels)
    
    # BARIS YANG TADI KEPOTONG SEKARANG SUDAH DI-BREAK BIAR AMAN!
    persentase = []
    for c in counts:
        p_hitung = (c / total) * 100
        persentase.append(round(p_hitung))
    
    hasil_deteksi = []
    for i, rgb in enumerate(warna_pusat):
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        warna_terdekat = "Putih"
        jarak_terkecil = float('inf')
        
        for n_w, rgb_ref in KAMUS_WARNA.items():
            jarak = np.sqrt(
                (r - rgb_ref[0])**2 + 
                (g - rgb_ref[1])**2 + 
                (b - rgb_ref[2])**2
            )
            if jarak < jarak_terkecil:
                jarak_terkecil = jarak
                warna_terdekat = n_w
                
        hasil_deteksi.append({
            "nama": warna_terdekat, 
            "persen": persentase[i]
        })
    return hasil_deteksi

# ==========================================
# 6. MENU NAVIGASI UTAMA
# ==========================================
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle")

menu = st.sidebar.radio(
    "Pilih Hak Akses:", 
    ["Pembeli", "Admin"]
)

# ==================== SISI PEMBELI ====================
if menu == "Pembeli":
    st.header("👤 Profil Kamu")
    col1, col2 = st.columns(2)
    with col1:
        pilihan_gender = st.selectbox(
            "Gender:", 
            ["Pria", "Wanita"]
        )
    with col2:
        pilihan_usia = st.selectbox(
            "Usia:", 
            ["Gen Z", "Milenial / Gen Z"]
        )

    st.markdown("---")
    st.header("📸 Upload Foto")
    file_foto = st.file_uploader(
        "Pilih foto...", 
        type=["jpg", "png"]
    )

    if 'beli_aktif' not in st.session_state: 
        st.session_state.beli_aktif = False
    if 'hasil_rekomendasi' not in st.session_state: 
        st.session_state.hasil_rekomendasi = None
    if 'w_1' not in st.session_state: st.session_state.w_1 = ""
    if 'w_2' not in st.session_state: st.session_state.w_2 = ""
    if 'p_1' not in st.session_state: st.session_state.p_1 = 0
    if 'p_2' not in st.session_state: st.session_state.p_2 = 0

    if file_foto is not None:
        image = Image.open(file_foto)
        st.image(
            image, 
            caption="Foto Kamu", 
            use_container_width=True
        )
        
        tombol_cari = st.button("CARI GAYA 🚀")

        if tombol_cari:
            with st.spinner('Proses AI...'):
                img_arr = io.BytesIO()
                image.save(img_arr, format='JPEG')
                img_bytes = img_arr.getvalue()
                
                hasil_ai = query_ai_vision(img_bytes)
                d_warna = dapatkan_warna_all(image, k=2)

            st.session_state.w_1 = d_warna[0]['nama']
            st.session_state.w_2 = d_warna[1]['nama']
            st.session_state.p_1 = d_warna[0]['persen']
            st.session_state.p_2 = d_warna[1]['persen']

            f_w = df_stok['warna'].isin([
                st.session_state.w_1, 
                st.session_state.w_2
            ])
            f_g = (df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')
            f_u = df_stok['target_usia'].str.contains(pilihan_usia)
            
            res = df_stok[f_w & f_g & f_u]
            if res.empty:
                res = df_stok[f_g & f_u]

            st.session_state.hasil_rekomendasi = res
            st.session_state.beli_aktif = True

        if st.session_state.beli_aktif:
            st.markdown("#### **🎨 Warna Terdeteksi:**")
            st.info(f"🎨 {st.session_state.w_1} ({st.session_state.p_1}%)")
            st.info(f"🎨 {st.session_state.w_2} ({st.session_state.p_2}%)")

            st.markdown("---")
            st.subheader("📦 Rekomendasi Bundle")

            total_harga = 0
            df_hasil = st.session_state.hasil_rekomendasi
            for idx, row in df_hasil.iterrows():
                st.markdown(f"**{row['nama_produk']}**")
                st.write(f"Harga: Rp {row['harga']:,}")
                total_harga += row['harga']
            
            st.markdown(f"### **Total: Rp {total_harga:,}**")
            
            if st.button("🛒 BELI SEKARANG"):
                st.balloons()
                c_duit = st.empty()
                for _ in range(2):
                    c_duit.markdown(
                        "<h1 style='text-align:center;'>"
                        "💰 💸 💵</h1>", 
                        unsafe_allow_html=True
                    )
                    time.sleep(0.3)
                    c_duit.markdown(
                        "<h1 style='text-align:center;'>"
                        "💸 💵 💰</h1>", 
                        unsafe_allow_html=True
                    )
                    time.sleep(0.3)
                c_duit.empty()
                st.success("🎉 TRANSAKSI BERHASIL!")
                st.session_state.beli_aktif = False

# ==================== SISI ADMIN ====================
else:
    st.header("📊 Admin Dashboard")
    st.dataframe(df_stok, use_container_width=True)
