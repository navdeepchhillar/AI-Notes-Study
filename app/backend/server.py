from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
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
from openai import OpenAI

# =========================
# ENV + CLIENTS
# =========================
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not MONGO_URL:
    raise ValueError("MONGO_URL missing in .env")
if not DB_NAME:
    raise ValueError("DB_NAME missing in .env")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY missing in .env")

mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]

openai_client = OpenAI(api_key=OPENAI_API_KEY)

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


def build_combined_text(files: list) -> str:
    return "\n\n---\n\n".join([
        f"File: {f['filename']}\n\n{f.get('extracted_text', '')}"
        for f in files if f.get("extracted_text")
    ])


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

        extracted_text = ""

        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(content)

        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            extracted_text = extract_text_from_docx(content)

        elif file.content_type == "text/plain":
            extracted_text = extract_text_from_txt(content)

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        file_obj = UploadedFile(
            filename=file.filename,
            content_type=file.content_type,
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
        logging.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@api_router.get("/files", response_model=List[UploadedFile])
async def get_files():
    files = await db.files.find({}, {"_id": 0}).to_list(1000)

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

        combined_text = build_combined_text(files)

        if not combined_text.strip():
            raise HTTPException(status_code=400, detail="No text found")

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.4,
            messages=[
                {
                    "role": "system",
                    "content": "Create detailed, structured study notes with headings, bullets, summaries, and examples."
                },
                {
                    "role": "user",
                    "content": combined_text[:12000]
                }
            ]
        )

        generated_notes = response.choices[0].message.content

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
        logging.error(f"Process notes error: {e}")
        raise HTTPException(status_code=500, detail="Notes generation failed")


@api_router.get("/combined-notes", response_model=List[CombinedNotes])
async def get_combined_notes():
    notes = await db.combined_notes.find({}, {"_id": 0}).to_list(1000)

    for n in notes:
        if isinstance(n["created_at"], str):
            n["created_at"] = datetime.fromisoformat(n["created_at"])

    return notes


@api_router.post("/generate-mindmap", response_model=MindMap)
async def generate_mindmap(request: GenerateMindMapRequest):
    try:
        files = await db.files.find(
            {"id": {"$in": request.file_ids}},
            {"_id": 0}
        ).to_list(1000)

        if not files:
            raise HTTPException(status_code=404, detail="No files found")

        combined_text = build_combined_text(files)

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "Return valid JSON for a ReactFlow mind map with nodes and edges."
                },
                {
                    "role": "user",
                    "content": f"""
Create JSON:

{{
  "nodes": [
    {{"id":"1","label":"Main Topic","level":0}}
  ],
  "edges": [
    {{"from":"1","to":"2"}}
  ]
}}

Material:
{combined_text[:8000]}
"""
                }
            ]
        )

        mindmap_data = json.loads(response.choices[0].message.content)

        mindmap_obj = MindMap(
            title=request.title,
            nodes=mindmap_data.get("nodes", []),
            edges=mindmap_data.get("edges", []),
            file_ids=request.file_ids
        )

        doc = mindmap_obj.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()

        await db.mindmaps.insert_one(doc)
        return mindmap_obj

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Mindmap error: {e}")
        raise HTTPException(status_code=500, detail="Mind map generation failed")


@api_router.get("/mindmaps", response_model=List[MindMap])
async def get_mindmaps():
    mindmaps = await db.mindmaps.find({}, {"_id": 0}).to_list(1000)

    for m in mindmaps:
        if isinstance(m["created_at"], str):
            m["created_at"] = datetime.fromisoformat(m["created_at"])

    return mindmaps


# =========================
# MIDDLEWARE
# =========================
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
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