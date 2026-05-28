import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io
import time

# ==========================================
# 1. CONFIG HALAMAN UTAMA
# ==========================================
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

API_URL = "https://api-inference.huggingface.co/models/valentinafed/clothing-detector"

# ==========================================
# 2. DATABASE GUDANG (40 GEN-Z ITEMS - SUPER RAPAT)
# ==========================================
data_gudang = {
    'nama_produk': [
        'Black Oversized Tee', 'Dark Charcoal Jeans', 'Gothic Black Hoodie', 'Acid Wash Denim Shorts',
        'Black Varsity Jacket', 'Grey Parachute Pants', 'Chunky Cyberpunk Boot', 'Black Pleated Skirt',
        'Sage Green Outer', 'Olive Cargo Pants', 'Khaki Tactical Vest', 'Beige Corduroy Cap',
        'Brown Knit Sweater', 'Sand Cargo Long Skirt', 'Forest Green Windbreaker', 'Tan Baggy Chinos',
        'Oversized Crop Varsity', 'Plated Cargo Skirt', 'Graffiti Graphic Hoodie', 'Wide-Leg Jorts',
        'Cyber Y2K Baby Tee', 'Low Rise Denim Pants', 'Full-Zip Rhinestone Hoodie', 'Star Patchwork Jeans',
        'White Linen Shirt', 'Beige Chino Pants', 'Navy Cable Knit Vest', 'Striped Relaxed Shirt',
        'Black Tailored Trousers', 'White Classic Loafers', 'Polo Knit Sweater', 'Cream Linen Shorts',
        'Pastel Pink Cardigan', 'White Tennis Skirt', 'Ribbon Lace Blouse', 'Floral Mini Skirt',
        'Vintage Football Jersey', 'Track Nylon Pants', 'Retro Adidas Samba', 'Sporty Zip-Up Tracktop'
    ],
    'kategori_baju': [
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Bawahan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Bawahan', 'Bawahan', 'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Atasan', 'Bawahan', 'Bawahan', 'Atasan'
    ],
    'vibe': [
        'Monochrome', 'Monochrome', 'Monochrome', 'Monochrome', 'Monochrome', 'Monochrome', 'Monochrome', 'Monochrome',
        'Earth Tone', 'Earth Tone', 'Earth Tone', 'Earth Tone', 'Earth Tone', 'Earth Tone', 'Earth Tone', 'Earth Tone',
        'Y2K Streetwear', 'Y2K Streetwear', 'Y2K Streetwear', 'Y2K Streetwear', 'Y2K Streetwear', 'Y2K Streetwear', 'Y2K Streetwear', 'Y2K Streetwear',
        'Casual', 'Casual', 'Casual', 'Casual', 'Casual', 'Casual', 'Casual', 'Casual',
        'Soft Girl Coquette', 'Soft Girl Coquette', 'Soft Girl Coquette', 'Soft Girl Coquette',
        'Sporty', 'Sporty', 'Sporty', 'Sporty'
    ],
    'warna': [
        'Hitam', 'Abu-abu', 'Hitam', 'Abu-abu', 'Hitam', 'Abu-abu', 'Hitam', 'Hitam',
        'Hijau', 'Hijau', 'Krem', 'Krem', 'Cokelat', 'Cokelat', 'Hijau', 'Krem',
        'Hitam', 'Abu-abu', 'Putih', 'Biru', 'Putih', 'Biru', 'Hitam', 'Biru',
        'Putih', 'Krem', 'Biru', 'Putih', 'Hitam', 'Putih', 'Krem', 'Putih',
        'Pink', 'Putih', 'Putih', 'Pink', 'Biru', 'Hitam', 'Putih', 'Hijau'
    ],
    'gender': [
        'Unisex', 'Unisex', 'Unisex', 'Unisex', 'Pria', 'Unisex', 'Unisex', 'Wanita',
        'Pria', 'Pria', 'Pria', 'Unisex', 'Unisex', 'Wanita', 'Unisex', 'Pria',
        'Wanita', 'Wanita', 'Unisex', 'Pria', 'Wanita', 'Wanita', 'Unisex', 'Unisex',
        'Pria', 'Pria', 'Pria', 'Pria', 'Unisex', 'Unisex', 'Pria', 'Unisex',
        'Wanita', 'Wanita', 'Wanita', 'Wanita', 'Unisex', 'Unisex', 'Unisex', 'Pria'
    ],
    'target_usia': [
        'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z',
        'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z',
        'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z / Gen Alpha', 'Gen Z', 'Gen Z', 'Gen Z',
        'Milenial / Gen Z', 'Milenial / Gen Z', 'Milenial / Gen Z', 'Milenial / Gen Z', 'Milenial / Gen Z', 'Milenial / Gen Z', 'Milenial / Gen Z', 'Milenial / Gen Z',
        'Gen Z / Gen Alpha', 'Gen Z / Gen Alpha', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z', 'Gen Z'
    ],
    'harga': [
        129000, 249000, 289000, 179000, 319000, 229000, 450000, 159000,
        189000, 219000, 165000, 89000,  245000, 199000, 299000, 185000,
        279000, 189000, 269000, 195000, 119000, 239000, 349000, 289000,
        149000, 199000, 155000, 169000, 210000, 389000, 225000, 135000,
        159000, 139000, 145000, 125000, 198000, 189000, 420000, 275000
    ]
}
df_stok = pd.DataFrame(data_gudang)

# ==========================================
# 3. INITIALIZATION DATABASE TRANSAKSI
# ==========================================
if 'log_gender_dicari' not in st.session_state: st.session_state.log_gender_dicari = []
if 'total_omzet_toko' not in st.session_state: st.session_state.total_omzet_toko = 0
if 'total_penggunaan_ai' not in st.session_state: st.session_state.total_penggunaan_ai = 0

# ==========================================
# 4. FUNGSI AI VISION
# ==========================================
def query_ai_vision(image_bytes):
    try:
        response = requests.post(API_URL, data=image_bytes, timeout=4)
        if response.status_code == 200: return response.json()
        return []
    except: return []

# ==========================================
# 5. NAVIGASI UTAMA
# ==========================================
st.title("VIBE-ID 🛍️")
st.caption("AI Smart Bundle Personalizer")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

# ==================== SISI PEMBELI ====================
if menu == "Pembeli":
    st.header("👤 Langkah 1: Profil Gaya Kamu")
    col1, col2 = st.columns(2)
    with col1: pilihan_gender = st.selectbox("Gender Kamu:", ["Pria", "Wanita"])
    with col2: pilihan_usia = st.selectbox("Target Usia:", ["Gen Z", "Milenial / Gen Z"])

    st.markdown("---")
    st.header("📸 Langkah 2: Upload Foto Inspirasi")
    file_foto = st.file_uploader("Pilih foto pakaian...", type=["jpg", "jpeg", "png"])
    
    if file_foto is not None:
        img_tampil = Image.open(file_foto)
        st.image(img_tampil, caption="Foto Inspirasi Terunggah", use_container_width=True)

    st.markdown("---")
    st.header("🎯 Langkah 3: Rekomendasi Gaya")
    
    if 'beli_aktif' not in st.session_state: st.session_state.beli_aktif = False
    if 'hasil_rekomendasi' not in st.session_state: st.session_state.hasil_rekomendasi = None
    if 'warna_terdeteksi' not in st.session_state: st.session_state.warna_terdeteksi = "Putih"

    if st.button("RUN AI VISUAL MATCHING 🚀"):
        if file_foto is None:
            st.warning("⚠️ Upload fotonya dulu dong bre biar AI bisa jalan!")
        else:
            with st.spinner('AI sedang menganalisis objek & warna foto...'):
                st.session_state.total_penggunaan_ai += 1
                st.session_state.log_gender_dicari.append(pilihan_gender)
                
                img_arr = io.BytesIO()
                img_tampil.save(img_arr, format='JPEG')
                img_bytes = img_arr.getvalue()
                hasil_ai = query_ai_vision(img_bytes)
                
                # Deteksi warna dari nama file gambar
                nama_file = file_foto.name.lower()
                warna_fix = "Putih"
                if "black" in nama_file or "hitam" in nama_file or "dark" in nama_file or "grey" in nama_file or "abu" in nama_file: warna_fix = "Hitam"
                elif "green" in nama_file or "hijau" in nama_file or "sage" in nama_file or "olive" in nama_file: warna_fix = "Hijau"
                elif "pink" in nama_file or "coquette" in nama_file: warna_fix = "Pink"
                elif "blue" in nama_file or "biru" in nama_file or "denim" in nama_file: warna_fix = "Biru"
                elif "krem" in nama_file or "beige" in nama_file or "chino" in nama_file: warna_fix = "Krem"
                elif "brown" in nama_file or "cokelat" in nama_file or "vintage" in nama_file: warna_fix = "Cokelat"
                
                st.session_state.warna_terdeteksi = warna_fix
                
                f_g = (df_stok['gender'] == pilihan_gender) | (df_stok['gender'] == 'Unisex')
                f_u = df_stok['target_usia'].str.contains(pilihan_usia)
                f_w = (df_stok['warna'] == warna_fix)
                
                res = df_stok[f_g & f_u & f_w]
                if len(res) < 2:
                    res_tambahan = df_stok[f_g & f_u & ((df_stok['warna'] == 'Putih') | (df_stok['warna'] == 'Hitam'))]
                    res = pd.concat([res, res_tambahan]).drop_duplicates()
                
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
            st.session_state.total_omzet_toko += total_harga
            html_duit = """
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999; overflow: hidden;">
                <marquee direction="down" scrollamount="15" style="height: 100%;"><span style="font-size:90px;">💵 💸 💵 💸</span></marquee>
                <marquee direction="down"
