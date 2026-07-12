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
# ⚠️ PASTIKAN LINK INI ADALAH PRODUCTION URL WEBHOOK N8N KAMU
N8N_DATA_URL = "https://casanovaxie.app.n8n.cloud/webhook/Ambil-stok-gudang"

@st.cache_data(ttl=10) # Perkecil cache ke 10 detik biar cepat update
def load_data_from_n8n():
    try:
        response = requests.get(N8N_DATA_URL)
        if response.status_code == 200:
            df = pd.DataFrame(response.json())
            
            # 1. Bersihkan spasi di nama kolom bawaan Google Sheets
            df.columns = [str(col).strip() for col in df.columns]
            
            # 2. Buang baris header duplikat (jika ada teks 'Item ID' di baris tengah)
            if 'Item ID' in df.columns:
                df = df[df['Item ID'] != 'Item ID']
            
            # 3. MAPPING (Penerjemah kolom)
            mapping_kolom = {
                'Nama Barang': 'nama_produk',
                'Kategori': 'kategori_baju',
                'Gaya (Style)': 'vibe',
                'Warna': 'warna',
                'Gender': 'gender',
                'Harga': 'harga'
            }
            df = df.rename(columns=mapping_kolom)
            
            # 4. PENGAMAN MUTLAK: Jika kolom yang dicari kodingan bawah tidak ada, buatkan manual biar tidak KeyError
            for col_wajib in ['nama_produk', 'kategori_baju', 'vibe', 'warna', 'gender', 'harga']:
                if col_wajib not in df.columns:
                    df[col_wajib] = "" # kasih nilai string kosong biar ga crash
            
            # Kolom tiruan tambahan
            if 'target_usia' not in df.columns: df['target_usia'] = 'Gen Z'
            if 'url_gambar' not in df.columns: df['url_gambar'] = 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500'
                
            return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari n8n: {e}")
    
    # Return dataframe cadangan dengan kolom lengkap jika request gagal
    return pd.DataFrame(columns=['nama_produk', 'kategori_baju', 'vibe', 'warna', 'gender', 'target_usia', 'harga', 'url_gambar'])

# Memanggil fungsi untuk mengambil data pakaian secara real-time
df_stok = load_data_from_n8n()

# Bersihkan format harga (buang "Rp" dan titik) agar bisa dihitung matematika
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

# 4. MODULAR FUNCTIONS
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
        print(data) 
        
        try:
            colors = data['result']['colors']['image_colors']
            if colors and len(colors) > 0:
                return colors[0]['closest_palette_color']
        except Exception as e:
            st.error(f"DEBUG: Error API: {e}") 
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
    
    # Tombol Analisis
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
            
            # 1. Simpan hasil mentah dari AI
            warna_str = str(warna_api).lower() if warna_api else "hitam"
            
            # 2. Logika Penentuan Warna
            if any(x in warna_str for x in ["pink", "magenta"]):
                hasil_warna = "Pink"
            elif any(x in warna_str for x in ["green", "lime"]):
                hasil_warna = "Hijau"
            elif any(x in warna_str for x in ["blue", "navy"]):
                hasil_warna = "Biru"
            elif any(x in warna_str for x in ["beige", "tan", "khaki", "cream"]):
                hasil_warna = "Krem"
            elif any(x in warna_str for x in ["white"]):
                hasil_warna = "Putih"
            elif any(x in warna_str for x in ["brown", "chocolate"]):
                hasil_warna = "Cokelat"
            elif any(x in warna_str for x in ["black", "grey", "charcoal"]):
                hasil_warna = "Hitam"
            else:
                hasil_warna = "Monochrome"
            
            # 3. KUNCI HASIL DI SESSION STATE
            st.session_state.warna_terdeteksi = hasil_warna
            
            # Mencari produk yang sesuai warna di database dinamis
            matching_products = df_stok[df_stok['warna'].str.lower() == hasil_warna.lower()]
            st.session_state.hasil_rekomendasi = matching_products
            
            # Jika tidak ada produk dengan warna itu, ambil 2 data teratas sebagai backup
            if len(st.session_state.hasil_rekomendasi) == 0:
                st.session_state.hasil_rekomendasi = df_stok.head(2)
                
            st.session_state.beli_aktif = True
            st.rerun()

    # TAMPILKAN HASIL (Gunakan Session State agar tidak hilang saat Rerun)
    if st.session_state.get('beli_aktif'):
        st.success(f"🎨 Warna terdeteksi: **{st.session_state.warna_terdeteksi}**")
        df_hasil = st.session_state.hasil_rekomendasi
        
        if not df_hasil.empty:
            cols = st.columns(len(df_hasil))
            total_harga = 0
            for i, (idx, row) in enumerate(df_hasil.iterrows()):
                with cols[i]:
                    if 'url_gambar' in row and row['url_gambar']:
                        st.image(row['url_gambar'], use_container_width=True)
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
        df_rekomendasi_stok = df_stok[df_stok['vibe'] == top_vibe].head(3)
        
        if not df_rekomendasi_stok.empty:
            cols_produk = st.columns(len(df_rekomendasi_stok))
            for i, (idx, row) in enumerate(df_rekomendasi_stok.iterrows()):
                with cols_produk[i]:
                    if 'url_gambar' in row and row['url_gambar']:
                        st.image(row['url_gambar'], caption=row['nama_produk'], use_container_width=True)
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
