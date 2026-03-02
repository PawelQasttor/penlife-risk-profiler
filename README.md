# PenLife Risk Profiler - Cloud Run Service

Automated PDF processing service that extracts risk questionnaire data from Cashcalc PDFs and populates PenLife Risk Profiler templates.

## Features

- 🚀 **Cloud Run Ready** - Containerized and optimized for Google Cloud Run
- 🔄 **Consistent Processing** - Handles all Cashcalc PDFs with same structure
- 📄 **Template Overlay** - Preserves PenLife branding by overlaying text on existing template
- ⚡ **Fast API** - RESTful API with automatic documentation
- 🧪 **Local Testing** - Full local development environment
- ✅ **Validation** - Ensures PDF structure matches expected format

## Quick Start (Local Development)

### Option 1: Python Virtual Environment (Recommended for Development)

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Option 2: Docker (Matches Cloud Run)

```bash
# Build the container
docker build -t penlife-risk-profiler .

# Run locally
docker run -p 8080:8080 penlife-risk-profiler
```

### Option 3: Docker Compose (Hot-Reload Development)

```bash
# Start with hot-reload
docker-compose up

# Rebuild after dependency changes
docker-compose up --build
```

## Using the API

### Interactive Documentation

Visit `http://localhost:8080/docs` for Swagger UI with interactive testing.

### cURL Example

```bash
curl -X POST "http://localhost:8080/api/v1/fill-risk-profiler" \
  -H "accept: application/pdf" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/Cashcalc_risk_doc.pdf" \
  --output "PenLife_Risk_Profiler_Completed.pdf"
```

### Python Example

```python
import requests

# Upload Cashcalc PDF
with open("Cashcalc_risk_doc.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8080/api/v1/fill-risk-profiler",
        files={"file": f}
    )

# Save populated PenLife PDF
if response.status_code == 200:
    with open("output.pdf", "wb") as out:
        out.write(response.content)
    print("PDF generated successfully!")
else:
    print(f"Error: {response.json()}")
```

## API Endpoints

### `POST /api/v1/fill-risk-profiler`

Upload a Cashcalc risk questionnaire PDF and receive a populated PenLife Risk Profiler PDF.

**Request:**
- Content-Type: `multipart/form-data`
- Parameter: `file` (PDF file)

**Response:**
- Content-Type: `application/pdf`
- Body: Populated PenLife Risk Profiler PDF

**Status Codes:**
- `200` - Success
- `400` - Invalid PDF structure or format
- `413` - File too large (>10MB)
- `500` - Processing error

### `GET /health`

Health check endpoint for Cloud Run.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/

# Test with sample PDFs
python tests/test_sample_pdfs.py
```

## Deployment to Google Cloud Run

### Prerequisites

- Google Cloud Project
- gcloud CLI installed and authenticated
- Billing enabled

### Deploy

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export SERVICE_NAME="penlife-risk-profiler"
export REGION="us-central1"

# Build and deploy
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 60

# Get the service URL
gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.url)'
```

### Environment Variables (Optional)

```bash
# Deploy with environment variables
gcloud run deploy $SERVICE_NAME \
  --source . \
  --set-env-vars="MAX_FILE_SIZE_MB=10,LOG_LEVEL=INFO"
```

## Project Structure

```
penlife-risk-profiler/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── requirements-dev.txt             # Development dependencies
├── Dockerfile                       # Container definition
├── docker-compose.yml               # Local development setup
├── .dockerignore                    # Docker build exclusions
├── .gitignore                       # Git exclusions
├── README.md                        # This file
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                # API route definitions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py         # Extract data from Cashcalc PDF
│   │   ├── pdf_filler.py            # Fill PenLife template
│   │   └── validator.py             # PDF structure validation
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic data models
│   └── config/
│       ├── __init__.py
│       ├── extraction_patterns.json # Cashcalc extraction patterns
│       └── template_coordinates.json# PenLife coordinate mapping
├── templates/
│   └── PenLife Risk Profiler.pdf    # Template file
└── tests/
    ├── __init__.py
    ├── test_extractor.py            # Extraction tests
    ├── test_filler.py               # Filling tests
    └── test_sample_pdfs.py          # End-to-end tests
```

## Configuration

### Extraction Patterns (`app/config/extraction_patterns.json`)

Defines how to extract data from Cashcalc PDFs. Modify this if the source PDF structure changes.

### Template Coordinates (`app/config/template_coordinates.json`)

Defines where to place text in the PenLife template. Adjust coordinates if template layout changes.

## Development

### Code Style

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

### Adding New Fields

1. Update `extraction_patterns.json` with new field patterns
2. Update `template_coordinates.json` with new field positions
3. Update `RiskProfileData` model in `schemas.py`
4. Test with sample PDFs

## Troubleshooting

### PDF Text Not Appearing

- Check coordinate values in `template_coordinates.json`
- Verify font is available in the container
- Check if text color matches background

### Extraction Errors

- Verify Cashcalc PDF has expected structure
- Check page numbers in extraction patterns
- Review logs for specific error messages

### Local Development Issues

**Port already in use:**
```bash
# Change port
uvicorn main:app --reload --port 8081
```

**Module import errors:**
```bash
# Ensure you're in the project root and venv is activated
cd penlife-risk-profiler
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

## Performance

- **Cold Start**: ~2-3 seconds (Cloud Run)
- **Warm Request**: ~500ms - 1s per PDF
- **Memory Usage**: ~200-300MB per request
- **Recommended Cloud Run Config**: 1 CPU, 1Gi memory

## Security Considerations

- File size limits enforced (10MB default)
- PDF validation before processing
- No persistent storage of uploaded files
- CORS headers configurable
- Consider adding authentication for production

## License

Proprietary - PenLife Associates

## Support

For issues or questions, contact: enquiries@pen-life.co.uk
