# AI Notes & Study

A full-stack app that turns your raw study material (PDFs, Word docs, text files) into AI-generated structured notes and interactive mind maps.

Upload your lecture slides, textbook chapters, or messy notes → the app extracts the text, sends it to OpenAI, and gives you back clean, organized study notes and a visual mind map you can explore.

---

## What it does

<<<<<<< HEAD
- **Upload files** — drag and drop PDFs, `.docx`, or `.txt` files. Text is extracted automatically on upload.
- **Generate combined notes** — pick one or more uploaded files and generate detailed, structured study notes (headings, bullets, summaries, examples) from their combined content.
- **Generate mind maps** — turn the same material into a visual mind map (nodes + edges), rendered interactively with React Flow.
- **Browse history** — previously generated notes and mind maps are saved and listed for later viewing.
=======
- **Upload files** - drag and drop PDFs, `.docx`, or `.txt` files. Text is extracted automatically on upload.
- **Generate combined notes** - pick one or more uploaded files and generate detailed, structured study notes (headings, bullets, summaries, examples) from their combined content.
- **Generate mind maps** - turn the same material into a visual mind map (nodes + edges), rendered interactively with React Flow.
- **Browse history** - previously generated notes and mind maps are saved and listed for later viewing.
>>>>>>> cf183460b0493f34123c739f460ed73b775960b9

---

## Tech stack

**Backend**
<<<<<<< HEAD
- FastAPI (Python) — REST API under `/api`
- MongoDB (via Motor, async driver) — stores uploaded files, generated notes, and mind maps
- OpenAI API (`gpt-4o-mini`) — generates notes and mind map structure
- PyPDF2 / python-docx — text extraction from PDF and Word files
=======
- FastAPI (Python) - REST API under `/api`
- MongoDB (via Motor, async driver) - stores uploaded files, generated notes, and mind maps
- OpenAI API (`gpt-4o-mini`) - generates notes and mind map structure
- PyPDF2 / python-docx - text extraction from PDF and Word files
>>>>>>> cf183460b0493f34123c739f460ed73b775960b9

**Frontend**
- React 19 + React Router
- Tailwind CSS
<<<<<<< HEAD
- React Flow — interactive mind map rendering
- Axios — API calls
- Sonner — toast notifications
=======
- React Flow - interactive mind map rendering
- Axios - API calls
- Sonner - toast notifications
>>>>>>> cf183460b0493f34123c739f460ed73b775960b9

---

## Project structure

```
AI-Notes-Study/
├── app/
│   ├── backend/
│   │   ├── server.py              # FastAPI app — all API routes
│   │   ├── requirements.txt       # Python dependencies
│   │   └── .env                   # Backend secrets (not committed)
│   └── frontend/
│       ├── src/
│       │   ├── App.js             # Root component + router
│       │   ├── pages/
│       │   │   └── Dashboard.js   # Main app page
│       │   ├── components/
│       │   │   ├── FileUploadZone.js
│       │   │   ├── FileList.js
│       │   │   ├── ProcessNotesDialog.js
│       │   │   ├── CombinedNotesList.js
│       │   │   ├── ViewNoteDialog.js
│       │   │   ├── GenerateMindMapDialog.js
│       │   │   ├── MindMapsList.js
│       │   │   └── ViewMindMapDialog.js
│       │   └── .env               # Frontend env vars (not committed)
│       ├── package.json
│       └── craco.config.js
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+ and Yarn (or npm)
- A MongoDB instance (local or Atlas connection string)
<<<<<<< HEAD
- An OpenAI API key
=======
- An google-genai API key
>>>>>>> cf183460b0493f34123c739f460ed73b775960b9

---

## Setup

### 1. Backend

```bash
cd app/backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create `app/backend/.env` with:

```bash
<<<<<<< HEAD
OPENAI_API_KEY=your_openai_api_key
MONGO_URL=your_mongodb_connection_string
DB_NAME=your_database_name
CORS_ORIGINS=http://localhost:3000   # optional, defaults to "*"
=======
GEMINI_API_KEY=your_openai_api_key
MONGO_URL=your_mongodb_connection_string
DB_NAME=your_database_name

>>>>>>> cf183460b0493f34123c739f460ed73b775960b9
```

Run the API:

```bash
uvicorn server:app --reload --port 8000
```

The API is now running at `http://127.0.0.1:8000`, with all routes under `/api`.

### 2. Frontend

```bash
cd app/frontend
<<<<<<< HEAD
yarn install    # or: npm install
=======
npm install    
>>>>>>> cf183460b0493f34123c739f460ed73b775960b9
```

Create `app/frontend/src/.env` with:

```bash
REACT_APP_BACKEND_URL=http://127.0.0.1:8000
```

Run the app:

```bash
<<<<<<< HEAD
yarn start      # or: npm start
=======
npm start
>>>>>>> cf183460b0493f34123c739f460ed73b775960b9
```

The app opens at `http://localhost:3000`.

---

## API overview

All routes are prefixed with `/api`.

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Health check / hello message |
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload a file (PDF, DOCX, or TXT); extracts and stores its text |
| `GET` | `/files` | List all uploaded files |
| `DELETE` | `/files/{file_id}` | Delete an uploaded file |
| `POST` | `/process-notes` | Generate structured study notes from selected file(s) |
| `GET` | `/combined-notes` | List previously generated notes |
| `POST` | `/generate-mindmap` | Generate a mind map (nodes/edges) from selected file(s) |
| `GET` | `/mindmaps` | List previously generated mind maps |

---

## Notes

- Supported upload formats: PDF (`application/pdf`), Word (`.docx`), and plain text (`.txt`). Other file types are rejected.
- Both `/process-notes` and `/generate-mindmap` truncate combined input text (12,000 / 8,000 characters respectively) before sending it to the OpenAI API, so very large uploads may be partially summarized.
- No secrets are committed — both `.env` files are gitignored. Fill them in locally following the Setup section above.
