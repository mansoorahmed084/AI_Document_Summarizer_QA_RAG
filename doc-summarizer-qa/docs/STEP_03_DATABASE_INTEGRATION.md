# Step 3: Database Integration

## 📋 Overview

Step 3 migrates the application from in-memory storage to persistent database storage using PostgreSQL for metadata and Firestore for document content. This provides data persistence, scalability, and production-ready storage architecture.

**Status:** ✅ **COMPLETED**

---

## 🎯 Objectives Achieved

1. ✅ **PostgreSQL Integration** - SQLAlchemy models and connection management
2. ✅ **Firestore Integration** - Document content and chunks storage
3. ✅ **Database Models** - Document and Request tracking models
4. ✅ **Storage Migration** - Migrated from in-memory to persistent storage
5. ✅ **Session Management** - FastAPI dependency injection for database sessions
6. ✅ **Graceful Degradation** - Fallback mechanisms for local development
7. ✅ **Database Initialization** - Automatic table creation on startup

---

## 🏗️ Architecture Decisions

### 1. Dual Storage Strategy

**PostgreSQL (Metadata):**
- Document metadata (filename, upload time, status, file size)
- Summary storage
- Request history tracking
- Structured, relational data

**Firestore (Content):**
- Full extracted text
- Document chunks
- Unstructured, document-based storage
- Better for large text content

**Rationale:**
- **Separation of Concerns**: Metadata vs. content
- **Performance**: PostgreSQL for queries, Firestore for large text
- **Scalability**: Firestore scales better for document storage
- **Cost**: Optimize storage costs by using the right tool

### 2. SQLAlchemy ORM

**Why SQLAlchemy:**
- Industry-standard ORM for Python
- Type-safe model definitions
- Easy migrations and schema management
- Works seamlessly with FastAPI

**Models Created:**
- `Document` - Document metadata
- `Request` - API request tracking (for Step 4-5)

### 3. Session Management

**FastAPI Dependency Injection:**
```python
async def endpoint(db: Session = Depends(get_db)):
    # Database session automatically managed
    pass
```

**Benefits:**
- Automatic session lifecycle management
- Connection pooling
- Transaction handling
- Clean, testable code

### 4. Graceful Degradation

**Firestore Fallback:**
- In-memory cache if Firestore unavailable
- Allows local development without GCP setup
- Clear warning messages
- App continues to function

**PostgreSQL:**
- Connection errors handled gracefully
- Startup warnings instead of failures
- Allows development without database initially

---

## 📊 Database Schema

### PostgreSQL Tables

#### `documents` Table

| Column | Type | Description |
|--------|------|-------------|
| id | String (PK) | UUID document identifier |
| filename | String | Original filename |
| upload_time | DateTime | Upload timestamp (indexed) |
| status | Enum | Processing status (indexed) |
| file_size | Integer | File size in bytes |
| text_length | Integer | Extracted text length |
| chunk_count | Integer | Number of chunks |
| summary | Text | AI-generated summary |

**Indexes:**
- `id` (primary key)
- `upload_time` (for sorting)
- `status` (for filtering)
- `filename` (for searching)

#### `requests` Table

| Column | Type | Description |
|--------|------|-------------|
| id | String (PK) | UUID request identifier |
| doc_id | String | Document ID (indexed) |
| request_type | Enum | Type: summarize or qa (indexed) |
| timestamp | DateTime | Request timestamp (indexed) |
| latency_ms | Integer | Request latency in milliseconds |

**Purpose:** Track API usage for monitoring and analytics (used in Step 4-5)

---

### Firestore Structure

```
documents/
  {doc_id}/
    text: string          # Full extracted text
    chunks: array[string] # Text chunks
    updated_at: timestamp # Last update time
```

**Collection:** `documents` (configurable via `FIRESTORE_COLLECTION_DOCUMENTS`)

---

## 🔧 Implementation Details

### Database Models

**File:** `app/db/models.py`

**Document Model:**
```python
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False, index=True)
    upload_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(SQLEnum(DocumentStatus), nullable=False)
    file_size = Column(Integer, nullable=True)
    text_length = Column(Integer, nullable=True)
    chunk_count = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
```

**Features:**
- Enum for status (type-safe)
- Automatic UUID generation
- Timestamp defaults
- Indexes for performance

### Database Connection

**File:** `app/db/base.py`

**Key Components:**
- `engine` - SQLAlchemy engine with connection pooling
- `SessionLocal` - Session factory
- `Base` - Declarative base for models
- `get_db()` - FastAPI dependency for sessions
- `init_db()` - Initialize tables

**Connection String:**
```python
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
```

### Document Storage Service

**File:** `app/services/document_storage.py`

**Methods:**
- `store_document()` - Store metadata + content
- `get_document()` - Get metadata from PostgreSQL
- `get_document_text()` - Get text from Firestore
- `get_document_chunks()` - Get chunks from Firestore
- `list_documents()` - Paginated listing
- `update_document_summary()` - Update summary
- `delete_document()` - Delete from both stores

**Storage Flow:**
1. Store metadata in PostgreSQL
2. Store content in Firestore
3. If Firestore fails, use in-memory fallback

### Firestore Service

**File:** `app/services/firestore_service.py`

**Features:**
- Graceful import handling
- Fallback to in-memory cache
- Error handling and logging
- Configurable collection name

**Methods:**
- `store_document_content()` - Store text and chunks
- `get_document_text()` - Retrieve text
- `get_document_chunks()` - Retrieve chunks
- `delete_document_content()` - Delete content

---

## 📡 API Changes

### Updated Endpoints

All document endpoints now use database sessions:

**Before (Step 2):**
```python
document_storage = InMemoryDocumentStorage()
# Global instance
```

**After (Step 3):**
```python
async def endpoint(db: Session = Depends(get_db)):
    storage = DocumentStorage(db)
    # Per-request instance with session
```

**Endpoints Updated:**
- `POST /documents/upload` - Now persists to database
- `GET /documents/{doc_id}` - Retrieves from database
- `GET /documents` - Queries database with pagination

### Response Format

**Unchanged** - API responses remain the same for backward compatibility.

---

## 🚀 Database Initialization

### Automatic Initialization

**On Application Startup:**
```python
@app.on_event("startup")
async def startup_event():
    init_db()  # Creates tables if they don't exist
```

### Manual Initialization

**Script:** `scripts/init_db.py`

```bash
python scripts/init_db.py
```

**What it does:**
- Creates all database tables
- Validates database connection
- Provides helpful error messages

---

## ⚙️ Configuration

### Required Settings

**PostgreSQL:**
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=docsummarizer
```

**Firestore (Optional for local dev):**
```env
GCP_PROJECT_ID=your-project-id
FIRESTORE_COLLECTION_DOCUMENTS=documents
```

### Connection String

Automatically built from settings:
```
postgresql://{user}:{password}@{host}:{port}/{db}
```

Or set directly:
```env
DATABASE_URL=postgresql://user:pass@host:port/db
```

---

## 🧪 Testing

### Local Development Setup

**Option 1: Full Setup**
1. Install and start PostgreSQL
2. Create database: `CREATE DATABASE docsummarizer;`
3. Set GCP credentials for Firestore
4. Run application

**Option 2: Minimal Setup (PostgreSQL only)**
1. Install and start PostgreSQL
2. Create database
3. Firestore will use in-memory fallback
4. App functions normally (content lost on restart)

**Option 3: No Database (Development)**
- App starts with warnings
- Tables created on first use (if connection works)
- Firestore uses in-memory fallback

### Database Setup Commands

**PostgreSQL:**
```bash
# Create database
createdb docsummarizer

# Or using psql
psql -U postgres
CREATE DATABASE docsummarizer;
```

**Initialize Tables:**
```bash
python scripts/init_db.py
```

### Testing Endpoints

**Upload Document:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@sample.pdf"
```

**Verify Persistence:**
1. Upload document
2. Restart server
3. Retrieve document - should still exist!

**List Documents:**
```bash
curl "http://localhost:8000/documents"
```

---

## 🔍 Code Quality

- ✅ No linter errors
- ✅ Type hints throughout
- ✅ Comprehensive error handling
- ✅ Graceful degradation
- ✅ Clear separation of concerns
- ✅ Database session management
- ✅ Transaction safety

---

## 📈 Performance Considerations

### Connection Pooling

- SQLAlchemy engine uses connection pooling
- `pool_pre_ping=True` verifies connections
- Automatic reconnection on failure

### Query Optimization

- Indexes on frequently queried columns
- Pagination for large result sets
- Efficient joins and filters

### Firestore

- Document-based storage (fast reads)
- No complex queries needed
- Scales automatically

---

## 🚨 Error Handling

### Database Connection Errors

**Startup:**
- Warning message, app continues
- Tables created on first use

**Runtime:**
- HTTP 500 for database errors
- Clear error messages
- Transaction rollback on failure

### Firestore Errors

**Unavailable:**
- Falls back to in-memory cache
- Warning messages logged
- App continues to function

**Connection Errors:**
- Graceful degradation
- Retry logic (future enhancement)
- Clear error logging

---

## 🔄 Migration from Step 2

### What Changed

1. **Storage Backend:**
   - In-memory → PostgreSQL + Firestore
   - Global instance → Per-request instances

2. **Session Management:**
   - No sessions → FastAPI dependency injection
   - Manual cleanup → Automatic cleanup

3. **Persistence:**
   - Lost on restart → Persistent storage
   - No backup → Database backups possible

### Backward Compatibility

- ✅ API responses unchanged
- ✅ Same endpoint signatures
- ✅ Same data models
- ✅ No breaking changes

---

## 🚀 What's Next

### Step 4: Summarization API
- Vertex AI integration
- Store summaries in PostgreSQL
- Update document summary field
- Endpoint: `POST /documents/{doc_id}/summarize`

### Step 5: Q&A API
- Retrieve chunks from Firestore
- RAG-lite implementation
- Vertex AI for answers
- Track requests in `requests` table
- Endpoint: `POST /documents/{doc_id}/qa`

### Future Enhancements
- Database migrations (Alembic)
- Connection retry logic
- Firestore batch operations
- Database backup strategies
- Read replicas for scaling

---

## 📝 Key Takeaways

1. **Dual Storage**: PostgreSQL for metadata, Firestore for content
2. **Session Management**: FastAPI dependency injection
3. **Graceful Degradation**: App works without all services
4. **Persistence**: Data survives server restarts
5. **Production Ready**: Proper connection pooling and error handling

---

**Step 3 Status:** ✅ **COMPLETE**

**Next Step:** Step 4 - Summarization API (Vertex AI Integration)
