import numpy as np
import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io
import gc
from streamlit_option_menu import option_menu

# =====================================================================
# 1. CONFIG & STYLING MODERN (CSS INJECTION)
# =====================================================================
st.set_page_config(
    page_title="VIBE-ID — AI Outfit & Fashion Suite",
    page_icon="https://ibb.co.com/Z6dCMx8w",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling SaaS / Dark Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: #0B0F17;
        color: #E2E8F0;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1250px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }

    .vibe-banner {
        background: linear-gradient(135deg, #312E81 0%, #1E1B4B 50%, #0F172A 100%);
        border: 1px solid #4338CA;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.3);
    }

    .vibe-banner h1 {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 2.2rem;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .vibe-banner p {
        color: #C7D2FE;
        font-size: 1rem;
        margin-top: 6px;
        margin-bottom: 0;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        color: #FFFFFF !important;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
    }

    div[data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
    }

    div[data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.9rem !important;
    }

    div[data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# API & Webhook URLs
API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
N8N_DATA_URL = "https://csnvxie.app.n8n.cloud/webhook/Ambil-stok-gudang"
N8N_CHAT_URL = "https://csnvxie.app.n8n.cloud/webhook-test/VibeID-ChattBot"

# Sidebar Navigation
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #818CF8; font-weight:700;'>https://ibb.co.com/Z6dCMx8w VIBE-ID</h2>", unsafe_allow_html=True)
    st.caption("AI Smart Outfit Personalizer & Analytics")
    st.markdown("---")
    
    menu = option_menu(
        menu_title="HAK AKSES",
        options=["Pembeli", "Admin"],
        icons=["bag-check-fill", "speedometer"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#818CF8", "font-size": "16px"},
            "nav-link": {"font-size": "14px", "color": "#94A3B8", "border-radius": "8px", "margin": "4px 0px"},
            "nav-link-selected": {"background-color": "#4F46E5", "color": "#FFFFFF", "font-weight": "600"}
        }
    )

# Header Top Banner
st.markdown("""
<div class="vibe-banner">
    <h1>VIBE-ID Smart Assistant & Analytics</h1>
    <p>Visual AI Outfit Matcher • n8n Automated Inventory • Business Intelligence Hub</p>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# 2. HELPER & DATABASE FUNCTIONS
# =====================================================================
def get_dominant_color(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((1, 1), resample=Image.BOX) 
        color = img.getpixel((0, 0))
        del img 
        gc.collect()
        return color
    except Exception:
        return (255, 255, 255)

def get_color_name(rgb):
    r, g, b = rgb
    if r < 40 and g < 40 and b < 40: return "Hitam"
    if r > 220 and g > 220 and b > 220: return "Putih"
    if r > 120 and r > g + 40 and r > b + 40: return "Merah"
    if r < 100 and g > 180 and b < 100: return "Hijau"
    if r < 100 and g < 100 and b > 180: return "Biru"
    if r > 180 and r > 180 and b < 100: return "Kuning"
    if r > 180 and g < 100 and b > 180: return "Ungu"
    if abs(r - g) < 30 and abs(g - b) < 30 and abs(r - b) < 30: return "Abu-abu"
    return "Warna Campuran"

def query_ai_vision(image_bytes):
    headers = {"Authorization": "Bearer hf_AAsldkfjHsdkfjHskdjfHskdjfHskdjfHskd"} 
    try:
        response = requests.post(API_URL, headers=headers, data=image_bytes, timeout=5)
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                return str(res_json[0].get('label', '')).lower()
    except Exception:
        return "error"
    return "unknown"

@st.cache_resource(show_spinner=False)
def load_data_from_n8n():
    df = pd.DataFrame()
    try:
        response = requests.get(N8N_DATA_URL, timeout=5) 
        if response.status_code == 200:
            raw_data = response.json()
            if isinstance(raw_data, list) and len(raw_data) > 0:
                if 'json' in raw_data[0]:
                    df = pd.DataFrame([item['json'] for item in raw_data if 'json' in item])
                else:
                    df = pd.DataFrame(raw_data)
            else:
                df = pd.DataFrame(raw_data)
            del raw_data 
            gc.collect()
            
        if not df.empty:
            df.columns = [str(col).strip() for col in df.columns]
            if 'Item ID' in df.columns:
                df = df[df['Item ID'] != 'Item ID']
                
            mapping_kolom = {
                'Nama Barang': 'nama_produk',
                'Kategori': 'kategori_baju',
                'Gaya (Style)': 'vibe',
                'Warna': 'warna',
                'Gender': 'gender',
                'Harga': 'harga'
            }
            df = df.rename(columns=mapping_kolom)
            
            kolom_wajib = ['nama_produk', 'kategori_baju', 'vibe', 'warna', 'gender', 'harga', 'target_usia', 'url_gambar']
            for col in kolom_wajib:
                if col not in df.columns:
                    if col == 'harga': df[col] = 0
                    elif col == 'target_usia': df[col] = 'Gen Z'
                    elif col == 'url_gambar': df[col] = 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500'
                    else: df[col] = ''
            
            # Format Kolom Harga Langsung di Fungsi
            df['harga'] = df['harga'].astype(str).str.replace('Rp', '', regex=False).str.replace('.', '', regex=False).str.strip()
            df['harga'] = pd.to_numeric(df['harga'], errors='coerce').fillna(0)
            return df
    except Exception as e:
        st.error(f"Gagal mengambil data dari n8n: {e}")
    
    return pd.DataFrame(columns=['nama_produk', 'kategori_baju', 'vibe', 'warna', 'gender', 'target_usia', 'harga', 'url_gambar'])

df_stok = load_data_from_n8n()

# =====================================================================
# 3. INITIALIZATION STATE
# =====================================================================
if 'log_gender_dicari' not in st.session_state: st.session_state.log_gender_dicari = []
if 'log_vibe_dibeli' not in st.session_state: st.session_state.log_vibe_dibeli = []
if 'log_produk_dibeli' not in st.session_state: st.session_state.log_produk_dibeli = []
if 'total_omzet_toko' not in st.session_state: st.session_state.total_omzet_toko = 0
if 'total_penggunaan_ai' not in st.session_state: st.session_state.total_penggunaan_ai = 0
if 'warna_terdeteksi' not in st.session_state: st.session_state.warna_terdeteksi = None
if 'ai_label_terdeteksi' not in st.session_state: st.session_state.ai_label_terdeteksi = None
if 'beli_aktif' not in st.session_state: st.session_state.beli_aktif = False
if 'hasil_rekomendasi' not in st.session_state: st.session_state.hasil_rekomendasi = None

if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa aku bantu buat cari outfit atau cek stok hari ini? 🙌"}]

def query_chatbot_n8n(user_text):
    try:
        payload = {"message": user_text}
        response = requests.post(N8N_CHAT_URL, json=payload, timeout=8)
        
        if response.status_code == 200:
            res_data = response.json()
            if isinstance(res_data, list) and len(res_data) > 0: res_data = res_data[0]
            if isinstance(res_data, dict) and 'json' in res_data: res_data = res_data['json']
            if isinstance(res_data, dict):
                return res_data.get("output", res_data.get("response", res_data.get("reply", "Format JSON valid, tapi isi teks tidak ditemukan.")))
            return str(res_data)
    except Exception as e:
        return f"Gagal tersambung ke Chatbot n8n: {e}"
    return "Bot sedang tidak merespon."

# =====================================================================
# 4. USER INTERFACE (UI) LAYOUT
# =====================================================================
if menu == "Pembeli":
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.subheader("👤 Step 1: Profil Gaya Kamu")
        col1, col2 = st.columns(2)
        pilihan_gender = col1.selectbox("Gender Kamu:", ["Wanita", "Pria"])
        pilihan_usia = col2.selectbox("Target Usia:", ["Gen Z", "Milenial / Gen Z"])

        st.subheader("📸 Step 2: Input Foto Pakaian")
        tab_cam, tab_file = st.tabs(["📷 Real Cam", "📁 Upload Foto"])
        
        img_file_buffer = None
        with tab_cam:
            foto_kamera = st.camera_input("Ambil foto pakaian kamu")
            if foto_kamera: img_file_buffer = foto_kamera
        with tab_file:
            file_foto = st.file_uploader("Upload file pakaian...", type=["jpg", "jpeg", "png"])
            if file_foto: img_file_buffer = file_foto

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 RUN AI VISUAL MATCHING", use_container_width=True):
            if img_file_buffer is None:
                st.warning("⚠️ Ambil foto atau upload file dulu, bre!")
            else:
                img_bytes = img_file_buffer.getvalue() 
                if len(img_bytes) > 2 * 1024 * 1024:
                    st.error("Foto terlalu besar! Maksimal 2MB.")
                else:
                    st.session_state.total_penggunaan_ai += 1
                    st.session_state.log_gender_dicari.append(pilihan_gender)
                    
                    # 1. Deteksi Warna
                    rgb_dominan = get_dominant_color(img_bytes)
                    nama_warna = get_color_name(rgb_dominan)
                    
                    # 2. Deteksi Klasifikasi AI HuggingFace
                    ai_label = query_ai_vision(img_bytes)
                    
                    matching_products = pd.DataFrame()
                    if df_stok is not None and not df_stok.empty and 'warna' in df_stok.columns:
                        matching_products = df_stok[df_stok['warna'].astype(str).str.lower().str.contains(nama_warna.lower(), na=False)]
                    
                    if matching_products.empty:
                        matching_products = df_stok.head(3) if df_stok is not None else pd.DataFrame()
                    
                    st.session_state.hasil_rekomendasi = matching_products
                    st.session_state.warna_terdeteksi = nama_warna
                    st.session_state.ai_label_terdeteksi = ai_label
                    st.session_state.beli_aktif = True
                    st.rerun()

    with col_right:
        st.subheader("🎯 Step 3: Rekomendasi Outfit")
        if st.session_state.get('beli_aktif'):
            col_tag1, col_tag2 = st.columns(2)
            col_tag1.success(f"🎨 Warna: **{st.session_state.get('warna_terdeteksi', 'Unknown')}**")
            col_tag2.info(f"🤖 AI ViT Label: **{st.session_state.get('ai_label_terdeteksi', 'N/A')}**")
            
            df_hasil = st.session_state.get('hasil_rekomendasi')
            
            if df_hasil is not None and not df_hasil.empty:
                cols = st.columns(min(len(df_hasil), 3))
                total_harga = 0
                for i, (idx, row) in enumerate(df_hasil.iterrows()):
                    if i < 3:
                        with cols[i]:
                            if 'url_gambar' in row and row['url_gambar']:
                                st.image(row['url_gambar'], use_container_width=True)
                            st.write(f"**{row['nama_produk']}**")
                            total_harga += float(row.get('harga', 0))
                
                st.markdown("---")
                st.markdown(f"### Total Bundle: **Rp {total_harga:,.0f}**")
                
                if st.button("🛒 BELI SATU PAKET SEKARANG", use_container_width=True):
                    st.session_state.total_omzet_toko += total_harga
                    
                    for idx, row in df_hasil.iterrows():
                        if 'vibe' in row and row['vibe']:
                            st.session_state.log_vibe_dibeli.append(row['vibe'])
                        if 'nama_produk' in row and row['nama_produk']:
                            st.session_state.log_produk_dibeli.append(row['nama_produk'])
                            
                    st.balloons()
                    st.success("🎉 Transaksi Berhasil! Terima kasih sudah berbelanja.")
                    st.session_state.beli_aktif = False
            else:
                st.warning("Tidak ada rekomendasi yang cocok.")
        else:
            st.info("👈 Silakan upload foto dan klik **RUN AI VISUAL MATCHING** di sebelah kiri untuk melihat rekomendasi outfit.")

    st.markdown("---")
    
    # POP-UP CHATBOT N8N (FIKSasi: Tanpa st.rerun agar dialog tidak tertutup)
    @st.dialog("💬 VIBE-ID Smart Assistant")
    def tampilkan_chatbot_popup():
        st.caption("Tanyakan ketersediaan stok, harga, atau rekomendasi langsung ke AI n8n")
        chat_container = st.container(height=320)
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        prompt = st.chat_input("Ketik pesan kamu...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("Memikirkan jawaban..."):
                        response_bot = query_chatbot_n8n(prompt)
                        st.markdown(response_bot)
            st.session_state.messages.append({"role": "assistant", "content": response_bot})

    st.info("💡 Butuh bantuan rekomendasi atau tanya ketersediaan stok produk?")
    if st.button("💬 Buka AI Assistant Chatbot", use_container_width=True):
        tampilkan_chatbot_popup()

else:
    # DASBOR ADMIN / ANALYTICS
    st.subheader("📈 Real-Time Business Intelligence & Market Trends Dashboard")
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Scan AI Visual", f"{st.session_state.total_penggunaan_ai} Kali")
    
    gender_terbanyak = max(set(st.session_state.log_gender_dicari), key=st.session_state.log_gender_dicari.count) if st.session_state.log_gender_dicari else "Belum Ada Data"
    col_b.metric("Pasar Terpopuler", gender_terbanyak)
    col_c.metric("Total Omzet Toko", f"Rp {st.session_state.total_omzet_toko:,.0f}")
    
    st.markdown("---")
    col_trend, col_table = st.columns([1, 1], gap="large")
    
    with col_trend:
        st.subheader("🔥 Vibe Style Terpopuler")
        if st.session_state.log_vibe_dibeli:
            df_vibe_log = pd.DataFrame(st.session_state.log_vibe_dibeli, columns=['Vibe Style'])
            vibe_counts = df_vibe_log['Vibe Style'].value_counts()
            st.bar_chart(vibe_counts)
            top_vibe = vibe_counts.index[0]
            st.info(f"💡 **Insight:** Pakaian bertema **{top_vibe}** sedang menjadi tren teratas.")
        else:
            st.warning("📊 Lakukan simulasi pembelian di menu Pembeli untuk melihat grafik tren.")

    with col_table:
        st.subheader(f"📋 Data Stok Gudang Live ({len(df_stok)} Produk)")
        if not df_stok.empty:
            kolom_tampil = [col for col in ['nama_produk', 'kategori_baju', 'vibe', 'warna', 'harga'] if col in df_stok.columns]
            st.dataframe(df_stok[kolom_tampil], use_container_width=True, height=300)
        else:
            st.info("Belum ada data stok yang terload dari database.")
