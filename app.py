import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io

# 1. CONFIG & KONSTANTA UTAMA
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")
menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"

# =====================================================================
# 2. DATABASE GUDANG (OTOMATIS AMBIL DARI GOOGLE SHEETS VIA N8N)
# =====================================================================
N8N_DATA_URL = "https://casanovaxie.app.n8n.cloud/webhook/ambil-stok-gudang"

@st.cache_data(ttl=5)
def load_data_from_n8n():
    try:
        response = requests.get(N8N_DATA_URL)
        if response.status_code == 200:
            raw_data = response.json()
            
            # Jika n8n membungkus datanya dalam list, kita bongkar row-nya
            if isinstance(raw_data, list):
                if len(raw_data) > 0 and 'json' in raw_data[0]:
                    cleaned_list = [item['json'] for item in raw_data if 'json' in item]
                    df = pd.DataFrame(cleaned_list)
                else:
                    df = pd.DataFrame(raw_data)
            else:
                df = pd.DataFrame(raw_data)
            
            # Bersihkan spasi di nama kolom
            df.columns = [str(col).strip() for col in df.columns]
            
            # Buang baris header duplikat dari Google Sheets
            if 'Item ID' in df.columns:
                df = df[df['Item ID'] != 'Item ID']
            
            # Terjemahkan nama kolom Google Sheets kamu ke kodingan
            mapping_kolom = {
                'Nama Barang': 'nama_produk',
                'Kategori': 'kategori_baju',
                'Gaya (Style)': 'vibe',
                'Warna': 'warna',
                'Gender': 'gender',
                'Harga': 'harga'
            }
            df = df.rename(columns=mapping_kolom)
            
            # SUNTIKAN WAJIB AMAN: Pastikan kolom 'warna' dkk selalu eksis di DataFrame
            kolom_wajib = ['nama_produk', 'kategori_baju', 'vibe', 'warna', 'gender', 'harga', 'target_usia', 'url_gambar']
            for col in kolom_wajib:
                if col not in df.columns:
                    if col == 'harga':
                        df[col] = 0
                    elif col == 'target_usia':
                        df[col] = 'Gen Z'
                    elif col == 'url_gambar':
                        df[col] = 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500'
                    else:
                        df[col] = ''
            return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari n8n: {e}")
    
    return pd.DataFrame(columns=['nama_produk', 'kategori_baju', 'vibe', 'warna', 'gender', 'target_usia', 'harga', 'url_gambar'])

# Memanggil load data
df_stok = load_data_from_n8n()

# Bersihkan format harga dari Google Sheets (menghilangkan Rp dan Titik)
if not df_stok.empty and 'harga' in df_stok.columns:
    df_stok['harga'] = df_stok['harga'].astype(str).str.replace('Rp', '', regex=False).str.replace('.', '', regex=False).str.strip()
    df_stok['harga'] = pd.to_numeric(df_stok['harga'], errors='coerce').fillna(0)
# =====================================================================

# 3. INITIALIZATION STATE
if 'log_gender_dicari' not in st.session_state: st.session_state.log_gender_dicari = []
if 'log_vibe_dibeli' not in st.session_state: st.session_state.log_vibe_dibeli = []
if 'log_produk_dibeli' not in st.session_state: st.session_state.log_produk_dibeli = []
if 'total_omzet_toko' not in st.session_state: st.session_state.total_omzet_toko = 0
if 'total_penggunaan_ai' not in st.session_state: st.session_state.total_penggunaan_ai = 0
if 'warna_terdeteksi' not in st.session_state: st.session_state.warna_terdeteksi = None
if 'beli_aktif' not in st.session_state: st.session_state.beli_aktif = False
if 'hasil_rekomendasi' not in st.session_state: st.session_state.hasil_rekomendasi = None

# 4. MODULAR FUNCTIONS (IMAGGA VISION)
def query_ai_vision(image_bytes):
    api_key = 'acc_d031a6e3c3ee970' 
    api_secret = '6dc4113b118dac5fe001f31232e1852b' 
    
    files = {'image': image_bytes}
    response = requests.post(
        'https://api.imagga.com/v2/colors',
        auth=(api_key, api_secret),
        files=files
    )
    
    if response.status_code == 200:
        data = response.json()
        try:
            colors = data['result']['colors']['image_colors']
            if colors and len(colors) > 0:
                return colors[0]['closest_palette_color']
        except Exception as e:
            return "Warna Tidak Terdeteksi"
    return "Warna Tidak Terdeteksi"

# 5. USER INTERFACE (UI) LAYOUT
if menu == "Pembeli":
    st.caption("AI Smart Bundle Personalizer")
    st.header("👤 Langkah 1: Profil Gaya Kamu")
    col1, col2 = st.columns(2)
    pilihan_gender = col1.selectbox("Gender Kamu:", ["Wanita", "Pria"])
    pilihan_usia = col2.selectbox("Target Usia:", ["Gen Z", "Milenial / Gen Z"])

    st.markdown("---")
    st.header("📸 Langkah 2: Input Foto Pakaian")
    tab_cam, tab_file = st.tabs(["📷 Gunakan Real Cam", "📁 Upload File Foto"])
    
    img_file_buffer = None
    with tab_cam:
        foto_kamera = st.camera_input("Posisikan baju kamu di depan kamera")
        if foto_kamera: img_file_buffer = foto_kamera
    with tab_file:
        file_foto = st.file_uploader("Pilih file foto dari penyimpanan...", type=["jpg", "jpeg", "png"])
        if file_foto: img_file_buffer = file_foto

    st.markdown("---")
    st.header("🎯 Langkah 3: Rekomendasi Gaya")
    
    if st.button("RUN AI VISUAL MATCHING 🚀"):
        if img_file_buffer is None:
            st.warning("⚠️ Ambil foto atau upload file dulu!")
        elif df_stok.empty:
            st.error("⚠️ Data produk kosong, periksa kembali koneksi Webhook n8n Anda!")
        else:
            st.session_state.total_penggunaan_ai += 1
            st.session_state.log_gender_dicari.append(pilihan_gender)
            
            img_bytes = img_file_buffer.getvalue() if hasattr(img_file_buffer, "getvalue") else img_file_buffer.read()
            warna_api = query_ai_vision(img_bytes)
            
            warna_str = str(warna_api).lower() if warna_api else "hitam"
            
            # Logika Filter Warna
            if any(x in warna_str for x in ["pink", "magenta"]): hasil_warna = "Pink"
            elif any(x in warna_str for x in ["green", "lime"]): hasil_warna = "Hijau"
            elif any(x in warna_str for x in ["blue", "navy"]): hasil_warna = "Biru"
            elif any(x in warna_str for x in ["beige", "tan", "khaki", "cream"]): hasil_warna = "Krem"
            elif any(x in warna_str for x in ["white"]): hasil_warna = "Putih"
            elif any(x in warna_str for x in ["brown", "chocolate"]): hasil_warna = "Cokelat"
            elif any(x in warna_str for x in ["black", "grey", "charcoal", "moss", "claret"]): hasil_warna = "Hitam"
            else: hasil_warna = "Monochrome"
            
            st.session_state.warna_terdeteksi = hasil_warna
            
            # Memfilter produk secara AMAN
            if 'warna' in df_stok.columns and not df_stok.empty:
                matching_products = df_stok[df_stok['warna'].astype(str).str.lower().str.contains(hasil_warna.lower(), na=False)]
            else:
                matching_products = df_stok.head(0)
                
            st.session_state.hasil_rekomendasi = matching_products
            
            if len(st.session_state.hasil_rekomendasi) == 0:
                st.session_state.hasil_rekomendasi = df_stok.head(2)
                
            st.session_state.beli_aktif = True
            st.rerun()

    # TAMPILKAN HASIL
    if st.session_state.get('beli_aktif'):
        st.success(f"🎨 Warna terdeteksi (Palette/Closest): **{st.session_state.warna_terdeteksi}**")
        df_hasil = st.session_state.hasil_rekomendasi
        
        if df_hasil is not None and not df_hasil.empty:
            cols = st.columns(len(df_hasil))
            total_harga = 0
            for i, (idx, row) in enumerate(df_hasil.iterrows()):
                with cols[i]:
                    if 'url_gambar' in row and row['url_gambar']:
                        st.image(row['url_gambar'], width='stretch')
                    st.write(f"**{row['nama_produk']}**")
                    total_harga += row['harga']
            
            st.write(f"### Total: Rp {total_harga:,.0f}")
            
            if st.button("🛒 BELI SATU PAKET"):
                st.session_state.total_omzet_toko += total_harga
                for idx, row in df_hasil.iterrows():
                    st.session_state.log_vibe_dibeli.append(row['vibe'])
                    st.session_state.log_produk_dibeli.append(row['nama_produk'])
                    
                coin_html = """
                <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 9999; overflow: hidden;">
                    <style>
                        @keyframes drop {
                            0% { transform: translateY(-50px) rotate(0deg); opacity: 1; }
                            100% { transform: translateY(105vh) rotate(720deg); opacity: 0; }
                        }
                        .coin { position: absolute; font-size: 32px; animation: drop 2.5s linear infinite; }
                    </style>
                    <div class="coin" style="left: 20vw; animation-delay: 0s;">🪙</div>
                    <div class="coin" style="left: 50vw; animation-delay: 0.2s;">🪙</div>
                    <div class="coin" style="left: 80vw; animation-delay: 0.4s;">🪙</div>
                </div>
                """
                st.markdown(coin_html, unsafe_allow_html=True)
                st.success("🎉 Transaksi Berhasil! Terima Kasih atas Pembeliannya <3")
                st.session_state.beli_aktif = False
        else:
            st.warning("Tidak ada rekomendasi pakaian yang cocok untuk saat ini.")

# SISI ADMIN
else:
    st.caption("Real-Time Business Intelligence & Market Trends Dashboard")
    st.header("📈 Dasbor Analitik & Tren Outfit Penjualan")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Scan AI", f"{st.session_state.total_penggunaan_ai} Kali")
    
    gender_terbanyak = max(set(st.session_state.log_gender_dicari), key=st.session_state.log_gender_dicari.count) if st.session_state.log_gender_dicari else "Belum Ada Data"
    col_b.metric("Pasar Terpopuler", gender_terbanyak)
    col_c.metric("Total Pendapatan", f"Rp {st.session_state.total_omzet_toko:,.0f}")
    
    st.markdown("---")
    st.subheader("🔥 Vibe Terpopuler (Berdasarkan Hasil Penjualan)")
    
    if st.session_state.log_vibe_dibeli:
        df_vibe_log = pd.DataFrame(st.session_state.log_vibe_dibeli, columns=['Vibe Style'])
        vibe_counts = df_vibe_log['Vibe Style'].value_counts()
        st.bar_chart(vibe_counts)
        
        top_vibe = vibe_counts.index[0]
        st.info(f"💡 **Insight Bisnis:** Gaya pakaian bertema **{top_vibe}** saat ini menjadi tren teratas.")
        
        st.markdown(f"#### 📦 Produk Rekomendasi Restock (Tema: {top_vibe})")
        if 'vibe' in df_stok.columns:
            df_rekomendasi_stok = df_stok[df_stok['vibe'] == top_vibe].head(3)
            if not df_rekomendasi_stok.empty:
                cols_produk = st.columns(len(df_rekomendasi_stok))
                for i, (idx, row) in enumerate(df_rekomendasi_stok.iterrows()):
                    with cols_produk[i]:
                        if 'url_gambar' in row and row['url_gambar']:
                            st.image(row['url_gambar'], caption=row['nama_produk'], width='stretch')
                        st.caption(f"Harga: Rp {row['harga']:,.0f}")
    else:
        st.warning("📊 Silakan lakukan simulasi pembelian di menu 'Pembeli' terlebih dahulu!")

    st.markdown("---")
    st.subheader(f"📋 Seluruh Data Stok Gudang Ditarik dari Google Sheets ({len(df_stok)} Produk)")
    if not df_stok.empty:
        kolom_tampil = [col for col in ['nama_produk', 'kategori_baju', 'vibe', 'warna', 'harga'] if col in df_stok.columns]
        st.dataframe(df_stok[kolom_tampil], use_container_width=True)
    else:
        st.info("Belum ada data stok yang terload dari database.")
