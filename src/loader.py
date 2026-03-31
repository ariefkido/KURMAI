# src/loader.py
# ============================================================
# Memuat dan mem-parsing file JSON peraturan menjadi
# list of LangChain Document objects
#
# Format JSON yang diharapkan: array of flat objects, tiap object
# merepresentasikan satu ayat dengan field:
#   source, bab, judul_bab, pasal, ayat, full_context, text, char_count
# ============================================================

import json
import logging
import re
from collections import defaultdict
from pathlib import Path

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Regex untuk membersihkan noise nomor halaman, misal "- 3 -"
_PAGE_NUMBER_RE = re.compile(r"\s*-\s*\d+\s*-\s*$")


def _clean_text(text: str) -> str:
    """Hapus noise nomor halaman di akhir teks."""
    return _PAGE_NUMBER_RE.sub("", text).strip()


def load_regulation(json_path: Path, reg_key: str, reg_label: str) -> list[Document]:
    """
    Muat satu file JSON peraturan (format: array of ayat) dan kembalikan
    sebagai list Document.

    Strategi chunking: gabungkan semua ayat dalam satu pasal menjadi
    satu Document, agar konteks per pasal tetap utuh saat retrieval.

    Metadata per Document:
    - source        : reg_key (identifier internal)
    - label         : nama peraturan tampil
    - source_name   : nilai field 'source' dari JSON
    - bab           : nomor bab
    - judul_bab     : judul bab
    - pasal         : nomor pasal
    - full_context  : breadcrumb konteks (dari ayat pertama pasal)
    """
    if not json_path.exists():
        logger.warning(f"File tidak ditemukan: {json_path}")
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, list) or not raw:
        logger.warning(f"Format JSON tidak sesuai atau kosong: {json_path}")
        return []

    # Kelompokkan ayat-ayat per pasal (key: (bab, pasal))
    pasal_groups: dict[tuple, list[dict]] = defaultdict(list)
    for item in raw:
        key = (item.get("bab", ""), item.get("pasal", ""))
        pasal_groups[key].append(item)

    documents = []
    for (bab, pasal_nomor), ayat_list in pasal_groups.items():
        # Susun teks pasal dari semua ayatnya
        lines = []

        # Header pasal
        first = ayat_list[0]
        judul_bab = first.get("judul_bab", "")
        breadcrumb = f"BAB {bab} — {judul_bab} | Pasal {pasal_nomor}"
        lines.append(breadcrumb)

        for item in ayat_list:
            nomor_ayat = str(item.get("ayat", "0"))
            text = _clean_text(item.get("text", ""))
            if not text:
                continue

            if nomor_ayat == "0":
                # Intro pasal tanpa nomor ayat
                lines.append(text)
            else:
                lines.append(f"({nomor_ayat}) {text}")

        page_content = "\n".join(lines)

        # Ambil breadcrumb paling dalam (ayat terakhir) sebagai referensi
        full_context = first.get("full_context", breadcrumb)

        doc = Document(
            page_content=page_content,
            metadata={
                "source": reg_key,
                "label": reg_label,
                "source_name": first.get("source", ""),
                "bab": bab,
                "judul_bab": judul_bab,
                "pasal": pasal_nomor,
                "full_context": full_context,
            },
        )
        documents.append(doc)

    logger.info(f"Loaded {len(documents)} pasal dari {json_path.name}")
    return documents


def load_all_regulations(regulations: dict) -> list[Document]:
    """Muat semua peraturan yang terdaftar di config.REGULATIONS."""
    all_docs = []
    for key, info in regulations.items():
        docs = load_regulation(
            json_path=info["path"],
            reg_key=key,
            reg_label=info["label"],
        )
        all_docs.extend(docs)

    logger.info(f"Total dokumen dimuat: {len(all_docs)}")
    return all_docs
