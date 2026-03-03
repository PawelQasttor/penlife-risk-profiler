"""
API route definitions
"""

import logging
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

from app.services.pdf_extractor import PDFExtractor
from app.services.pdf_filler import PDFFiller
from app.services.validator import PDFValidator

# Google Cloud Storage support (optional)
try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# Request models
class ProcessGCSRequest(BaseModel):
    """Request to process PDF from Google Cloud Storage"""
    gcs_path: str
    discussion_points: Optional[str] = None
    output_gcs_path: Optional[str] = None


def download_from_gcs(gcs_path: str) -> bytes:
    """Download file from Google Cloud Storage"""
    if not GCS_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Google Cloud Storage not available. Install google-cloud-storage"
        )

    if not gcs_path.startswith("gs://"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GCS path: {gcs_path}. Must start with gs://"
        )

    try:
        path_parts = gcs_path[5:].split("/", 1)
        bucket_name = path_parts[0]
        blob_path = path_parts[1] if len(path_parts) > 1 else ""

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        return blob.download_as_bytes()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download from GCS: {str(e)}"
        )


def upload_to_gcs(gcs_path: str, data: bytes) -> str:
    """Upload file to Google Cloud Storage"""
    if not GCS_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="Google Cloud Storage not available"
        )

    if not gcs_path.startswith("gs://"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid GCS path: {gcs_path}. Must start with gs://"
        )

    try:
        path_parts = gcs_path[5:].split("/", 1)
        bucket_name = path_parts[0]
        blob_path = path_parts[1] if len(path_parts) > 1 else ""

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_string(data, content_type="application/pdf")

        return gcs_path
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload to GCS: {str(e)}"
        )


@router.post("/process-from-gcs",
             summary="Process PDF from Google Cloud Storage",
             description="Process a PDF from GCS with optional discussion points")
async def process_from_gcs(request: ProcessGCSRequest):
    """
    Process Cashcalc PDF from Google Cloud Storage and upload result back to GCS

    Args:
        request: GCS paths and optional discussion points

    Returns:
        dict with output GCS path and metadata

    Raises:
        HTTPException: If processing fails
    """
    try:
        logger.info(f"Processing from GCS: {request.gcs_path}")

        # Download PDF from GCS
        pdf_bytes = download_from_gcs(request.gcs_path)
        logger.info(f"Downloaded {len(pdf_bytes)} bytes from GCS")

        # Extract data
        extractor = PDFExtractor()
        risk_profile_data = extractor.extract_data(pdf_bytes)

        logger.info(f"Extracted data for client: {risk_profile_data.client_info.full_name}")

        # Fill template with discussion points
        filler = PDFFiller()
        output_pdf_bytes = filler.fill_template(
            risk_profile_data,
            pdf_bytes,
            request.discussion_points
        )

        logger.info(f"Generated filled PDF ({len(output_pdf_bytes)} bytes)")

        # Determine output path
        output_path = request.output_gcs_path
        if not output_path:
            # Add _filled before .pdf extension
            output_path = request.gcs_path.replace(".pdf", "_filled.pdf")

        # Upload to GCS
        upload_to_gcs(output_path, output_pdf_bytes)
        logger.info(f"Uploaded to GCS: {output_path}")

        return {
            "success": True,
            "output_gcs_path": output_path,
            "client_name": risk_profile_data.client_info.full_name,
            "file_size_kb": len(output_pdf_bytes) / 1024,
            "discussion_points_included": bool(request.discussion_points)
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error processing from GCS: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.post("/fill-risk-profiler",
             response_class=StreamingResponse,
             summary="Fill PenLife Risk Profiler",
             description="Upload a Cashcalc risk questionnaire PDF and receive a populated PenLife Risk Profiler PDF")
async def fill_risk_profiler(
    file: UploadFile = File(..., description="Cashcalc risk questionnaire PDF"),
    discussion_points: Optional[str] = Form(None, description="Optional discussion points")
):
    # Normalize empty strings to None
    if discussion_points is not None and not discussion_points.strip():
        discussion_points = None
    """
    Process Cashcalc PDF and generate populated PenLife Risk Profiler

    Args:
        file: Uploaded Cashcalc PDF file

    Returns:
        StreamingResponse: Populated PenLife Risk Profiler PDF

    Raises:
        HTTPException: If file is invalid or processing fails
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="File must be a PDF"
            )

        # Read file content
        content = await file.read()

        # Check file size
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
            )

        logger.info(f"Processing file: {file.filename} ({len(content)} bytes)")

        # Step 1: Validate PDF structure
        validator = PDFValidator()
        is_valid, validation_message = validator.validate_cashcalc_structure(content)

        if not is_valid:
            logger.warning(f"PDF validation failed: {validation_message}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid PDF structure: {validation_message}"
            )

        # Step 2: Extract data from Cashcalc PDF
        extractor = PDFExtractor()
        risk_profile_data = extractor.extract_data(content)

        logger.info(f"Extracted data for client: {risk_profile_data.client_info.full_name}")

        # Step 3: Fill PenLife template with discussion points
        filler = PDFFiller()
        output_pdf_bytes = filler.fill_template(risk_profile_data, content, discussion_points)

        # Create filename from client name
        client_name = risk_profile_data.client_info.full_name.replace(" ", "_")
        output_filename = f"PenLife_Risk_Profiler_{client_name}.pdf"

        logger.info(f"Successfully generated PDF: {output_filename}")

        # Return PDF as streaming response
        return StreamingResponse(
            io.BytesIO(output_pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{output_filename}"'
            }
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.post("/extract-data",
             summary="Extract Data Only",
             description="Extract structured data from Cashcalc PDF without generating output PDF")
async def extract_data_only(
    file: UploadFile = File(..., description="Cashcalc risk questionnaire PDF")
):
    """
    Extract data from Cashcalc PDF and return as JSON

    Useful for debugging or integration with other systems
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="File must be a PDF"
            )

        # Read file content
        content = await file.read()

        # Check file size
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
            )

        # Validate PDF structure
        validator = PDFValidator()
        is_valid, validation_message = validator.validate_cashcalc_structure(content)

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid PDF structure: {validation_message}"
            )

        # Extract data
        extractor = PDFExtractor()
        risk_profile_data = extractor.extract_data(content)

        return risk_profile_data

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error extracting data: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting data: {str(e)}"
        )
