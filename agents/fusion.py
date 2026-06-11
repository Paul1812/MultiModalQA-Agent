"""
Multimodal Fusion Agent
Combines visual context, OCR text, and retrieved document context
into a unified representation for the Answer Generation Agent.
"""

from typing import Optional


class MultimodalFusionAgent:
    """Fuses all modality signals into a single enriched context string."""

    def fuse(
        self,
        question:      str,
        image_context: str = "",
        doc_context:   str = "",
        ocr_text:      str = "",
    ) -> str:
        sections = [f"USER QUESTION:\n{question}\n"]

        if image_context:
            sections.append(
                "VISUAL ANALYSIS (from Image Processing Agent):\n"
                + image_context
            )

        if ocr_text:
            sections.append(
                "OCR EXTRACTED TEXT (from images):\n"
                + ocr_text[:2000]   # cap to avoid token overflow
            )

        if doc_context:
            sections.append(
                "RETRIEVED DOCUMENT CONTEXT (RAG):\n"
                + doc_context[:3000]
            )

        if len(sections) == 1:
            sections.append(
                "NOTE: No additional context was retrieved. "
                "Answer from general knowledge."
            )

        return "\n\n" + ("\n\n" + "─" * 60 + "\n\n").join(sections)

    def modalities_present(
        self,
        image_context: str,
        doc_context:   str,
        ocr_text:      str,
    ) -> list:
        present = []
        if image_context: present.append("vision")
        if ocr_text:      present.append("ocr")
        if doc_context:   present.append("rag")
        return present
