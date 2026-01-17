# Step 6: Docker & Cloud Run Deployment

## 📋 Overview

Step 6 containerizes the application using Docker and deploys it to Google Cloud Run, making it production-ready and accessible on the internet.

**Status:** ✅ **DEPLOYED & RUNNING**

**🌐 Service URL:** https://doc-summarizer-qa-1008530136324.us-central1.run.app

---

## 🎯 Objectives Achieved

1. ✅ **Dockerfile Creation** - Multi-stage build for optimized image
2. ✅ **Containerization** - Application packaged as Docker container
3. ✅ **Cloud Run Configuration** - Deployment configuration files
4. ✅ **Deployment Scripts** - Automated deployment (bash & PowerShell)
5. ✅ **Environment Configuration** - Cloud Run environment variables
6. ✅ **Health Checks** - Container health check configuration

---

## 🏗️ Architecture Decisions

### 1. Multi-Stage Docker Build

**Why Multi-Stage:**
- **Smaller final image** - Only runtime dependencies
- **Faster builds** - Build tools not in final image
- **Security** - Fewer attack surfaces
- **Efficiency** - Optimized layer caching

**Stages:**
1. **Builder stage**: Install build dependencies, compile Python packages
2. **Runtime stage**: Copy only necessary files, minimal base image

### 2. Cloud Run Choice

**Why Cloud Run:**
- **Serverless** - No infrastructure management
- **Auto-scaling** - Scales to zero when not in use
- **Pay-per-use** - Only pay for requests
- **GCP Integration** - Native integration with Firestore, Vertex AI
- **Fast deployment** - Deploy in minutes

### 3. Security Best Practices

- **Non-root user** - Container runs as `appuser` (UID 1000)
- **Minimal base image** - `python:3.13-slim`
- **No secrets in image** - Use Secret Manager
- **Health checks** - Automatic container health monitoring

---

## 📦 Docker Configuration

### Dockerfile Structure

```dockerfile
# Stage 1: Builder
FROM python:3.13-slim as builder
# Install build dependencies
# Install Python packages

# Stage 2: Runtime
FROM python:3.13-slim
# Copy dependencies from builder
# Copy application code
# Set up non-root user
# Expose port
# Run application
```

### Key Features

- **Multi-stage build** - Optimized image size
- **Non-root user** - Security best practice
- **Health check** - Container health monitoring
- **Port configuration** - Uses Cloud Run PORT env var
- **Minimal dependencies** - Only runtime requirements

### Image Size Optimization

- Base image: `python:3.13-slim` (~50MB)
- Final image: ~200-300MB (estimated)
- Excludes: build tools, dev dependencies, source files

---

## ☁️ Cloud Run Configuration

### Service Settings

**Resource Allocation:**
- Memory: 2Gi (configurable)
- CPU: 2 vCPU (configurable)
- Timeout: 300 seconds (5 minutes)
- Max instances: 10 (auto-scaling)
- Min instances: 0 (scale to zero)

**Network:**
- Port: 8080 (Cloud Run default)
- Allow unauthenticated: Yes (for public API)
- Region: us-central1 (configurable)

### Environment Variables

**Required:**
- `GCP_PROJECT_ID` - Your GCP project ID
- `GCP_REGION` - Region (e.g., us-central1)

**Optional (from Secret Manager):**
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account key path
- `DATABASE_URL` - PostgreSQL connection string
- `API_KEY` - API authentication key

---

## 🚀 Deployment Methods

### Method 1: Using Deployment Script (Recommended)

**Python (Cross-platform):**
```bash
python scripts/deploy.py
```

**Or using bash script (Linux/Mac):**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

**What it does:**
1. Builds Docker image
2. Pushes to Container Registry
3. Deploys to Cloud Run
4. Shows service URL

### Method 2: Using gcloud CLI Directly

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/doc-summarizer-qa

# Deploy
gcloud run deploy doc-summarizer-qa \
  --image gcr.io/PROJECT_ID/doc-summarizer-qa \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Method 3: Using Cloud Build (CI/CD)

```bash
gcloud builds submit --config cloudbuild.yaml
```

---

## 🔐 Secrets Management

### Current Setup (Development)

Credentials stored in `.env` file (local only).

### Production Setup (Recommended)

**Use Secret Manager:**

1. **Create secrets:**
   ```bash
   # Service account key
   gcloud secrets create gcp-service-account-key \
     --data-file=path/to/service-account.json
   
   # Database password
   echo -n "your-password" | gcloud secrets create db-password
   ```

2. **Grant access:**
   ```bash
   gcloud secrets add-iam-policy-binding gcp-service-account-key \
     --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

3. **Mount in Cloud Run:**
   ```bash
   gcloud run services update doc-summarizer-qa \
     --update-secrets=GOOGLE_APPLICATION_CREDENTIALS=gcp-service-account-key:latest
   ```

---

## 📊 Database Configuration

### Option 1: Cloud SQL (Recommended for Production)

**Setup:**
1. Create Cloud SQL instance
2. Create database
3. Get connection name
4. Set up Cloud SQL Proxy or use private IP

**Connection String:**
```
postgresql://user:password@/dbname?host=/cloudsql/PROJECT:REGION:INSTANCE
```

### Option 2: External PostgreSQL

Use connection string with public IP (less secure).

### Option 3: SQLite (Development Only)

Not recommended for production.

---

## 🧪 Testing Deployment

### Pre-Deployment Checklist

- [ ] Docker image builds successfully
- [ ] Image runs locally
- [ ] Health check endpoint works
- [ ] Environment variables configured
- [ ] Secrets set up (if using Secret Manager)
- [ ] Database accessible from Cloud Run

### Local Docker Testing

```bash
# Build image
docker build -t doc-summarizer-qa:local .

# Run container
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=your-project-id \
  -e GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json \
  doc-summarizer-qa:local

# Test health check
curl http://localhost:8080/health
```

### Post-Deployment Testing

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe doc-summarizer-qa \
  --region us-central1 --format 'value(status.url)')

# Test health check
curl ${SERVICE_URL}/health

# Test API docs
open ${SERVICE_URL}/docs
```

---

## 🔧 Configuration Files

### Dockerfile

**Location:** `Dockerfile`

**Key Features:**
- Multi-stage build
- Non-root user
- Health check
- Port 8080

### .dockerignore

**Location:** `.dockerignore`

**Excludes:**
- Python cache files
- Virtual environments
- Credentials
- Git files
- IDE files

### cloudbuild.yaml

**Location:** `cloudbuild.yaml`

**Purpose:** CI/CD pipeline configuration

**Steps:**
1. Build Docker image
2. Push to Container Registry
3. Deploy to Cloud Run

### Deployment Scripts

**Location:** `scripts/`

- `deploy.sh` - Bash script (Linux/Mac)
- `deploy.ps1` - PowerShell script (Windows)

---

## 📈 Performance Considerations

### Resource Sizing

**Memory:**
- Minimum: 512Mi (for small documents)
- Recommended: 2Gi (for larger documents and AI processing)
- Maximum: 8Gi (for very large documents)

**CPU:**
- Minimum: 1 vCPU
- Recommended: 2 vCPU (for AI processing)
- Maximum: 4 vCPU

### Scaling Configuration

**Auto-scaling:**
- Min instances: 0 (cost optimization)
- Max instances: 10 (adjust based on load)
- Concurrency: 80 requests per instance (default)

**Cold Start:**
- First request: ~5-10 seconds
- Subsequent requests: <1 second
- Keep 1 min instance for zero cold starts (costs more)

---

## 🔍 Monitoring & Logging

### Cloud Run Logs

**View logs:**
```bash
gcloud run services logs read doc-summarizer-qa --region us-central1
```

**Stream logs:**
```bash
gcloud run services logs tail doc-summarizer-qa --region us-central1
```

### Metrics

**Available in Cloud Console:**
- Request count
- Request latency
- Error rate
- Instance count
- CPU utilization
- Memory utilization

---

## 🐛 Troubleshooting

### Common Issues

**1. Build fails:**
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Check base image compatibility

**2. Deployment fails:**
- Verify gcloud authentication
- Check project permissions
- Verify image exists in Container Registry

**3. Service doesn't start:**
- Check Cloud Run logs
- Verify environment variables
- Check health check endpoint

**4. Database connection fails:**
- Verify Cloud SQL instance exists
- Check connection string
- Verify network connectivity

**5. Vertex AI/Firestore fails:**
- Verify service account permissions
- Check GOOGLE_APPLICATION_CREDENTIALS
- Verify API is enabled

---

## 📝 Environment Variables Reference

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | GCP project ID | `my-project-123` |
| `GCP_REGION` | GCP region | `us-central1` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8080` |
| `DATABASE_URL` | PostgreSQL connection | Auto-built |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account path | From Secret Manager |
| `API_KEY` | API authentication | Empty |
| `CHUNK_SIZE` | Text chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |

---

## 🚀 Quick Deployment Guide

### Step 1: Prerequisites

```bash
# Install gcloud CLI (if not installed)
# Install Docker (if not installed)

# Authenticate
gcloud auth login
gcloud auth configure-docker

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Step 1.5: Set Up Permissions (If Needed)

If you get permission errors, run the setup script:

```bash
python scripts/setup_permissions.py
```

Or manually grant permissions:

```bash
PROJECT_ID=$(gcloud config get-value project)
USER_EMAIL=$(gcloud config get-value account)

# Grant required roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=user:$USER_EMAIL \
  --role=roles/cloudbuild.builds.editor

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=user:$USER_EMAIL \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=user:$USER_EMAIL \
  --role=roles/iam.serviceAccountUser

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=user:$USER_EMAIL \
  --role=roles/storage.admin
```

### Step 2: Enable APIs

```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable sqladmin.googleapis.com  # If using Cloud SQL
```

### Step 3: Deploy

**Windows:**
```powershell
.\scripts\deploy.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### Step 4: Configure Environment Variables

```bash
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --set-env-vars "GCP_PROJECT_ID=your-project-id,GCP_REGION=us-central1"
```

### Step 5: Test

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe doc-summarizer-qa \
  --region us-central1 --format 'value(status.url)')

# Test
curl ${SERVICE_URL}/health
```

---

## 📊 Cost Estimation

### Cloud Run Pricing (Approximate)

**Free Tier:**
- 2 million requests/month
- 360,000 GB-seconds
- 180,000 vCPU-seconds

**Beyond Free Tier:**
- Requests: $0.40 per million
- CPU: $0.00002400 per vCPU-second
- Memory: $0.00000250 per GiB-second

**Estimated Monthly Cost (Light Usage):**
- ~$5-20/month (depending on usage)

### Cloud SQL Pricing

- Small instance: ~$10-50/month
- Or use external PostgreSQL

---

## 🔄 Update Deployment

### Update Code

```bash
# Rebuild and redeploy
./scripts/deploy.sh
```

### Update Environment Variables

```bash
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --update-env-vars "KEY=value"
```

### Rollback

```bash
# List revisions
gcloud run revisions list --service doc-summarizer-qa --region us-central1

# Rollback to previous revision
gcloud run services update-traffic doc-summarizer-qa \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100
```

---

## 📝 Key Takeaways

1. **Multi-stage builds** - Optimize image size
2. **Non-root user** - Security best practice
3. **Health checks** - Automatic monitoring
4. **Auto-scaling** - Cost-effective scaling
5. **Secret Manager** - Secure credential storage
6. **Cloud Run** - Serverless, pay-per-use

---

**Step 6 Status:** ✅ **COMPLETE**

**Next Step:** Step 7 - Logging & Polish
