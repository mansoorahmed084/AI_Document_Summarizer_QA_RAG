# 🎯 AI Document Summarizer & Q&A Backend

A production-ready backend service that ingests documents (PDF/Text), extracts content, stores metadata, and provides **AI-powered summarization and question-answering APIs**, designed for deployment on GCP.

## 🚀 Features

- **REST APIs** for document management
- **Document Upload** (PDF/Text support)
- **Text Extraction** from documents
- **AI Summarization** using Vertex AI
- **Q&A over Documents** (RAG-lite approach)
- **Metadata Storage** (PostgreSQL + Firestore)
- **Scalable Deployment** on GCP Cloud Run
- **Logging & Monitoring** integration

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL (for metadata)
- GCP Project with Vertex AI enabled
- Firestore database

## 🛠️ Setup

1. **Clone and navigate to the project:**
   ```bash
   cd doc-summarizer-qa
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Upgrade pip, setuptools, and wheel (recommended):**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** If you encounter Rust compilation errors on Windows, ensure you have the latest pip, setuptools, and wheel. The requirements use versions with pre-built wheels to avoid compilation.

5. **Create a `.env` file:**
   ```env
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=docsummarizer
   GCP_PROJECT_ID=your-project-id
   GCP_REGION=us-central1
   API_KEY=your-api-key
   ```

6. **Run the application:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## 📁 Project Structure

```
doc-summarizer-qa/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   └── v1/
│   │       ├── health.py       # Health check endpoint
│   │       └── documents.py    # Document endpoints
│   ├── core/
│   │   └── config.py           # Configuration settings
│   ├── db/
│   │   ├── base.py             # Database connection & session
│   │   └── models.py            # SQLAlchemy models
│   ├── models/
│   │   ├── document.py          # Pydantic request/response models
│   │   └── ai.py                # AI request/response models
│   ├── services/
│   │   ├── text_extractor.py    # PDF and text extraction
│   │   ├── document_storage.py  # Document storage (PostgreSQL + Firestore)
│   │   ├── firestore_service.py # Firestore operations
│   │   └── vertex_ai_service.py # Vertex AI for summarization & Q&A
│   └── utils/
│       └── chunking.py           # Text chunking utilities
├── scripts/
│   └── init_db.py               # Database initialization script
├── docs/
│   ├── STEP_01_FOUNDATION.md     # Step 1 documentation
│   ├── STEP_02_TEXT_EXTRACTION.md # Step 2 documentation
│   ├── STEP_03_DATABASE_INTEGRATION.md # Step 3 documentation
│   └── STEP_04_SUMMARIZATION_API.md # Step 4 documentation
├── requirements.txt
└── README.md
```

## 🔌 API Endpoints

### System
- `GET /health` - Health check

### Documents
- `POST /documents/upload` - Upload and process a document (extracts text, chunks content)
- `GET /documents/{doc_id}` - Get document metadata by ID
- `GET /documents` - List all documents with pagination

### AI
- `POST /documents/{doc_id}/summarize` - Summarize document using Vertex AI
- `POST /documents/{doc_id}/qa` - Ask questions about document (RAG-lite)

## 🏗️ Architecture

```
Client (Android / Web)
        |
        v
   FastAPI Backend
        |
        |-- Document Upload
        |-- Text Extraction
        |-- Chunking
        |
        +--> PostgreSQL (metadata)
        +--> Firestore (doc text / chunks)
        |
        +--> Vertex AI (Summarization / Q&A)
        |
        +--> Cloud Logging & Monitoring
```

## 📝 Development Status

- ✅ Step 1: FastAPI skeleton, models, `/health` and `/upload` endpoints
- ✅ Step 2: Text extraction (PDF/Text), chunking, and document storage
- ✅ Step 3: Database integration (PostgreSQL + Firestore)
- ✅ Step 4: Summarization API (Vertex AI integration)
- ⏳ Step 5: Q&A API
- ⏳ Step 6: Docker + Cloud Run deployment
- ⏳ Step 7: Logging + polish

## 📄 License

MIT
