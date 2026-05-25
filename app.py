import streamlit as st
import pandas as pd
import requests
from PIL import Image
import io
import numpy as np
from sklearn.cluster import KMeans
import time

# ==========================================
# 1. SETTING HALAMAN & CONFIG UTAMA
# ==========================================
st.set_page_config(
    page_title="VIBE-ID App",
    page_icon="🛍️",
    layout="centered"
)

# ==========================================
# 2. DATABASE PRODUK (VERSI VERTIKAL)
# ==========================================
data_gudang = {
    'nama_produk': [
        'White Linen Shirt', 
        'Beige Chino Pants', 
        'Sage Green Outer', 
        'Olive Cargo Pants',
        'Black Oversized Tee', 
        'Dark Charcoal Jeans', 
        'Oversized Crop Varsity', 
        'Plated Cargo Skirt',
        'Pastel Pink Cardigan', 
        'White Tennis Skirt', 
        'Vintage Corduroy Jacket', 
        'Retro Baggy Pants',
        'Crimson Red Hoodie', 
        'Navy Blue Bomber', 
        'Mustard Yellow Sweater', 
        'Royal Blue Denim'
    ],
    'kategori_baju': [
        'Atasan', 'Bawahan', 
        'Atasan', 'Bawahan', 
        'Atasan', 'Bawahan', 
        'Atasan', 'Bawahan',
        'Atasan', 'Bawahan', 
        'Atasan', 'Bawahan', 
        'Atasan', 'Atasan', 
        'Atasan', 'Bawahan'
    ],
    'vibe': [
        'Casual', 'Casual', 
        'Earth Tone', 'Earth Tone', 
        'Monochrome', 'Monochrome', 
        'Y2K Streetwear', 'Y2K Streetwear',
        'Soft Girl Coquette', 
        'Soft Girl Coquette', 
        'Vintage Retro', 'Vintage Retro', 
        'Bold Streetwear', 'Sporty', 
        'Indie Aesthetic', 'Casual'
    ],
    'warna': [
        'Putih', 'Krem', 
        'Hijau', 'Hijau', 
        'Hitam', 'Abu-abu', 
        'Hitam', 'Abu-abu',
        'Pink', 'Putih', 
        'Cokelat', 'Cokelat', 
        'Merah', 'Biru', 
        'Kuning', 'Biru'
    ],
    'gender': [
        'Pria', 'Pria', 
        'Pria', 'Pria', 
        'Unisex', 'Unisex', 
        'Wanita', 'Wanita',
        'Wanita', 'Wanita', 
        'Unisex', 'Unisex', 
        'Unisex', 'Pria', 
        'Unisex', 'Unisex'
    ],
    'target_usia': [
        'Milenial / Gen Z', 
        'Milenial / Gen Z', 
        'Gen Z', 'Gen Z', 
        'Gen Z', 'Gen Z', 
        'Gen Z', 'Gen Z',
        'Gen Z / Gen Alpha', 
        'Gen Z / Gen Alpha', 
        'Gen Z', 'Gen Z', 
        'Gen Z', 'Milenial / Gen Z', 
        'Gen Z', 'Milenial / Gen Z'
    ],
    'harga': [
        149000, 199000, 
        189000, 219000, 
        129000, 249000, 
        279000, 189000,
        159000, 139000, 
        329000, 229000, 
        259000, 299000, 
        179000, 219000
    ],
    'stok': [
        15, 10, 7, 12, 
        20, 14, 9, 11, 
        8, 12, 6, 13, 
        7, 5, 6, 10
    ]
}
df_stok = pd.DataFrame(data_gudang)

# ==========================================
# 3. KAMUS WARNA UNIVERSAL
# ==========================================
KAMUS_WARNA = {
    "Putih": (240, 240, 240), 
    "Hitam": (20, 20, 20), 
    "Abu-abu": (128, 128, 128),
    "Merah": (220, 30, 30), 
    "Biru": (30, 30, 220), 
    "Hijau": (30, 150, 30),
    "Kuning": (230, 230, 30), 
    "Krem": (240, 220, 180), 
    "Cokelat": (110, 70, 40),
    "Pink": (240, 130, 180), 
    "Ungu": (130, 30, 180), 
    "Orange": (240, 130, 30)
}

# ==========================================
# 4. FUNGSI DETEKSI AI VISION
# ==========================================
def query_ai_vision(image_bytes):
    try:
        API_URL = (
            "https://api-inference."
            "huggingface.co/models/"
            "valentinafed/"
            "clothing-detector"
        )
        response = requests
