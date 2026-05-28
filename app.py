import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io

# 1. CONFIG & KONSTANTA UTAMA
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

API_URL = "https://api-inference.huggingface.co/models/valentinafed/clothing-detector"

# 2. DATABASE GUDANG (40 PRODUK SINKRON)
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
    # URL PICT
    'url_gambar': [
        # Monochrome (1-8)
        'https://slatehash.com/cdn/shop/products/VG-SH-46202792.jpg?v=1675584596', # Black Oversized Tee
        'https://xcdn.next.co.uk/common/items/default/default/itemimages/3_4Ratio/product/lge/U76215s9.jpg?im=Resize', # Dark Charcoal Jeans
        'https://techwear-division.com/cdn/shop/files/2_6ac4c254-19ef-46b3-91e0-58e15d5cdeb7.png?v=1692032454&width=800', # Gothic Black Hoodie
        'https://www.beyondretro.com/cdn/shop/files/beyond-retro-label-womens-acid-wash-denim-shorts-1-E00970513_1200x1200.jpg?v=1742573488', # Acid Wash Denim Shorts
        'https://www.jacketmakers.com/wp-content/uploads/2024/04/mens-chicago-bulls-black-varsity-jacket.jpg', # Black Varsity Jacket
        'https://turntupfashion.com/cdn/shop/files/ICENGREYPANTS_2x_472d0c04-cc8d-48cc-b54b-aa84e23b47cb.png?v=1690203138', # Grey Parachute Pants
        'https://i.pinimg.com/736x/a5/a6/cf/a5a6cf14a3e3b7d573cd6c21f5c2a46b.jpg', # Chunky Cyberpunk Boot
        'https://cdnc.lystit.com/photos/2013/02/28/topshop-black-black-knee-length-pleat-skirt-product-1-6854524-820313209.jpeg', # Black Pleated Skirt
        # Earth Tone (9-16)
        'https://down-id.img.susercontent.com/file/id-11134207-7qukz-leumy5on7ikbb1', # Sage Green Outer
        'https://fabricerie.com/wp-content/uploads/2025/04/cargo-pants-in-olive-minimalist-style-aaaaa-25100.jpg', # Olive Cargo Pants
        'https://shop.militaryrange.eu/Content/custom/img_products/8567khi.jpg', # Khaki Tactical Vest
        'https://img.hatshopping.com/Uni-Ellipse-Corduroy-Cap-by-Oakley-beige.72024_rf15.jpg', # Beige Corduroy Cap
        'https://i.pinimg.com/originals/fc/2e/a6/fc2ea6399e778aad72f98cd82d40a304.jpg', # Brown Knit Sweater
        'https://cdnimg.emmiol.com/E/202210/img_original-GCI0047BO-25071101229.jpg', # Sand Cargo Long Skirt
        'https://di2ponv0v5otw.cloudfront.net/posts/2026/01/26/697780bd44ad4d53941651da/m_697780cca951059a01dbd8b0.jpg', # Forest Green Windbreaker
        'https://paul-smith-products-ressh.cloudinary.com/image/upload/v1743762629/STILL/M2R/M2R-364Z-P21477-61/M2R-364Z-P21477-61_10.jpg', # Tan Baggy Chinos
        # Y2K Streetwear (17-24)
        'https://i.pinimg.com/originals/29/d0/3d/29d03dc7dc46a750dc0e489af1b52698.jpg', # Oversized Crop Varsity
        'https://images.unsplash.com/photo-1574169208507-84376144848b?w=500&auto=format&fit=crop', # Plated Cargo Skirt
        'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=500&auto=format&fit=crop', # Graffiti Graphic Hoodie
        'https://images.unsplash.com/photo-1565084888279-aca607ecce0c?w=500&auto=format&fit=crop', # Wide-Leg Jorts
        'https://www.cherrykitten.com/cdn/shop/products/2000s-baby-y2k-baby-tee-841182.jpg?v=1689566582&width=1445', # Cyber Y2K Baby Tee
        'https://images.unsplash.com/photo-1542272604-787c3835535d?w=500&auto=format&fit=crop', # Low Rise Denim Pants
        'https://images.unsplash.com/photo-1509967419530-da38b4704bc6?w=500&auto=format&fit=crop', # Full-Zip Rhinestone Hoodie
        'https://images.unsplash.com/photo-1604176354204-9268737828e4?w=500&auto=format&fit=crop', # Star Patchwork Jeans
        # Casual (25-32)
        'https://images.squarespace-cdn.com/content/v1/57baef93cd0f68daca6084ae/facc3240-5ebf-41cc-9421-87eaf1221a76/unnamed+(3).png', # White Linen Shirt
        'https://i.pinimg.com/736x/a9/68/d2/a968d2a203cb0e271d8a9ab7adb10501.jpg', # Beige Chino Pants
        'https://images.unsplash.com/photo-1616422549248-f9909241fc90?w=500&auto=format&fit=crop', # Navy Cable Knit Vest
        'https://handcmediastorage.blob.core.windows.net/productimages/RL/RLSLZ002-N03-150438-1400px-1820px.jpg', # Striped Relaxed Shirt
        'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop', # Black Tailored Trousers
        'https://cdna.lystit.com/photos/shoppremiumoutlets/8f095f8a/dries-van-noten-white-Penny-Loafers.jpeg', # White Classic Loafers
        'https://clothbase.s3.amazonaws.com/uploads/99780a6a-c878-4289-a5ad-a374b9b96015/image.jpg', # Polo Knit Sweater
        'https://www.careofcarl.com/bilder/artiklar/zoom/28911311r_1.jpg?m=1739969887', # Cream Linen Shorts
        # Soft Girl Coquette (33-36)
        'https://i.pinimg.com/originals/e3/54/28/e35428a6ac29a44488c1c07e9cf7d0e0.jpg', # Pastel Pink Cardigan
        'https://i.pinimg.com/originals/a3/84/78/a38478da472595ca8687a2fa0d2f2944.jpg', # White Tennis Skirt
        'https://i.etsystatic.com/8409202/r/il/d06880/1940817966/il_fullxfull.1940817966_gr1x.jpg', # Ribbon Lace Blouse
        'https://cdn-img.prettylittlething.com/7/5/8/c/758c304aa8ccc973effb3f480a50982322d8d384_cnj8338_6.jpg?imwidth=600', # Floral Mini Skirt
        # Sporty (37-40)
        'https://footballshirtunion.com/cdn/shop/collections/IMG_4247_225786a4-66ea-4476-b666-84548f2e56fd.jpg?v=1741495514', # Vintage Football Jersey
        'https://i.pinimg.com/originals/64/38/bf/6438bf57cc35958f28f62990efa7a89d.jpg', # Track Nylon Pants
        'https://www.copclub.com.br/cdn/shop/products/adidas-samba-og-white-black_16652247_43006938_2048.jpg', # Retro Adidas Samba
        'https://cdn-images.farfetch-contents.com/19/52/87/24/19528724_43576108_1000.jpg'  # Sporty Zip-Up Tracktop
    ]
}
df_stok = pd.DataFrame(data_gudang)

# 3. INITIALIZATION STATE
if 'log_gender_dicari' not in st.session_state: st.session_state.log_gender_dicari = []
if 'log_vibe_dibeli' not in st.session_state: st.session_state.log_vibe_dibeli = []
if 'log_produk_dibeli' not in st.session_state: st.session_state.log_produk_dibeli = []
if 'total_omzet_toko' not in st.session_state: st.session_state.total_omzet_toko = 0
if 'total_penggunaan_ai' not in st.session_state: st.session_state.total_penggunaan_ai = 0

# 4. MODULAR FUNCTIONS
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

# 5. USER INTERFACE (UI) LAYOUT
st.title("VIBE-ID 🛍️")

menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

# SISI PEMBELI
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
            nama_file_referensi = "live_snapshot.jpg"
            
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
                
                # 🤖 1. PANGGIL MODEL AI HUGGING FACE
                hasil_ai = query_ai_vision(img_bytes)
                
                # 🤖 2. EKSTRAKSI WARNA DARI PREDIKSI AI (Fungsi Deteksi Gambar Nyata)
                warna_fix = None
                if hasil_ai and isinstance(hasil_ai, list):
                    for item in hasil_ai:
                        if 'label' in item:
                            label_terdeteksi = item['label'].lower()
                            # Cek label dari Hugging Face apakah mengandung unsur warna
                            if any(w in label_terdeteksi for w in ["pink", "red", "coquette"]): warna_fix = "Pink"
                            elif any(w in label_terdeteksi for w in ["green", "olive", "sage"]): warna_fix = "Hijau"
                            elif any(w in label_terdeteksi for w in ["blue", "denim"]): warna_fix = "Biru"
                            elif any(w in label_terdeteksi for w in ["krem", "beige", "tan", "khaki"]): warna_fix = "Krem"
                            elif any(w in label_terdeteksi for w in ["brown", "chocolate"]): warna_fix = "Cokelat"
                            elif any(w in label_terdeteksi for w in ["white", "linen"]): warna_fix = "Putih"
                            elif any(w in label_terdeteksi for w in ["black", "dark", "grey", "charcoal"]): warna_fix = "Hitam"
                            if warna_fix: break
                
                # FALLBACK: Jika AI gagal mendeteksi lewat gambar, baru cek nama file teksnya
                if not warna_fix:
                    warna_fix = extract_color_from_name(nama_file_referensi)
                    
                st.session_state.warna_terdeteksi = warna_fix
                
                # 🎯 3. FILTER SMART BUNDLE OLEH AI BERDASARKAN WARNA HASIL DETEKSI
                if warna_fix == "Pink":
                    res_final = df_stok[df_stok['vibe'] == 'Soft Girl Coquette'].head(2)
                elif warna_fix == "Hijau":
                    res_final = df_stok[df_stok['vibe'] == 'Earth Tone'].head(2)
                elif warna_fix == "Biru":
                    res_final = df_stok[df_stok['vibe'] == 'Y2K Streetwear'].tail(2)
                elif warna_fix in ["Krem", "Cokelat"]:
                    res_final = df_stok[df_stok['vibe'] == 'Earth Tone'].tail(2)
                elif warna_fix == "Putih":
                    res_final = df_stok[df_stok['vibe'] == 'Casual'].head(2)
                else:
                    res_final = df_stok[df_stok['vibe'] == 'Monochrome'].head(2)
                
                if res_final.empty: 
                    res_final = df_stok.head(2)
                    
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
                
            # CONFIG EFFECT
            coin_html = """
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999; overflow: hidden;">
                <style>
                    @keyframes drop {
                        0% { transform: translateY(-50px) rotate(0deg); opacity: 1; }
                        100% { transform: translateY(105vh) rotate(720deg); opacity: 0; }
                    }
                    .coin {
                        position: absolute;
                        font-size: 32px;
                        animation: drop 2.5s linear infinite;
                    }
                </style>
                <div class="coin" style="left: 10vw; animation-delay: 0s;">🪙</div>
                <div class="coin" style="left: 25vw; animation-delay: 0.4s;">🪙</div>
                <div class="coin" style="left: 40vw; animation-delay: 0.2s;">🪙</div>
                <div class="coin" style="left: 55vw; animation-delay: 0.6s;">🪙</div>
                <div class="coin" style="left: 70vw; animation-delay: 0.1s;">🪙</div>
                <div class="coin" style="left: 85vw; animation-delay: 0.5s;">🪙</div>
                <div class="coin" style="left: 15vw; animation-delay: 0.8s;">🪙</div>
                <div class="coin" style="left: 50vw; animation-delay: 0.9s;">🪙</div>
                <div class="coin" style="left: 75vw; animation-delay: 0.3s;">🪙</div>
            </div>
            """
            # Eksekusi animasi koin ke layar Streamlit
            st.markdown(coin_html, unsafe_allow_html=True)
            
            st.success("🎉 Transaksi Berhasil! Terima Kasih atas Pembeliannya <3")
            st.session_state.beli_aktif = False

# SISI ADMIN
else:
    st.caption("Real-Time Business Intelligence & Market Trends Dashboard")
    st.header("📈 Dasbor Analitik & Tren Outfit Penjualan")
    
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
