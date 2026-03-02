#!/bin/bash
# Deploy PenLife Risk Profiler to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${GCLOUD_PROJECT_ID:-your-project-id}"
SERVICE_NAME="penlife-risk-profiler"
REGION="${GCLOUD_REGION:-us-central1}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "====================================="
echo "Deploying PenLife Risk Profiler"
echo "====================================="
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo "====================================="

# Step 1: Build and push Docker image
echo ""
echo "Step 1: Building Docker image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Step 2: Deploy to Cloud Run
echo ""
echo "Step 2: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"

# Step 3: Get service URL
echo ""
echo "Step 3: Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format 'value(status.url)')

echo ""
echo "====================================="
echo "✅ Deployment Complete!"
echo "====================================="
echo "Service URL: ${SERVICE_URL}"
echo ""
echo "API Endpoints:"
echo "  - Health: ${SERVICE_URL}/health"
echo "  - Docs: ${SERVICE_URL}/docs"
echo "  - GCS Processing: ${SERVICE_URL}/api/v1/process-from-gcs"
echo "  - File Upload: ${SERVICE_URL}/api/v1/fill-risk-profiler"
echo ""
echo "Test with:"
echo "curl -X POST \"${SERVICE_URL}/api/v1/process-from-gcs\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"gcs_path\":\"gs://bucket/file.pdf\"}'"
echo "====================================="
