import numpy as np
import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io
import gc
import random
from streamlit_option_menu import option_menu

# =====================================================================
# 1. CONFIG & STYLING MODERN (CSS INJECTION)
# =====================================================================
st.set_page_config(
    page_title="VIBE-ID — AI Outfit & Fashion Suite",
    page_icon="VIBEID LOGO.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

    /* Perbaikan Tombol Utama & Form Submit agar teks selalu putih kontras */
    .stButton > button, div[data-testid="stForm"] button[type="submit"] {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        width: 100%;
    }

    .stButton > button:hover, div[data-testid="stForm"] button[type="submit"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5);
        color: #FFFFFF !important;
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
    
    .receipt-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #F8FAFC !important;
    }

    .success-popup {
        background: linear-gradient(135deg, #065F46 0%, #047857 100%);
        border: 1px solid #10B981;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        color: #FFFFFF;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# API & Webhook URLs
N8N_DATA_URL = "https://csnvxie.app.n8n.cloud/webhook/Ambil-stok-gudang"
N8N_CHAT_URL = "https://csnvxie.app.n8n.cloud/webhook-test/VibeID-ChattBot"

# Sidebar Navigation
with st.sidebar:
    st.image("VIBEID LOGO.png", width=200)
    st.markdown("---")
    
    menu = option_menu(
        menu_title="AKSES",
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
    if r < 45 and g < 45 and b < 45: return "Hitam"
    if r > 210 and g > 210 and b > 210: return "Putih"
    
    if r > g and r > b:
        if g > 130 and b < 100: return "Kuning"
        if g > 100 and b < 80: return "Jingga"
        if abs(r - g) < 25 and abs(g - b) < 25: return "Abu-abu"
        return "Merah"
    elif g > r and g > b:
        if r > 130 and b < 100: return "Kuning"
        if abs(r - g) < 25 and abs(g - b) < 25: return "Abu-abu"
        return "Hijau"
    else:
        if r > 120 and g < 100: return "Ungu"
        if r > 150 and g > 150: return "Biru Muda"
        if abs(r - g) < 25 and abs(g - b) < 25: return "Abu-abu"
        return "Biru"
    
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
if 'order_success' not in st.session_state: st.session_state.order_success = False
if 'last_order_details' not in st.session_state: st.session_state.last_order_details = {}
if 'form_reset_counter' not in st.session_state: st.session_state.form_reset_counter = 0

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
# 4. PROFESSIONAL PAYMENT DIALOG POP-UP
# =====================================================================
@st.dialog("🛍️ Secure Checkout — VIBE-ID Store")
def tampilkan_payment_dialog(df_hasil, total_harga):
    if st.session_state.order_success:
        st.markdown("""
        <div class="success-popup">
            <h2 style="margin:0; color:#FFFFFF;">🎉 PEMBAYARAN BERHASIL!</h2>
            <p style="margin:5px 0 0 0; color:#D1FAE5;">Transaksi Anda telah dikonfirmasi oleh sistem gateway.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🧾 Ringkasan Invoice Resmi")
        st.write(f"**No. Pesanan:** `INV-VIBE-{random.randint(10000, 99999)}`")
        st.write(f"**Metode Bayar:** {st.session_state.last_order_details.get('metode', 'Virtual Account')}")
        st.write(f"**Total Dibayar:** **Rp {total_harga:,.0f}**")
        st.markdown("Kurir ekspedisi akan segera menjemput paket outfit kamu dari gudang. Terima kasih telah berbelanja! 🚀")
        
        if st.button("Selesai & Reset ke Beranda", use_container_width=True):
            st.session_state.order_success = False
            st.session_state.beli_aktif = False
            st.session_state.hasil_rekomendasi = None
            st.session_state.warna_terdeteksi = None
            st.session_state.ai_label_terdeteksi = None
            st.session_state.form_reset_counter += 1
            st.rerun()
        return

    st.markdown("### Ringkasan Belanja Paket Outfit")
    
    for idx, row in df_hasil.iterrows():
        st.markdown(f"- **{row['nama_produk']}** — `Rp {float(row.get('harga', 0)):,.0f}`")
    
    st.markdown("---")
    biaya_admin = 2500
    grand_total = total_harga + biaya_admin
    
    st.markdown(f"""
    <div class="receipt-box">
        <span style="color: #94A3B8;">Subtotal Produk:</span> <b style="color: #F8FAFC;">Rp {total_harga:,.0f}</b><br>
        <span style="color: #94A3B8;">Biaya Layanan / Admin:</span> <b style="color: #F8FAFC;">Rp {biaya_admin:,.0f}</b><br>
        <hr style="border-color: #334155; margin: 8px 0;">
        <span style="color: #38BDF8; font-size: 1.1rem; font-weight: 700;">Total Pembayaran: Rp {grand_total:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)
    
    metode_bayar = st.selectbox(
        "Pilih Metode Pembayaran:", 
        ["Virtual Account BCA", "Virtual Account Mandiri", "QRIS (Instan & Otomatis)", "GoPay / OVO / Dana", "COD (Bayar di Tempat)"]
    )
    
    if "Virtual Account" in metode_bayar or "QRIS" in metode_bayar:
        va_num = f"8888{random.randint(100000000, 999999999)}"
        st.info(f"💡 Kode / Nomor Pembayaran Anda: **`{va_num}`** (Simulasi aktif 24 Jam)")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Batal", use_container_width=True):
            st.rerun()
    with col_btn2:
        if st.button("✅ Bayar Sekarang", use_container_width=True):
            with st.spinner("Memproses transaksi perbankan & gateway..."):
                import time
                time.sleep(1.2)
                
                st.session_state.total_omzet_toko += grand_total
                st.session_state.last_order_details = {"metode": metode_bayar}
                
                for idx, row in df_hasil.iterrows():
                    if 'vibe' in row and row['vibe']:
                        st.session_state.log_vibe_dibeli.append(row['vibe'])
                    if 'nama_produk' in row and row['nama_produk']:
                        st.session_state.log_produk_dibeli.append(row['nama_produk'])
                
                st.session_state.order_success = True
                st.balloons()
                st.rerun()

# =====================================================================
# 5. USER INTERFACE (UI) LAYOUT
# =====================================================================
if menu == "Pembeli":
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        with st.form(key=f"matching_form_{st.session_state.form_reset_counter}", clear_on_submit=True):
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
            submit_matching = st.form_submit_button("🚀 RUN AI VISUAL MATCHING")

        if submit_matching:
            if img_file_buffer is None:
                st.warning("⚠️ Ambil foto atau upload file dulu, bre!")
            else:
                img_bytes = img_file_buffer.getvalue() 
                if len(img_bytes) > 2 * 1024 * 1024:
                    st.error("Foto terlalu besar! Maksimal 2MB.")
                else:
                    st.session_state.total_penggunaan_ai += 1
                    st.session_state.log_gender_dicari.append(pilihan_gender)
                    
                    rgb_dominan = get_dominant_color(img_bytes)
                    nama_warna = get_color_name(rgb_dominan)
                    ai_label = f"stylish {nama_warna.lower()} outfit"
                    
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
        
        # Hanya tampil jika beli_aktif True dan data rekomendasinya valid/tidak kosong
        if st.session_state.get('beli_aktif') and st.session_state.get('hasil_rekomendasi') is not None and not st.session_state.get('hasil_rekomendasi').empty:
            col_tag1, col_tag2 = st.columns(2)
            col_tag1.success(f"🎨 Warna: **{st.session_state.get('warna_terdeteksi', 'Unknown')}**")
            col_tag2.info(f"🤖 AI ViT Label: **{st.session_state.get('ai_label_terdeteksi', 'N/A')}**")
            
            df_hasil = st.session_state.get('hasil_rekomendasi')
            
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
                st.session_state.order_success = False
                tampilkan_payment_dialog(df_hasil, total_harga)
        else:
            st.info("👈 Silakan upload foto dan klik **RUN AI VISUAL MATCHING** di sebelah kiri untuk melihat rekomendasi outfit.")

    st.markdown("---")
    
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
