#!/bin/bash
# Deployment script for GCP Cloud Run

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  PenLife Risk Profiler - GCP Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if required variables are set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${YELLOW}Error: GCP_PROJECT_ID environment variable not set${NC}"
    echo "Usage: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

# Configuration
SERVICE_NAME="penlife-risk-profiler"
REGION="${GCP_REGION:-us-central1}"
IMAGE_NAME="gcr.io/${GCP_PROJECT_ID}/${SERVICE_NAME}"

echo -e "\n${GREEN}Configuration:${NC}"
echo "  Project ID: $GCP_PROJECT_ID"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Image: $IMAGE_NAME"

# Step 1: Enable required APIs
echo -e "\n${GREEN}Step 1: Enabling required GCP APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    aiplatform.googleapis.com \
    --project=$GCP_PROJECT_ID

# Step 2: Build container image
echo -e "\n${GREEN}Step 2: Building container image...${NC}"
gcloud builds submit \
    --tag $IMAGE_NAME \
    --project=$GCP_PROJECT_ID \
    .

# Step 3: Deploy to Cloud Run
echo -e "\n${GREEN}Step 3: Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-env-vars "GCP_PROJECT_ID=$GCP_PROJECT_ID,GCP_LOCATION=$REGION,ENABLE_AI_VALIDATION=true,ENABLE_TEXT_OPTIMIZATION=true" \
    --project=$GCP_PROJECT_ID

# Step 4: Get service URL
echo -e "\n${GREEN}Step 4: Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --format 'value(status.url)' \
    --project=$GCP_PROJECT_ID)

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\nService URL: ${YELLOW}$SERVICE_URL${NC}"
echo -e "\nTest endpoints:"
echo -e "  Health: ${YELLOW}$SERVICE_URL/health${NC}"
echo -e "  Config: ${YELLOW}$SERVICE_URL/config${NC}"
echo -e "  API Docs: ${YELLOW}$SERVICE_URL/docs${NC}"

echo -e "\n${GREEN}Upload a PDF:${NC}"
echo -e "  curl -X POST ${YELLOW}$SERVICE_URL/process-pdf${NC} \\"
echo -e "    -F 'file=@your-file.pdf' \\"
echo -e "    --output result.pdf"
