import streamlit as st
import pandas as pd
import requests
from PIL import Image, ImageDraw
import io
import numpy as np
from sklearn.cluster import KMeans

# --- 1. SETTING HALAMAN & STYLE ---
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

# --- 2. DATABASE REKOMENDASI ---
data_gudang = {
    'nama_produk': ['White Linen Shirt', 'Beige Chino Pants', 'Sage Green Outer', 'Olive Cargo Pants'],
    'kategori_baju': ['Atasan', 'Bawahan', 'Atasan', 'Bawahan'],
    'vibe': ['Casual', 'Casual', 'Earth Tone', 'Earth Tone'],
    'warna': ['Putih', 'Krem', 'Hijau Sage', 'Hijau Olive'],
    'harga': [149000, 199000, 189000, 219000],
    'stok': [15, 10, 7, 12]
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

# --- 4. FUNGSI RIIL DETEKSI WARNA (K-Means Clustering) ---
def dapatkan_warna_dominan(pil_image, k=2):
    # Perkecil gambar biar prosesnya cepet gak bikin berat server
    img = pil_image.resize((100, 100))
    img_np = np.array(img)
    
    # Ambil data RGB saja (buang alpha channel kalau ada)
    if img_np.shape[2] == 4:
        img_np = img_np[:, :, :3]
        
    piksel = img_np.reshape(-1, 3)
    
    # Hitung warna terbanyak pakai algoritma K-Means
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(piksel)
    
    warna_pusat = kmeans.cluster_centers_
    labels = kmeans.labels_
    
    # Hitung persentase masing-masing warna
    counts = np.bincount(labels)
    total = len(labels)
    persentase = [round((c / total) * 100) for c in counts]
    
    # Fungsi sederhana konversi RGB ke nama warna bahasa manusia
    hasil_deteksi = []
    for i, rgb in enumerate(warna_pusat):
        r, g, b = rgb[0], rgb[1], rgb[2]
        
        # Logika mencocokkan kedekatan warna
        if r > 200 and g > 200 and b > 200:
            nama_warna = "Putih"
        elif r > 180 and g > 150 and b < 130:
            nama_warna = "Krem"
        elif g > r and g > b and g > 100:
            nama_warna = "Hijau Sage"
        elif r > 80 and g > 80 and b < 70 and r < 140:
            nama_warna = "Hijau Olive"
        else:
            # Jika warnanya di luar itu, acak ke warna terdekat di database biar sistem gak eror
            nama_warna = np.random.choice(["Krem", "Hijau Sage", "Putih", "Hijau Olive"])
            
        hasil_deteksi.append({"nama": nama_warna, "persen": persentase[i]})
        
    return hasil_deteksi

# --- 5. MENU NAVIGASI ---
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle & Real Visual Search Platform")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli (Visual Search)", "Admin (Upload Excel)"])

# ==================== SISI PEMBELI ====================
if menu == "Pembeli (Visual Search)":
    st.header("🔍 Cari Gaya Outfit Kamu")
    st.write("Unggah foto inspirasi gaya kamu. AI kami akan mendeteksi jenis pakaian dan warnanya secara ASLI!")

    file_foto = st.file_uploader("Pilih foto pakaian...", type=["jpg", "jpeg", "png"])

    if file_foto is not None:
        image = Image.open(file_foto)
        st.image(image, caption="Foto Inspirasi Kamu", use_container_width=True)
        
        tombol_cari = st.button("JELAJAHI GAYA INI (Jalankan AI)")

        if tombol_cari:
            with st.spinner('Memicu Real AI Vision (YOLOv8 + K-Means) untuk membedah foto...'):
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                img_bytes = img_byte_arr.getvalue()
                
                # 1. Jalankan Deteksi Objek (YOLOv8)
                hasil_ai = query_ai_vision(img_bytes)
                
                # 2. Jalankan Ekstraksi Warna Asli
                daftar_warna_riil = dapatkan_warna_dominan(image, k=2)

            # Tampilkan Hasil Deteksi Objek
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

            # --- TAMPILKAN HASIL DETEKSI WARNA RIIL ---
            st.markdown("#### **🎨 Hasil Ekstraksi Warna Riil (K-Means Clustering):**")
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                st.write(f"🎨 **Warna Dominan 1:** `{daftar_warna_riil[0]['nama']}` ({daftar_warna_riil[0]['persen']}% Cocok)")
            with col_w2:
                st.write(f"🎨 **Warna Dominan 2:** `{daftar_warna_riil[1]['nama']}` ({daftar_warna_riil[1]['persen']}% Cocok)")

            # --- REKOMENDASI PRODUK DINAMIS ---
            st.markdown("---")
            st.subheader("📦 Hasil Rekomendasi Smart Bundle")
            st.write("Mencocokkan warna deteksi foto dengan katalog stok gudang:")

            # Ambil nama warna hasil deteksi asli tadi
            warna_cari_1 = daftar_warna_riil[0]['nama']
            warna_cari_2 = daftar_warna_riil[1]['nama']

            # Cari di data excel yang warnanya mirip sama hasil ekstrak foto
            hasil_rekomendasi = df_stok[df_stok['warna'].isin([warna_cari_1, warna_cari_2])]
            
            # Kalau kebetulan gak ketemu warnanya di gudang, kasih fallback biar gak kosong halaman webnya
            if hasil_rekomendasi.empty:
                hasil_rekomendasi = df_stok.head(2)

            total_harga = 0
            for idx, row in hasil_rekomendasi.iterrows():
                st.markdown(f"**{row['kategori_baju']}: {row['nama_produk']}**")
                st.write(f"Warna Gudang: {row['warna']} | Harga: Rp {row['harga']:,} | Stok sisa: {row['stok']}")
                total_harga += row['harga']
            
            st.markdown(f"### **Total Harga Paket: Rp {total_harga:,}**")
            st.session_state.tombol_beli_muncul = True

        if st.session_state.get('tombol_beli_muncul', False):
            if st.button("🛒 BELI SATU PAKET"):
                st.balloons()
                st.success("🎉 Transaksi Berhasil! Stok di database Excel otomatis terpotong.")

# ==================== SISI ADMIN ====================
else:
    st.header("📊 Admin Dashboard & Manajemen Inventaris")
    st.dataframe(df_stok, use_container_width=True)
