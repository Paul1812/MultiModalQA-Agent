import streamlit as st
import os, time, base64
from pathlib import Path
from PIL import Image
import io

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MultiModalQA-Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── inject CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* dark base */
.stApp { background: #0a0a0f; color: #e8e8f0; }

/* sidebar */
[data-testid="stSidebar"] {
    background: #0f0f1a;
    border-right: 1px solid #1e1e3a;
}

/* title */
.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #7c6af7 0%, #4fc3f7 60%, #81ecec 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    margin-bottom: 0;
}
.sub-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    color: #555580;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 2px;
}

/* agent pipeline card */
.pipeline-step {
    background: #12121f;
    border: 1px solid #1e1e3a;
    border-left: 3px solid #7c6af7;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #aaaacc;
    transition: border-color 0.3s;
}
.pipeline-step.active {
    border-left-color: #4fc3f7;
    color: #4fc3f7;
    background: #0d1220;
}
.pipeline-step.done {
    border-left-color: #00e676;
    color: #00e676;
    background: #0a1510;
}

/* chat bubbles */
.chat-user {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px 12px 4px 12px;
    padding: 14px 18px;
    margin: 10px 0;
    max-width: 85%;
    margin-left: auto;
    color: #d0d0f0;
    font-size: 0.95rem;
}
.chat-agent {
    background: #0f1520;
    border: 1px solid #1e2a3a;
    border-radius: 4px 12px 12px 12px;
    padding: 14px 18px;
    margin: 10px 0;
    max-width: 95%;
    color: #c8d8e8;
    font-size: 0.95rem;
    line-height: 1.6;
}
.chat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
    opacity: 0.5;
}

/* metric cards */
.metric-card {
    background: #0f0f1a;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 14px;
    text-align: center;
}
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    color: #7c6af7;
    font-weight: 700;
}
.metric-label {
    font-size: 0.72rem;
    color: #555580;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* input area */
.stTextArea textarea {
    background: #0f0f1a !important;
    border: 1px solid #2a2a4a !important;
    color: #e0e0f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 10px !important;
}
.stTextArea textarea:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.15) !important;
}

/* buttons */
.stButton button {
    background: linear-gradient(135deg, #7c6af7, #4fc3f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 1px !important;
    padding: 10px 24px !important;
    transition: opacity 0.2s !important;
}
.stButton button:hover { opacity: 0.85 !important; }

/* file uploader */
[data-testid="stFileUploader"] {
    background: #0f0f1a;
    border: 1.5px dashed #2a2a4a;
    border-radius: 12px;
    padding: 10px;
}

/* divider */
hr { border-color: #1e1e3a !important; }

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; }

/* OCR box */
.ocr-box {
    background: #080812;
    border: 1px solid #1e1e3a;
    border-radius: 8px;
    padding: 12px;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: #8888aa;
    white-space: pre-wrap;
    max-height: 200px;
    overflow-y: auto;
}

/* tag pills */
.tag {
    display: inline-block;
    background: #1a1a30;
    border: 1px solid #2a2a4a;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.72rem;
    color: #8888bb;
    margin: 2px;
    font-family: 'Space Mono', monospace;
}

.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}
.dot-active { background: #4fc3f7; animation: pulse 1.2s infinite; }
.dot-done   { background: #00e676; }
.dot-idle   { background: #2a2a4a; }

@keyframes pulse {
    0%,100% { opacity:1; } 50% { opacity:0.3; }
}
</style>
""", unsafe_allow_html=True)

# ── imports after page config ─────────────────────────────────────────────────
from agents.orchestrator import MCPController
from agents.classifier  import InputClassificationAgent
from agents.image_proc  import ImageProcessingAgent
from agents.retrieval   import TextRetrievalAgent
from agents.fusion      import MultimodalFusionAgent
from agents.answer_gen  import AnswerGenerationAgent
from utils.helpers      import format_sources

# ── session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("history",        []),
    ("pipeline_state", {}),
    ("session_stats",  {"queries": 0, "images": 0, "chunks": 0}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="main-title">MQA</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">MultiModal QA Agent</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### 🔑 Configuration")
    api_key = st.text_input("OpenAI API Key", type="password",
                            value=os.environ.get("OPENAI_API_KEY", ""),
                            placeholder="sk-...")
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    use_local_model = st.checkbox(
        "Use local model (no OpenAI key required)",
        value=True,
        help="Use an open-source local model for answer generation. Only enable OpenAI when you want to use your API key."
    )
    if use_local_model:
        st.info("Local model mode selected. No OpenAI API key is required.")

    use_ocr = st.toggle("Enable OCR", value=True)
    use_rag  = st.toggle("Enable RAG", value=True)
    model    = st.selectbox("Vision Model", ["gpt-4o", "gpt-4-turbo", "gpt-4-vision-preview"])

    st.markdown("---")
    st.markdown("#### 🔄 Agent Pipeline")
    pipeline_steps = [
        ("MCP Controller",      "mcp"),
        ("Input Classifier",    "classify"),
        ("Image Processor",     "image"),
        ("Text Retrieval",      "retrieval"),
        ("Fusion Agent",        "fusion"),
        ("Answer Generation",   "answer"),
    ]
    ps = st.session_state.pipeline_state
    for label, key in pipeline_steps:
        state  = ps.get(key, "idle")
        dot_cls = {"active": "dot-active", "done": "dot-done"}.get(state, "dot-idle")
        step_cls = {"active": "active", "done": "done"}.get(state, "")
        st.markdown(
            f'<div class="pipeline-step {step_cls}">'
            f'<span class="status-dot {dot_cls}"></span>{label}'
            f'</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📊 Session Stats")
    c1, c2, c3 = st.columns(3)
    stats = st.session_state.session_stats
    for col, val, lbl in [(c1, stats["queries"], "Queries"),
                          (c2, stats["images"],  "Images"),
                          (c3, stats["chunks"],  "Chunks")]:
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-value">{val}</div>'
                f'<div class="metric-label">{lbl}</div>'
                f'</div>', unsafe_allow_html=True)

    if st.button("🗑 Clear History"):
        st.session_state.history = []
        st.rerun()

# ── main area ─────────────────────────────────────────────────────────────────
st.markdown('<h1 class="main-title">MultiModalQA-Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Multi-Agent · MCP · RAG · Vision · OCR</p>', unsafe_allow_html=True)
st.markdown("---")

col_chat, col_upload = st.columns([3, 2], gap="large")

# ── upload panel ──────────────────────────────────────────────────────────────
with col_upload:
    st.markdown("#### 📎 Upload Context")
    uploaded_images = st.file_uploader(
        "Images / Screenshots / Diagrams",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    uploaded_docs = st.file_uploader(
        "Text Documents",
        type=["txt", "pdf", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_images:
        st.markdown(f"**{len(uploaded_images)} image(s) ready**")
        for img_file in uploaded_images[:3]:
            img = Image.open(img_file)
            st.image(img, caption=img_file.name, use_container_width=True)
        st.session_state.session_stats["images"] = len(uploaded_images)

    if uploaded_docs:
        st.markdown("**Documents:**")
        for d in uploaded_docs:
            st.markdown(f'<span class="tag">📄 {d.name}</span>', unsafe_allow_html=True)

# ── chat panel ────────────────────────────────────────────────────────────────
with col_chat:
    st.markdown("#### 💬 Ask a Question")

    # history display
    chat_container = st.container()
    with chat_container:
        for turn in st.session_state.history:
            st.markdown(
                f'<div class="chat-label">YOU</div>'
                f'<div class="chat-user">{turn["question"]}</div>',
                unsafe_allow_html=True)
            st.markdown(
                f'<div class="chat-label">AGENT</div>'
                f'<div class="chat-agent">{turn["answer"]}</div>',
                unsafe_allow_html=True)
            if turn.get("ocr_text"):
                with st.expander("🔍 OCR Extracted Text"):
                    st.markdown(f'<div class="ocr-box">{turn["ocr_text"]}</div>',
                                unsafe_allow_html=True)
            if turn.get("sources"):
                with st.expander("📚 Retrieved Sources"):
                    st.markdown(turn["sources"])
            st.markdown("---")

    # input
    question = st.text_area("Your question", placeholder="Ask anything about the uploaded content…",
                            height=90, label_visibility="collapsed")
    run_btn  = st.button("▶  Run Agent Pipeline", use_container_width=True)

    if run_btn:
        if not question.strip():
            st.warning("Please enter a question.")
        elif not use_local_model and not api_key:
            st.error("Add your OpenAI API key in the sidebar, or enable local model mode.")
        else:
            # ── pipeline execution ────────────────────────────────────────────
            def set_state(key, state):
                st.session_state.pipeline_state[key] = state

            with st.spinner(""):
                progress_placeholder = st.empty()

                try:
                    # 1 MCP Controller
                    set_state("mcp", "active"); time.sleep(0.3)
                    controller = MCPController(model=model, use_ocr=use_ocr, use_rag=use_rag)
                    set_state("mcp", "done")

                    # 2 Classify
                    set_state("classify", "active"); time.sleep(0.2)
                    classifier   = InputClassificationAgent()
                    input_type   = classifier.classify(question, uploaded_images, uploaded_docs)
                    set_state("classify", "done")

                    # 3 Image processing
                    ocr_text     = ""
                    image_context= ""
                    set_state("image", "active")
                    if uploaded_images and input_type in ("image", "multimodal"):
                        img_agent    = ImageProcessingAgent(api_key=api_key, model=model)
                        img_results  = img_agent.process(uploaded_images, question)
                        image_context= img_results.get("description", "")
                        ocr_text     = img_results.get("ocr_text", "")
                    set_state("image", "done")

                    # 4 Retrieval
                    set_state("retrieval", "active"); time.sleep(0.2)
                    ret_agent    = TextRetrievalAgent()
                    doc_context  = ret_agent.retrieve(question, uploaded_docs, ocr_text)
                    chunks       = ret_agent.last_chunks
                    st.session_state.session_stats["chunks"] += len(chunks)
                    set_state("retrieval", "done")

                    # 5 Fusion
                    set_state("fusion", "active"); time.sleep(0.2)
                    fusion_agent = MultimodalFusionAgent()
                    fused        = fusion_agent.fuse(question, image_context, doc_context, ocr_text)
                    set_state("fusion", "done")

                    # 6 Answer
                    set_state("answer", "active")
                    gen_agent    = AnswerGenerationAgent(
                        api_key=api_key,
                        model=model,
                        use_local=use_local_model,
                    )
                    answer       = gen_agent.generate(question, fused, input_type)
                    set_state("answer", "done")

                    sources_md   = format_sources(chunks)
                    st.session_state.history.append({
                        "question": question,
                        "answer":   answer,
                        "ocr_text": ocr_text,
                        "sources":  sources_md,
                    })
                    st.session_state.session_stats["queries"] += 1

                except Exception as e:
                    st.error(f"Pipeline error: {e}")
                    import traceback; st.code(traceback.format_exc())

            st.rerun()
