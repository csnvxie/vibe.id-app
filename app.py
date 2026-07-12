import streamlit as st
import pandas as pd
import requests

# =====================================================================
# 1. CONFIG & KONSTANTA
# =====================================================================
st.set_page_config(page_title="VIBE-ID App", page_icon="🛍️", layout="centered")
menu = st.sidebar.radio("Pilih Hak Akses:", ["Pembeli", "Admin"])

N8N_DATA_URL = "https://casanovaxie.app.n8n.cloud/webhook/ambil-stok-gudang"
N8N_CHAT_URL = "https://casanovaxie.app.n8n.cloud/webhook/VibeID-ChattBot"
API_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"

# =====================================================================
# 2. FUNGSI LOAD DATA (DENGAN PENGECEKAN AMAN)
# =====================================================================
@st.cache_data(ttl=5)
def load_data_from_n8n():
    try:
        response = requests.get(N8N_DATA_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            # Pembersihan kolom sederhana
            df.columns = [str(col).strip() for col in df.columns]
            return df
        return None
    except:
        return None

df_stok = load_data_from_n8n()

# =====================================================================
# 3. INITIALIZATION STATE
# =====================================================================
if 'total_penggunaan_ai' not in st.session_state: st.session_state.total_penggunaan_ai = 0
if 'log_gender_dicari' not in st.session_state: st.session_state.log_gender_dicari = []
if 'total_omzet_toko' not in st.session_state: st.session_state.total_omzet_toko = 0
if 'messages' not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Halo! Ada yang bisa aku bantu?"}]

# =====================================================================
# 4. TAMPILAN APLIKASI
# =====================================================================
if menu == "Pembeli":
    st.header("👤 Profil Gaya Kamu")
    # ... (kode input lainnya)
    st.write("Silakan gunakan fitur AI untuk rekomendasi.")

else: # BAGIAN ADMIN (DENGAN INDENTASI YANG BENAR)
    st.header("📈 Dasbor Admin")
    
    # Metrik
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Scan", f"{st.session_state.total_penggunaan_ai}")
    col3.metric("Omzet", f"Rp {st.session_state.total_omzet_toko:,.0f}")
    
    st.markdown("---")
    
    # BAGIAN DATA GUDANG (FIXED INDENTATION)
    jumlah_stok = len(df_stok) if df_stok is not None else 0
    st.subheader(f"📋 Seluruh Data Stok Gudang ({jumlah_stok} Produk)")

    if df_stok is not None and not df_stok.empty:
        st.dataframe(df_stok, use_container_width=True)
    else:
        st.info("Belum ada data stok yang terload dari database (Cek n8n).")
