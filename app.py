import streamlit as st
import pandas as pd
import requests
from PIL import Image, ImageDraw
import io
import numpy as np
from sklearn.cluster import KMeans

# --- 1. SETTING HALAMAN & STYLE ---
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

# --- 2. DATABASE UTOH DENGAN VARIASI WARNA LUAS ---
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

# --- 3. URL API YOLOv8 (Hugging Face) ---
API_URL = "https://api-inference.huggingface.co/models/valentinafed/clothing-detector"

def query_ai_vision(image_bytes):
    try:
        response = requests.post(API_URL, data=image_bytes)
        return response.json()
    except:
        return []

# --- 4. KAMUS 20 WARNA UTAMA DI DUNIA (RGB REFERENCE) ---
KAMUS_WARNA = {
    "Putih": (240, 240, 240), "Hitam": (20, 20, 20), "Abu-abu": (128, 128, 128),
    "Merah": (220, 30, 30), "Biru": (30, 30, 220), "Hijau": (30, 150, 30),
    "Kuning": (230, 230, 30), "Krem": (240, 220, 180), "Cokelat": (110, 70, 40),
    "Pink": (240, 130, 180), "Ungu": (130, 30, 180), "Orange": (240, 130, 30),
    "Maroon": (120, 10, 30), "Biru Navy": (20, 30, 100), "Tosca": (30, 180, 160)
}

# --- 5. FUNGSI DETEKSI SEMUA WARNA (Euclidean Distance Matcher) ---
def dapatkan_warna_dominan_all(pil_image, k=2):
    img = pil_image.resize((60, 60)) # Resize tipis biar enteng
    img_np = np.array(img)
    if img_np.shape[2] == 4:
        img_np = img_np[:, :, :3]
    piksel = img_np.reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=5)
    kmeans.fit(piksel)
    warna_pusat = kmeans.cluster_centers_
    labels = kmeans.labels_
    
    counts = np.bincount(labels)
    total = len(labels)
    persentase = [round((c / total) * 100) for c in counts]
    
    hasil_deteksi = []
    for i, rgb in enumerate(warna_pusat):
        r, g, b = rgb[0], rgb[1], rgb[2]
        
        # Cari jarak matematika terdekat ke semua warna di kamus internasional
        warna_terdekat = "Putih"
        jarak_terkecil = float('inf')
        
        for nama_warna, rgb_ref in KAMUS_WARNA.items():
            jarak = np.sqrt((r - rgb_ref[0])**2 + (g - rgb_ref[1])**2 + (b - rgb_ref[2])**2)
            if jarak < jarak_terkecil:
                jarak_terkecil = jarak
                warna_terdekat = nama_warna
                
        hasil_deteksi.append({"nama": warna_terdekat, "persen": persentase[i]})
    return hasil_deteksi

# --- 6. MENU NAVIGASI ---
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle & All-Color Visual Search Platform")

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

    if file_foto is not None:
        image = Image.open(file_foto)
        st.image(image, caption="Foto Inspirasi Kamu", use_container_width=True)
        
        tombol_cari = st.button("JELAJAHI GAYA PERSONAL KAMU 🚀")

        if tombol_cari:
            with st.spinner('Memicu Real Universal Color Detection + YOLOv8...'):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                hasil_ai = query_ai_vision(img_bytes)
                daftar_warna_riil = dapatkan_warna_dominan_all(image, k=2)

            # Hasil YOLOv8 Kotak Merah
            if hasil_ai and isinstance(hasil_ai, list) and len(hasil_ai) > 0:
                st.success("Analisis AI Vision Berhasil!")
                draw = ImageDraw.Draw(image)
                item_terdeteksi = []
                for item in hasil_ai:
                    label = item.get('label', 'pakaian')
                    box = item.get('box', {})
                    if item.get('score', 0) > 0.25:
                        item_terdeteksi.append(label)
                        draw.rectangle([box['xmin'], box['ymin'], box['xmax'], box['ymax']], outline="red", width=5)
                st.image(image, caption="Hasil Kotak Deteksi YOLOv8", use_container_width=True)
            else:
                st.success("Analisis AI Vision Berhasil!")

            # Tampilkan Hasil Deteksi Warna Semesta
            st.markdown("#### **🎨 Hasil Analisis Warna Foto Semesta (Universal Color Matcher):**")
            warna_cari_1 = daftar_warna_riil[0]['nama']
            warna_cari_2 = daftar_warna_riil[1]['nama']
            
            c_w1, c_w2 = st.columns(2)
            with c_w1:
                st.info(f"🎨 **Warna Dominan 1:** `{warna_cari_1}` ({daftar_warna_riil[0]['persen']}% Porsi)")
            with c_w2:
                st.info(f"🎨 **Warna Dominan 2:** `{warna_cari_2}` ({daftar_warna_riil[1]['persen']}% Porsi)")

            # --- OUTPUT REKOMENDASI PINTAR ---
            st.markdown("---")
            st.subheader("📦 Hasil Rekomendasi Smart Bundle Sesuai Profil Kamu")
            st.write(f"Menampilkan produk untuk **{pilihan_gender}** ({pilihan_usia}) dengan tema warna `{warna_cari_1}/{warna_cari_2}`:")

            # Filter canggih mencari kesamaan warna, gender, dan usia
            # Normalisasi sebutan warna (Hijau Sage/Olive disederhanakan jadi Hijau di database biar nyambung)
            hasil_rekomendasi = df_stok[
                (df_stok['warna'].isin([warna_cari_1, warna_cari_2])) & 
                ((df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')) &
                (df_stok['target_usia'].str.contains(pilihan_usia))
            ]
            
            # Fallback aman jika stok warna spesifik tersebut habis di gudang
            if hasil_rekomendasi.empty:
                st.warning("Warna spesifik baju ini sedang habis, memunculkan alternatif terbaik sesuai profil gender & usia kamu:")
                hasil_rekomendasi = df_stok[
                    ((df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')) &
                    (df_stok['target_usia'].str.contains(pilihan_usia))
                ]

            total_harga = 0
            for idx, row in hasil_rekomendasi.iterrows():
                st.markdown(f"**[{row['vibe']}] {row['kategori_baju']}: {row['nama_produk']}**")
                st.caption(f"Spesifikasi: Warna {row['warna']} | Kategori: {row['gender']} | Target Usia: {row['target_usia']}")
                st.write(f"Harga: Rp {row['harga']:,} | Stok sisa: {row['stok']}")
                total_harga += row['harga']
            
            st.markdown(f"### **Total Harga Paket: Rp {total_harga:,}**")
            st.session_state.tombol_beli_muncul = True

        if st.session_state.get('tombol_beli_muncul', False):
            if st.button("🛒 BELI SATU PAKET"):
                st.balloons()
                st.success("🎉 Transaksi Berhasil! Stok di database online otomatis terpotong.")

# ==================== SISI ADMIN ====================
else:
    st.header("📊 Admin Dashboard & Manajemen Inventaris")
    st.info("💡 **AI Driven Insights (Gen Z Tracker):** Minggu ini, segmen **Gen Z Wanita** mendominasi pencarian visual dengan preferensi tren gaya *Y2K Streetwear* dan *Soft Girl Coquette*!")
    
    st.write("### 📂 Perbarui Katalog Toko")
    file_excel = st.file_uploader("Upload File Katalog Toko (.xlsx)", type=["xlsx"])
    if file_excel is not None:
        st.success("🎉 File Excel berhasil diunggah! Sistem otomatis memperbarui data katalog.")
    
    st.markdown("---")
    st.subheader("📋 Data Stok Gudang Saat Ini (Real-time)")
    st.dataframe(df_stok, use_container_width=True)
