"""
Text Retrieval Agent
Implements Retrieval-Augmented Generation (RAG) using:
  - SentenceTransformers for embeddings
  - FAISS for vector similarity search
Falls back to keyword search when dependencies are missing.
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TextRetrievalAgent:
    """Retrieves relevant text chunks from uploaded documents and OCR output."""

    CHUNK_SIZE = 400   # characters per chunk
    OVERLAP    = 80
    TOP_K      = 4

    def __init__(self):
        self.last_chunks: List[Dict[str, str]] = []
        self._index  = None
        self._chunks: List[str] = []
        self._model  = None
        self._ready  = False
        self._try_init()

    def _try_init(self):
        try:
            from sentence_transformers import SentenceTransformer
            import faiss, numpy as np
            self._SentenceTransformer = SentenceTransformer
            self._faiss = faiss
            self._np    = np
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            self._ready = True
            logger.info("[Retrieval] FAISS + SentenceTransformers ready.")
        except ImportError as e:
            logger.warning(f"[Retrieval] Falling back to keyword search: {e}")

    # ── public ────────────────────────────────────────────────────────────────
    def retrieve(
        self,
        query:    str,
        doc_files: Optional[List[Any]] = None,
        ocr_text:  str = "",
    ) -> str:
        raw_texts = self._load_texts(doc_files, ocr_text)
        if not raw_texts:
            return ""

        self._chunks = self._chunk(raw_texts)
        if not self._chunks:
            return ""

        if self._ready:
            results = self._faiss_search(query)
        else:
            results = self._keyword_search(query)

        self.last_chunks = results
        return "\n\n---\n\n".join(r["text"] for r in results)

    # ── loading ───────────────────────────────────────────────────────────────
    def _load_texts(self, doc_files, ocr_text: str) -> str:
        parts = []
        if ocr_text:
            parts.append(ocr_text)
        if doc_files:
            for f in doc_files:
                try:
                    f.seek(0)
                    raw = f.read()
                    if isinstance(raw, bytes):
                        text = raw.decode("utf-8", errors="ignore")
                    else:
                        text = raw
                    parts.append(f"[Source: {f.name}]\n{text}")
                except Exception as e:
                    logger.warning(f"[Retrieval] Could not read {f.name}: {e}")
        return "\n\n".join(parts)

    # ── chunking ──────────────────────────────────────────────────────────────
    def _chunk(self, text: str) -> List[str]:
        chunks, start = [], 0
        while start < len(text):
            end = start + self.CHUNK_SIZE
            chunks.append(text[start:end].strip())
            start = end - self.OVERLAP
        return [c for c in chunks if len(c) > 30]

    # ── FAISS search ──────────────────────────────────────────────────────────
    def _faiss_search(self, query: str) -> List[Dict[str, str]]:
        np = self._np; faiss = self._faiss
        embeddings = self._model.encode(self._chunks, convert_to_numpy=True)
        dim   = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings.astype("float32"))
        q_emb = self._model.encode([query], convert_to_numpy=True).astype("float32")
        k     = min(self.TOP_K, len(self._chunks))
        _, ids = index.search(q_emb, k)
        return [{"text": self._chunks[i], "source": f"chunk_{i}"} for i in ids[0] if i >= 0]

    # ── keyword fallback ──────────────────────────────────────────────────────
    def _keyword_search(self, query: str) -> List[Dict[str, str]]:
        words  = set(re.findall(r"\w+", query.lower()))
        scored = []
        for i, chunk in enumerate(self._chunks):
            chunk_words = set(re.findall(r"\w+", chunk.lower()))
            score = len(words & chunk_words)
            if score:
                scored.append((score, i, chunk))
        scored.sort(reverse=True)
        return [{"text": c, "source": f"chunk_{i}"} for _, i, c in scored[: self.TOP_K]]
