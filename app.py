# app.py
# ============================================================
# KURMAI — Streamlit UI
# ============================================================

import logging
import os
import sys

import streamlit as st
from dotenv import load_dotenv

# Pastikan src/ bisa di-import
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

import config
from src.loader import load_all_regulations
from src.vectorstore import build_vectorstore, get_retriever
from src.chain import build_chain, stream_answer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="centered",
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .block-container { max-width: 800px; padding-top: 2rem; }
    .stChatMessage { border-radius: 12px; }
    #MainMenu, footer, header { visibility: hidden; }
    .app-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .app-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
    }
    .app-header p {
        color: #888;
        font-size: 0.95rem;
        margin-top: 0;
    }
    .source-badge {
        display: inline-block;
        background: #1a1a2e;
        color: #e0e0e0;
        font-size: 0.72rem;
        padding: 2px 8px;
        border-radius: 99px;
        margin: 2px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class="app-header">
    <h1>{config.APP_ICON} {config.APP_TITLE}</h1>
    <p>{config.APP_SUBTITLE}</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# API KEY CHECK
# ============================================================
api_key = os.getenv("GOOGLE_API_KEY", "")
if not api_key:
    st.error("GOOGLE_API_KEY tidak ditemukan. Tambahkan ke file `.env`.")
    st.stop()

# ============================================================
# INIT — load & index (cached per session)
# ============================================================
@st.cache_resource(show_spinner="Memuat dan mengindeks peraturan...")
def init_rag(api_key: str):
    docs = load_all_regulations(config.REGULATIONS)
    if not docs:
        return None, None

    vs = build_vectorstore(docs, api_key)
    if vs is None:
        return None, None

    retriever = get_retriever(vs)
    chain = build_chain(retriever, api_key)
    return chain, len(docs)


chain, doc_count = init_rag(api_key)

if chain is None:
    st.error(
        "Gagal memuat peraturan. Pastikan file JSON tersedia di folder `database/`."
    )
    st.info("Lihat README.md untuk format JSON yang diharapkan.")
    st.stop()

# Info peraturan yang dimuat
with st.expander("📋 Peraturan yang dimuat", expanded=False):
    for key, info in config.REGULATIONS.items():
        path = info["path"]
        status = "✅" if path.exists() else "❌ file tidak ditemukan"
        st.markdown(f"- **{info['label']}** {status}")

# ============================================================
# CHAT STATE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": config.WELCOME_MESSAGE}
    ]

# Tampilkan history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ============================================================
# INPUT
# ============================================================
if prompt := st.chat_input("Tulis pertanyaan Anda..."):
    # Tampilkan pesan user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate & stream jawaban
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            for chunk in stream_answer(chain, prompt):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Terjadi kesalahan: {e}"
            response_placeholder.error(full_response)
            logger.exception("Error saat generate jawaban")

    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### KURMAI")
    st.caption("Asisten Peraturan berbasis AI")
    st.divider()

    st.markdown("**Peraturan aktif:**")
    for key, info in config.REGULATIONS.items():
        st.markdown(f"- {info['label']}")

    st.divider()

    if st.button("🗑️ Reset percakapan", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": config.WELCOME_MESSAGE}
        ]
        st.rerun()

    st.divider()
    st.caption("Jawaban didasarkan pada peraturan yang dimuat. Bukan merupakan nasihat hukum resmi.")
