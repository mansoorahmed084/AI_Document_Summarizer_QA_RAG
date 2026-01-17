# 🚀 Quick Deployment Guide

## Prerequisites

1. **Install Docker**: https://docs.docker.com/get-docker/
2. **Install gcloud CLI**: https://cloud.google.com/sdk/docs/install
3. **GCP Project**: Create or select a GCP project
4. **Enable APIs**: Run the commands below

## Quick Start

### 1. Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com  # If using Cloud SQL
```

### 1.5. Set Up Permissions (If You Get Permission Errors)

If you encounter permission errors, run:

```bash
python scripts/setup_permissions.py
```

This will grant the necessary IAM roles to your account.

### 2. Authenticate

```bash
gcloud auth login
gcloud auth configure-docker
gcloud config set project YOUR_PROJECT_ID
```

### 3. Deploy

**Python (Cross-platform - Recommended):**
```bash
python scripts/deploy.py
```

**Or using bash script (Linux/Mac):**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 4. Configure Environment Variables

After deployment, set environment variables:

```bash
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --set-env-vars "GCP_PROJECT_ID=your-project-id,GCP_REGION=us-central1"
```

### 5. Test

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe doc-summarizer-qa \
  --region us-central1 --format 'value(status.url)')

# Test health check
curl ${SERVICE_URL}/health

# Open API docs
echo "API Docs: ${SERVICE_URL}/docs"
```

## Local Docker Testing

```bash
# Build image
docker build -t doc-summarizer-qa:local .

# Run container
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=your-project-id \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json \
  -v /path/to/key.json:/path/to/key.json:ro \
  doc-summarizer-qa:local

# Test
curl http://localhost:8080/health
```

## Troubleshooting

See `docs/STEP_06_DEPLOYMENT.md` for detailed troubleshooting guide.
