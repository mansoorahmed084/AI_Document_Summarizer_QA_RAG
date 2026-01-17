# Deployment Troubleshooting Guide

## Container Failed to Start

### Error: "The user-provided container failed to start and listen on the port"

**Symptoms:**
- Deployment fails with timeout error
- Container doesn't start within allocated timeout
- Logs show startup errors

**Common Causes:**

1. **Database Connection Blocking Startup**
   - The app tries to connect to a database that doesn't exist
   - Solution: Database initialization is now non-blocking

2. **Missing Environment Variables**
   - Required GCP credentials not set
   - Solution: Set `GCP_PROJECT_ID` and `GCP_REGION` in Cloud Run

3. **Service Initialization Failures**
   - Firestore or Vertex AI initialization fails
   - Solution: Services now initialize gracefully on first use

**Fixes Applied:**

1. ✅ Made database initialization non-blocking
2. ✅ Added connection timeout (5 seconds)
3. ✅ Made service initialization graceful (don't fail startup)
4. ✅ Health endpoint works even if services aren't initialized

**Next Steps:**

1. Rebuild and redeploy:
   ```bash
   python scripts/deploy.py
   ```

2. Check Cloud Run logs if deployment still fails:
   ```bash
   gcloud run services logs read doc-summarizer-qa --region us-central1
   ```

3. Verify environment variables are set:
   ```bash
   gcloud run services describe doc-summarizer-qa --region us-central1
   ```

## Database Connection Issues

If you're using Cloud SQL, make sure:

1. Cloud SQL instance exists
2. Cloud Run service account has `cloudsql.client` role
3. Connection string is correct
4. Cloud SQL Proxy is configured (if using Unix socket)

See `docs/CLOUD_SQL_SETUP.md` for details.

## Service Account Permissions

Make sure the Cloud Run service account has:
- `roles/cloudsql.client` (if using Cloud SQL)
- `roles/datastore.user` (for Firestore)
- `roles/aiplatform.user` (for Vertex AI)

## Viewing Logs

```bash
# Stream logs
gcloud run services logs tail doc-summarizer-qa --region us-central1

# View recent logs
gcloud run services logs read doc-summarizer-qa --region us-central1 --limit 50
```
