# GCP Setup Guide

This guide will help you set up Google Cloud Platform (GCP) for the AI Document Summarizer & Q&A Backend.

## 📋 Prerequisites

- Google account
- GCP account (free tier available)
- Internet connection

---

## 🚀 Option 1: Install Google Cloud SDK (Recommended)

### Windows Installation

1. **Download Google Cloud SDK:**
   - Visit: https://cloud.google.com/sdk/docs/install
   - Download the Windows installer
   - Run the installer and follow the prompts

2. **Verify Installation:**
   ```powershell
   gcloud --version
   ```

3. **Initialize gcloud:**
   ```powershell
   gcloud init
   ```
   - Sign in with your Google account
   - Select or create a project
   - Choose default region (e.g., `us-central1`)

### Alternative: Using Chocolatey (Windows)

```powershell
# Install Chocolatey if not already installed
# Then install gcloud
choco install gcloudsdk
```

### Alternative: Using PowerShell Script

```powershell
# Download and install gcloud
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

---

## 🎯 Option 2: Manual Setup (No CLI Required)

If you prefer not to install gcloud CLI, you can set up GCP manually:

### Step 1: Create GCP Project

1. Go to: https://console.cloud.google.com/
2. Sign in with your Google account
3. Click "Select a project" → "New Project"
4. Enter project name (e.g., "doc-summarizer")
5. Click "Create"
6. Note your **Project ID** (not the project name)

### Step 2: Enable Vertex AI API

1. In GCP Console, go to: https://console.cloud.google.com/apis/library
2. Search for "Vertex AI API"
3. Click on "Vertex AI API"
4. Click "Enable"

### Step 3: Create Service Account

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "Create Service Account"
3. Enter name: "doc-summarizer-service"
4. Click "Create and Continue"
5. Grant role: "Vertex AI User"
6. Click "Continue" → "Done"

### Step 4: Create and Download Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON"
5. Download the key file
6. **Save it securely** (e.g., `gcp-key.json`)

**⚠️ Important:** The downloaded file should be a **JSON object** (starts with `{`), not just a string or token. It should contain keys like `type`, `project_id`, `private_key`, `client_email`, etc.

**Verify your file:**
```powershell
python -c "import json; f=open('gcp-key.json'); d=json.load(f); print('Valid!' if isinstance(d, dict) and 'project_id' in d else 'Invalid - not a proper service account JSON!')"
```

### Step 5: Set Environment Variable

**Windows PowerShell:**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\gcp-key.json"
```

**Windows Command Prompt:**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\gcp-key.json
```

**Permanent (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable('GOOGLE_APPLICATION_CREDENTIALS', 'C:\path\to\gcp-key.json', 'User')
```

**Or add to `.env` file:**
```env
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\gcp-key.json
```

---

## ⚙️ Application Configuration

### Update `.env` File

Add these variables to your `.env` file:

```env
# GCP Configuration
GCP_PROJECT_ID=your-project-id-here
GCP_REGION=us-central1
VERTEX_AI_MODEL=gemini-pro

# Optional: Service account key path
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\gcp-key.json
```

**Important:**
- Replace `your-project-id-here` with your actual GCP Project ID
- The Project ID is different from the Project Name
- You can find it in GCP Console → Project Settings

---

## 🔐 Authentication Methods

### Method 1: Service Account Key (Recommended for Production)

1. Follow "Option 2: Manual Setup" above
2. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
3. Application will automatically use the key

### Method 2: Application Default Credentials (Development)

If you have gcloud CLI installed:

```powershell
gcloud auth application-default login
```

This creates credentials that the application will use automatically.

### Method 3: User Credentials (Development)

```powershell
gcloud auth login
```

---

## ✅ Verify Setup

### Test with gcloud CLI (if installed):

```powershell
# Check authentication
gcloud auth list

# Test Vertex AI access
gcloud ai models list --region=us-central1
```

### Test with Application:

1. Start your application:
   ```powershell
   uvicorn app.main:app --reload
   ```

2. Check startup logs:
   - Should see: `✅ Vertex AI initialized with model: gemini-pro`
   - If you see warnings, check your configuration

3. Test summarization endpoint:
   ```powershell
   # First upload a document
   curl -X POST "http://localhost:8000/documents/upload" -F "file=@sample.pdf"
   
   # Then summarize (replace {doc_id} with actual ID)
   curl -X POST "http://localhost:8000/documents/{doc_id}/summarize?max_length=300"
   ```

---

## 🆓 Free Tier & Costs

### Free Tier:
- Vertex AI: $300 free credits for new accounts
- First 60 requests/month free (Gemini Pro)
- Check: https://cloud.google.com/free

### Cost Estimates:
- **Summarization**: ~$0.001-0.01 per document (depends on length)
- **Q&A**: ~$0.001-0.01 per question
- Very affordable for development/testing

### Monitor Usage:
- GCP Console → Billing → Reports
- Set up billing alerts

---

## 🐛 Troubleshooting

### Issue: "AI service is not available"

**Possible causes:**
1. `GCP_PROJECT_ID` not set in `.env`
2. Vertex AI API not enabled
3. Authentication not configured
4. Service account lacks permissions

**Solutions:**
1. Check `.env` file has `GCP_PROJECT_ID`
2. Enable Vertex AI API in GCP Console
3. Verify authentication (check startup logs)
4. Ensure service account has "Vertex AI User" role

### Issue: "Permission denied"

**Solution:**
- Grant "Vertex AI User" role to service account
- Or use `gcloud auth application-default login`

### Issue: "Project not found"

**Solution:**
- Verify Project ID (not Project Name)
- Check project exists in GCP Console
- Ensure you have access to the project

### Issue: "Module not found: google.cloud.aiplatform"

**Solution:**
```powershell
pip install google-cloud-aiplatform
```

---

## 📝 Quick Setup Checklist

- [ ] GCP account created
- [ ] Project created (note Project ID)
- [ ] Vertex AI API enabled
- [ ] Service account created (or gcloud authenticated)
- [ ] Credentials configured
- [ ] `.env` file updated with `GCP_PROJECT_ID`
- [ ] Application restarted
- [ ] Tested summarization endpoint

---

## 🔒 Security Best Practices

1. **Never commit credentials:**
   - Add `gcp-key.json` to `.gitignore`
   - Use environment variables
   - Use secret management in production

2. **Limit permissions:**
   - Service account should only have "Vertex AI User" role
   - Don't use owner/admin roles

3. **Rotate keys:**
   - Regularly rotate service account keys
   - Revoke old keys

4. **Monitor usage:**
   - Set up billing alerts
   - Review API usage regularly

---

## 🚀 Production Deployment

For production (Cloud Run, GKE, etc.):

1. **Use Workload Identity** (recommended):
   - No keys needed
   - Automatic authentication
   - More secure

2. **Or use Secret Manager:**
   - Store service account key in Secret Manager
   - Access via application code

3. **Set environment variables:**
   - `GCP_PROJECT_ID` in Cloud Run config
   - No need for `GOOGLE_APPLICATION_CREDENTIALS` if using Workload Identity

---

## 📚 Additional Resources

- **GCP Documentation**: https://cloud.google.com/docs
- **Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
- **Authentication Guide**: https://cloud.google.com/docs/authentication
- **Free Tier**: https://cloud.google.com/free

---

## 💡 Tips

1. **Start with free tier** - Test everything before upgrading
2. **Use separate projects** - Dev, staging, production
3. **Monitor costs** - Set up billing alerts early
4. **Test locally first** - Use service account key for local dev
5. **Read error messages** - They're usually helpful

---

**Need Help?**
- Check application startup logs for warnings
- Verify all environment variables are set
- Test with a simple document first
- Check GCP Console for API enablement status
