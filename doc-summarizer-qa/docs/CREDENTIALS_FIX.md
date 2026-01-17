# 🔧 Credentials File Issue - Quick Fix

## Problem Identified

Your credentials file at `C:\temp\AI\secret_keys\gcp\gcp_key.json` contains:
```
"9ec143fca1e6dbacbbc21ac8a7cd6b5a1bdade42"
```

This is **just a string**, not a proper service account JSON file.

## What It Should Look Like

A valid service account JSON file should look like this:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

## How to Fix

### Step 1: Download the Correct Service Account Key

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Select your project
3. Click on your service account (or create one if needed)
4. Go to the **"Keys"** tab
5. Click **"Add Key"** → **"Create new key"**
6. Choose **"JSON"** format
7. Download the file

### Step 2: Replace Your Current File

1. **Backup** your current file (just in case):
   ```powershell
   Copy-Item "C:\temp\AI\secret_keys\gcp\gcp_key.json" "C:\temp\AI\secret_keys\gcp\gcp_key.json.backup"
   ```

2. **Replace** with the downloaded JSON file:
   - Save the downloaded file to: `C:\temp\AI\secret_keys\gcp\gcp_key.json`
   - Make sure it's the full JSON object, not just a string

### Step 3: Verify the File

Run this to verify:
```powershell
python -c "import json; f=open(r'C:\temp\AI\secret_keys\gcp\gcp_key.json'); d=json.load(f); print('Valid!' if isinstance(d, dict) and 'project_id' in d else 'Invalid!')"
```

You should see: `Valid!`

### Step 4: Restart Your Application

```powershell
uvicorn app.main:app --reload
```

You should now see:
- ✅ Firestore client initialized
- ✅ Vertex AI initialized with model: gemini-pro

## Alternative: Use gcloud CLI

If you prefer not to use a service account file:

```powershell
gcloud auth application-default login
```

This sets up Application Default Credentials that the libraries will use automatically.

---

**Note:** The current file appears to be a token or hash, not a service account key. You need the full JSON key file from GCP Console.
