# Cloud SQL Setup Guide

## Overview

For production deployment, you'll need a PostgreSQL database. This guide shows how to set up Cloud SQL (managed PostgreSQL) on GCP.

---

## Option 1: Cloud SQL (Recommended for Production)

### Step 1: Create Cloud SQL Instance

```bash
gcloud sql instances create doc-summarizer-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_ROOT_PASSWORD
```

**Tier Options:**
- `db-f1-micro` - Smallest (suitable for development, ~$7/month)
- `db-g1-small` - Small (suitable for production, ~$25/month)
- `db-n1-standard-1` - Standard (better performance, ~$50/month)

### Step 2: Create Database

```bash
gcloud sql databases create docsummarizer \
  --instance=doc-summarizer-db
```

### Step 3: Create Database User

```bash
gcloud sql users create appuser \
  --instance=doc-summarizer-db \
  --password=YOUR_PASSWORD
```

### Step 4: Get Connection Name

```bash
gcloud sql instances describe doc-summarizer-db \
  --format='value(connectionName)'
```

Output: `PROJECT_ID:REGION:INSTANCE_NAME`

### Step 5: Configure Cloud Run Connection

**Option A: Unix Socket (Recommended)**

```bash
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --add-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME \
  --set-env-vars "DATABASE_URL=postgresql://appuser:password@/docsummarizer?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME"
```

**Option B: Private IP**

```bash
# Enable private IP
gcloud sql instances patch doc-summarizer-db \
  --network=default \
  --no-assign-ip

# Use private IP in connection string
DATABASE_URL=postgresql://appuser:password@PRIVATE_IP:5432/docsummarizer
```

### Step 6: Grant Cloud Run Service Account Access

```bash
# Get Cloud Run service account
SERVICE_ACCOUNT=$(gcloud run services describe doc-summarizer-qa \
  --region us-central1 \
  --format 'value(spec.template.spec.serviceAccountName)')

# Grant Cloud SQL Client role
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudsql.client"
```

---

## Option 2: External PostgreSQL

If you have an existing PostgreSQL database:

```bash
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=postgresql://user:password@HOST:5432/dbname"
```

**Note:** Ensure the database is accessible from Cloud Run (public IP or VPC).

---

## Option 3: SQLite (Development Only)

For local development without PostgreSQL:

```python
# In app/db/base.py, use SQLite
DATABASE_URL = "sqlite:///./docsummarizer.db"
```

**⚠️ Not recommended for production!**

---

## Initialize Database Tables

After deployment, initialize tables:

```bash
# Option 1: SSH into Cloud Run (if enabled)
gcloud run services proxy doc-summarizer-qa --region us-central1

# Option 2: Run init script locally pointing to Cloud SQL
python scripts/init_db.py
```

Or tables will be created automatically on first request (if connection works).

---

## Connection String Format

### Cloud SQL (Unix Socket)
```
postgresql://user:password@/dbname?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
```

### Cloud SQL (Private IP)
```
postgresql://user:password@PRIVATE_IP:5432/dbname
```

### External PostgreSQL
```
postgresql://user:password@HOST:5432/dbname
```

---

## Security Best Practices

1. **Use Secret Manager** for passwords:
   ```bash
   echo -n "your-password" | gcloud secrets create db-password
   
   gcloud run services update doc-summarizer-qa \
     --update-secrets=DATABASE_URL=db-password:latest
   ```

2. **Use least privilege** - Grant only necessary permissions

3. **Enable SSL** - Use SSL connections for production

4. **Private IP** - Use private IP when possible (more secure)

---

## Troubleshooting

### Connection Refused

- Verify Cloud SQL instance is running
- Check connection name format
- Verify service account has `cloudsql.client` role

### Authentication Failed

- Verify username and password
- Check database exists
- Verify user has proper permissions

### Timeout

- Check firewall rules
- Verify network connectivity
- Check instance is in same region

---

## Cost Estimation

**Cloud SQL db-f1-micro:**
- ~$7-10/month
- 0.6 GB RAM
- Shared CPU
- 10 GB storage

**Cloud SQL db-g1-small:**
- ~$25-30/month
- 1.7 GB RAM
- Shared CPU
- 10 GB storage

---

For more details, see: https://cloud.google.com/sql/docs/postgres
