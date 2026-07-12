import streamlit as st
import pandas as pd
from PIL import Image
import requests
import io

# =====================================================================
# 1. CONFIG & KONSTANTA UTAMA
# =====================================================================
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")
menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

# URL API Model & Webhook n8n
API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
N8N_DATA_URL = "https://casanovaxie.app.n8n.cloud/webhook/ambil-stok-gudang"
N8N_CHAT_URL = "https://casanovaxie.app.n8n.cloud/webhook/VibeID-ChattBot"

# =====================================================================
# 2. DATABASE GUDANG (AMBIL DARI GOOGLE SHEETS VIA N8N)
# =====================================================================
@st.cache_data(ttl=5)
def load_data_from_n8n():
    try:
        response = requests.get(N8N_DATA_URL)
        if response.status_code == 200:
            raw_data = response.json()
            if isinstance(raw_data, list):
                if len(raw_data) > 0 and 'json' in raw_data[0]:
                    cleaned_list = [item['json'] for item in raw_data if 'json' in item]
                    df = pd.DataFrame(cleaned_list)
                else:
                    df = pd.DataFrame(raw_data)
            else:
                df = pd.DataFrame(raw_data)
            df.columns = [str(col).strip() for col in df.columns]
            mapping_kolom = {'Nama Barang': 'nama_produk', 'Kategori': 'kategori_baju', 'Gaya (Style)': 'vibe', 'Warna': 'warna', 'Gender': 'gender', 'Harga': 'harga'}
            df = df.rename(columns=mapping_kolom)
            return df
    except Exception as e:
        return pd.DataFrame()
    return pd.DataFrame()

df_stok = load_data_from_n8n()

# =====================================================================
# 3. INITIALIZATION STATE
# =====================================================================
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa aku bantu?"}]
state_vars = ['log_gender_dicari', 'log_vibe_dibeli', 'log_produk_dibeli', 'total_omzet_toko', 'total_penggunaan_ai', 'warna_terdeteksi', 'beli_aktif', 'hasil_rekomendasi']
for var in state_vars:
    if var not in st.session_state: st.session_state[var] = [] if 'log' in var else (0 if 'total' in var else None)

# =====================================================================
# 4. MODULAR FUNCTIONS
# =====================================================================
def query_chatbot_n8n(user_text):
    try:
        payload = {"message": user_text}
        response = requests.post(N8N_CHAT_URL, json=payload)
        if response.status_code == 200:
            res_data = response.json()
            if isinstance(res_data, list) and len(res_data) > 0: res_data = res_data[0]
            if isinstance(res_data, dict) and 'json' in res_data: res_data = res_data['json']
            return res_data.get("output", "Bot sedang memproses...")
    except: return "Bot tidak merespon."
    return "Bot sedang tidak merespon."

# =====================================================================
# 5. UI LAYOUT
# =====================================================================
if menu == "Pembeli":
    st.title("🛍️ VIBE-ID Smart Assistant")
    
    # --- CHATBOT POPOVER ---
    with st.popover("💬 Chat Bantuan (Click Here)", use_container_width=True):
        st.subheader("VIBE-ID Smart Assistant")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Tanya stok/harga..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response_bot = query_chatbot_n8n(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response_bot})
            st.rerun()

    # --- KONTEN UTAMA ---
    st.header("👤 Langkah 1: Profil Gaya Kamu")
    col1, col2 = st.columns(2)
    pilihan_gender = col1.selectbox("Gender Kamu:", ["Wanita", "Pria"])
    pilihan_usia = col2.selectbox("Target Usia:", ["Gen Z", "Milenial"])
    
    # [Sisa kode visual matching kamu tetap di sini...]
    # (Pastikan kode visual matching kamu tidak terhapus saat copy paste)
    
else:
    st.header("📈 Dasbor Admin")
    # [Sisa kode admin kamu di sini...]
