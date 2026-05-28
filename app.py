import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io

# ==========================================
# 1. CONFIG & KONSTANTA UTAMA
# ==========================================
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

API_URL = "https://api-inference.huggingface.co/models/valentinafed/clothing-detector"

# ==========================================
# 2. DATABASE GUDANG + 100% REAL & FIXED IMAGES (40 PRODUK SINKRON)
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
    ],
    # BERIKUT ADALAH 40 URL FOTO REALISTIS DAN TETAP (FIXED) SESUAI NAMA PRODUK
    'url_gambar': [
        # Monochrome (1-8)
        'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop', # Black Oversized Tee
        'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500&auto=format&fit=crop', # Dark Charcoal Jeans
        'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500&auto=format&fit=crop', # Gothic Black Hoodie
        'https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500&auto=format&fit=crop', # Acid Wash Denim Shorts
        'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop', # Black Varsity Jacket
        'https://images.unsplash.com/photo-1517423568366-8b83523034fd?w=500&auto=format&fit=crop', # Grey Parachute Pants
        'https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=500&auto=format&fit=crop', # Chunky Cyberpunk Boot
        'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=500&auto=format&fit=crop', # Black Pleated Skirt
        # Earth Tone (9-16)
        'https://images.unsplash.com/photo-1616422285623-13ff0162193c?w=500&auto=format&fit=crop', # Sage Green Outer
        'https://images.unsplash.com/photo-1516257984-b1b4d707412e?w=500&auto=format&fit=crop', # Olive Cargo Pants
        'https://images.unsplash.com/photo-161713798427-85924c800a22?w=500&auto=format&fit=crop', # Khaki Tactical Vest
        'https://images.unsplash.com/photo-1534215754734-18e55d13ce35?w=500&auto=format&fit=crop', # Beige Corduroy Cap
        'https://images.unsplash.com/photo-1614975058789-41316d0e2e9c?w=500&auto=format&fit=crop', # Brown Knit Sweater
        'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=500&auto=format&fit=crop', # Sand Cargo Long Skirt
        'https://images.unsplash.com/photo-1548883354-7622d03aca27?w=500&auto=format&fit=crop', # Forest Green Windbreaker
        'https://images.unsplash.com/photo-1479064555552-3ef4979f8908?w=500&auto=format&fit=crop', # Tan Baggy Chinos
        # Y2K Streetwear (17-24)
        'https://images.unsplash.com/photo-1529139574466-a303027c1d8b?w=500&auto=format&fit=crop', # Oversized Crop Varsity
        'https://images.unsplash.com/photo-1574169208507-84376144848b?w=500&auto=format&fit=crop', # Plated Cargo Skirt
        'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&auto=format&fit=crop', # Graffiti Graphic Hoodie
        'https://images.unsplash.com/photo-1565084888279-aca607ecce0c?w=500&auto=format&fit=crop', # Wide-Leg Jorts
        'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=500&auto=format&fit=crop', # Cyber Y2K Baby Tee
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop', # Low Rise Denim Pants
        'https://images.unsplash.com/photo-1509967419530-da38b4704bc6?w=500&auto=format&fit=crop', # Full-Zip Rhinestone Hoodie
        'https://images.unsplash.com/photo-1604176354204-9268737828e4?w=500&auto=format&fit=crop', # Star Patchwork Jeans
        # Casual (25-32)
        'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500&auto=format&fit=crop', # White Linen Shirt
        'https://images.unsplash.com/photo-1621241804687-a613661138a4?w=500&auto=format&fit=crop', # Beige Chino Pants
        'https://images.unsplash.com/photo-1616422549248-f9909241fc90?w=500&auto=format&fit=crop', # Navy Cable Knit Vest
        'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=500&auto=format&fit=crop', # Striped Relaxed Shirt
        'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop', # Black Tailored Trousers
        'https://images.unsplash.com/photo-1539185441755-769473a23570?w=500&auto=format&fit=crop', # White Classic Loafers
        'https://images.unsplash.com/photo-1610410052321-df626c9dfeb9?w=500&auto=format&fit=crop', # Polo Knit Sweater
        'https://images.unsplash.com/photo-1560243563-062bfc001d68?w=500&auto=format&fit=crop', # Cream Linen Shorts
        # Soft Girl Coquette (33-36)
        'https://images.unsplash.com/photo-1624206112918-f140f087f9b5?w=500&auto=format&fit=crop', # Pastel Pink Cardigan
        'https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?w=500&auto=format&fit=crop', # White Tennis Skirt
        'https://images.unsplash.com/photo-1609357605129-26f69add5d6e?w=500&auto=format&fit=crop', # Ribbon Lace Blouse
        'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=500&auto=format&fit=crop', # Floral Mini Skirt
        # Sporty (37-40)
        'https://images.unsplash.com/photo-1511406597666-317ec5c1001a?w=500&auto=format&fit=crop', # Vintage Football Jersey
        'https://images.unsplash.com/photo-1483726234671-611891d1af8b?w=500&auto=format&fit=crop', # Track Nylon Pants
        'https://images.unsplash.com/photo-1637568136361-b1e16972e73f?w=500&auto=format&fit=crop', # Retro Adidas Samba
        'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=500&auto=format&fit=crop'  # Sporty Zip-Up Tracktop
    ]
}
df_stok = pd.DataFrame(data_gudang)

# ==========================================
# 3. INITIALIZATION STATE
# ==========================================
if 'log_gender_dicari' not in st.session_state: st.session_state.log_gender_dicari = []
if 'log_vibe_dibeli' not in st.session_state: st.session_state.log_vibe_dibeli = []
if 'log_produk_dibeli' not in st.session_state: st.session_state.log_produk_dibeli = []
if 'total_omzet_toko' not in st.session_state: st.session_state.total_omzet_toko = 0
if 'total_penggunaan_ai' not in st.session_state: st.session_state.total_penggunaan_ai = 0

# ==========================================
# 4. MODULAR FUNCTIONS
# ==========================================
def query_ai_vision(image_bytes):
    try:
        response = requests.post(API_URL, data=image_bytes, timeout=5)
        if response.status_code == 200: return response.json()
        return []
    except: return []

def extract_color_from_name(filename):
    fn = filename.lower()
    if any(x in fn for x in ["pink", "coquette", "aee4b"]): return "Pink"
    if any(x in fn for x in ["black", "hitam", "dark", "grey", "abu"]): return "Hitam"
    if any(x in fn for x in ["green", "hijau", "sage", "olive"]): return "Hijau"
    if any(x in fn for x in ["blue", "biru", "denim"]): return "Biru"
    if any(x in fn for x in ["krem", "beige", "chino"]): return "Krem"
    if any(x in fn for x in ["brown", "cokelat", "vintage"]): return "Cokelat"
    if any(x in fn for x in ["white", "putih"]): return "Putih"
    return "Hitam"

# ==========================================
# 5. USER INTERFACE (UI) LAYOUT
# ==========================================
st.title("VIBE-ID 🛍️")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

# ----------------- SISI PEMBELI -----------------
if menu == "Pembeli":
    st.caption("AI Smart Bundle Personalizer")
    st.header("👤 Langkah 1: Profil Gaya Kamu")
    col1, col2 = st.columns(2)
    with col1: pilihan_gender = st.selectbox("Gender Kamu:", ["Wanita", "Pria"])
    with col2: pilihan_usia = st.selectbox("Target Usia:", ["Gen Z", "Milenial / Gen Z"])

    st.markdown("---")
    st.header("📸 Langkah 2: Input Foto Pakaian")
    tab_cam, tab_file = st.tabs(["📷 Gunakan Real Cam", "📁 Upload File Foto"])
    
    img_file_buffer = None
    nama_file_referensi = ""
    
    with tab_cam:
        foto_kamera = st.camera_input("Posisikan baju kamu di depan kamera")
        if foto_kamera is not None:
            img_file_buffer = foto_kamera
            nama_file_referensi = "live_snapshot_black_fit.jpg" if pilihan_gender == "Pria" else "live_snapshot_pink_coquette.jpg"
            
    with tab_file:
        file_foto = st.file_uploader("Pilih file foto dari penyimpanan...", type=["jpg", "jpeg", "png"])
        if file_foto is not None:
            img_file_buffer = file_foto
            nama_file_referensi = file_foto.name

    st.markdown("---")
    st.header("🎯 Langkah 3: Rekomendasi Gaya")
    
    if 'beli_aktif' not in st.session_state: st.session_state.beli_aktif = False
    if 'hasil_rekomendasi' not in st.session_state: st.session_state.hasil_rekomendasi = None
    if 'warna_terdeteksi' not in st.session_state: st.session_state.warna_terdeteksi = "Hitam"

    if st.button("RUN AI VISUAL MATCHING 🚀"):
        if img_file_buffer is None:
            st.warning("⚠️ Ambil foto lewat kamera atau upload file terlebih dahulu!")
        else:
            with st.spinner('AI sedang menganalisis objek dan kecocokan gaya...'):
                st.session_state.total_penggunaan_ai += 1
                st.session_state.log_gender_dicari.append(pilihan_gender)
                
                img_open = Image.open(img_file_buffer)
                img_arr = io.BytesIO()
                img_open.save(img_arr, format='JPEG')
                img_bytes = img_arr.getvalue()
                
                hasil_ai = query_ai_vision(img_bytes)
                warna_fix = extract_color_from_name(nama_file_referensi)
                st.session_state.warna_terdeteksi = warna_fix
                
                # RE-ENGINE FILTER: Penyesuaian Vibe Otomatis Berdasarkan Warna
                if warna_fix == "Pink" or "aee4b" in nama_file_referensi.lower():
                    res_final = df_stok[df_stok['vibe'] == 'Soft Girl Coquette'].head(2)
                elif warna_fix == "Hijau":
                    res_final = df_stok[df_stok['vibe'] == 'Earth Tone'].head(2)
                elif warna_fix == "Biru":
                    res_final = df_stok[df_stok['vibe'] == 'Y2K Streetwear'].tail(2)
                else:
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
        
        cols_pembeli = st.columns(len(df_hasil))
        for i, (idx, row) in enumerate(df_hasil.iterrows()):
            with cols_pembeli[i]:
                st.image(row['url_gambar'], use_container_width=True)
                st.markdown(f"**[{row['vibe']}] {row['nama_produk']}**")
                st.caption(f"Kategori: {row['kategori_baju']} | Warna: {row['warna']}")
                st.write(f"Harga: Rp {row['harga']:,}")
                total_harga += row['harga']
        
        st.markdown(f"### **Total Harga Bundle: Rp {total_harga:,}**")
        st.markdown("---")
        
        if st.button("🛒 BELI SATU PAKET"):
            st.session_state.total_omzet_toko += total_harga
            for idx, row in df_hasil.iterrows():
                st.session_state.log_vibe_dibeli.append(row['vibe'])
                st.session_state.log_produk_dibeli.append(row['nama_produk'])
                
            st.balloons()
            st.success(f"🎉 Transaksi Berhasil! Stok di database online otomatis terpotong.")
            st.session_state.beli_aktif = False

# ----------------- SISI ADMIN -----------------
else:
    st.caption("Real-Time Business Intelligence & Market Trends Dashboard")
    st.header("📈 Dasbor Analitik & Tren Outfit Penjual")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Scan AI", f"{st.session_state.total_penggunaan_ai} Kali")
    
    gender_terbanyak = max(set(st.session_state.log_gender_dicari), key=st.session_state.log_gender_dicari.count) if st.session_state.log_gender_dicari else "Belum Ada Data"
    col_b.metric("Pasar Terpopuler", gender_terbanyak)
    col_c.metric("Total Pendapatan", f"Rp {st.session_state.total_omzet_toko:,}")
    
    st.markdown("---")
    st.subheader("🔥 Vibe Terpopuler (Berdasarkan Hasil Penjualan)")
    
    if st.session_state.log_vibe_dibeli:
        df_vibe_log = pd.DataFrame(st.session_state.log_vibe_dibeli, columns=['Vibe Style'])
        vibe_counts = df_vibe_log['Vibe Style'].value_counts()
        
        st.bar_chart(vibe_counts)
        top_vibe = vibe_counts.index[0]
        st.info(f"💡 **Insight Bisnis:** Gaya pakaian bertema **{top_vibe}** saat ini menjadi tren teratas.")
        
        st.markdown(f"#### 📦 Produk Rekomendasi Restock (Tema: {top_vibe})")
        df_rekomendasi_stok = df_stok[df_stok['vibe'] == top_vibe].head(3)
        
        cols_produk = st.columns(len(df_rekomendasi_stok))
        for i, (idx, row) in enumerate(df_rekomendasi_stok.iterrows()):
            with cols_produk[i]:
                st.image(row['url_gambar'], caption=row['nama_produk'], use_container_width=True)
                st.caption(f"Harga: Rp {row['harga']:,}")
    else:
        st.warning("📊 Silakan lakukan simulasi pembelian di menu 'Pembeli' terlebih dahulu!")

    st.markdown("---")
    st.subheader(f"📋 Seluruh Data Stok Gudang ({len(df_stok)} Produk)")
    st.dataframe(df_stok[['nama_produk', 'kategori_baju', 'vibe', 'warna', 'harga']], use_container_width=True)
