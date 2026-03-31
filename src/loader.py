# src/loader.py
# ============================================================
# Memuat dan mem-parsing file JSON peraturan menjadi
# list of LangChain Document objects
# ============================================================

import json
import logging
from pathlib import Path
from typing import Optional

from langchain.schema import Document

logger = logging.getLogger(__name__)


def _extract_text_from_pasal(pasal: dict) -> str:
    """Konversi satu pasal (dengan ayat-ayatnya) menjadi teks bersih."""
    lines = []
    nomor = pasal.get("nomor", "")
    judul = pasal.get("judul", "")

    header = f"Pasal {nomor}"
    if judul:
        header += f" — {judul}"
    lines.append(header)

    for ayat in pasal.get("ayat", []):
        nomor_ayat = ayat.get("nomor", "")
        teks = ayat.get("teks", "").strip()
        if teks:
            prefix = f"({nomor_ayat}) " if nomor_ayat else ""
            lines.append(f"{prefix}{teks}")

        # Sub-ayat / huruf jika ada
        for item in ayat.get("items", []):
            huruf = item.get("huruf", "")
            teks_item = item.get("teks", "").strip()
            if teks_item:
                prefix = f"  {huruf}. " if huruf else "  - "
                lines.append(f"{prefix}{teks_item}")

    return "\n".join(lines)


def load_regulation(json_path: Path, reg_key: str, reg_label: str) -> list[Document]:
    """
    Muat satu file JSON peraturan dan kembalikan sebagai list Document.

    Setiap Document merepresentasikan satu pasal, dengan metadata:
    - source     : reg_key
    - label      : nama peraturan
    - judul_peraturan
    - nomor_peraturan
    - tahun
    - pasal
    """
    if not json_path.exists():
        logger.warning(f"File tidak ditemukan: {json_path}")
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    pasal_list = data.get("pasal", [])

    if not pasal_list:
        logger.warning(f"Tidak ada data pasal di {json_path}")
        return []

    documents = []
    for pasal in pasal_list:
        text = _extract_text_from_pasal(pasal)
        if not text.strip():
            continue

        doc = Document(
            page_content=text,
            metadata={
                "source": reg_key,
                "label": reg_label,
                "judul_peraturan": meta.get("judul", ""),
                "nomor_peraturan": meta.get("nomor", ""),
                "tahun": str(meta.get("tahun", "")),
                "tentang": meta.get("tentang", ""),
                "pasal": pasal.get("nomor", ""),
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
