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

API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
N8N_DATA_URL = "https://casanovaxie.app.n8n.cloud/webhook/ambil-stok-gudang"
N8N_CHAT_URL = "https://casanovaxie.app.n8n.cloud/webhook/VibeID-ChattBot"

# =====================================================================
# 2. DATABASE GUDANG
# =====================================================================
@st.cache_data(ttl=5)
def load_data_from_n8n():
    try:
        response = requests.get(N8N_DATA_URL)
        if response.status_code == 200:
            raw_data = response.json()
            cleaned_list = [item['json'] for item in raw_data if 'json' in item] if isinstance(raw_data, list) else raw_data
            df = pd.DataFrame(cleaned_list)
            df.columns = [str(col).strip() for col in df.columns]
            df = df.rename(columns={'Nama Barang': 'nama_produk', 'Kategori': 'kategori_baju', 'Gaya (Style)': 'vibe', 'Warna': 'warna', 'Harga': 'harga'})
            return df
    except: return pd.DataFrame(columns=['nama_produk', 'kategori_baju', 'vibe', 'warna', 'harga', 'url_gambar'])
    return pd.DataFrame()

df_stok = load_data_from_n8n()

# =====================================================================
# 3. STATE & FUNGSI
# =====================================================================
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa dibantu?"}]
for var in ['log_gender_dicari', 'log_vibe_dibeli', 'total_omzet_toko', 'total_penggunaan_ai', 'beli_aktif', 'hasil_rekomendasi']:
    if var not in st.session_state: st.session_state[var] = [] if 'log' in var else (0 if 'total' in var else None)

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
# 4. UI PEMBELI
# =====================================================================
if menu == "Pembeli":
    st.title("🛍️ VIBE-ID Smart Assistant")
    with st.popover("💬 Chat Bantuan (Click Here)", use_container_width=True):
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if prompt := st.chat_input("Tanya stok/harga..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "assistant", "content": query_chatbot_n8n(prompt)})
            st.rerun()

    st.header("👤 Langkah 1: Profil Gaya Kamu")
    col1, col2 = st.columns(2)
    pilihan_gender = col1.selectbox("Gender Kamu:", ["Wanita", "Pria"])
    pilihan_usia = col2.selectbox("Target Usia:", ["Gen Z", "Milenial"])

    st.header("📸 Langkah 2: Input Foto Pakaian")
    tab_cam, tab_file = st.tabs(["📷 Gunakan Real Cam", "📁 Upload File Foto"])
    
    img_file_buffer = None
    
    with tab_cam:
        foto_kamera = st.camera_input("Posisikan baju kamu di depan kamera")
        if foto_kamera: img_file_buffer = foto_kamera
            
    with tab_file:
        file_foto = st.file_uploader("Pilih file foto dari penyimpanan...", type=["jpg", "jpeg", "png"])
        if file_foto: img_file_buffer = file_foto

    # Pastikan variabel img_file_buffer ini nanti dipakai di tombol RUN AI
    
    if st.button("RUN AI VISUAL MATCHING 🚀"):
        st.session_state.total_penggunaan_ai += 1
        st.session_state.log_gender_dicari.append(pilihan_gender)
        if img_file_buffer is not None:
    img_bytes = img_file_buffer.getvalue() if hasattr(img_file_buffer, "getvalue") else img_file_buffer.read()
        tebakan = query_ai_vision(img_bytes)
        st.session_state.warna_terdeteksi = "Merah" if any(x in tebakan for x in ["shirt", "jersey"]) else "Biru"
        st.session_state.hasil_rekomendasi = df_stok.head(2)
        st.session_state.beli_aktif = True
        st.rerun()

    if st.session_state.beli_aktif:
        st.success(f"🎨 Rekomendasi warna: {st.session_state.warna_terdeteksi}")
        for _, row in st.session_state.hasil_rekomendasi.iterrows():
            st.image(row.get('url_gambar', ''), width=200)
            st.write(f"**{row['nama_produk']}** - Rp {row['harga']}")
        if st.button("🛒 BELI PAKET"):
            st.session_state.total_omzet_toko += 100000
            st.success("Transaksi Berhasil!")
            st.session_state.beli_aktif = False

# =====================================================================
# 5. UI ADMIN
# =====================================================================
else:
    st.header("📈 Dasbor Admin")
    st.metric("Pendapatan", f"Rp {st.session_state.total_omzet_toko:,.0f}")
    st.bar_chart(pd.DataFrame(st.session_state.log_vibe_dibeli, columns=['Vibe']).value_counts())
    st.dataframe(df_stok, use_container_width=True)
