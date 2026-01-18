# Database Setup for Cloud Run

## 🚨 Current Issue

The deployed service is trying to connect to PostgreSQL at `localhost:5432`, which doesn't exist in Cloud Run. You need to configure a database connection.

**Error:** `connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused`

---

## ✅ Solution Options

### Option 1: Cloud SQL (Recommended for Production)

Cloud SQL is Google's managed PostgreSQL service, perfect for Cloud Run.

#### Step 1: Create Cloud SQL Instance

```bash
gcloud sql instances create doc-summarizer-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=YOUR_SECURE_PASSWORD
```

**Tier Options:**
- `db-f1-micro` - Smallest (~$7/month, good for testing)
- `db-g1-small` - Small (~$25/month, production-ready)
- `db-n1-standard-1` - Standard (~$50/month, better performance)

#### Step 2: Create Database

```bash
gcloud sql databases create docsummarizer \
  --instance=doc-summarizer-db
```

#### Step 3: Create Database User

```bash
gcloud sql users create appuser \
  --instance=doc-summarizer-db \
  --password=YOUR_USER_PASSWORD
```

#### Step 4: Get Connection Name

```bash
gcloud sql instances describe doc-summarizer-db \
  --format='value(connectionName)'
```

Output: `PROJECT_ID:REGION:INSTANCE_NAME` (e.g., `myaisummarizerqa-484611:us-central1:doc-summarizer-db`)

#### Step 5: Grant Cloud Run Service Account Access

```bash
# Get Cloud Run service account
SERVICE_ACCOUNT=$(gcloud run services describe doc-summarizer-qa \
  --region us-central1 \
  --format 'value(spec.template.spec.serviceAccountName)')

# Grant Cloud SQL Client role
gcloud projects add-iam-policy-binding myaisummarizerqa-484611 \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/cloudsql.client"
```

#### Step 6: Update Cloud Run Service with Database Connection

```bash
# Get connection name
CONNECTION_NAME=$(gcloud sql instances describe doc-summarizer-db \
  --format='value(connectionName)')

# Update Cloud Run service
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --add-cloudsql-instances ${CONNECTION_NAME} \
  --set-env-vars "DATABASE_URL=postgresql://appuser:YOUR_USER_PASSWORD@/docsummarizer?host=/cloudsql/${CONNECTION_NAME}"
```

**Connection String Format:**
```
postgresql://USER:PASSWORD@/DATABASE?host=/cloudsql/PROJECT_ID:REGION:INSTANCE_NAME
```

#### Step 7: Initialize Database Tables

After deployment, initialize the tables:

```bash
# Option 1: Use Cloud SQL Proxy locally
# Download Cloud SQL Proxy: https://cloud.google.com/sql/docs/postgres/sql-proxy
# Then run: python scripts/init_db.py

# Option 2: SSH into Cloud Run (if enabled)
# Or tables will be created automatically on first successful connection
```

---

### Option 2: External PostgreSQL

If you have an existing PostgreSQL database accessible from the internet:

```bash
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=postgresql://user:password@HOST:5432/dbname"
```

**Note:** Ensure the database:
- Is accessible from Cloud Run's IP ranges
- Has firewall rules allowing Cloud Run access
- Uses SSL for security

---

### Option 3: Disable Database (Use Firestore Only)

If you want to use only Firestore for storage (no PostgreSQL):

```bash
# Leave DATABASE_URL empty or unset
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --update-env-vars "DATABASE_URL="
```

**Limitations:**
- Document metadata won't be stored in PostgreSQL
- Request history won't be tracked
- Some features may not work

---

## 🔐 Using Secret Manager (Recommended)

For better security, store database password in Secret Manager:

### Step 1: Create Secret

```bash
echo -n "YOUR_USER_PASSWORD" | gcloud secrets create db-password
```

### Step 2: Grant Access

```bash
# Get Cloud Run service account
SERVICE_ACCOUNT=$(gcloud run services describe doc-summarizer-qa \
  --region us-central1 \
  --format 'value(spec.template.spec.serviceAccountName)')

# Grant secret accessor role
gcloud secrets add-iam-policy-binding db-password \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 3: Update Service with Secret

```bash
CONNECTION_NAME=$(gcloud sql instances describe doc-summarizer-db \
  --format='value(connectionName)')

gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --add-cloudsql-instances ${CONNECTION_NAME} \
  --update-secrets=DATABASE_URL=db-password:latest \
  --set-env-vars "DATABASE_URL=postgresql://appuser:$(gcloud secrets versions access latest --secret=db-password)@/docsummarizer?host=/cloudsql/${CONNECTION_NAME}"
```

**Or use Secret Manager in the connection string:**
```bash
# Set DATABASE_URL to reference the secret
gcloud run services update doc-summarizer-qa \
  --region us-central1 \
  --update-secrets=DATABASE_PASSWORD=db-password:latest \
  --set-env-vars "DATABASE_URL=postgresql://appuser:${DATABASE_PASSWORD}@/docsummarizer?host=/cloudsql/${CONNECTION_NAME}"
```

---

## 🧪 Testing the Connection

After configuring the database:

1. **Check service logs:**
   ```bash
   gcloud run services logs tail doc-summarizer-qa --region us-central1
   ```

2. **Test health endpoint:**
   ```bash
   curl https://doc-summarizer-qa-1008530136324.us-central1.run.app/health
   ```

3. **Test document upload:**
   ```bash
   curl -X POST https://doc-summarizer-qa-1008530136324.us-central1.run.app/documents/upload \
     -F "file=@test.pdf"
   ```

---

## 📊 Quick Setup Script

Use the Python setup script:

```bash
python scripts/setup_cloud_sql.py
```

This script will:
1. ✅ Check if Cloud SQL instance exists (or create it)
2. ✅ Create database and user
3. ✅ Generate secure passwords
4. ✅ Grant Cloud Run service account access
5. ✅ Configure Cloud Run with database connection
6. ✅ Provide connection details

**Interactive prompts:**
- Asks for confirmation before creating resources
- Handles existing instances gracefully
- Shows passwords (save them securely!)

---

## 🔍 Troubleshooting

### Connection Refused

- Verify Cloud SQL instance is running
- Check connection name format
- Verify service account has `cloudsql.client` role
- Check Cloud Run service has `--add-cloudsql-instances` flag

### Authentication Failed

- Verify username and password
- Check database exists
- Verify user has proper permissions

### Timeout

- Check firewall rules
- Verify network connectivity
- Check instance is in same region

---

## 💰 Cost Estimation

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

## 📝 Next Steps

After setting up the database:

1. **Initialize tables:**
   - Tables will be created automatically on first connection
   - Or run `python scripts/init_db.py` locally with Cloud SQL Proxy

2. **Test the API:**
   - Upload a document
   - Check it's stored in both PostgreSQL and Firestore

3. **Monitor:**
   - Check Cloud Run logs
   - Monitor Cloud SQL metrics

---

For more details, see `docs/CLOUD_SQL_SETUP.md`
