#!/bin/bash
# Deployment script for Cloud Run

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying AI Document Summarizer & Q&A to Cloud Run${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Project: ${PROJECT_ID}${NC}"

# Set variables
SERVICE_NAME="doc-summarizer-qa"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Build Docker image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:latest .

# Push to Container Registry
echo -e "${YELLOW}📤 Pushing image to Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"

# Check if service exists
if gcloud run services describe ${SERVICE_NAME} --region ${REGION} &>/dev/null; then
    echo -e "${YELLOW}   Updating existing service...${NC}"
    DEPLOY_CMD="update"
else
    echo -e "${YELLOW}   Creating new service...${NC}"
    DEPLOY_CMD="deploy"
fi

gcloud run services ${DEPLOY_CMD} ${SERVICE_NAME} \
    --image ${IMAGE_NAME}:latest \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080 \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},GCP_REGION=${REGION}"

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}🌐 Service URL: ${SERVICE_URL}${NC}"
echo -e "${GREEN}📚 API Docs: ${SERVICE_URL}/docs${NC}"
echo -e "${GREEN}❤️  Health Check: ${SERVICE_URL}/health${NC}"
