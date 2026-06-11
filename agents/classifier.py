"""
Input Classification Agent
Determines whether a query is text-only, image-only, or multimodal.
"""

from typing import List, Optional


class InputClassificationAgent:
    """Classifies the modality of the user's input."""

    def classify(
        self,
        question: str,
        images: Optional[List] = None,
        docs:   Optional[List] = None,
    ) -> str:
        """
        Returns one of: 'text', 'image', 'multimodal'
        """
        has_images = bool(images)
        has_docs   = bool(docs) or bool(question.strip())

        if has_images and has_docs:
            return "multimodal"
        if has_images:
            return "image"
        return "text"

    def describe(self, modality: str) -> str:
        descriptions = {
            "text":       "Text-only query — activating RAG retrieval pipeline.",
            "image":      "Image-only query — activating vision + OCR pipeline.",
            "multimodal": "Multimodal query — activating full pipeline (vision + RAG + OCR).",
        }
        return descriptions.get(modality, "Unknown modality.")
