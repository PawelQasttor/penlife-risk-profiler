"""
Test with actual sample PDFs
Run this to test end-to-end processing
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_extractor import PDFExtractor
from app.services.pdf_filler import PDFFiller
from app.services.validator import PDFValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_extraction():
    """Test extracting data from sample Cashcalc PDF"""
    # Path to sample PDF (adjust as needed)
    sample_pdf = Path(__file__).parent.parent.parent / "Cashcalc risk doc for George.pdf"

    if not sample_pdf.exists():
        logger.error(f"Sample PDF not found: {sample_pdf}")
        return False

    logger.info(f"Testing extraction from: {sample_pdf}")

    # Read PDF
    with open(sample_pdf, "rb") as f:
        pdf_bytes = f.read()

    # Validate
    validator = PDFValidator()
    is_valid, message = validator.validate_cashcalc_structure(pdf_bytes)
    logger.info(f"Validation: {message}")

    if not is_valid:
        logger.error("PDF validation failed")
        return False

    # Extract
    extractor = PDFExtractor()
    data = extractor.extract_data(pdf_bytes)

    logger.info(f"Extracted data for: {data.client_info.full_name}")
    logger.info(f"Risk profile: {data.risk_profile_result.risk_level}")

    if data.adjusted_risk_profile:
        logger.info(f"Adjusted risk: {data.adjusted_risk_profile.adjusted_level}")

    return True


def test_full_pipeline():
    """Test complete pipeline from Cashcalc to PenLife"""
    sample_pdf = Path(__file__).parent.parent.parent / "Cashcalc risk doc for George.pdf"

    if not sample_pdf.exists():
        logger.error(f"Sample PDF not found: {sample_pdf}")
        return False

    logger.info("Testing full pipeline...")

    # Read PDF
    with open(sample_pdf, "rb") as f:
        pdf_bytes = f.read()

    # Validate
    validator = PDFValidator()
    is_valid, message = validator.validate_cashcalc_structure(pdf_bytes)

    if not is_valid:
        logger.error(f"Validation failed: {message}")
        return False

    # Extract
    extractor = PDFExtractor()
    data = extractor.extract_data(pdf_bytes)

    # Fill template
    filler = PDFFiller()
    output_bytes = filler.fill_template(data)

    # Save output
    output_path = Path(__file__).parent.parent / "test_output.pdf"
    with open(output_path, "wb") as f:
        f.write(output_bytes)

    logger.info(f"✅ Success! Output saved to: {output_path}")
    logger.info(f"   File size: {len(output_bytes)} bytes")

    return True


def calibrate_template():
    """Generate calibration PDF to find exact coordinates"""
    logger.info("Generating calibration PDF...")

    filler = PDFFiller()
    output_path = Path(__file__).parent.parent / "template_calibration.pdf"
    filler.calibrate_coordinates(str(output_path))

    logger.info(f"✅ Calibration PDF saved to: {output_path}")
    logger.info("   Open this file to find exact coordinates for text placement")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "calibrate":
        calibrate_template()
    elif len(sys.argv) > 1 and sys.argv[1] == "extract":
        test_extraction()
    else:
        test_full_pipeline()
