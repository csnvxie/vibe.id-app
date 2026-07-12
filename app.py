import streamlit as st
import pandas as pd
import requests

# =====================================================================
# 1. CONFIG & KONSTANTA
# =====================================================================
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")

API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
N8N_DATA_URL = "https://casanovaxie.app.n8n.cloud/webhook/ambil-stok-gudang"
N8N_CHAT_URL = "https://casanovaxie.app.n8n.cloud/webhook/VibeID-ChattBot"

# =====================================================================
# 2. LOAD DATA (DIPANGGIL DI AWAL AGAR DATA SELALU ADA)
# =====================================================================
@st.cache_data(ttl=5)
def load_data_from_n8n():
    try:
        response = requests.get(N8N_DATA_URL)
        if response.status_code == 200:
            data = response.json()
            # Bersihkan data agar jadi dataframe yang valid
            cleaned = [item['json'] for item in data if 'json' in item] if isinstance(data, list) else data
            return pd.DataFrame(cleaned)
    except: return pd.DataFrame()
    return pd.DataFrame()

df_stok = load_data_from_n8n()

# =====================================================================
# 3. SIDEBAR & NAVIGATION
# =====================================================================
menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

# =====================================================================
# 4. LOGIKA APLIKASI
# =====================================================================
# Inisialisasi State
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa dibantu?"}]
if 'img_buffer' not in st.session_state: st.session_state.img_buffer = None
if 'beli_aktif' not in st.session_state: st.session_state.beli_aktif = False

# =====================================================================
# 5. UI PEMBELI
# =====================================================================
if menu == "Pembeli":
    st.title("🛍️ VIBE-ID Smart Assistant")
    
    # 5.1 Chatbot Popover
    with st.popover("💬 Chat Bantuan"):
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if prompt := st.chat_input("Tanya stok/harga..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Panggil fungsi chat (disederhanakan)
            st.session_state.messages.append({"role": "assistant", "content": "Fitur chat aktif."})
            st.rerun()

    # 5.2 Langkah 1 (Gender & Usia) - PASTI MUNCUL
    st.header("👤 Langkah 1: Profil Gaya")
    col1, col2 = st.columns(2)
    col1.selectbox("Gender:", ["Wanita", "Pria"], key="gender")
    col2.selectbox("Usia:", ["Gen Z", "Milenial"], key="usia")

    # 5.3 Langkah 2 (Kamera & Upload)
    st.header("📸 Langkah 2: Input Foto")
    tab_cam, tab_file = st.tabs(["📷 Kamera", "📁 Upload"])
    with tab_cam:
        if cam := st.camera_input("Ambil foto"): st.session_state.img_buffer = cam
    with tab_file:
        if file := st.file_uploader("Pilih file"): st.session_state.img_buffer = file

    # 5.4 Tombol AI & Hasil
    if st.button("RUN AI VISUAL MATCHING 🚀"):
        st.session_state.beli_aktif = True
        st.rerun()

    if st.session_state.beli_aktif:
        st.subheader("🔮 Hasil Rekomendasi:")
        st.dataframe(df_stok.head(3), use_container_width=True) # Menampilkan contoh data
        if st.button("🛒 BELI PAKET"):
            st.success("Transaksi Berhasil!")
            st.session_state.beli_aktif = False

# =====================================================================
# 6. UI ADMIN
# =====================================================================
else:
    st.header("📈 Dasbor Admin - Stok Gudang")
    if not df_stok.empty:
        st.dataframe(df_stok, use_container_width=True)
    else:
        st.warning("Data stok tidak ditemukan atau kosong.")
