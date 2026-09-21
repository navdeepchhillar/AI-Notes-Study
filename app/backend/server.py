from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import io
import json
import PyPDF2
import docx
from google import genai

# =========================
# ENV + CLIENTS
# =========================
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not MONGO_URL:
    raise ValueError("MONGO_URL missing in .env")
if not DB_NAME:
    raise ValueError("DB_NAME missing in .env")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY missing in .env")

mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # set GEMINI_MODEL in .env to switch models
NOTES_CHAR_LIMIT = 12000
MINDMAP_CHAR_LIMIT = 8000
MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

# =========================
# APP
# =========================
app = FastAPI(title="AI Notes Study API")
api_router = APIRouter(prefix="/api")


# =========================
# MODELS
# =========================
class UploadedFile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    content_type: str
    size: int
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    extracted_text: Optional[str] = None


class CombinedNotes(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    file_ids: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MindMap(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    nodes: List[dict]
    edges: List[dict]
    file_ids: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProcessNotesRequest(BaseModel):
    file_ids: List[str]
    title: str


class GenerateMindMapRequest(BaseModel):
    file_ids: List[str]
    title: str


# =========================
# HELPERS
# =========================
def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        logging.error(f"PDF extraction error: {e}")
        return ""


def extract_text_from_docx(file_content: bytes) -> str:
    try:
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        return "\n".join([p.text for p in doc.paragraphs]).strip()
    except Exception as e:
        logging.error(f"DOCX extraction error: {e}")
        return ""


def extract_text_from_txt(file_content: bytes) -> str:
    try:
        return file_content.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        logging.error(f"TXT extraction error: {e}")
        return ""


def detect_kind(filename: Optional[str], content_type: Optional[str]) -> Optional[str]:
    """Return 'pdf' | 'docx' | 'txt' | None.

    Trusts the browser's MIME type, but falls back to the file extension when the
    browser sends a generic/empty type (common on Windows for .docx/.txt).
    """
    name = (filename or "").lower()
    ctype = (content_type or "").split(";")[0].strip().lower()
    if ctype == "application/pdf":
        return "pdf"
    if ctype == DOCX_MIME:
        return "docx"
    if ctype == "text/plain":
        return "txt"
    if ctype in ("", "application/octet-stream"):
        if name.endswith(".pdf"):
            return "pdf"
        if name.endswith(".docx"):
            return "docx"
        if name.endswith(".txt"):
            return "txt"
    return None


CANONICAL_MIME = {"pdf": "application/pdf", "docx": DOCX_MIME, "txt": "text/plain"}


def build_combined_text(files: list, limit: int) -> str:
    """Join the files' text, giving each selected file an equal share of `limit`
    so that later files are not silently cut off by earlier, longer ones."""
    usable = [f for f in files if (f.get("extracted_text") or "").strip()]
    if not usable:
        return ""
    per_file = max(limit // len(usable), 500)
    return "\n\n---\n\n".join(
        f"File: {f['filename']}\n\n{f['extracted_text'][:per_file]}" for f in usable
    )


async def generate_text(prompt: str) -> str:
    """Call Gemini without blocking the event loop; never return empty text."""
    def _call():
        return gemini_client.models.generate_content(model=GEMINI_MODEL, contents=prompt)

    response = await run_in_threadpool(_call)
    text = getattr(response, "text", None)
    if not text or not text.strip():
        raise HTTPException(
            status_code=502,
            detail="The AI returned an empty response (it may have been blocked). Please try again.",
        )
    return text


def parse_mindmap(raw: str) -> dict:
    """Extract and normalise the mind map JSON that the model returned.

    Tolerates code fences / surrounding prose, numeric ids, and source/target
    edge keys; drops edges that point at nodes that do not exist.
    """
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object found")
    data = json.loads(raw[start:end + 1])
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")

    nodes, seen = [], set()
    for i, n in enumerate(data.get("nodes") or []):
        if not isinstance(n, dict):
            continue
        node_id = str(n.get("id", i + 1))
        if node_id in seen:
            continue
        seen.add(node_id)
        level = n.get("level", 0)
        nodes.append({
            "id": node_id,
            "label": str(n.get("label") or n.get("name") or n.get("title") or node_id),
            "level": level if isinstance(level, int) else 0,
        })

    edges = []
    for e in data.get("edges") or []:
        if not isinstance(e, dict):
            continue
        a = e.get("from", e.get("source"))
        b = e.get("to", e.get("target"))
        if a is None or b is None:
            continue
        a, b = str(a), str(b)
        if a in seen and b in seen and a != b:
            edges.append({"from": a, "to": b})

    if not nodes:
        raise ValueError("mind map has no nodes")
    return {"nodes": nodes, "edges": edges}


# =========================
# ROUTES
# =========================
@api_router.get("/")
async def root():
    return {"message": "AI Study Notes API Running"}


@api_router.get("/health")
async def health():
    return {"status": "healthy"}


@api_router.post("/upload", response_model=UploadedFile)
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="File too large (max 25 MB)")

        kind = detect_kind(file.filename, file.content_type)
        if kind == "pdf":
            extracted_text = extract_text_from_pdf(content)
        elif kind == "docx":
            extracted_text = extract_text_from_docx(content)
        elif kind == "txt":
            extracted_text = extract_text_from_txt(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type (use PDF, DOCX or TXT)")

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in this file (scanned PDFs and corrupt files are not supported).",
            )

        file_obj = UploadedFile(
            filename=file.filename or "untitled",
            content_type=CANONICAL_MIME[kind],
            size=len(content),
            extracted_text=extracted_text
        )

        doc = file_obj.model_dump()
        doc["uploaded_at"] = doc["uploaded_at"].isoformat()

        await db.files.insert_one(doc)
        return file_obj

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Upload failed")


@api_router.get("/files", response_model=List[UploadedFile])
async def get_files():
    # The full extracted text is not needed to show the list, so don't ship it.
    files = await db.files.find({}, {"_id": 0, "extracted_text": 0}).to_list(1000)
    for f in files:
        if isinstance(f["uploaded_at"], str):
            f["uploaded_at"] = datetime.fromisoformat(f["uploaded_at"])
    return files


@api_router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    result = await db.files.delete_one({"id": file_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="File not found")
    return {"message": "File deleted successfully"}


@api_router.post("/process-notes", response_model=CombinedNotes)
async def process_notes(request: ProcessNotesRequest):
    try:
        files = await db.files.find(
            {"id": {"$in": request.file_ids}},
            {"_id": 0}
        ).to_list(1000)

        if not files:
            raise HTTPException(status_code=404, detail="No files found")

        combined_text = build_combined_text(files, NOTES_CHAR_LIMIT)

        if not combined_text.strip():
            raise HTTPException(status_code=400, detail="No text found")

        prompt = (
            "Create detailed, structured study notes with headings, bullets, summaries, and examples.\n\n"
            + combined_text
        )
        generated_notes = await generate_text(prompt)

        notes_obj = CombinedNotes(
            title=request.title,
            content=generated_notes,
            file_ids=request.file_ids
        )

        doc = notes_obj.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()

        await db.combined_notes.insert_one(doc)
        return notes_obj

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Process notes error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Notes generation failed: {str(e)}")


@api_router.get("/combined-notes", response_model=List[CombinedNotes])
async def get_combined_notes():
    notes = await db.combined_notes.find({}, {"_id": 0}).to_list(1000)
    for n in notes:
        if isinstance(n["created_at"], str):
            n["created_at"] = datetime.fromisoformat(n["created_at"])
    return notes


@api_router.delete("/combined-notes/{note_id}")
async def delete_combined_note(note_id: str):
    result = await db.combined_notes.delete_one({"id": note_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted successfully"}


@api_router.post("/generate-mindmap", response_model=MindMap)
async def generate_mindmap(request: GenerateMindMapRequest):
    try:
        files = await db.files.find(
            {"id": {"$in": request.file_ids}},
            {"_id": 0}
        ).to_list(1000)

        if not files:
            raise HTTPException(status_code=404, detail="No files found")

        combined_text = build_combined_text(files, MINDMAP_CHAR_LIMIT)

        if not combined_text.strip():
            raise HTTPException(status_code=400, detail="No text found")

        prompt = f"""Return ONLY valid JSON with no markdown formatting, no code blocks, no explanation.
The JSON must have this exact structure:
{{
  "nodes": [
    {{"id": "1", "label": "Main Topic", "level": 0}},
    {{"id": "2", "label": "Subtopic", "level": 1}}
  ],
  "edges": [
    {{"from": "1", "to": "2"}}
  ]
}}

Create a mind map from this material:
{combined_text}"""

        raw = await generate_text(prompt)
        try:
            mindmap_data = parse_mindmap(raw)
        except ValueError as e:  # includes json.JSONDecodeError
            logging.error(f"Mindmap parse error: {e}; raw={raw[:300]!r}")
            raise HTTPException(
                status_code=502,
                detail="The AI returned a mind map in an unexpected format. Please try again.",
            )

        mindmap_obj = MindMap(
            title=request.title,
            nodes=mindmap_data["nodes"],
            edges=mindmap_data["edges"],
            file_ids=request.file_ids
        )

        doc = mindmap_obj.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()

        await db.mindmaps.insert_one(doc)
        return mindmap_obj

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Mindmap error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Mind map generation failed: {str(e)}")


@api_router.get("/mindmaps", response_model=List[MindMap])
async def get_mindmaps():
    mindmaps = await db.mindmaps.find({}, {"_id": 0}).to_list(1000)
    for m in mindmaps:
        if isinstance(m["created_at"], str):
            m["created_at"] = datetime.fromisoformat(m["created_at"])
    return mindmaps


@api_router.delete("/mindmaps/{mindmap_id}")
async def delete_mindmap(mindmap_id: str):
    result = await db.mindmaps.delete_one({"id": mindmap_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mind map not found")
    return {"message": "Mind map deleted successfully"}


# =========================
# MIDDLEWARE
# =========================
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# =========================
# SHUTDOWN
# =========================
@app.on_event("shutdown")
async def shutdown_db_client():
    mongo_client.close()
