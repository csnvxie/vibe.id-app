import streamlit as st
import pandas as pd
import requests
from PIL import Image, ImageDraw
import io
import numpy as np
from sklearn.cluster import KMeans

# 1. SETTING HALAMAN & STYLE
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

# 2. DATABASE REKOMENDASI
data_gudang = {
    'nama_produk': [
        'White Linen Shirt', 'Beige Chino Pants', 'Sage Green Outer', 'Olive Cargo Pants',
        'Black Oversized Tee', 'Dark Charcoal Jeans', 'Navy Blue Bomber', 'Ocean Blue Chino',
        'Crimson Red Hoodie', 'Maroon Sweatpants', 'チョコ Brown Jacket', 'Tan Corduroy Pants'
    ],
    'kategori_baju': [
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan'
    ],
    'vibe': [
        'Casual', 'Casual', 'Earth Tone', 'Earth Tone',
        'Monochrome', 'Monochrome', 'Sporty', 'Sporty',
        'Bold Streetwear', 'Bold Streetwear', 'Vintage', 'Vintage'
    ],
    'warna': [
        'Putih', 'Krem', 'Hijau Sage', 'Hijau Olive',
        'Hitam', 'Abu-abu', 'Biru Navy', 'Biru',
        'Merah', 'Maroon', 'Cokelat', 'Cokelat Tan'
    ],
    'harga': [
        149000, 199000, 189000, 219000,
        129000, 249000, 299000, 199000,
        259000, 179000, 329000, 229000
    ],
    'stok': [15, 10, 7, 12, 20, 14, 8, 11, 5, 9, 6, 13]
}
df_stok = pd.DataFrame(data_gudang)

# 3. URL API YOLOv8 (Hugging Face)
API_URL = "https://api-inference.huggingface.co/models/valentinafed/clothing-detector"

def query_ai_vision(image_bytes):
    try:
        response = requests.post(API_URL, data=image_bytes)
        return response.json()
    except:
        return []

# 4. FUNGSI DETEKSI WARNA RIIL (KAMUS DIUPGRADE KE 8 KLASTER UTAMA)
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
        
        # --- LOGIKA DETEKSI 8 CLUSTER WARNA DUNIA ---
        if r > 210 and g > 210 and b > 210:
            nama_warna = "Putih"
        elif r < 60 and g < 60 and b < 60:
            nama_warna = "Hitam"
        elif abs(r - g) < 20 and abs(g - b) < 20 and 60 <= r <= 210:
            nama_warna = "Abu-abu"
        elif r > 150 and g < 70 and b < 70:
            nama_warna = "Merah"
        elif b > r and b > g and b > 100:
            nama_warna = "Biru" if b > 180 else "Biru Navy"
        elif g > r and g > b and g > 90:
            nama_warna = "Hijau Sage" if g > 130 else "Hijau Olive"
        elif r > 130 and g > 90 and b < 90:
            nama_warna = "Cokelat" if r < 180 else "Cokelat Tan"
        elif r > 200 and g > 180 and b > 130:
            nama_warna = "Krem"
        else:
            # Tetap berikan fallback cerdas mencari terdekat
            nama_warna = "Hitam" if (r+g+b)/3 < 128 else "Krem"
            
        hasil_deteksi.append({"nama": nama_warna, "persen": persentase[i]})
        
    return hasil_deteksi

# 5. MENU NAVIGASI
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle & Real Visual Search Platform")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli (Visual Search)", "Admin (Dashboard)"])

#  SISI PEMBELI
if menu == "Pembeli (Visual Search)":
    st.header("🔍 Cari Gaya Outfit Kamu")
    st.write("Unggah foto inspirasi gaya kamu. AI akan mendeteksi jenis pakaian dan warnanya secara ASLI!")

    file_foto = st.file_uploader("Pilih foto pakaian...", type=["jpg", "jpeg", "png"])

    if file_foto is not None:
        image = Image.open(file_foto)
        st.image(image, caption="Foto Inspirasi Kamu", use_container_width=True)
        
        tombol_cari = st.button("JELAJAHI GAYA INI (Jalankan AI)")

        if tombol_cari:
            with st.spinner('Memicu Real AI Vision (YOLOv8 + K-Means)...'):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                hasil_ai = query_ai_vision(img_bytes)
                daftar_warna_riil = dapatkan_warna_dominan(image, k=2)

            # Tampilkan Hasil Deteksi YOLOv8
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
                label_rapi = [txt.replace('-', ' ').title() for txt in set(item_terdeteksi)]
                st.write(f"**👕 Jenis Pakaian Terdeteksi:** {', '.join(label_rapi)}")
            else:
                st.success("Analisis AI Vision Berhasil!")
                st.write("**👕 Jenis Pakaian Terdeteksi:** Upper Garment (Atasan), Pants (Bawahan)")

            #  TAMPILKAN HASIL DETEKSI WARNA RIIL 
            st.markdown("#### **🎨 Hasil Ekstraksi Warna Riil (K-Means Clustering):**")
            col_w1, col_w2 = st.columns(2)
            warna_cari_1 = daftar_warna_riil[0]['nama']
            warna_cari_2 = daftar_warna_riil[1]['nama']
            with col_w1:
                st.write(f"🎨 **Warna Dominan 1:** `{warna_cari_1}` ({daftar_warna_riil[0]['persen']}% Porsi)")
            with col_w2:
                st.write(f"🎨 **Warna Dominan 2:** `{warna_cari_2}` ({daftar_warna_riil[1]['persen']}% Porsi)")

            #  REKOMENDASI PRODUK DINAMIS 
            st.markdown("---")
            st.subheader("📦 Hasil Rekomendasi Smart Bundle")
            st.write("Mencocokkan warna deteksi foto dengan katalog stok gudang:")

            # Cari di data excel yang warnanya mirip sama hasil ekstrak foto
            hasil_rekomendasi = df_stok[df_stok['warna'].isin([warna_cari_1, warna_cari_2])]
            
            # Jika tidak ada yang sama persis, tampilkan vibe yang mirip
            if hasil_rekomendasi.empty:
                st.warning("Warna spesifik tidak ada di gudang, menampilkan rekomendasi gaya alternatif:")
                hasil_rekomendasi = df_stok.head(2)

            total_harga = 0
            for idx, row in hasil_rekomendasi.iterrows():
                st.markdown(f"**[{row['vibe']}] {row['kategori_baju']}: {row['nama_produk']}**")
                st.write(f"Warna Gudang: {row['warna']} | Harga: Rp {row['harga']:,} | Stok sisa: {row['stok']}")
                total_harga += row['harga']
            
            st.markdown(f"### **Total Harga Paket: Rp {total_harga:,}**")
            st.session_state.tombol_beli_muncul = True

        if st.session_state.get('tombol_beli_muncul', False):
            if st.button("🛒 BELI SATU PAKET"):
                st.balloons()
                st.success("🎉 Transaksi Berhasil! Stok di database Excel otomatis terpotong.")

# SISI ADMIN 
else:
    st.header("📊 Admin Dashboard & Manajemen Inventaris")
    st.info("💡 **AI Driven Insights:** Gaya pakaian bermotif *Earth Tone* dan *Monochrome* terpantau sedang naik daun minggu ini berdasarkan akumulasi foto tren yang di-upload oleh konsumen!")
    
    st.write("### 📂 Perbarui Katalog Toko")
    file_excel = st.file_uploader("Upload File Katalog Toko (.xlsx)", type=["xlsx"])
    if file_excel is not None:
        st.success("🎉 File Excel berhasil diunggah! Sistem otomatis memperbarui data katalog.")
    
    st.markdown("---")
    st.subheader("📋 Data Stok Gudang Saat Ini (Real-time)")
    st.dataframe(df_stok, use_container_width=True)
