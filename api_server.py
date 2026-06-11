import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional
from PIL import Image

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_server")

# Import existing agents
from agents.orchestrator import MCPController
from agents.classifier  import InputClassificationAgent
from agents.image_proc  import ImageProcessingAgent
from agents.retrieval   import TextRetrievalAgent
from agents.fusion      import MultimodalFusionAgent
from agents.answer_gen  import AnswerGenerationAgent
from utils.helpers      import format_sources

app = FastAPI(title="MultiModalQA-Agent API Server")

# Allow CORS for static frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check():
    return {"status": "ok"}

UPLOAD_DIR = Path("uploads_temp")
UPLOAD_DIR.mkdir(exist_ok=True)

class MockStreamlitFile:
    """Mock file class that mimics Streamlit's UploadedFile behavior for the agents."""
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.name = filepath.name
        self.cursor = 0

    def seek(self, pos: int):
        self.cursor = pos

    def read(self) -> bytes:
        with open(self.filepath, "rb") as f:
            f.seek(self.cursor)
            return f.read()

@app.post("/query")
async def handle_query(
    question: str = Form(...),
    use_local_model: bool = Form(True),
    api_key: str = Form(""),
    use_ocr: bool = Form(True),
    use_rag: bool = Form(True),
    model: str = Form("gpt-4o"),
    files: Optional[List[UploadFile]] = File(None)
):
    # Clear previous uploads temp files to save space
    for f in UPLOAD_DIR.glob("*"):
        try:
            if f.is_file():
                f.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete temp file {f.name}: {e}")

    uploaded_images = []
    uploaded_docs = []

    # Save incoming files to temp directory
    if files:
        for file in files:
            if not file.filename:
                continue
            ext = Path(file.filename).suffix.lower()
            temp_path = UPLOAD_DIR / file.filename
            
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create a mock streamlit file wrapper
            mock_file = MockStreamlitFile(temp_path)
            
            if ext in (".png", ".jpg", ".jpeg", ".webp"):
                uploaded_images.append(mock_file)
            elif ext in (".txt", ".pdf", ".md"):
                uploaded_docs.append(mock_file)

    try:
        # 1. MCP Controller
        controller = MCPController(model=model, use_ocr=use_ocr, use_rag=use_rag)

        # 2. Input Classification Agent
        classifier = InputClassificationAgent()
        input_type = classifier.classify(question, uploaded_images, uploaded_docs)

        # 3. Image Processing Agent
        ocr_text = ""
        image_context = ""
        if uploaded_images and input_type in ("image", "multimodal"):
            img_agent = ImageProcessingAgent(api_key=api_key, model=model)
            img_results = img_agent.process(uploaded_images, question)
            image_context = img_results.get("description", "")
            ocr_text = img_results.get("ocr_text", "")

        # 4. Text Retrieval Agent
        doc_context = ""
        chunks = []
        if use_rag:
            ret_agent = TextRetrievalAgent()
            doc_context = ret_agent.retrieve(question, uploaded_docs, ocr_text)
            chunks = ret_agent.last_chunks

        # 5. Multimodal Fusion Agent
        fusion_agent = MultimodalFusionAgent()
        fused = fusion_agent.fuse(question, image_context, doc_context, ocr_text)

        # 6. Answer Generation Agent
        gen_agent = AnswerGenerationAgent(
            api_key=api_key,
            model=model,
            use_local=use_local_model,
        )
        answer = gen_agent.generate(question, fused, input_type)
        sources_md = format_sources(chunks)

        return {
            "status": "success",
            "input_type": input_type,
            "answer": answer,
            "ocr_text": ocr_text,
            "sources": sources_md
        }

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)
