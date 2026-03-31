# KURMAI — Chatbot Peraturan

Chatbot berbasis RAG untuk menjawab pertanyaan seputar peraturan yang telah dimuat.

## Struktur Project

```
kurmai/
├── database/               # Folder peraturan (JSON)
│   └── kur/
│       └── peraturan.json  # Contoh: file peraturan KUR
├── src/
│   ├── loader.py           # Load & parse JSON peraturan
│   ├── vectorstore.py      # Build FAISS index dari dokumen
│   └── chain.py            # RAG chain dengan Gemini
├── app.py                  # Streamlit UI
├── config.py               # Konfigurasi (API key, paths, dll)
├── requirements.txt
└── .env                    # GEMINI_API_KEY (tidak di-commit)
```

## Cara Menambah Peraturan Baru

1. Buat subfolder di `database/`, misal `database/umkm/`
2. Taruh file JSON peraturan di sana
3. Daftarkan di `config.py` pada `REGULATIONS` dict
4. Restart app — index akan dibangun ulang otomatis

## Format JSON Peraturan

Array of flat objects, satu object per ayat:

```json
[
  {
    "source": "Nama Peraturan Lengkap",
    "bab": "I",
    "judul_bab": "KETENTUAN UMUM",
    "pasal": "1",
    "ayat": "0",
    "full_context": "BAB I > KETENTUAN UMUM > Pasal 1",
    "text": "Teks isi pasal atau ayat...",
    "char_count": 61
  },
  {
    "source": "Nama Peraturan Lengkap",
    "bab": "I",
    "judul_bab": "KETENTUAN UMUM",
    "pasal": "1",
    "ayat": "1",
    "full_context": "BAB I > KETENTUAN UMUM > Pasal 1 > Ayat (1)",
    "text": "Teks ayat pertama...",
    "char_count": 294
  }
]
```

Catatan:
- `ayat: "0"` = intro pasal tanpa nomor ayat
- `char_count` tidak wajib, hanya informatif
- Loader akan mengelompokkan semua ayat dalam satu pasal menjadi satu Document

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Isi GEMINI_API_KEY di .env
streamlit run app.py
```
