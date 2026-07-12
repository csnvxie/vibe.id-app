import streamlit as st
import requests
from streamlit_camera_input_live import camera_input_live

# =========================================================================
# ⚙️ CONFIGURATION & SETTINGS
# =========================================================================
# Ganti dengan URL Production Webhook n8n kamu yang baru (AI Agent Gemini)
N8N_WEBHOOK_URL = "https://casanovaxie.app.n8n.cloud/webhook/VibeID-ChattBot"

st.set_page_config(page_title="VIBE-ID - AI Outfit Scanner & Chat", page_icon="🛍️", layout="wide")

# =========================================================================
# 🏠 TOP HEADER
# =========================================================================
st.title("🛍️ VIBE-ID — AI Outfit Scanner & Smart Assistant")
st.write("Deteksi vibe pakaianmu lewat kamera secara real-time atau tanya langsung ke asisten AI kami!")
st.markdown("---")

# Kita bagi jadi 2 kolom: Kiri untuk Kamera & Deteksi, Kanan untuk Live Chatbot (Topping)
col1, col2 = st.columns([1.2, 1])

# =========================================================================
# 📸 KOLOM 1: AI CAMERA SCANNER (Fitur Utama yang Awal)
# =========================================================================
with col1:
    st.subheader("📷 Live Vibe Scanner")
    st.write("Arahkan kameramu ke pakaian yang sedang kamu pakai/pilih:")
    
    # Memanggil komponen kamera live awal
    image = camera_input_live(show_controls=True, key="outfit_camera")
    
    if image is not None:
        st.image(image, caption="Foto berhasil diambil!", use_container_width=True)
        
        # Tombol untuk trigger proses deteksi AI
        if st.button("Scan & Cocokkan Vibe Baju 🚀"):
            # Siapkan pesan otomatis untuk n8n agar menganalisis (bisa disesuaikan dengan kebutuhan parsing gambar lo sebelumnya)
            pesan_kamera = (
                "Halo Gemini, saya baru saja mengambil foto pakaian saya lewat kamera. "
                "Tolong analisis vibe/gaya pakaian saat ini, beri rekomendasi mix-and-match yang cocok, "
                "dan carikan produk yang sesuai dari Google Sheets stok gudang kita ya!"
            )
            
            try:
                with st.spinner("AI sedang menganalisis foto dan mencocokkan stok gudang..."):
                    # Kirim trigger ke webhook n8n
                    res = requests.post(N8N_WEBHOOK_URL, json={"message": pesan_kamera})
                    
                if res.status_code == 200:
                    data = res.json()
                    hasil_scan = data.get("output", data.get("response", "Gagal memproses analisis gambar."))
                    
                    st.markdown("### 🎯 Hasil Analisis Vibe & Rekomendasi:")
                    st.success(hasil_scan)
                else:
                    st.error(f"Gagal terhubung ke n8n. Kode Error: {res.status_code}")
            except Exception as e:
                st.error(f"Error sistem kamera: {e}")

# =========================================================================
# 💬 KOLOM 2: LIVE CHATBOT GEMINI (Topping Tambahan di Samping)
# =========================================================================
with col2:
    st.subheader("💬 Tanya Asisten AI (Real-time Stok)")
    st.write("Mau tanya ukuran, warna lain, atau harga baju spesifik? Chat di sini:")
    
    # Wadah komponen chat agar memiliki batas scroll yang rapi
    chat_container = st.container(height=400)
    
    # Inisialisasi riwayat chat agar tidak hilang saat halaman reload
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Menampilkan riwayat chat lama ke dalam container
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
    # Input box chat pembeli (diletakkan di bawah container)
    if user_input := st.chat_input("Tanya stok, misal: 'Ada kemeja flanel warna biru size L gak?'"):
        
        # Tampilkan chat pembeli di layar
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Kirim teks chat ke Webhook n8n AI Agent
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
