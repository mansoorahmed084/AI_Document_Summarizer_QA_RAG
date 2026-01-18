# AI Document Summarizer & Q&A - Frontend

A modern, clean frontend interface for the AI Document Summarizer & Q&A application, inspired by Smallpdf's design.

## Features

- 📄 **Drag & Drop File Upload** - Easy document upload
- 📝 **AI-Powered Summaries** - Automatic document summarization
- 💬 **Interactive Q&A** - Ask questions about your documents
- 📱 **Responsive Design** - Works on all devices
- 🎨 **Modern UI** - Clean, intuitive interface

## Setup

### Option 1: Serve Locally

1. Update the API URL in `app.js`:
   ```javascript
   const API_BASE_URL = 'https://your-cloud-run-url.run.app';
   ```

2. Serve the files using a local server:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   
   # Using PHP
   php -S localhost:8000
   ```

3. Open `http://localhost:8000` in your browser

### Option 2: Deploy to Cloud Storage / Hosting

1. Upload all files to a static hosting service (Firebase Hosting, Netlify, Vercel, etc.)
2. Update the API URL in `app.js`
3. Deploy

### Option 3: Integrate with FastAPI

You can serve the frontend from your FastAPI application:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

## Configuration

Update the `API_BASE_URL` constant in `app.js` to point to your Cloud Run service:

```javascript
const API_BASE_URL = 'https://doc-summarizer-qa-ymcfd2ddoq-uc.a.run.app';
```

## Features

### Document Upload
- Drag and drop files
- Click to browse
- Supports PDF, TXT, DOC, DOCX

### Document Management
- View all uploaded documents
- Select documents to work with
- See upload status and metadata

### AI Summarization
- Automatic summary generation
- Refresh summaries on demand
- Clean, readable format

### Question & Answer
- Ask questions about documents
- Suggested questions for quick start
- Conversation history
- Real-time answers

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Customization

### Colors
Edit `styles.css` to customize the color scheme:

```css
:root {
    --primary-color: #0066ff;
    --primary-hover: #0052cc;
    /* ... */
}
```

### API Endpoints
The frontend expects these endpoints:
- `POST /documents/upload` - Upload document
- `GET /documents` - List documents
- `GET /documents/{id}` - Get document details
- `POST /documents/{id}/summarize` - Generate summary
- `POST /documents/{id}/qa` - Ask question

## License

Part of the AI Document Summarizer & Q&A project.
