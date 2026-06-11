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
    initial_sidebar_state="collapsed",
)

# ── inject CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

*, html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
.stApp { background: #080808; }

/* ── HERO ── */
.hero {
    background: #080808;
    padding: 90px 72px 80px;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid #161616;
}
.hero::before {
    content: '';
    position: absolute;
    top: -200px; right: -100px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(124,106,247,0.07) 0%, transparent 65%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -150px; left: 20%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(79,195,247,0.06) 0%, transparent 65%);
    pointer-events: none;
}
.eyebrow {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #7c6af7;
    margin-bottom: 22px;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(3rem, 5.5vw, 5rem);
    font-weight: 800;
    color: #ffffff;
    line-height: 1.03;
    letter-spacing: -0.03em;
    margin-bottom: 24px;
}
.hero-title em { color: #4fc3f7; font-style: normal; }
.hero-desc {
    font-size: 1.05rem;
    color: #a0a0ab;
    max-width: 580px;
    line-height: 1.75;
    margin-bottom: 40px;
    font-weight: 300;
}
.tags { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 50px; }
.tag {
    background: #111;
    border: 1px solid #1e1e1e;
    color: #8888aa;
    font-size: 0.75rem;
    padding: 5px 13px;
    border-radius: 100px;
    font-family: 'DM Sans', sans-serif;
}

/* ── FEATURES ── */
.features {
    background: #080808;
    padding: 80px 72px;
    border-bottom: 1px solid #111;
}
.feat-label {
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #7c6af7;
    margin-bottom: 14px;
}
.feat-heading {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 48px;
    letter-spacing: -0.02em;
}
.feat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 16px;
}
.feat-card {
    background: #0d0d0d;
    border: 1px solid #161616;
    border-radius: 14px;
    padding: 28px 22px;
    transition: border-color 0.2s, transform 0.2s;
}
.feat-card:hover { border-color: #7c6af7; transform: translateY(-2px); }
.feat-n {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #222233;
    margin-bottom: 14px;
}
.feat-t {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.92rem;
    color: #e0e0e0;
    margin-bottom: 8px;
}
.feat-d { font-size: 0.81rem; color: #8e8e93; line-height: 1.65; }

/* ── TOOL PAGE ── */
.tool-page { background: #080808; min-height: 100vh; padding: 52px 72px 80px; }
.tool-heading {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.025em;
    margin-bottom: 6px;
}
.tool-sub { font-size: 0.88rem; color: #666; margin-bottom: 36px; }

/* ── Config bar ── */
.cfg {
    background: #0d0d0d;
    border: 1px solid #161616;
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 32px;
}
.cfg-label {
    font-size: 0.67rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #8888aa;
    margin-bottom: 6px;
}

/* ── Inputs ── */
.input-lbl {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #ccc;
    margin-bottom: 10px;
}
.stTextArea textarea {
    background: #0d0d0d !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 12px !important;
    color: #ddd !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.87rem !important;
    padding: 14px !important;
    transition: border-color 0.2s !important;
}
.stTextArea textarea:focus { border-color: #7c6af7 !important; outline: none !important; }
.stTextInput input {
    background: #0d0d0d !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 10px !important;
    color: #ddd !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
}
.stSelectbox > div > div {
    background: #0d0d0d !important;
    border: 1px solid #1a1a1a !important;
    border-radius: 10px !important;
    color: #ddd !important;
}
.stCheckbox > label > span {
    color: #aaa !important;
    font-size: 0.85rem !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c6af7, #4fc3f7) !important;
    color: #000000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 13px 28px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ── Step header ── */
.sh { display: flex; align-items: flex-start; gap: 14px; margin-bottom: 22px; margin-top: 36px; }
.sn {
    background: #7c6af7;
    color: #000;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 0.78rem;
    min-width: 30px; height: 30px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-top: 2px;
}
.st-title { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1.1rem; color: #e0e0e0; }
.st-desc { font-size: 0.8rem; color: #8888aa; margin-top: 2px; }

/* ── Status boxes / Console logs ── */
.alog {
    background: #0a0a0a;
    border: 1px solid #141414;
    border-left: 3px solid #7c6af7;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-family: 'DM Sans', monospace;
    font-size: 0.8rem;
    color: #a0a0ab;
    margin: 5px 0;
}

/* ── Result display ── */
.chat-box {
    background: #0d0d0d;
    border: 1px solid #161616;
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 20px;
}

.chat-user {
    background: #111122;
    border: 1px solid #1e1e33;
    border-radius: 12px 12px 4px 12px;
    padding: 14px 18px;
    margin: 10px 0;
    max-width: 85%;
    margin-left: auto;
    color: #e0e0f0;
    font-size: 0.95rem;
}

.chat-agent {
    background: #0b0f19;
    border: 1px solid #121e30;
    border-radius: 4px 12px 12px 12px;
    padding: 18px 22px;
    margin: 10px 0;
    color: #e0f0ff;
    font-size: 0.98rem;
    line-height: 1.75;
}

.chat-lbl {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #7c6af7;
    margin-bottom: 4px;
}

.ocr-box {
    background: #06060c;
    border: 1px solid #121225;
    border-radius: 10px;
    padding: 16px;
    font-family: 'DM Sans', monospace;
    font-size: 0.85rem;
    color: #a0a0ab;
    line-height: 1.6;
    max-height: 300px;
    overflow-y: auto;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 2px; border-bottom: 1px solid #141414; background: transparent; }
.stTabs [data-baseweb="tab"] { font-family: 'Syne', sans-serif !important; font-weight: 600 !important; font-size: 0.83rem !important; color: #666 !important; padding: 10px 20px !important; background: transparent !important; }
.stTabs [aria-selected="true"] { color: #e0e0e0 !important; border-bottom: 2px solid #7c6af7 !important; }

/* ── Expander ── */
.streamlit-expanderHeader { background: #0d0d0d !important; border: 1px solid #161616 !important; border-radius: 10px !important; color: #e0e0e0 !important; font-size: 0.83rem !important; }
.stSlider [data-testid="stSlider"] { color: #7c6af7; }

/* Divider */
.div { height: 1px; background: #161616; margin: 36px 0; }
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
    ("page",           "landing"),
    ("history",        []),
    ("pipeline_state", {}),
    ("session_stats",  {"queries": 0, "images": 0, "chunks": 0}),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ═════════════════════════════════════════════════════════════════════════════
# LANDING PAGE
# ═════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">✦ IEEE Conference Paper Project — WMU Warsaw</div>
        <div class="hero-title">MultiModalQA-Agent<br><em>fully agentic.</em></div>
        <div class="hero-desc">
            A pipeline of 6 specialized AI agents coordinates via Model Context Protocol (MCP) to analyze text documents and images, generating grounded, explainable answers.
        </div>
        <div class="tags">
            <span class="tag">🤖 MCP Orchestration</span>
            <span class="tag">🖼 Vision Understanding</span>
            <span class="tag">🔍 Tesseract OCR</span>
            <span class="tag">📚 FAISS Semantic Retrieval (RAG)</span>
            <span class="tag">🔄 Multimodal Fusion</span>
            <span class="tag">💡 Grounded Answers</span>
        </div>
    </div>
    <div class="features">
        <div class="feat-label">✦ Pipeline Architecture</div>
        <div class="feat-heading">Six agents.<br>One unified schema.</div>
        <div class="feat-grid">
            <div class="feat-card"><div class="feat-n">01</div><div class="feat-t">MCP Controller</div><div class="feat-d">Coordinates tools, routes tasks to appropriate agents, and maintains global state using the Model Context Protocol.</div></div>
            <div class="feat-card"><div class="feat-n">02</div><div class="feat-t">Input Classifier</div><div class="feat-d">Analyzes your question and uploaded contexts to determine the modality (text, image, or multimodal) for optimized routing.</div></div>
            <div class="feat-card"><div class="feat-n">03</div><div class="feat-t">Image Processor</div><div class="feat-d">Performs layout understanding via GPT-4 Vision and extracts text using Tesseract OCR from screenshots or diagrams.</div></div>
            <div class="feat-card"><div class="feat-n">04</div><div class="feat-t">Text Retrieval</div><div class="feat-d">Performs fast semantic vector search over uploaded documents using FAISS and SentenceTransformers embeddings.</div></div>
        </div>
        <div class="feat-grid">
            <div class="feat-card"><div class="feat-n">05</div><div class="feat-t">Multimodal Fusion</div><div class="feat-d">Harmonizes OCR texts, image descriptions, and retrieved document chunks into a unified context representation.</div></div>
            <div class="feat-card"><div class="feat-n">06</div><div class="feat-t">Answer Generation</div><div class="feat-d">Generates factual, grounded answers using GPT-4o or fallbacks to a local offline FLAN-T5 model on your computer.</div></div>
            <div class="feat-card"><div class="feat-n">07</div><div class="feat-t">Source Citations</div><div class="feat-d">Explicitly cites which modalities and documents informed each part of the answer in a "Sources Used" summary.</div></div>
            <div class="feat-card"><div class="feat-n">08</div><div class="feat-t">FastAPI Web API</div><div class="feat-d">Exposes the multi-agent pipeline through a lightweight backend for integration with public web interfaces.</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        if st.button("✦ Launch MultiModalQA-Agent", use_container_width=True):
            st.session_state.page = "tool"
            st.rerun()

    st.markdown("<div style='height:48px'></div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# TOOL PAGE
# ═════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="tool-page">', unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("← Home"):
            st.session_state.page = "landing"
            st.rerun()
    with col_nav2:
        if st.button("🗑 Clear Chat History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.markdown('<div class="tool-heading">MultiModalQA-Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="tool-sub">Provide text or image contexts, type your question, and execute the agent pipeline.</div>', unsafe_allow_html=True)

    # Config bar in the main page
    st.markdown('<div class="cfg">', unsafe_allow_html=True)
    cc1, cc2, cc3, cc4 = st.columns([2, 1, 1, 1])
    with cc1:
        st.markdown('<div class="cfg-label">OpenAI API Key</div>', unsafe_allow_html=True)
        api_key_input = st.text_input("api_key", type="password",
                                     value=os.environ.get("OPENAI_API_KEY", ""),
                                     placeholder="sk-...", label_visibility="collapsed")
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            api_key = api_key_input
        else:
            api_key = ""
    with cc2:
        st.markdown('<div class="cfg-label">Vision Model</div>', unsafe_allow_html=True)
        model_choice = st.selectbox("model", ["gpt-4o", "gpt-4-turbo", "gpt-4-vision-preview"], label_visibility="collapsed")
    with cc3:
        st.markdown('<div class="cfg-label">Inference Mode</div>', unsafe_allow_html=True)
        use_local_model_chk = st.checkbox("Use Local Model", value=True)
    with cc4:
        st.markdown('<div class="cfg-label">Enabled Components</div>', unsafe_allow_html=True)
        use_ocr = st.checkbox("OCR Extraction", value=True)
        use_rag = st.checkbox("RAG Retrieval", value=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Inputs Layout
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown('<div class="input-lbl">🖼 Image Contexts</div>', unsafe_allow_html=True)
        uploaded_images = st.file_uploader(
            "Images / Screenshots / Diagrams",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_images:
            st.markdown(f"**{len(uploaded_images)} image(s) loaded**")
            for img_file in uploaded_images[:2]: # preview up to 2
                img = Image.open(img_file)
                st.image(img, caption=img_file.name, use_container_width=True)
            st.session_state.session_stats["images"] = len(uploaded_images)

    with col2:
        st.markdown('<div class="input-lbl">📚 Document Contexts</div>', unsafe_allow_html=True)
        uploaded_docs = st.file_uploader(
            "Text Documents",
            type=["txt", "pdf", "md"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if uploaded_docs:
            st.markdown(f"**{len(uploaded_docs)} document(s) loaded**")
            for d in uploaded_docs:
                st.markdown(f'<span class="tag">📄 {d.name}</span>', unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="input-lbl">💬 Ask a Question</div>', unsafe_allow_html=True)
    question = st.text_area("Your question", placeholder="Ask anything about the uploaded content…",
                            height=100, label_visibility="collapsed")
    
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    run_btn = st.button("✦ Run Agent Pipeline", use_container_width=True)

    if run_btn:
        if not question.strip():
            st.error("Please enter a question.")
        elif not use_local_model_chk and not api_key:
            st.error("Please add your OpenAI API key in the configuration bar, or check 'Use Local Model'.")
        else:
            # Running the pipeline steps visually!
            st.markdown('<div class="div"></div>', unsafe_allow_html=True)
            
            # Step 1
            st.markdown('<div class="sh"><div class="sn">1</div><div><div class="st-title">MCP Controller</div><div class="st-desc">Establishing Model Context Protocol state and tool availability</div></div></div>', unsafe_allow_html=True)
            try:
                controller = MCPController(model=model_choice, use_ocr=use_ocr, use_rag=use_rag)
                st.markdown('<div class="alog">✓ Controller initialized successfully</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Controller initialization failed: {e}")
                st.stop()

            st.markdown('<div class="div"></div>', unsafe_allow_html=True)

            # Step 2
            st.markdown('<div class="sh"><div class="sn">2</div><div><div class="st-title">Input Classifier Agent</div><div class="st-desc">Analyzing question modality and context files</div></div></div>', unsafe_allow_html=True)
            try:
                classifier = InputClassificationAgent()
                input_type = classifier.classify(question, uploaded_images, uploaded_docs)
                st.markdown(f'<div class="alog">✓ Modality classified as: <b>{input_type.upper()}</b></div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Classification failed: {e}")
                st.stop()

            st.markdown('<div class="div"></div>', unsafe_allow_html=True)

            # Step 3
            st.markdown('<div class="sh"><div class="sn">3</div><div><div class="st-title">Image Processing Agent</div><div class="st-desc">Performing visual description and layout OCR</div></div></div>', unsafe_allow_html=True)
            ocr_text = ""
            image_context = ""
            try:
                if uploaded_images and input_type in ("image", "multimodal"):
                    img_agent = ImageProcessingAgent(api_key=api_key, model=model_choice)
                    with st.spinner("Processing images..."):
                        img_results = img_agent.process(uploaded_images, question)
                    image_context = img_results.get("description", "")
                    ocr_text = img_results.get("ocr_text", "")
                    st.markdown(f'<div class="alog">✓ Visual description generated ({len(image_context)} chars)</div>', unsafe_allow_html=True)
                    if ocr_text:
                        st.markdown(f'<div class="alog">✓ OCR extracted: {len(ocr_text)} characters of text</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alog">✦ Skipped: No images uploaded or classified for vision processing</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Image processing failed: {e}")
                st.stop()

            st.markdown('<div class="div"></div>', unsafe_allow_html=True)

            # Step 4
            st.markdown('<div class="sh"><div class="sn">4</div><div><div class="st-title">Text Retrieval Agent</div><div class="st-desc">Searching and indexing document text chunks semantically</div></div></div>', unsafe_allow_html=True)
            doc_context = ""
            chunks = []
            try:
                if uploaded_docs and use_rag:
                    ret_agent = TextRetrievalAgent()
                    with st.spinner("Retrieving document context..."):
                        doc_context = ret_agent.retrieve(question, uploaded_docs, ocr_text)
                    chunks = ret_agent.last_chunks
                    st.session_state.session_stats["chunks"] += len(chunks)
                    st.markdown(f'<div class="alog">✓ RAG completed: Retrieved {len(chunks)} relevant document chunks</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alog">✦ Skipped: No documents uploaded or RAG disabled</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Text retrieval failed: {e}")
                st.stop()

            st.markdown('<div class="div"></div>', unsafe_allow_html=True)

            # Step 5
            st.markdown('<div class="sh"><div class="sn">5</div><div><div class="st-title">Multimodal Fusion Agent</div><div class="st-desc">Aligning and merging vision, OCR, and document signals</div></div></div>', unsafe_allow_html=True)
            fused = ""
            try:
                fusion_agent = MultimodalFusionAgent()
                fused = fusion_agent.fuse(question, image_context, doc_context, ocr_text)
                st.markdown('<div class="alog">✓ Fused multimodal context synthesized successfully</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Fusion failed: {e}")
                st.stop()

            st.markdown('<div class="div"></div>', unsafe_allow_html=True)

            # Step 6
            st.markdown('<div class="sh"><div class="sn">6</div><div><div class="st-title">Answer Generation Agent</div><div class="st-desc">Generating factual answer grounded on fused data</div></div></div>', unsafe_allow_html=True)
            try:
                gen_agent = AnswerGenerationAgent(
                    api_key=api_key,
                    model=model_choice,
                    use_local=use_local_model_chk,
                )
                with st.spinner("Generating answer..."):
                    answer = gen_agent.generate(question, fused, input_type)
                st.markdown('<div class="alog">✓ Grounded answer generated successfully</div>', unsafe_allow_html=True)
                
                sources_md = format_sources(chunks)
                st.session_state.history.append({
                    "question": question,
                    "answer": answer,
                    "ocr_text": ocr_text,
                    "sources": sources_md,
                })
                st.session_state.session_stats["queries"] += 1
            except Exception as e:
                st.error(f"Answer generation failed: {e}")
                st.stop()

            st.markdown('<div class="div"></div>', unsafe_allow_html=True)
            st.rerun()

    # Conversation history display below
    if st.session_state.history:
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="tool-heading" style="font-size:1.5rem;">Pipeline Output & Results</div>', unsafe_allow_html=True)
        
        # Display the most recent result first
        for idx, turn in enumerate(reversed(st.session_state.history)):
            st.markdown(f"""
            <div class="chat-box">
                <div class="chat-lbl">YOU</div>
                <div class="chat-user">{turn["question"]}</div>
                <div class="chat-lbl">AGENT</div>
                <div class="chat-agent">{turn["answer"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            tab_ctx, tab_src = st.tabs([f"🔍 Extracted Context #{len(st.session_state.history)-idx}", f"📚 Sources #{len(st.session_state.history)-idx}"])
            with tab_ctx:
                if turn.get("ocr_text"):
                    st.markdown("**OCR Extracted Text:**")
                    st.markdown(f'<div class="ocr-box">{turn["ocr_text"]}</div>', unsafe_allow_html=True)
                else:
                    st.caption("No image OCR text extracted for this query.")
            with tab_src:
                if turn.get("sources"):
                    st.markdown(turn["sources"])
                else:
                    st.caption("No semantic RAG documents cited.")
            
            st.markdown("<div class='div'></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
