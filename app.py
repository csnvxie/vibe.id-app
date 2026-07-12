import streamlit as st
import pandas as pd
import requests

# =====================================================================
# 1. CONFIG & KONSTANTA UTAMA
# =====================================================================
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")
menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

# URL API Model & Webhook n8n (Pastikan URL ini menggunakan jalur PRODUCTION tanpa -test)
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
                cleaned_list = [item['json'] for item in raw_data if 'json' in item]
                df = pd.DataFrame(cleaned_list if cleaned_list else raw_data)
            else:
                df = pd.DataFrame(raw_data)
            
            df.columns = [str(col).strip() for col in df.columns]
            mapping_kolom = {'Nama Barang': 'nama_produk', 'Kategori': 'kategori_baju', 'Gaya (Style)': 'vibe', 'Warna': 'warna', 'Harga': 'harga'}
            df = df.rename(columns=mapping_kolom)
            return df
    except: return pd.DataFrame()
    return pd.DataFrame()

df_stok = load_data_from_n8n()

# =====================================================================
# 3. INITIALIZATION STATE
# =====================================================================
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa aku bantu?"}]
# Inisialisasi state lainnya
state_vars = ['log_gender_dicari', 'log_vibe_dibeli', 'total_omzet_toko', 'total_penggunaan_ai', 'beli_aktif', 'hasil_rekomendasi', 'warna_terdeteksi']
for var in state_vars:
    if var not in st.session_state: st.session_state[var] = [] if 'log' in var else (0 if 'total' in var else None)

# =====================================================================
# 4. FUNGSI CHATBOT (DENGAN RESPOND TO WEBHOOK)
# =====================================================================
def query_chatbot_n8n(user_text):
    try:
        payload = {"message": user_text}
        response = requests.post(N8N_CHAT_URL, json=payload)
        if response.status_code == 200:
            res_data = response.json()
            if isinstance(res_data, list): res_data = res_data[0]
            if isinstance(res_data, dict) and 'json' in res_data: res_data = res_data['json']
            return res_data.get("output", "Bot sedang memproses...")
    except Exception as e: return f"Error: {e}"
    return "Bot tidak merespon."

# =====================================================================
# 5. UI LAYOUT
# =====================================================================
if menu == "Pembeli":
    st.title("🛍️ VIBE-ID Smart Assistant")
    
    # --- CHATBOT POPOVER (FLOTING STYLE) ---
    with st.popover("💬 Chat Bantuan", use_container_width=True):
        st.subheader("VIBE-ID Assistant")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ketik pesanmu..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response_bot = query_chatbot_n8n(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response_bot})
            st.rerun()

    # Konten utama aplikasi (Langkah 1, 2, 3...)
    st.header("📸 Visual Matching")
    # [Tambahkan sisa kode UI kamu di sini...]

else:
    st.header("📈 Dasbor Admin")
    # [Tambahkan sisa kode Admin kamu di sini...]
