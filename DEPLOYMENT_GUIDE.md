# Deployment Guide - Cloud Run via CLI

## Prerequisites

1. **Google Cloud SDK** installed:
   ```bash
   # Install gcloud CLI
   # https://cloud.google.com/sdk/docs/install
   ```

2. **Git** installed

3. **Google Cloud Project** with billing enabled

## Step 1: Setup Git Repository

```bash
# Navigate to project
cd C:/projects/penlife/penlife-risk-profiler

# Initialize git (if not already done)
git init

# Create .gitignore
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
*.pdf
!templates/*.pdf
.env
.venv
*.log
.DS_Store
output/
test_output.pdf
calibration_output.pdf
coordinates_picked.json
EOF

# Add all files
git add .

# Commit
git commit -m "Initial commit - PenLife Risk Profiler"

# Create GitHub repo (if needed)
# Go to https://github.com/new and create a new repo
# Then connect:
git remote add origin https://github.com/YOUR_USERNAME/penlife-risk-profiler.git
git branch -M main
git push -u origin main
```

## Step 2: Google Cloud Setup

### Login to Google Cloud

```bash
# Login to your Google account
gcloud auth login

# Set your project ID
export GCLOUD_PROJECT_ID="your-project-id"
gcloud config set project $GCLOUD_PROJECT_ID

# Set region
export GCLOUD_REGION="us-central1"
gcloud config set run/region $GCLOUD_REGION

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  storage-api.googleapis.com \
  storage-component.googleapis.com
```

### Create Service Account (for GCS access)

```bash
# Create service account
gcloud iam service-accounts create penlife-processor \
  --display-name="PenLife PDF Processor"

# Grant Cloud Storage access
gcloud projects add-iam-policy-binding $GCLOUD_PROJECT_ID \
  --member="serviceAccount:penlife-processor@${GCLOUD_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

## Step 3: Deploy to Cloud Run

### Option A: Using Deployment Script

```bash
# Make script executable
chmod +x deploy_to_cloudrun.sh

# Deploy
GCLOUD_PROJECT_ID=your-project-id ./deploy_to_cloudrun.sh
```

### Option B: Manual Deployment

```bash
# Build and push Docker image
gcloud builds submit --tag gcr.io/$GCLOUD_PROJECT_ID/penlife-risk-profiler

# Deploy to Cloud Run
gcloud run deploy penlife-risk-profiler \
  --image gcr.io/$GCLOUD_PROJECT_ID/penlife-risk-profiler \
  --platform managed \
  --region $GCLOUD_REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --service-account penlife-processor@${GCLOUD_PROJECT_ID}.iam.gserviceaccount.com

# Get service URL
gcloud run services describe penlife-risk-profiler \
  --platform managed \
  --region $GCLOUD_REGION \
  --format 'value(status.url)'
```

## Step 4: Test the Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe penlife-risk-profiler \
  --platform managed \
  --region $GCLOUD_REGION \
  --format 'value(status.url)')

# Test health endpoint
curl ${SERVICE_URL}/health

# Test GCS processing
curl -X POST "${SERVICE_URL}/api/v1/process-from-gcs" \
  -H "Content-Type: application/json" \
  -d '{
    "gcs_path": "gs://your-bucket/source.pdf",
    "discussion_points": "• Point 1\n• Point 2",
    "output_gcs_path": "gs://your-bucket/output/filled.pdf"
  }'
```

## API Endpoints

Once deployed, your service will have:

- **Health Check**: `GET /health`
- **API Docs**: `GET /docs`
- **Process from GCS**: `POST /api/v1/process-from-gcs`
  ```json
  {
    "gcs_path": "gs://bucket/source.pdf",
    "discussion_points": "Optional text",
    "output_gcs_path": "gs://bucket/output.pdf"
  }
  ```
- **File Upload**: `POST /api/v1/fill-risk-profiler`
  - Form data with file upload
  - Optional `discussion_points` field

## Switching Google Accounts

To switch to a different Google account:

```bash
# Logout current account
gcloud auth revoke

# Login with new account
gcloud auth login

# List accounts
gcloud auth list

# Switch between accounts
gcloud config set account NEW_ACCOUNT@gmail.com
```

## Environment Variables

Set these in your deployment:

- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID (auto-set)
- Service account credentials are auto-configured via Cloud Run

## Monitoring

```bash
# View logs
gcloud run services logs read penlife-risk-profiler \
  --region $GCLOUD_REGION \
  --limit 50

# View service details
gcloud run services describe penlife-risk-profiler \
  --region $GCLOUD_REGION
```

## Updating the Service

```bash
# After making code changes
git add .
git commit -m "Your changes"
git push

# Redeploy
./deploy_to_cloudrun.sh
```

## Cost Optimization

```bash
# Set min instances to 0 (scale to zero)
gcloud run services update penlife-risk-profiler \
  --region $GCLOUD_REGION \
  --min-instances 0

# Set max instances
gcloud run services update penlife-risk-profiler \
  --region $GCLOUD_REGION \
  --max-instances 5
```

## Troubleshooting

```bash
# Check build logs
gcloud builds list --limit 5

# Check deployment logs
gcloud run services logs read penlife-risk-profiler --region $GCLOUD_REGION

# Test locally with Docker
docker build -t penlife-test .
docker run -p 8080:8080 penlife-test
```
