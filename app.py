import streamlit as st
import requests

# =========================================================================
# ⚙️ CONFIGURATION & SETTINGS
# =========================================================================
# Ganti dengan URL Production Webhook n8n kamu yang baru (AI Agent Gemini)
N8N_WEBHOOK_URL = "https://casanovaxie.app.n8n.cloud/webhook/VibeID-ChattBot"

st.set_page_config(page_title="VIBE-ID - Smart Outfit Assistant", page_icon="🛍️", layout="wide")

# =========================================================================
# 🏠 TOP HEADER
# =========================================================================
st.title("🛍️ VIBE-ID — Asisten Toko & Gaya Baju Pintar")
st.write("Temukan gaya pakaian terbaikmu secara otomatis atau langsung tanya ke AI Agent kami!")
st.markdown("---")

# Membuat dua kolom besar agar tampilan aplikasi rapi dan seimbang
col1, col2 = st.columns([1, 1.2])

# =========================================================================
# 📋 KOLOM 1: REKOMENDASI GAYA AUTOMATIC (Kuesioner Input)
# =========================================================================
with col1:
    st.subheader("🎯 Cari Tahu Vibe Pakaianmu")
    st.write("Isi formulir singkat di bawah ini untuk dicocokkan dengan stok kami:")
    
    with st.form("outfit_form"):
        nama = st.text_input("Nama Kamu", placeholder="Contoh: Budi")
        
        kategori = st.selectbox(
            "Kategori Pakaian yang Dicari",
            ["Atasan (Kaos/Kemeja)", "Bawahan (Celana/Rok)", "Outerwear (Jaket/Hoodie)", "Terusan (Dress/Setelan)"]
        )
        
        vibe = st.selectbox(
            "Gaya / Vibe yang Diinginkan",
            ["Casual / Santai", "Formal / Kerja", "Streetwear / Hypebeast", "Korean Style", "Minimalist / Quiet Luxury"]
        )
        
        target_usia = st.selectbox(
            "Target Usia / Kategori",
            ["Anak-anak", "Remaja (Teenager)", "Dewasa Muda (Young Adult)", "Dewasa (Adult)"]
        )
        
        warna_favorit = st.text_input("Warna Pakaian Favorit", placeholder="Contoh: Hitam, Earth Tone, Pastel")
        
        submit_btn = st.form_submit_button("Cari Rekomendasi 🚀")
        
    if submit_btn:
        if not nama or not warna_favorit:
            st.warning("Yuk, isi Nama dan Warna Favorit kamu dulu ya!")
        else:
            st.success(f"Halo {nama}! Kuesioner kamu berhasil diproses.")
            
            # Teks otomatis yang dirakit berdasarkan jawaban kuesioner
            pesan_otomatis = (
                f"Halo Gemini, saya sedang merekomendasikan pakaian untuk {nama}. "
                f"Tolong carikan di Google Sheets produk dengan kategori '{kategori}', "
                f"gaya/vibe '{vibe}', target usia '{target_usia}', dan utamakan warna '{warna_favorit}'."
            )
            
            # Otomatis nembak ke n8n untuk minta rekomendasi berdasarkan kuesioner
            try:
                with st.spinner("Mencari kecocokan baju di gudang..."):
                    res = requests.post(N8N_WEBHOOK_URL, json={"message": pesan_otomatis})
                    
                if res.status_code == 200:
                    data = res.json()
                    jawaban_rekomendasi = data.get("output", data.get("response", "Gagal memproses rekomendasi."))
                    
                    st.markdown("### 🏷️ Rekomendasi Untukmu:")
                    st.info(jawaban_rekomendasi)
                else:
                    st.error(f"Gagal terhubung ke n8n. Kode Error: {res.status_code}")
            except Exception as e:
                st.error(f"Error sistem: {e}")

# =========================================================================
# 💬 KOLOM 2: LIVE CHATBOT (AI AGENT GEMINI 2.5 FLASH)
# =========================================================================
with col2:
    st.subheader("💬 Tanya Asisten AI (Real-time Stok)")
    st.write("Mau cek ketersediaan ukuran atau tanya warna lain? Ketik langsung di bawah:")
    
    # Wadah komponen chat agar memiliki batas scroll yang rapi
    chat_container = st.container(height=450)
    
    # Inisialisasi riwayat chat agar tidak hilang saat halaman reload
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Menampilkan riwayat chat lama ke dalam container
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Input box chat pembeli (diletakkan di bawah container)
    if user_input := st.chat_input("Tanya stok, misal: 'Kemeja hitam ukuran M ready gak?'"):
        
        # Tampilkan chat pembeli di layar
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Kirim teks ke Webhook n8n AI Agent
        try:
            with chat_container:
                with st.spinner("Gemini sedang mengecek database..."):
                    response = requests.post(N8N_WEBHOOK_URL, json={"message": user_input})
                    
            if response.status_code == 200:
                res_data = response.json()
                bot_reply = res_data.get("output", res_data.get("response", "Maaf, robot gagal merespons."))
                
                # Tampilkan balasan Gemini di layar
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            else:
                st.error(f"Koneksi n8n bermasalah. Status: {response.status_code}")
                
        except Exception as e:
            st.error(f"Gagal menghubungi server: {e}")
