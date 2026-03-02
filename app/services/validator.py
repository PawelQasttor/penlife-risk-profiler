"""
PDF validation service
Validates that uploaded PDFs match expected Cashcalc structure
"""

import logging
import io
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFValidator:
    """Validates Cashcalc PDF structure"""

    EXPECTED_PAGE_COUNT_MIN = 5
    EXPECTED_PAGE_COUNT_MAX = 7
    REQUIRED_TEXT_MARKERS = [
        "Attitude to Risk Questionnaire Results",
        "Questionnaire Answers",
        "Capacity For Loss",
        "Knowledge And Experience"
    ]

    def validate_cashcalc_structure(self, pdf_bytes: bytes) -> tuple[bool, str]:
        """
        Validate that PDF has expected Cashcalc structure

        Args:
            pdf_bytes: PDF file as bytes

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        try:
            # Open PDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            # Check page count
            page_count = len(doc)
            if page_count < self.EXPECTED_PAGE_COUNT_MIN or page_count > self.EXPECTED_PAGE_COUNT_MAX:
                return False, f"Expected {self.EXPECTED_PAGE_COUNT_MIN}-{self.EXPECTED_PAGE_COUNT_MAX} pages, got {page_count}"

            # Extract all text
            all_text = ""
            for page in doc:
                all_text += page.get_text()

            # Check for required text markers
            missing_markers = []
            for marker in self.REQUIRED_TEXT_MARKERS:
                if marker not in all_text:
                    missing_markers.append(marker)

            if missing_markers:
                return False, f"Missing required sections: {', '.join(missing_markers)}"

            # Validate first page has client name
            first_page = doc[0]
            first_page_text = first_page.get_text()

            if "for" not in first_page_text or "Created by" not in first_page_text:
                return False, "First page missing client information"

            doc.close()

            logger.info(f"PDF validation successful: {page_count} pages")
            return True, "Valid Cashcalc PDF structure"

        except Exception as e:
            logger.error(f"PDF validation error: {e}")
            return False, f"Error validating PDF: {str(e)}"


    def validate_template(self, template_path: str) -> tuple[bool, str]:
        """
        Validate PenLife template PDF exists and is accessible

        Args:
            template_path: Path to template PDF

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        try:
            doc = fitz.open(template_path)
            page_count = len(doc)
            doc.close()

            if page_count < 8:
                return False, f"Template has only {page_count} pages, expected at least 8"

            return True, "Valid template"

        except Exception as e:
            logger.error(f"Template validation error: {e}")
            return False, f"Error validating template: {str(e)}"
