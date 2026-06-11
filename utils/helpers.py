"""Utility helpers for the MultiModalQA-Agent."""

from typing import List, Dict


def format_sources(chunks: List[Dict[str, str]]) -> str:
    if not chunks:
        return ""
    lines = []
    for i, chunk in enumerate(chunks, 1):
        preview = chunk["text"][:180].replace("\n", " ")
        lines.append(f"**[{i}]** `{chunk.get('source', 'chunk')}` — {preview}…")
    return "\n\n".join(lines)
