import streamlit as st
import requests

# 1. Masukkan URL Webhook n8n kamu di sini
# (Ambil dari node Webhook n8n yang "Production URL" ya, bro, jangan yang Test URL)
N8N_WEBHOOK_URL = "https://casanovaxie.app.n8n.cloud/webhook/VibeID-ChattBot"

st.title("🛍️ VIBE-ID - Asisten Belanja")
st.write("Tanya apa saja seputar stok baju, gaya, warna, dan harga di sini!")

# Inisialisasi riwayat chat di Streamlit agar tidak hilang saat reload
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menampilkan chat lama yang ada di session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kolom input chat pembeli
if user_input := st.chat_input("Ketik pesan kamu di sini..."):
    
    # 2. Tampilkan chat pembeli ke layar
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 3. Kirim data chat ke n8n Webhook
    payload = {"message": user_input}
    
    try:
        with st.spinner("Si Gemini lagi mikir & cek gudang..."):
            response = requests.post(N8N_WEBHOOK_URL, json=payload)
            
        if response.status_code == 200:
            # Mengambil teks balasan dari AI Agent n8n
            # (n8n AI Agent biasanya mengembalikan json berupa {'output': 'jawaban bot'} atau langsung teks)
            res_data = response.json()
            
            # Kita coba ambil key 'output' atau 'response' sesuai format AI Agent n8n
            bot_reply = res_data.get("output", res_data.get("response", "Gagal membaca balasan bot."))
            
            # 4. Tampilkan balasan Gemini ke layar Streamlit
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            
        else:
            st.error(f"Waduh, gagal nembak n8n. Error code: {response.status_code}")
            
    except Exception as e:
        st.error(f"Gagal terhubung ke server n8n: {e}")
