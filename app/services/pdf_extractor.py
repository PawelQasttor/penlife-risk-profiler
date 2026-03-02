"""
PDF extraction service
Extracts structured data from Cashcalc risk questionnaire PDFs
"""

import logging
import re
import fitz  # PyMuPDF
from typing import Optional

from app.models.schemas import (
    RiskProfileData,
    ClientInfo,
    RiskQuestionnaireAnswers,
    CapacityForLoss,
    KnowledgeExperience,
    RiskProfileResult,
    AdjustedRiskProfile
)

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extracts data from Cashcalc PDF"""

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean extracted text to fix encoding issues"""
        if not text:
            return text

        # Fix common encoding issues
        replacements = {
            'â€™': "'",  # Smart apostrophe
            'â€œ': '"',  # Smart quote left
            'â€': '"',   # Smart quote right
            'â€"': '-',  # Em dash
            'â€"': '-',  # En dash
            'â€¦': '...',  # Ellipsis
            'Â': '',     # Non-breaking space artifacts
            'â€˜': "'",  # Left single quote
            'â€²': "'",  # Right single quote
            'â··': "'",  # Another apostrophe variant
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Normalize whitespace
        text = ' '.join(text.split())

        return text

    def extract_data(self, pdf_bytes: bytes) -> RiskProfileData:
        """
        Extract all data from Cashcalc PDF

        Args:
            pdf_bytes: PDF file as bytes

        Returns:
            RiskProfileData object with extracted data
        """
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        try:
            # Extract from each page
            client_info = self._extract_client_info(doc[0])
            questionnaire = self._extract_questionnaire_answers(doc[1])
            capacity = self._extract_capacity_for_loss(doc[2])
            knowledge = self._extract_knowledge_experience(doc[2])
            risk_result = self._extract_risk_profile(doc[3])
            adjusted_risk = self._extract_adjusted_risk_profile(doc[5]) if len(doc) > 5 else None

            doc.close()

            return RiskProfileData(
                client_info=client_info,
                questionnaire_answers=questionnaire,
                capacity_for_loss=capacity,
                knowledge_experience=knowledge,
                risk_profile_result=risk_result,
                adjusted_risk_profile=adjusted_risk
            )

        except Exception as e:
            logger.error(f"Error extracting data: {e}", exc_info=True)
            doc.close()
            raise

    def _extract_client_info(self, page) -> ClientInfo:
        """Extract client information from first page"""
        text = page.get_text()

        # Extract client name (after "for" and before "Created by")
        name_match = re.search(r'for\s+([^\n]+)\s+Created by', text, re.DOTALL)
        full_name = name_match.group(1).strip() if name_match else "Unknown Client"

        # Extract created by
        created_by_match = re.search(r'Created by\s+([^\n]+)', text)
        created_by = created_by_match.group(1).strip() if created_by_match else "Unknown Adviser"

        # Extract company (just PenLife Associates)
        company = "PenLife Associates"

        # Extract date
        date_match = re.search(r'Completed on\s+([^\n]+)', text)
        completion_date = date_match.group(1).strip() if date_match else "Unknown Date"

        return ClientInfo(
            full_name=full_name,
            created_by=created_by,
            company=company,
            completion_date=completion_date
        )

    def _extract_questionnaire_answers(self, page) -> RiskQuestionnaireAnswers:
        """Extract questionnaire answers from page 2"""
        text = page.get_text()

        def extract_answer(question_num: int, text: str) -> str:
            """Extract answer for a specific question number"""
            # Match question statement (ending with . or ? or :), then newline, then capture answer
            # Stop at next question number or "Investment Term"
            pattern = rf'{question_num}\.\s+.+?[.?:]\s*\n(.+?)(?=\n\d+\.|Investment Term|$)'
            match = re.search(pattern, text, re.DOTALL)
            if match:
                answer = match.group(1).strip()
                # Clean up multi-line answers
                answer = ' '.join(answer.split('\n'))
                # Clean encoding issues
                answer = self._clean_text(answer)
                return answer
            return "Not provided"

        # Extract investment term
        term_match = re.search(r'Investment Term\s+([^\n]+)', text)
        investment_term = term_match.group(1).strip() if term_match else "Not specified"

        return RiskQuestionnaireAnswers(
            q1_explore_opportunities=extract_answer(1, text),
            q2_best_return=extract_answer(2, text),
            q3_typical_attitude=extract_answer(3, text),
            q4_past_risk=extract_answer(4, text),
            q5_safe_steady=extract_answer(5, text),
            q6_high_growth=extract_answer(6, text),
            q7_willing_to_invest=extract_answer(7, text),
            q8_friend_describe=extract_answer(8, text),
            q9_highs_and_lows=extract_answer(9, text),
            q10_two_products=extract_answer(10, text),
            q11_small_certain=extract_answer(11, text),
            q12_losses_or_gains=extract_answer(12, text),
            q13_money_safe=extract_answer(13, text),
            investment_term=investment_term
        )

    def _extract_capacity_for_loss(self, page) -> CapacityForLoss:
        """Extract capacity for loss answers from page 3"""
        text = page.get_text()

        def extract_capacity_answer(question_num: int, text: str) -> str:
            """Extract capacity for loss answer"""
            # Match question, then look for answer starting on new line
            pattern = rf'{question_num}\.\s+.+?\n((?:Yes|No|Not |I |Maybe|Sometimes|Always|Never|Strongly).+?)(?=\n\d+\.|Knowledge And Experience|$)'
            match = re.search(pattern, text, re.DOTALL)
            if match:
                answer = match.group(1).strip()
                answer = ' '.join(answer.split('\n'))
                # Clean encoding issues
                answer = self._clean_text(answer)
                return answer
            return "Not provided"

        return CapacityForLoss(
            emergency_expenses=extract_capacity_answer(1, text),
            daily_living_expenses=extract_capacity_answer(2, text),
            significant_proportion=extract_capacity_answer(3, text),
            major_commitments=extract_capacity_answer(4, text),
            dependants=extract_capacity_answer(5, text)
        )

    def _extract_knowledge_experience(self, page) -> KnowledgeExperience:
        """Extract knowledge and experience from page 3"""
        text = page.get_text()

        # Extract after "Knowledge And Experience" section
        knowledge_section = re.search(r'Knowledge And Experience\s+(.+?)$', text, re.DOTALL)

        if knowledge_section:
            section_text = knowledge_section.group(1)

            def extract_knowledge_answer(question_num: int, text: str) -> str:
                # Match question, then look for answer starting on new line
                # Answer typically starts with Yes/No/I/Not etc.
                pattern = rf'{question_num}\.\s+.+?\n((?:Yes|No|Not |I |Maybe|Sometimes|Always|Never|Strongly).+?)(?=\n\d+\.|$)'
                match = re.search(pattern, text, re.DOTALL)
                if match:
                    answer = match.group(1).strip()
                    answer = ' '.join(answer.split('\n'))
                    # Clean encoding issues
                    answer = self._clean_text(answer)
                    return answer
                return "Not provided"

            return KnowledgeExperience(
                relevant_profession=extract_knowledge_answer(1, section_text),
                past_investments=extract_knowledge_answer(2, section_text)
            )

        return KnowledgeExperience(
            relevant_profession="Not provided",
            past_investments="Not provided"
        )

    def _extract_risk_profile(self, page) -> RiskProfileResult:
        """Extract risk profile result from page 4"""
        text = page.get_text()

        # Extract risk level (e.g., "4 - Moderate to Adventurous")
        risk_match = re.search(r'(\d+)\s+-\s+([^\n]+)', text)
        if risk_match:
            risk_number = int(risk_match.group(1))
            risk_level = f"{risk_number} - {risk_match.group(2).strip()}"
        else:
            risk_number = 3
            risk_level = "3 - Moderate"

        # Extract investment term
        term_match = re.search(r'(Short Term|Medium Term|Long Term)\s+\([^)]+\)', text)
        investment_term = term_match.group(0) if term_match else "Medium Term (8 - 15 Years)"

        # Extract growth rates (all three percentages appear together after labels)
        # Find the section with growth rates and extract all three percentages in order
        growth_section = re.search(r'Historic Growth Rates.*?(-?\d+\.\d+)%\s+(-?\d+\.\d+)%\s+(-?\d+\.\d+)%', text, re.DOTALL)
        if growth_section:
            min_rate = float(growth_section.group(1))
            max_rate = float(growth_section.group(2))
            avg_rate = float(growth_section.group(3))
        else:
            min_rate = None
            max_rate = None
            avg_rate = None

        # Extract description (paragraph after risk level)
        desc_match = re.search(r'\d+\s+-\s+[^\n]+\s+([^0-9]+?)(?=Suggested Asset Mix|$)', text, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""

        return RiskProfileResult(
            risk_level=risk_level,
            risk_number=risk_number,
            investment_term=investment_term,
            description=description,
            min_growth_rate=min_rate,
            max_growth_rate=max_rate,
            avg_growth_rate=avg_rate
        )

    def _extract_adjusted_risk_profile(self, page) -> Optional[AdjustedRiskProfile]:
        """Extract adjusted risk profile from page 6 (and adviser notes from page 5)"""
        text = page.get_text()

        if "Adjusted Attitude to Risk" not in text:
            return None

        # Extract adviser notes from previous page (page 5, index 4)
        # They appear between the risk profile result and adjusted risk profile
        adviser_notes = None
        try:
            # Get the document to access page 5
            # Note: 'page' is a page object, we need the document
            doc = page.parent
            if len(doc) > 4:
                page5 = doc[4]
                page5_text = page5.get_text()
                notes_match = re.search(r'Adviser notes\s+(.+?)(?=\n\n|$)', page5_text, re.DOTALL)
                if notes_match:
                    adviser_notes = notes_match.group(1).strip()
                    adviser_notes = self._clean_text(adviser_notes)
        except Exception as e:
            logger.warning(f"Could not extract adviser notes: {e}")

        # Extract adjusted level (e.g., "EValue Risk 5 Long Term (16+ Years)")
        # Look for pattern like "EValue Risk X" or just "X - Name"
        adjusted_match = re.search(r'(EValue Risk \d+[^\n]+|\d+\s+-\s+[^\n]+)', text)
        if adjusted_match:
            adjusted_level = adjusted_match.group(1).strip()
            # Extract number from adjusted level
            num_match = re.search(r'(\d+)', adjusted_level)
            adjusted_number = int(num_match.group(1)) if num_match else 5
        else:
            adjusted_level = "5 - Adventurous"
            adjusted_number = 5

        # Extract term
        term_match = re.search(r'(Short Term|Medium Term|Long Term)\s+\([^)]+\)', text)
        adjusted_term = term_match.group(0) if term_match else "Long Term (16+ Years)"

        # Extract growth rates (all three percentages appear together after labels)
        # Find the section with growth rates and extract all three percentages in order
        growth_section = re.search(r'Historic Growth Rates.*?(-?\d+\.\d+)%\s+(-?\d+\.\d+)%\s+(-?\d+\.\d+)%', text, re.DOTALL)
        if growth_section:
            min_rate = float(growth_section.group(1))
            max_rate = float(growth_section.group(2))
            avg_rate = float(growth_section.group(3))
        else:
            min_rate = None
            max_rate = None
            avg_rate = None

        # Extract description
        desc_match = re.search(r'EValue Risk \d+[^\n]+\s+([^0-9]+?)(?=Suggested Asset Mix|$)', text, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""

        # Adviser notes already extracted from page 5 above (lines 266-281)
        # Don't re-extract here as it would overwrite the value

        return AdjustedRiskProfile(
            adjusted_level=adjusted_level,
            adjusted_number=adjusted_number,
            adjusted_term=adjusted_term,
            description=description,
            min_growth_rate=min_rate,
            max_growth_rate=max_rate,
            avg_growth_rate=avg_rate,
            adviser_notes=adviser_notes
        )

    def _extract_percentage(self, text: str, pattern: str) -> Optional[float]:
        """Extract percentage value from text"""
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except (ValueError, IndexError):
                return None
        return None
