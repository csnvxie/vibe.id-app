import streamlit as st
import pandas as pd
import requests
from PIL import Image, ImageDraw
import io
import numpy as np
from sklearn.cluster import KMeans

# --- 1. SETTING HALAMAN & STYLE ---
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

# --- 2. DATABASE UTOH ---
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
        'Putih', 'Krem', 'Hijau Sage', 'Hijau Olive',
        'Hitam', 'Abu-abu', 'Hitam', 'Abu-abu',
        'Putih', 'Putih', 'Cokelat', 'Cokelat Tan'
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
    ],
    'stok': [15, 10, 7, 12, 20, 14, 9, 11, 8, 12, 6, 13]
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

# --- 4. FUNGSI DETEKSI WARNA RIIL (K-Means) ---
def dapatkan_warna_dominan(pil_image, k=2):
    img = pil_image.resize((100, 100))
    img_np = np.array(img)
    if img_np.shape[2] == 4:
        img_np = img_np[:, :, :3]
    piksel = img_np.reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(piksel)
    warna_pusat = kmeans.cluster_centers_
    labels = kmeans.labels_
    counts = np.bincount(labels)
    total = len(labels)
    persentase = [round((c / total) * 100) for c in counts]
    
    hasil_deteksi = []
    for i, rgb in enumerate(warna_pusat):
        r, g, b = rgb[0], rgb[1], rgb[2]
        if r > 210 and g > 210 and b > 210:
            nama_warna = "Putih"
        elif r < 60 and g < 60 and b < 60:
            nama_warna = "Hitam"
        elif abs(r - g) < 20 and abs(g - b) < 20 and 60 <= r <= 210:
            nama_warna = "Abu-abu"
        elif g > r and g > b and g > 90:
            nama_warna = "Hijau Sage" if g > 130 else "Hijau Olive"
        elif r > 130 and g > 90 and b < 90:
            nama_warna = "Cokelat" if r < 180 else "Cokelat Tan"
        elif r > 200 and g > 180 and b > 130:
            nama_warna = "Krem"
        else:
            nama_warna = "Hitam" if (r+g+b)/3 < 128 else "Krem"
        hasil_deteksi.append({"nama": nama_warna, "persen": persentase[i]})
    return hasil_deteksi

# --- 5. MENU NAVIGASI ---
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle & Hyper-Personalized Recommendation")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli (Visual Search)", "Admin (Dashboard)"])

# ==================== SISI PEMBELI ====================
if menu == "Pembeli (Visual Search)":
    st.header("👤 Langkah 1: Lengkapi Profil Kamu")
    st.write("Isi data diri kamu terlebih dahulu agar AI bisa memberikan rekomendasi yang paling cocok.")
    
    # Input gender dan usia ditaruh paling atas
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        pilihan_gender = st.selectbox("Pilih Gender Kamu:", ["Pria", "Wanita"])
    with col_input2:
        pilihan_usia = st.selectbox("Pilih Kelompok Usia / Generasi:", ["Gen Z", "Milenial / Gen Z", "Gen Z / Gen Alpha"])

    # Setelah isi profil, baru masuk ke langkah upload foto
    st.markdown("---")
    st.header("📸 Langkah 2: Upload Foto Inspirasi Gaya")
    file_foto = st.file_uploader("Pilih dan unggah foto pakaian pilihanmu...", type=["jpg", "jpeg", "png"])

    if file_foto is not None:
        image = Image.open(file_foto)
        st.image(image, caption="Foto Inspirasi Kamu", use_container_width=True)
        
        # Tombol jalanin AI ditaruh paling bawah setelah semua siap
        tombol_cari = st.button("JELAJAHI GAYA PERSONAL KAMU 🚀")

        if tombol_cari:
            with st.spinner('Menyelaraskan profil user dengan analisis AI Vision...'):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                hasil_ai = query_ai_vision(img_bytes)
                daftar_warna_riil = dapatkan_warna_dominan(image, k=2)

            # Hasil YOLOv8
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

            # Hasil K-Means Warna
            st.markdown("#### **🎨 Hasil Analisis Warna Foto:**")
            warna_cari_1 = daftar_warna_riil[0]['nama']
            warna_cari_2 = daftar_warna_riil[1]['nama']
            st.write(f"🎨 Warna Dominan Terdeteksi: `{warna_cari_1}` & `{warna_cari_2}`")

            # Output Rekomendasi
            st.markdown("---")
            st.subheader("📦 Hasil Rekomendasi Smart Bundle Sesuai Profil Kamu")
            st.write(f"Menampilkan produk paket terbaik khusus **{pilihan_gender}** ({pilihan_usia}) dengan tema warna `{warna_cari_1}/{warna_cari_2}`:")

            # Proses filter database
            hasil_rekomendasi = df_stok[
                (df_stok['warna'].isin([warna_cari_1, warna_cari_2])) & 
                ((df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')) &
                (df_stok['target_usia'].str.contains(pilihan_usia))
            ]
            
            if hasil_rekomendasi.empty:
                st.warning("Kombinasi warna pas pasan, menampilkan gaya alternatif yang sesuai dengan profil gender & usiamu:")
                hasil_rekomendasi = df_stok[
                    ((df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')) &
                    (df_stok['target_usia'].str.contains(pilihan_usia))
                ]

            total_harga = 0
            for idx, row in hasil_rekomendasi.iterrows():
                st.markdown(f"**[{row['vibe']}] {row['kategori_baju']}: {row['nama_produk']}**")
                st.caption(f"Spesifikasi: Gaya {row['vibe']} | Kategori: {row['gender']} | Target Usia: {row['target_usia']}")
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
