# API Key Authentication Setup

## 🔐 Security Implementation

The PenLife Risk Profiler API is now secured with API key authentication using Google Secret Manager.

## Configuration

### API Key Storage
- **Location**: Google Secret Manager
- **Secret Name**: `penlife-api-key`
- **Secret ID**: `projects/penlife-associates/secrets/penlife-api-key/versions/latest`
- **API Key**: `cuWoV4_zcBUPq1y_UvV5daYkInqW_TPtYtJ0ALAcwrM`

### Service Account Permissions
- **Service Account**: `penlife-risk-profiler@penlife-associates.iam.gserviceaccount.com`
- **Role**: `roles/secretmanager.secretAccessor`

## Public Endpoints (No Auth Required)

The following endpoints are publicly accessible for monitoring:
- `GET /` - Service information
- `GET /health` - Health check
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI schema

## Protected Endpoints (Auth Required)

All API endpoints require the `X-API-Key` header:
- `POST /api/v1/fill-risk-profiler` - PDF processing
- `POST /api/v1/process-from-gcs` - GCS integration
- `POST /api/v1/extract-data` - Data extraction

## Usage Examples

### cURL with API Key

```bash
curl -X POST "https://penlife-risk-profiler-gvxy3xpnta-nw.a.run.app/api/v1/fill-risk-profiler" \
  -H "X-API-Key: cuWoV4_zcBUPq1y_UvV5daYkInqW_TPtYtJ0ALAcwrM" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@Cashcalc_risk_doc.pdf" \
  --output "output.pdf"
```

### Python with API Key

```python
import requests

api_key = "cuWoV4_zcBUPq1y_UvV5daYkInqW_TPtYtJ0ALAcwrM"
headers = {"X-API-Key": api_key}

with open("Cashcalc_risk_doc.pdf", "rb") as f:
    response = requests.post(
        "https://penlife-risk-profiler-gvxy3xpnta-nw.a.run.app/api/v1/fill-risk-profiler",
        headers=headers,
        files={"file": f}
    )

if response.status_code == 200:
    with open("output.pdf", "wb") as out:
        out.write(response.content)
    print("✅ Success!")
else:
    print(f"❌ Error {response.status_code}: {response.json()}")
```

### Xano Integration

The Xano function `fill_risk_profiler` has been updated to include the API key automatically:

```xs
api.request {
  url = "https://penlife-risk-profiler-gvxy3xpnta-nw.a.run.app/api/v1/fill-risk-profiler"
  method = "POST"
  params = $request_params
  headers = []
    |push:"Content-Type: multipart/form-data"
    |push:"X-API-Key: cuWoV4_zcBUPq1y_UvV5daYkInqW_TPtYtJ0ALAcwrM"
  timeout = 120000
}
```

## Error Responses

### 401 Unauthorized (Missing API Key)
```json
{
  "error": "Unauthorized",
  "message": "Missing X-API-Key header"
}
```

### 403 Forbidden (Invalid API Key)
```json
{
  "error": "Forbidden",
  "message": "Invalid API key"
}
```

## Rotating the API Key

To rotate the API key:

1. Generate a new key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Create new version in Secret Manager:
```bash
echo -n "NEW_KEY_HERE" | gcloud secrets versions add penlife-api-key --data-file=-
```

3. Update Xano function with the new key

4. Cloud Run will automatically pick up the new version on next deployment or restart

## Local Development

For local development, set the API key as an environment variable:

```bash
export API_KEY="cuWoV4_zcBUPq1y_UvV5daYkInqW_TPtYtJ0ALAcwrM"
uvicorn main:app --reload --port 8080
```

## Security Best Practices

✅ **Implemented:**
- API key stored in Google Secret Manager (encrypted at rest)
- Service account with minimal permissions (secretAccessor only)
- Public endpoints limited to health checks and documentation
- Failed auth attempts logged for monitoring
- API key never committed to git

⚠️ **Recommendations:**
- Rotate API key every 90 days
- Monitor Cloud Logging for unauthorized access attempts
- Consider rate limiting per API key in the future
- Use different API keys for different clients/environments
