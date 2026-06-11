"""
Answer Generation Agent
Produces grounded, explainable answers from the fused multimodal context.
"""

import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are MultiModalQA-Agent, an expert AI assistant specialising in multimodal question answering.

Your answers are:
1. **Grounded** — based on the provided visual, OCR, and document context.
2. **Structured** — use markdown headings and bullet points where helpful.
3. **Explainable** — briefly state *which* source (image, OCR, document) informed each part of your answer.
4. **Honest** — if the context is insufficient, say so clearly rather than hallucinating.

Always end with a short "Sources Used" section listing which modalities contributed to your answer.
"""

LOCAL_PROMPT = """You are a helpful assistant.

Answer the question directly and concisely.
Do not repeat the question back to the user.
If the answer is unknown, say that you do not know.
Use the provided context only when it is relevant.
"""


class AnswerGenerationAgent:
    def __init__(
        self,
        api_key: str = "",
        model: str = "gpt-4o",
        use_local: bool = True,
        local_model_name: str = "google/flan-t5-small",
    ):
        self.api_key = api_key
        self.model = model
        self.use_local = use_local
        self.local_model_name = local_model_name
        self._local_model = None
        self._local_tokenizer = None
        self._local_device = None

    def generate(self, question: str, fused_context: str, input_type: str) -> str:
        if self.use_local or not self.api_key:
            return self._generate_local(question, fused_context)

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": fused_context},
                ],
                max_tokens=1500,
                temperature=0.3,
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.warning(f"[AnswerGen] OpenAI API call failed: {e}")
            try:
                local_answer = self._generate_local(question, fused_context)
                return (
                    f"⚠️ OpenAI unavailable ({e}). Falling back to local model.\n\n"
                    + local_answer
                )
            except Exception as local_e:
                logger.error(f"[AnswerGen] Local fallback failed: {local_e}")
                return self._fallback_answer(question, fused_context, e)

    def _load_local_model(self):
        if self._local_model is not None:
            return

        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        import torch

        self._local_device = "cuda" if torch.cuda.is_available() else "cpu"
        self._local_tokenizer = AutoTokenizer.from_pretrained(self.local_model_name)
        self._local_model = AutoModelForSeq2SeqLM.from_pretrained(self.local_model_name)
        self._local_model.to(self._local_device)

    def _generate_local(self, question: str, fused_context: str) -> str:
        self._load_local_model()
        
        # Extract clean context from fused_context (bypassing full structure that confuses small model)
        context_parts = []
        if "─" * 60 in fused_context:
            parts = fused_context.split("─" * 60)
            for p in parts[1:]:
                clean_p = p.strip()
                if "No additional context was retrieved" not in clean_p:
                    context_parts.append(clean_p)
        
        extracted_context = "\n\n".join(context_parts).strip()
        
        if extracted_context:
            prompt = f"Answer the question based on the context.\n\nContext:\n{extracted_context}\n\nQuestion: {question}\n\nAnswer:"
        else:
            prompt = f"Answer the question directly and concisely.\n\nQuestion: {question}\n\nAnswer:"
        inputs = self._local_tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        ).to(self._local_device)
        outputs = self._local_model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.1,
        )
        return self._local_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    # ── fallback ──────────────────────────────────────────────────────────────
    def _fallback_answer(self, question: str, context: str, error: Exception) -> str:
        has_image = "VISUAL ANALYSIS" in context
        has_ocr = "OCR EXTRACTED" in context
        has_rag = "RETRIEVED DOCUMENT" in context

        parts = [
            f"⚠️ **Live API unavailable** (`{error}`). "
            "Below is a structured summary from the pipeline:\n"
        ]

        if has_image:
            parts.append("**🖼 Visual context** was captured from your uploaded image(s).")
        if has_ocr:
            parts.append("**🔍 OCR text** was extracted from the image(s).")
        if has_rag:
            parts.append("**📚 Document context** was retrieved via the RAG pipeline.")

        parts.append(
            "\nTo receive a full AI-generated answer, please add a valid OpenAI API key "
            "in the sidebar. The pipeline completed successfully — only the final LLM call failed."
        )
        return "\n\n".join(parts)
