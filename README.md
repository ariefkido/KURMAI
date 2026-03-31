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

```json
{
  "metadata": {
    "judul": "Peraturan Menteri ...",
    "nomor": "...",
    "tahun": 2024,
    "tentang": "..."
  },
  "pasal": [
    {
      "nomor": "1",
      "judul": "Ketentuan Umum",
      "ayat": [
        {
          "nomor": "1",
          "teks": "..."
        }
      ]
    }
  ]
}
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Isi GEMINI_API_KEY di .env
streamlit run app.py
```
