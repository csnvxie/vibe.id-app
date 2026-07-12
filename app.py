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
# 2. LOAD DATA & FUNGSI AI
# =====================================================================
@st.cache_data(ttl=5)
def load_data_from_n8n():
    try:
        response = requests.get(N8N_DATA_URL)
        if response.status_code == 200:
            data = response.json()
            cleaned = [item['json'] for item in data if 'json' in item] if isinstance(data, list) else data
            df = pd.DataFrame(cleaned)
            df.columns = [str(col).strip() for col in df.columns]
            return df
    except: return pd.DataFrame()
    return pd.DataFrame()

df_stok = load_data_from_n8n()

def query_ai_vision(image_bytes):
    headers = {"Authorization": "Bearer hf_AAsldkfjHsdkfjHskdjfHskdjfHskdjfHskd"}
    try:
        response = requests.post(API_URL, headers=headers, data=image_bytes)
        return str(response.json()[0].get('label', '')).lower() if response.status_code == 200 else "unknown"
    except: return "unknown"

def query_chatbot_n8n(user_text):
    try:
        res = requests.post(N8N_CHAT_URL, json={"message": user_text})
        return res.json().get('output', '...') if res.status_code == 200 else "Bot error."
    except: return "Bot error."

# =====================================================================
# 3. STATE
# =====================================================================
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa dibantu?"}]
if 'img_buffer' not in st.session_state: st.session_state.img_buffer = None
if 'beli_aktif' not in st.session_state: st.session_state.beli_aktif = False
if 'total_omzet_toko' not in st.session_state: st.session_state.total_omzet_toko = 0

# =====================================================================
# 4. UI PEMBELI
# =====================================================================
if menu == "Pembeli":
    st.title("🛍️ VIBE-ID Smart Assistant")
    
    with st.popover("💬 Chat Bantuan", use_container_width=True):
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if prompt := st.chat_input("Tanya stok/harga..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": query_chatbot_n8n(prompt)})
            st.rerun()

    st.header("📸 Langkah 2: Input Foto")
    tab_cam, tab_file = st.tabs(["📷 Kamera", "📁 Upload"])
    with tab_cam:
        if foto := st.camera_input("Foto baju"): st.session_state.img_buffer = foto
    with tab_file:
        if file := st.file_uploader("Pilih file...", type=["jpg", "png"]): st.session_state.img_buffer = file

    if st.button("RUN AI VISUAL MATCHING 🚀"):
        if st.session_state.img_buffer:
            img_bytes = st.session_state.img_buffer.getvalue()
            label = query_ai_vision(img_bytes)
            
            # Deteksi warna berdasarkan label (bisa kamu sesuaikan logikanya)
            warna_target = "Merah" if any(x in label for x in ["shirt", "jersey", "t-shirt"]) else "Biru"
            
            # Cek kolom yang tersedia di dataframe secara otomatis
            cols = [c for c in df_stok.columns if 'warna' in c.lower() or 'Warna' in c]
            if cols:
                col_name = cols[0]
                st.session_state.hasil_rekomendasi = df_stok[df_stok[col_name].astype(str).str.contains(warna_target, case=False, na=False)]
                st.session_state.warna_terdeteksi = warna_target
                st.session_state.beli_aktif = True
                st.rerun()
            else:
                st.error(f"Kolom warna tidak ditemukan! Kolom yang ada: {list(df_stok.columns)}")
        else: st.warning("Silakan ambil foto atau upload file!")

    if st.session_state.beli_aktif:
        st.success(f"Ditemukan rekomendasi warna: **{st.session_state.warna_terdeteksi}**")
        st.dataframe(st.session_state.hasil_rekomendasi, use_container_width=True)
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
