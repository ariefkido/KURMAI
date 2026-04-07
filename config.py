# config.py
# ============================================================
# Konfigurasi KURMAI
# Untuk menambah peraturan baru: tambahkan entry di REGULATIONS
# ============================================================

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE_DIR = BASE_DIR / "database"

# ============================================================
# DAFTAR PERATURAN
# key  : identifier unik (dipakai internal)
# label: nama tampil di UI
# path : path ke file JSON relatif dari DATABASE_DIR
# ============================================================
REGULATIONS = {
    "kur": {
        "label": "KUR (Kredit Usaha Rakyat)",
        "path": DATABASE_DIR / "kur" / "peraturan.json",
    },
    # Contoh menambah peraturan baru:
    # "umkm": {
    #     "label": "Peraturan UMKM",
    #     "path": DATABASE_DIR / "umkm" / "peraturan.json",
    # },
}

# ============================================================
# SETTINGS RAG
# ============================================================
CHUNK_SIZE = 800          # Karakter per chunk
CHUNK_OVERLAP = 100       # Overlap antar chunk
TOP_K = 5                 # Jumlah chunk yang diambil per query

# ============================================================
# SETTINGS LLM
# ============================================================
GEMINI_MODEL = "gemini-2.0-flash"
EMBEDDING_MODEL = "text-embedding-004"

# ============================================================
# SETTINGS UI
# ============================================================
APP_TITLE = "KURMAI"
APP_SUBTITLE = "Asisten Peraturan Kredit Usaha Rakyat"
APP_ICON = "💬"
WELCOME_MESSAGE = (
    "Halo! Saya **KURMAI**, asisten yang siap membantu Anda "
    "memahami peraturan terkait **Kredit Usaha Rakyat (KUR)**.\n\n"
    "Silakan ajukan pertanyaan Anda."
)
