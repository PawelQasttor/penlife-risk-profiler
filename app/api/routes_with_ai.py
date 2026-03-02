"""
Enhanced API routes with Vertex AI integration
"""

import logging
import io
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional

from app.services.pdf_extractor import PDFExtractor
from app.services.pdf_filler import PDFFiller
from app.services.validator import PDFValidator
from app.services.vertex_ai_service import VertexAIService
from app.config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Constants
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def get_vertex_ai_service() -> Optional[VertexAIService]:
    """Dependency to get Vertex AI service if enabled"""
    if settings.enable_ai_validation and settings.gcp_project_id:
        return VertexAIService(
            project_id=settings.gcp_project_id,
            location=settings.gcp_location,
            model_name=settings.vertex_ai_model
        )
    return None


@router.post("/process-pdf",
             response_class=StreamingResponse,
             summary="Process Risk Profiler with AI Validation",
             description="Upload a Cashcalc PDF, validate with AI, and receive populated PenLife Risk Profiler")
async def process_pdf_with_ai(
    file: UploadFile = File(..., description="Cashcalc risk questionnaire PDF"),
    enable_optimization: bool = True,
    ai_service: Optional[VertexAIService] = Depends(get_vertex_ai_service)
):
    """
    Process Cashcalc PDF with AI validation and optimization

    Args:
        file: Uploaded Cashcalc PDF file
        enable_optimization: Whether to use AI for text optimization
        ai_service: Vertex AI service (injected)

    Returns:
        StreamingResponse: Populated PenLife Risk Profiler PDF with optimized text

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

        # Validate file size
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
            )

        logger.info(f"Processing file: {file.filename} ({len(content)} bytes)")

        # Step 1: Extract data from source PDF
        extractor = PDFExtractor()
        extracted_data = extractor.extract_data(content)

        logger.info(f"Extracted data for client: {extracted_data.client_info.full_name}")

        # Step 2: AI Validation and Optimization (if enabled)
        optimized_data = extracted_data
        ai_summary = "AI validation not enabled"

        if ai_service and enable_optimization:
            logger.info("Running AI validation and optimization...")

            validation_result = ai_service.validate_and_optimize_data(extracted_data)

            if validation_result.get("success"):
                optimized_data = validation_result.get("optimized_data", extracted_data)
                ai_summary = validation_result.get("summary", "No changes made")

                logger.info(f"AI optimization complete: {ai_summary}")

                # Log any validation issues
                validation = validation_result.get("validation", {})
                if validation.get("issues"):
                    logger.warning(f"Validation issues: {validation['issues']}")
                if validation.get("warnings"):
                    logger.warning(f"Validation warnings: {validation['warnings']}")
            else:
                logger.warning(f"AI validation failed: {validation_result.get('error', 'Unknown error')}")
                # Continue with original data
                optimized_data = extracted_data

        # Step 3: Fill template with optimized data
        filler = PDFFiller()
        filled_pdf = filler.fill_template(optimized_data, content)

        logger.info(f"Generated PDF: {len(filled_pdf)} bytes")

        # Step 4: Return filled PDF
        output_filename = f"{extracted_data.client_info.full_name.replace(' ', '_')}_Risk_Profiler.pdf"

        return StreamingResponse(
            io.BytesIO(filled_pdf),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{output_filename}"',
                "X-AI-Summary": ai_summary,
                "X-Client-Name": extracted_data.client_info.full_name,
                "X-Adviser": extracted_data.client_info.created_by
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )


@router.post("/validate-data",
             summary="Validate Extracted Data with AI",
             description="Extract and validate data from Cashcalc PDF using AI")
async def validate_data(
    file: UploadFile = File(..., description="Cashcalc risk questionnaire PDF"),
    ai_service: Optional[VertexAIService] = Depends(get_vertex_ai_service)
):
    """
    Extract data and validate with AI (no PDF generation)

    Returns validation results and optimized data suggestions
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        content = await file.read()

        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
            )

        # Extract data
        extractor = PDFExtractor()
        extracted_data = extractor.extract_data(content)

        # Run AI validation if available
        if ai_service:
            validation_result = ai_service.validate_and_optimize_data(extracted_data)
            return {
                "client_name": extracted_data.client_info.full_name,
                "validation": validation_result.get("validation", {}),
                "optimizations_applied": validation_result.get("optimizations_applied", False),
                "summary": validation_result.get("summary", ""),
                "success": validation_result.get("success", False)
            }
        else:
            return {
                "client_name": extracted_data.client_info.full_name,
                "validation": {
                    "is_valid": True,
                    "message": "AI validation not enabled"
                },
                "optimizations_applied": False,
                "summary": "Data extracted successfully (no AI validation)"
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_validation_enabled": settings.enable_ai_validation,
        "text_optimization_enabled": settings.enable_text_optimization,
        "gcp_project": settings.gcp_project_id or "not configured"
    }


@router.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "ai_validation": settings.enable_ai_validation,
        "text_optimization": settings.enable_text_optimization,
        "gcp_location": settings.gcp_location,
        "vertex_ai_model": settings.vertex_ai_model,
        "max_upload_size_mb": MAX_FILE_SIZE_MB
    }
