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
│   └── models/
│       ├── document.py          # Document models
│       └── ai.py                # AI request/response models
├── requirements.txt
└── README.md
```

## 🔌 API Endpoints

### System
- `GET /health` - Health check

### Documents
- `POST /documents/upload` - Upload a document
- `GET /documents/{doc_id}` - Get document by ID
- `GET /documents` - List all documents

### AI (Coming Soon)
- `POST /documents/{doc_id}/summarize` - Summarize document
- `POST /documents/{doc_id}/qa` - Ask questions about document

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
- ⏳ Step 2: Text extraction (PDF/Text)
- ⏳ Step 3: Database integration
- ⏳ Step 4: Summarization API
- ⏳ Step 5: Q&A API
- ⏳ Step 6: Docker + Cloud Run deployment
- ⏳ Step 7: Logging + polish

## 📄 License

MIT
