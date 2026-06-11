"""
Image Processing Agent
Handles OCR extraction and visual understanding via GPT-4 Vision.
Falls back gracefully when the API key is absent or a call fails.
"""

import base64
import io
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def _to_base64(file_obj) -> str:
    file_obj.seek(0)
    return base64.b64encode(file_obj.read()).decode("utf-8")


def _mime_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    return {"jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "webp": "image/webp"}.get(ext, "image/png")


class ImageProcessingAgent:
    """
    Processes uploaded images using:
      1. GPT-4o Vision  → rich textual description
      2. pytesseract    → OCR text extraction (optional, local)
    """

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model   = model

    # ── public ────────────────────────────────────────────────────────────────
    def process(self, image_files: List[Any], question: str) -> Dict[str, str]:
        description = self._vision_describe(image_files, question)
        ocr_text    = self._ocr_extract(image_files)
        return {"description": description, "ocr_text": ocr_text}

    # ── vision ────────────────────────────────────────────────────────────────
    def _vision_describe(self, image_files: List[Any], question: str) -> str:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            content = [{
                "type": "text",
                "text": (
                    f"You are a multimodal AI assistant. The user asks: '{question}'\n\n"
                    "Carefully analyse the provided image(s). Describe:\n"
                    "1. All visible text, labels, and annotations.\n"
                    "2. Diagrams, flowcharts, or structural elements.\n"
                    "3. Key visual concepts relevant to the question.\n"
                    "Be thorough and structured."
                ),
            }]

            for img in image_files:
                b64  = _to_base64(img)
                mime = _mime_type(img.name)
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "high"},
                })

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                max_tokens=1200,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.warning(f"[ImageAgent] Vision API failed: {e}")
            return f"[Vision analysis unavailable: {e}]"

    # ── OCR ───────────────────────────────────────────────────────────────────
    def _ocr_extract(self, image_files: List[Any]) -> str:
        texts = []
        try:
            import pytesseract
            from PIL import Image as PILImage

            for img_file in image_files:
                try:
                    img_file.seek(0)
                    pil_img = PILImage.open(img_file).convert("RGB")
                    text    = pytesseract.image_to_string(pil_img)
                    if text.strip():
                        texts.append(f"[{img_file.name}]\n{text.strip()}")
                except Exception as inner:
                    logger.warning(f"[OCR] {img_file.name}: {inner}")

        except ImportError:
            logger.info("[OCR] pytesseract not installed — skipping OCR.")

        return "\n\n".join(texts) if texts else ""
