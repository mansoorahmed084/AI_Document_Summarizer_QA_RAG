// Configuration - Use relative paths when served from same domain
const API_BASE_URL = window.location.origin + '/api';

// State
let currentDocumentId = null;
let documents = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupFileUpload();
    setupQuestionInput();
    loadDocuments();
});

// File Upload Setup
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });
}

// Handle file upload
async function handleFiles(files) {
    if (files.length === 0) return;

    const file = files[0]; // Handle first file for now
    showStatus('Uploading and processing document...');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/documents/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        currentDocumentId = data.doc_id;
        
        hideStatus();
        await loadDocuments();
        await loadSummary();
        showQASection();
        
        // Show success message
        showNotification('Document uploaded successfully!', 'success');
    } catch (error) {
        hideStatus();
        showNotification(`Error: ${error.message}`, 'error');
        console.error('Upload error:', error);
    }
}

// Load documents list
async function loadDocuments() {
    try {
        const response = await fetch(`${API_BASE_URL}/documents?skip=0&limit=100`);
        
        if (!response.ok) {
            throw new Error('Failed to load documents');
        }

        const data = await response.json();
        documents = data.documents || [];
        renderDocuments();
    } catch (error) {
        console.error('Error loading documents:', error);
    }
}

// Render documents list
function renderDocuments() {
    const container = document.getElementById('documentsList');
    const section = document.getElementById('documentsSection');

    if (documents.length === 0) {
        section.style.display = 'none';
        return;
    }

    section.style.display = 'block';
    container.innerHTML = documents.map(doc => `
        <div class="document-card ${doc.id === currentDocumentId ? 'active' : ''}">
            <div class="document-info">
                <div class="document-name">${escapeHtml(doc.filename)}</div>
                <div class="document-meta">
                    Uploaded: ${new Date(doc.upload_time).toLocaleString()} | 
                    Status: ${doc.status}
                </div>
            </div>
            <div class="document-actions">
                <button class="btn-icon" onclick="selectDocument('${doc.id}')" title="Select">
                    📄
                </button>
                <button class="btn-icon" onclick="loadSummary('${doc.id}')" title="View Summary">
                    📝
                </button>
            </div>
        </div>
    `).join('');
}

// Select document
async function selectDocument(docId) {
    currentDocumentId = docId;
    await loadSummary(docId);
    showQASection();
    loadDocuments(); // Refresh to highlight selected
}

// Load summary
async function loadSummary(docId = null) {
    const docIdToUse = docId || currentDocumentId;
    if (!docIdToUse) return;

    const summaryContent = document.getElementById('summaryContent');
    const summarySection = document.getElementById('summarySection');
    
    summarySection.style.display = 'block';
    summaryContent.innerHTML = '<div class="loading">Generating summary...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/documents/${docIdToUse}/summarize`, {
            method: 'POST'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate summary');
        }

        const data = await response.json();
        summaryContent.innerHTML = `
            <div class="summary-text">${escapeHtml(data.summary)}</div>
        `;
    } catch (error) {
        summaryContent.innerHTML = `
            <div class="error">Error: ${error.message}</div>
        `;
        console.error('Summary error:', error);
    }
}

// Setup question input
function setupQuestionInput() {
    const askBtn = document.getElementById('askQuestionBtn');
    const questionInput = document.getElementById('questionInput');
    const chips = document.querySelectorAll('.chip');

    // Ask button
    askBtn.addEventListener('click', () => {
        const question = questionInput.value.trim();
        if (question) {
            askQuestion(question);
        }
    });

    // Enter key
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            askBtn.click();
        }
    });

    // Suggested questions
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question');
            questionInput.value = question;
            askQuestion(question);
        });
    });

    // Refresh summary button
    document.getElementById('refreshSummaryBtn').addEventListener('click', () => {
        if (currentDocumentId) {
            loadSummary(currentDocumentId);
        }
    });
}

// Ask question
async function askQuestion(question) {
    if (!currentDocumentId) {
        showNotification('Please select a document first', 'error');
        return;
    }

    const askBtn = document.getElementById('askQuestionBtn');
    const questionInput = document.getElementById('questionInput');
    const answersContainer = document.getElementById('answersContainer');

    // Disable input
    askBtn.disabled = true;
    questionInput.disabled = true;
    askBtn.textContent = 'Asking...';

    // Add question to UI
    const questionDiv = document.createElement('div');
    questionDiv.className = 'answer-item';
    questionDiv.innerHTML = `
        <div class="answer-question">Q: ${escapeHtml(question)}</div>
        <div class="answer-text">Thinking...</div>
    `;
    answersContainer.insertBefore(questionDiv, answersContainer.firstChild);

    try {
        const response = await fetch(`${API_BASE_URL}/documents/${currentDocumentId}/qa`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get answer');
        }

        const data = await response.json();
        questionDiv.innerHTML = `
            <div class="answer-question">Q: ${escapeHtml(question)}</div>
            <div class="answer-text">${escapeHtml(data.answer)}</div>
        `;

        // Clear input
        questionInput.value = '';
    } catch (error) {
        questionDiv.innerHTML = `
            <div class="answer-question">Q: ${escapeHtml(question)}</div>
            <div class="answer-text error">Error: ${error.message}</div>
        `;
        console.error('Q&A error:', error);
    } finally {
        // Re-enable input
        askBtn.disabled = false;
        questionInput.disabled = false;
        askBtn.textContent = 'Ask';
    }
}

// Show/hide sections
function showStatus(message) {
    const statusSection = document.getElementById('statusSection');
    const statusMessage = document.getElementById('statusMessage');
    statusMessage.textContent = message;
    statusSection.style.display = 'block';
}

function hideStatus() {
    document.getElementById('statusSection').style.display = 'none';
}

function showQASection() {
    document.getElementById('qaSection').style.display = 'block';
}

// Notification
function showNotification(message, type = 'info') {
    // Simple notification - you can enhance this
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'error' ? '#dc3545' : '#28a745'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Utility
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
