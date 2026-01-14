# Step 2: Text Extraction & Processing

## 📋 Overview

Step 2 implements the core document processing functionality: extracting text from PDF and text files, chunking large documents for efficient processing, and storing extracted content. This step transforms the upload endpoint from a simple file validator into a fully functional document processor.

**Status:** ✅ **COMPLETED**

---

## 🎯 Objectives Achieved

1. ✅ **Text Extraction Service** - PDF and plain text file extraction
2. ✅ **Text Chunking** - Intelligent chunking with sentence/word boundary detection
3. ✅ **Document Storage** - In-memory storage (prepared for Firestore migration)
4. ✅ **Enhanced Upload Endpoint** - Full document processing pipeline
5. ✅ **Document Retrieval** - GET endpoints for single and list operations
6. ✅ **Error Handling** - Comprehensive error handling for extraction failures

---

## 🏗️ Architecture Decisions

### 1. Service Layer Pattern

Created dedicated service modules for separation of concerns:

```
app/services/
├── text_extractor.py      # PDF and text extraction
└── document_storage.py    # Document storage (in-memory → Firestore)
```

**Rationale:**
- **Single Responsibility**: Each service has one clear purpose
- **Testability**: Services can be tested independently
- **Maintainability**: Easy to swap implementations (e.g., Firestore in Step 3)
- **Reusability**: Services can be used across multiple endpoints

### 2. Text Extraction Strategy

**PDF Extraction:**
- Uses `PyPDF2` library
- Handles multi-page documents
- Graceful error handling for corrupted pages
- Validates that text content exists

**Text File Extraction:**
- UTF-8 encoding with Latin-1 fallback
- Handles various text encodings gracefully
- Strips whitespace appropriately

**Error Handling:**
- Clear error messages for different failure scenarios
- Distinguishes between empty documents and extraction failures
- HTTP 400 for client errors (bad files)
- HTTP 500 for unexpected server errors

### 3. Chunking Strategy

**Intelligent Chunking:**
- **Primary**: Sentence boundary detection (`. `, `! `, `? `, `\n\n`)
- **Fallback**: Word boundary detection (spaces)
- **Overlap**: Configurable overlap between chunks (default: 200 chars)
- **Size**: Configurable chunk size (default: 1000 chars)

**Why This Approach:**
- Preserves semantic meaning (sentence boundaries)
- Prevents cutting words in half
- Overlap ensures context continuity for RAG
- Configurable for different use cases

**Configuration:**
```python
CHUNK_SIZE: int = 1000      # Characters per chunk
CHUNK_OVERLAP: int = 200    # Overlap between chunks
```

### 4. Storage Strategy (Temporary)

**In-Memory Storage:**
- `InMemoryDocumentStorage` class for Step 2
- Stores documents, text, and chunks
- Prepared for Firestore migration in Step 3

**Data Structure:**
```python
{
    "id": "uuid",
    "filename": "document.pdf",
    "upload_time": datetime,
    "status": "processed",
    "file_size": 12345,
    "text_length": 5000,
    "chunk_count": 5,
    "summary": None  # Will be populated in Step 4
}
```

**Why In-Memory First:**
- Faster development iteration
- No external dependencies for Step 2
- Easy to test and validate logic
- Clear migration path to Firestore

---

## 📡 API Endpoints

### Document Upload (Enhanced)

#### `POST /documents/upload`

**What Changed:**
- ✅ Now extracts text from uploaded files
- ✅ Chunks large documents automatically
- ✅ Stores document metadata and content
- ✅ Returns processing statistics

**Request:**
- Content-Type: `multipart/form-data`
- Body: File (PDF or TXT)
- Max size: 10MB

**Processing Flow:**
1. Validate file extension and size
2. Extract text using `TextExtractor`
3. Chunk text using `TextChunker`
4. Store in `document_storage`
5. Return success with statistics

**Response:**
```json
{
  "doc_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "status": "processed",
  "message": "Document processed successfully. Extracted 5000 characters in 5 chunk(s).",
  "upload_time": "2024-01-15T10:30:00.000Z"
}
```

**Error Responses:**
- `400`: Invalid file type, size exceeded, no text content, extraction failure
- `500`: Unexpected server error

---

### Document Retrieval (New)

#### `GET /documents/{doc_id}`

**Purpose:** Get document metadata by ID

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "upload_time": "2024-01-15T10:30:00.000Z",
  "status": "processed",
  "summary": null,
  "file_size": 12345
}
```

**Error Responses:**
- `404`: Document not found

---

#### `GET /documents`

**Purpose:** List all documents with pagination

**Query Parameters:**
- `skip` (int, default: 0): Number of documents to skip
- `limit` (int, default: 100): Maximum documents to return

**Response:**
```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document.pdf",
      "upload_time": "2024-01-15T10:30:00.000Z",
      "status": "processed",
      "summary": null,
      "file_size": 12345
    }
  ],
  "total": 1
}
```

---

## 🔧 Implementation Details

### Text Extraction Service

**File:** `app/services/text_extractor.py`

**Key Methods:**
- `extract_from_pdf(file_content: bytes) -> str`
- `extract_from_text(file_content: bytes, encoding: str) -> str`
- `extract(file_content: bytes, file_extension: str) -> str`

**Features:**
- Handles multi-page PDFs
- Graceful page-level error handling
- Encoding fallback for text files
- Clear error messages

**Example Usage:**
```python
extractor = TextExtractor()
text = extractor.extract(file_content, ".pdf")
```

---

### Text Chunking Utility

**File:** `app/utils/chunking.py`

**Key Methods:**
- `chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]`
- `get_chunk_count(text: str, chunk_size: int) -> int`

**Chunking Algorithm:**
1. If text <= chunk_size, return single chunk
2. For each chunk:
   - Try to break at sentence boundary (last 20% of chunk)
   - Fallback to word boundary if no sentence boundary
   - Apply overlap for next chunk
3. Return list of chunks

**Example Usage:**
```python
chunker = TextChunker()
chunks = chunker.chunk_text(text, chunk_size=1000, chunk_overlap=200)
```

---

### Document Storage Service

**File:** `app/services/document_storage.py`

**Key Methods:**
- `store_document(doc_id, filename, text, chunks, file_size) -> dict`
- `get_document(doc_id) -> Optional[dict]`
- `get_document_text(doc_id) -> Optional[str]`
- `get_document_chunks(doc_id) -> Optional[list]`
- `list_documents(skip, limit) -> tuple[list, int]`
- `update_document_summary(doc_id, summary) -> bool`

**Storage Structure:**
- `_documents`: Metadata dictionary
- `_document_texts`: Full text content
- `_document_chunks`: Chunked text arrays

**Migration Path:**
- Current: In-memory dictionaries
- Step 3: Firestore collections
- Interface remains the same

---

## 📊 Configuration

### New Settings

Added to `app/core/config.py`:

```python
# Text Processing
CHUNK_SIZE: int = 1000      # Characters per chunk
CHUNK_OVERLAP: int = 200    # Overlap between chunks
```

**Configurable via `.env`:**
```env
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## 🧪 Testing

### Testing Status

✅ **All APIs tested and verified working correctly**

The following endpoints have been tested and confirmed functional:
- `POST /documents/upload` - Document upload and processing
- `GET /documents/{doc_id}` - Document retrieval
- `GET /documents` - Document listing with pagination

### Testing Methods

#### 1. Swagger UI Testing (Recommended)

The easiest way to test the APIs is through the auto-generated Swagger UI:

1. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access Swagger UI:**
   - Navigate to: http://localhost:8000/docs
   - All endpoints are interactive and can be tested directly

3. **Test Upload Endpoint:**
   - Click on `POST /documents/upload`
   - Click "Try it out"
   - Click "Choose File" and select a PDF or TXT file
   - Click "Execute"
   - Verify the response shows `status: "processed"` with extraction statistics

4. **Test Document Retrieval:**
   - Copy the `doc_id` from the upload response
   - Use `GET /documents/{doc_id}` to retrieve document metadata
   - Verify all fields are populated correctly

5. **Test Document Listing:**
   - Use `GET /documents` to list all uploaded documents
   - Test pagination with `skip` and `limit` parameters

#### 2. cURL Testing

**Test PDF Upload:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@sample.pdf"
```

**Test Text File Upload:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@sample.txt"
```

**Get Document:**
```bash
curl "http://localhost:8000/documents/{doc_id}"
```

**List Documents:**
```bash
curl "http://localhost:8000/documents?skip=0&limit=10"
```

### Verified Behaviors

✅ **PDF Processing:**
- ✅ Extracts text from all pages successfully
- ✅ Handles multi-page documents correctly
- ✅ Returns accurate chunk count in response message
- ✅ Processes PDFs of various sizes (tested with small to medium files)

✅ **Text File Processing:**
- ✅ Handles UTF-8 encoding correctly
- ✅ Preserves text formatting and line breaks
- ✅ Returns accurate character count and chunk information
- ✅ Works with plain text files of various sizes

✅ **Document Storage:**
- ✅ Documents are stored immediately after upload
- ✅ Metadata is correctly stored (filename, size, upload time, status)
- ✅ Text content and chunks are accessible via storage service
- ✅ Document retrieval returns complete metadata

✅ **API Responses:**
- ✅ Upload endpoint returns detailed processing statistics
- ✅ GET endpoints return properly formatted JSON responses
- ✅ Pagination works correctly for document listing
- ✅ Error responses are clear and informative

✅ **Error Handling:**
- ✅ Invalid file types are rejected with clear error messages
- ✅ File size limits are enforced correctly
- ✅ Empty documents are detected and rejected
- ✅ Non-existent document IDs return 404 errors

### Example Test Workflow

1. **Upload a PDF document:**
   ```
   POST /documents/upload
   Response: {
     "doc_id": "abc-123-def",
     "filename": "test.pdf",
     "status": "processed",
     "message": "Document processed successfully. Extracted 5000 characters in 5 chunk(s).",
     "upload_time": "2024-01-15T10:30:00.000Z"
   }
   ```

2. **Retrieve the document:**
   ```
   GET /documents/abc-123-def
   Response: {
     "id": "abc-123-def",
     "filename": "test.pdf",
     "upload_time": "2024-01-15T10:30:00.000Z",
     "status": "processed",
     "summary": null,
     "file_size": 12345
   }
   ```

3. **List all documents:**
   ```
   GET /documents
   Response: {
     "documents": [...],
     "total": 1
   }
   ```

### Performance Observations

- **Upload Processing:** Fast for typical document sizes (< 1MB)
- **Text Extraction:** Efficient for PDFs with text content
- **Chunking:** Handles documents of various sizes smoothly
- **Storage:** In-memory storage provides instant retrieval

### Known Limitations (Step 2)

- **Persistence:** Documents are lost on server restart (addressed in Step 3)
- **Concurrency:** No async processing for large files (future optimization)
- **File Storage:** Original files are not stored (only extracted text)

---

## 🔍 Code Quality

- ✅ No linter errors
- ✅ Type hints throughout
- ✅ Comprehensive error handling
- ✅ Docstrings for all methods
- ✅ Consistent code style
- ✅ Separation of concerns
- ✅ **APIs tested and verified working**

---

## 📈 Performance Considerations

### Current Implementation

- **In-Memory Storage**: Fast but not persistent
- **Synchronous Processing**: Simple but blocks during extraction
- **Chunking**: Efficient for documents up to ~100KB

### Future Optimizations (Step 3+)

- **Async Processing**: Background tasks for large files
- **Streaming**: For very large documents
- **Caching**: Store extraction results
- **Batch Processing**: Multiple files at once

---

## 🚀 What's Next

### Step 3: Database Integration
- Replace in-memory storage with PostgreSQL (metadata)
- Replace in-memory storage with Firestore (content/chunks)
- SQLAlchemy models for documents
- Firestore client integration
- Migration scripts

### Step 4: Summarization API
- Vertex AI integration
- Prompt engineering for summaries
- Store summaries in database
- Endpoint: `POST /documents/{doc_id}/summarize`

### Step 5: Q&A API
- RAG-lite implementation
- Context retrieval from chunks
- Vertex AI for question answering
- Endpoint: `POST /documents/{doc_id}/qa`

---

## 📝 Key Takeaways

1. **Service Layer**: Clean separation of extraction, chunking, and storage
2. **Intelligent Chunking**: Sentence/word boundaries preserve meaning
3. **Error Handling**: Clear, actionable error messages
4. **Migration Ready**: In-memory storage designed for easy Firestore migration
5. **Production Patterns**: Proper structure for scaling

---

---

## 📖 Quick Reference

### Common Usage Patterns

#### Upload and Retrieve Document
```python
# 1. Upload document
response = requests.post(
    "http://localhost:8000/documents/upload",
    files={"file": open("document.pdf", "rb")}
)
doc_id = response.json()["doc_id"]

# 2. Retrieve document metadata
doc = requests.get(f"http://localhost:8000/documents/{doc_id}").json()
print(f"Document: {doc['filename']}, Status: {doc['status']}")
```

#### List All Documents
```python
# Get first 10 documents
response = requests.get(
    "http://localhost:8000/documents",
    params={"skip": 0, "limit": 10}
)
documents = response.json()["documents"]
total = response.json()["total"]
```

#### Check Processing Status
```python
# After upload, check status
upload_response = requests.post(...).json()
if upload_response["status"] == "processed":
    print("Document processed successfully!")
    print(f"Message: {upload_response['message']}")
```

### Response Examples

**Successful Upload:**
```json
{
  "doc_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sample.pdf",
  "status": "processed",
  "message": "Document processed successfully. Extracted 5000 characters in 5 chunk(s).",
  "upload_time": "2024-01-15T10:30:00.000Z"
}
```

**Document Metadata:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sample.pdf",
  "upload_time": "2024-01-15T10:30:00.000Z",
  "status": "processed",
  "summary": null,
  "file_size": 12345
}
```

---

## ✅ Testing Confirmation

**Status:** All APIs have been tested and verified working correctly.

**Tested Endpoints:**
- ✅ `POST /documents/upload` - Successfully processes PDF and text files
- ✅ `GET /documents/{doc_id}` - Correctly retrieves document metadata
- ✅ `GET /documents` - Properly lists documents with pagination

**Test Results:**
- Text extraction working for both PDF and text files
- Chunking algorithm functioning correctly
- Document storage and retrieval operational
- Error handling working as expected
- API responses properly formatted

**Ready for:** Step 3 - Database Integration

---

**Step 2 Status:** ✅ **COMPLETE & TESTED**

**Next Step:** Step 3 - Database Integration (PostgreSQL + Firestore)
