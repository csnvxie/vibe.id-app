st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: #0B0F17;
        color: #E2E8F0;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1400px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: visible !important; background-color: transparent !important;}

    section[data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }

    .vibe-banner {
        background: linear-gradient(135deg, #312E81 0%, #1E1B4B 50%, #0F172A 100%);
        border: 1px solid #4338CA;
        border-radius: 16px;
        padding: 24px 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.3);
    }

    .vibe-banner h1 {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 1.9rem;
        margin: 0;
    }

    .vibe-banner p {
        color: #C7D2FE;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 0;
    }

    div[data-testid="stForm"] {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }

    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border-color: #334155 !important;
        border-radius: 10px !important;
    }
    
    div[data-baseweb="popover"], div[data-baseweb="menu"] {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
    }

    .stMarkdown h3, label {
        color: #F1F5F9 !important;
    }

    button[data-baseweb="tab"] {
        background-color: #1E293B !important;
        color: #94A3B8 !important;
        border-radius: 8px 8px 0 0 !important;
        border: 1px solid #334155 !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        border-color: #6366F1 !important;
    }

    /* --- FIX TOTAL BACKGROUND & BAGIAN BAWAH CAMERA INPUT --- */
    div[data-testid="stCameraInput"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px;
        padding: 10px;
    }

    div[data-testid="stCameraInput"] section, 
    div[data-testid="stCameraInput"] div, 
    div[data-testid="stCameraInput"] [data-baseweb="block"] {
        background-color: #1E293B !important;
    }

    /* Memaksa area container tombol ambil foto jadi gelap & teks tombol jadi kontras */
    div[data-testid="stCameraInput"] button {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border: 1px solid #475569 !important;
    }

    div[data-testid="stFileUploader"] {
        background-color: #1E293B !important;
        border: 1px dashed #334155 !important;
        border-radius: 12px;
        padding: 10px;
    }

    .stButton > button, div[data-testid="stForm"] button[type="submit"] {
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        width: 100%;
    }

    .receipt-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        color: #F8FAFC !important;
    }

    .success-card {
        background: linear-gradient(135deg, #065F46 0%, #047857 100%);
        border: 1px solid #10B981;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)
