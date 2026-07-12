import streamlit as st
import pandas as pd
import requests

# =====================================================================
# 1. CONFIG & KONSTANTA
# =====================================================================
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")
menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
N8N_DATA_URL = "https://casanovaxie.app.n8n.cloud/webhook/ambil-stok-gudang"
N8N_CHAT_URL = "https://casanovaxie.app.n8n.cloud/webhook/VibeID-ChattBot"

# =====================================================================
# 2. LOAD DATA
# =====================================================================
@st.cache_data(ttl=5)
def load_data_from_n8n():
    try:
        response = requests.get(N8N_DATA_URL)
        if response.status_code == 200:
            raw_data = response.json()
            cleaned = [item['json'] for item in raw_data if 'json' in item] if isinstance(raw_data, list) else raw_data
            df = pd.DataFrame(cleaned)
            df.columns = [str(col).strip() for col in df.columns]
            return df.rename(columns={'Nama Barang': 'nama_produk', 'Harga': 'harga', 'Warna': 'warna', 'Gaya (Style)': 'vibe'})
    except: return pd.DataFrame()
    return pd.DataFrame()

df_stok = load_data_from_n8n()

# =====================================================================
# 3. STATE & FUNGSI
# =====================================================================
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa dibantu?"}]
if 'total_omzet_toko' not in st.session_state: st.session_state.total_omzet_toko = 0

def query_chatbot_n8n(user_text):
    try:
        res = requests.post(N8N_CHAT_URL, json={"message": user_text})
        return res.json().get('output', '...') if res.status_code == 200 else "Bot error."
    except: return "Bot error."

# =====================================================================
# 4. UI PEMBELI
# =====================================================================
if menu == "Pembeli":
    st.title("🛍️ VIBE-ID Smart Assistant")
    
    # CHATBOT POPOVER
    with st.popover("💬 Chat Bantuan", use_container_width=True):
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if prompt := st.chat_input("Tanya stok/harga..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": query_chatbot_n8n(prompt)})
            st.rerun()

    st.header("👤 Langkah 1: Profil Gaya")
    col1, col2 = st.columns(2)
    col1.selectbox("Gender:", ["Wanita", "Pria"])
    col2.selectbox("Usia:", ["Gen Z", "Milenial"])

    st.header("📸 Langkah 2: Input Foto")
    tab_cam, tab_file = st.tabs(["📷 Kamera", "📁 Upload"])
    img_buffer = None
    with tab_cam: img_buffer = st.camera_input("Foto baju")
    with tab_file: img_buffer = st.file_uploader("Pilih file...", type=["jpg", "png"])

    if st.button("RUN AI VISUAL MATCHING 🚀"):
        if img_buffer:
            st.info("🔮 AI sedang menganalisis warna...")
            st.session_state.hasil_rekomendasi = df_stok.head(2)
            st.session_state.beli_aktif = True
            st.rerun()
        else: st.warning("Upload foto dulu!")

    if st.session_state.get('beli_aktif'):
        for _, row in st.session_state.hasil_rekomendasi.iterrows():
            st.write(f"**{row.get('nama_produk', 'Produk')}** - Rp {row.get('harga', 0)}")
        if st.button("🛒 BELI PAKET"):
            st.session_state.total_omzet_toko += 100000
            st.success("Transaksi Berhasil!")
            st.session_state.beli_aktif = False

# =====================================================================
# 5. UI ADMIN
# =====================================================================
else:
    st.header("📈 Dasbor Admin")
    st.metric("Total Pendapatan", f"Rp {st.session_state.total_omzet_toko:,.0f}")
    st.dataframe(df_stok, use_container_width=True)
