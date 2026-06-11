# MultiModalQA-Agent

A Multimodal Multi-Agent Question Answering System for Text and Images using MCP.
Powered by **OpenAI (GPT-4o)** + **FAISS & SBERT (all-MiniLM-L6-v2)** + **Tesseract OCR** — supports local CPU offline inference.

## Setup

### 1. Get an OpenAI API key (Optional)
- Go to https://platform.openai.com
- Sign up, set up billing, and go to API Keys → Create new secret key
- Copy the key (starts with `sk-`)
- *Note: If you do not have an API key, you can run the agent completely free offline using the built-in local `flan-t5-small` model!*

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

*For OCR support (optional):*
* **macOS**: `brew install tesseract`
* **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`

### 3. Run the app
```bash
streamlit run app.py --server.port 8504
```

### 4. Open in browser
Go to **http://localhost:8504**

Configure your API key (or check **Use Local Model**), upload your documents or images in the right-hand panel, type your question, and click **Run Agent Pipeline**.

---

## Project Structure

```
MultiModalQA-Agent/
├── app.py                          # Main Streamlit UI dashboard
├── api_server.py                   # FastAPI backend exposing the pipeline to the web
├── requirements.txt                # Python package dependencies
├── paper.tex                       # IEEE Conference Paper LaTeX source
├── sample_context.txt              # Sample geography/astronomy test contexts
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py             # MCP Controller (coordinates tools & state)
│   ├── classifier.py               # Input Classifier (determines text/image/multimodal)
│   ├── image_proc.py               # Image Processor (handles OCR & visual description)
│   ├── retrieval.py                # Text Retrieval Agent (FAISS + sentence-transformers)
│   ├── fusion.py                   # Multimodal Fusion Agent (synthesizes context data)
│   └── answer_gen.py               # Answer Generation Agent (generates explainable response)
└── utils/
    ├── __init__.py
    └── helpers.py                  # Format sources and display helpers
```

---

## Pipeline Steps

1. **MCP Controller** — Coordinates tool activation, agent task routing, and global workflow state via Model Context Protocol.
2. **Input Classifier Agent** — Detects input modality (text-only, image-only, or multimodal) to optimize the active agent path.
3. **Image Processing Agent** — Conducts visual layout understanding via GPT-4 Vision and local Tesseract OCR text extraction.
4. **Text Retrieval Agent** — Executes semantic document search using FAISS vector indexing and SBERT embeddings.
5. **Multimodal Fusion Agent** — Aligns and merges visual metadata, OCR extractions, and document chunks into a unified schema.
6. **Answer Generation Agent** — Produces grounded, explainable responses with source citations (supports OpenAI GPT-4o and offline T5 fallback).
