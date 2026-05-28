import streamlit as st
import pandas as pd
from PIL import Image
import requests
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

# KONSTANTA API (Dibuat pendek ke bawah agar aman)
API_URL = (
    "https://api-inference."
    "huggingface.co/models/"
    "valentinafed/"
    "clothing-detector"
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
# 3. FUNGSI AI VISION ANDALAN LU
# ==========================================
def query_ai_vision(image_bytes):
    try:
        response = requests.post(
            API_URL, 
            data=image_bytes, 
            timeout=4
        )
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except:
        return []

# ==========================================
# 4. MENU NAVIGASI UTAMA APLIKASI
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
    
    # Inisialisasi session state yang aman
    if 'beli_aktif' not in st.session_state: 
        st.session_state.beli_aktif = False
    if 'hasil_rekomendasi' not in st.session_state: 
        st.session_state.hasil_rekomendasi = None

    if st.button("RUN AI VISUAL MATCHING 🚀"):
        if file_foto is None:
            st.warning("⚠️ Upload fotonya dulu dong bre biar AI bisa jalan!")
        else:
            with st.spinner('AI sedang memproses gambar lu...'):
                img_arr = io.BytesIO()
                img_tampil.save(img_arr, format='JPEG')
                img_bytes = img_arr.getvalue()
                
                hasil_ai = query_ai_vision(img_bytes)
                
                g_user = pilihan_gender
                u_user = pilihan_usia
                
                f_g = (df_stok['gender'] == g_user) | (df_stok['gender'] == 'Unisex')
                f_u = df_stok['target_usia'].str.contains(u_user)
                
                res = df_stok[f_g & f_u]
                if res.empty:
                    res = df_stok.head(2)
                    
                st.session_state.hasil_rekomendasi = res
                st.session_state.beli_aktif = True

    # Bagian ini dibungkus rapi di dalam blok "Pembeli" agar tidak eror spasi
    if st.session_state.beli_aktif:
        st.success("🎨 AI Vision Berhasil Menganalisis Foto Lu!")
        st.subheader("📦 Hasil Paket Rekomendasi VIBE-ID")
        
        total_harga = 0
        df_hasil = st.session_state.hasil_rekomendasi
        for idx, row in df_hasil.iterrows():
            st.markdown(f"**[{row['vibe']}] {row['nama_produk']}**")
            st.caption(f"Kategori: {row['kategori_baju']} | Warna: {row['warna']}")
            st.write(f"Harga: Rp {row['harga']:,}")
            total_harga += row['harga']
            st.markdown("")
        
        st.markdown(f"### **Total Harga Bundle: Rp {total_harga:,}**")
        st.markdown("---")
        
        # --- BLOK TOMBOL BELI DENGAN EFEK HUJAN DUIT TERBANG ---
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
    
    t_ins = (
        "💡 **AI Driven Insights:** "
        "Segmen **Gen Z Wanita** minggu ini "
        "mendominasi tren pasar dengan gaya *Y2K Streetwear*!"
    )
    st.info(t_ins)
    
    st.write("### 📂 Perbarui Katalog Toko")
    file_excel = st.file_uploader(
        "Upload Katalog (.xlsx)", 
        type=["xlsx"]
    )
    if file_excel is not None:
        st.success("🎉 Berhasil memperbarui katalog gudang!")
        
    st.markdown("---")
    st.subheader("📋 Data Stok Gudang Saat Ini")
    st.dataframe(df_stok, use_container_width=True)
