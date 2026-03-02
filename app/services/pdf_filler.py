"""
PDF filler service
Fills PenLife Risk Profiler template with extracted data
"""

import logging
import os
import fitz  # PyMuPDF
from pathlib import Path

from app.models.schemas import RiskProfileData

logger = logging.getLogger(__name__)


class PDFFiller:
    """Fills PenLife Risk Profiler template with data"""

    def __init__(self):
        # Template path - UPDATED to use new template with smaller boxes
        self.template_path = Path(__file__).parent.parent.parent / "templates" / "PenLife Risk Profiler_1.pdf"

        # Font settings
        self.default_font = "helv"  # Helvetica
        self.default_font_size = 7  # Reduced to match original PDF
        self.default_color = (0, 0, 0)  # Black

        # Coordinate mappings (x, y positions on each page)
        # These will need to be calibrated based on the actual template
        self.coordinates = self._load_coordinates()

    def _extract_pie_charts(self, source_pdf_bytes: bytes) -> tuple:
        """
        Extract pie chart images from source PDF

        Args:
            source_pdf_bytes: Source PDF bytes

        Returns:
            Tuple of (page4_chart_bytes, page6_chart_bytes)
        """
        try:
            source_doc = fitz.open(stream=source_pdf_bytes, filetype="pdf")

            # Extract from page 4 (index 3) - image index 1 is the pie chart
            page4_chart = None
            if len(source_doc) > 3:
                page = source_doc[3]
                images = page.get_images()
                if len(images) > 1:
                    xref = images[1][0]  # Second image (index 1)
                    page4_chart = source_doc.extract_image(xref)["image"]

            # Extract from page 6 (index 5) - image index 1 is the pie chart
            page6_chart = None
            if len(source_doc) > 5:
                page = source_doc[5]
                images = page.get_images()
                if len(images) > 1:
                    xref = images[1][0]  # Second image (index 1)
                    page6_chart = source_doc.extract_image(xref)["image"]

            source_doc.close()
            return page4_chart, page6_chart

        except Exception as e:
            logger.warning(f"Could not extract pie charts: {e}")
            return None, None

    def _load_coordinates(self) -> dict:
        """
        Load coordinate mappings for template fields
        Coordinates calibrated using visual picker tool for NEW template (smaller boxes)
        Recalibrated on 2026-03-02 - boxes moved LEFT ~42-48 points
        max_lines: number of lines the field can wrap across (default 1)
        """
        return {
            "page_1": {
                "prepared_by": {"x": 324, "y": 1170, "size": 7}
            },
            "page_4": {  # Understanding your risk profile page
                # Investment experience (NEW: x=334 standardized, y+5 pixels lower)
                # BIGGER boxes in new template - max_width 240, max_lines 3
                "experience_q1": {"x": 334, "y": 191, "size": 6, "max_width": 220, "max_lines": 4},
                "experience_q2": {"x": 334, "y": 230, "size": 6, "max_width": 220, "max_lines": 4},

                # Capacity for loss (NEW: x=334 standardized, y+5 pixels lower)
                # BIGGER boxes in new template - max_width 220 (box width ~523 with padding), max_lines 3
                "capacity_q1": {"x": 334, "y": 361, "size": 6, "max_width": 220, "max_lines": 4},
                "capacity_q2": {"x": 334, "y": 403, "size": 6, "max_width": 220, "max_lines": 4},
                "capacity_q3": {"x": 334, "y": 443, "size": 6, "max_width": 220, "max_lines": 4},
                "capacity_q4": {"x": 334, "y": 483, "size": 6, "max_width": 220, "max_lines": 4},
                "capacity_q5": {"x": 334, "y": 524, "size": 6, "max_width": 220, "max_lines": 4},

                # Discussion points section
                "discussion_points": {"x": 36, "y": 583, "size": 7, "max_width": 520},
            },
            "page_6": {  # Your attitude for risk page (13 questions + investment term)
                # All questions (NEW: x=334 standardized, y+5 pixels lower)
                # BIGGER boxes in new template - max_width 240, max_lines 3
                "q1": {"x": 334, "y": 129, "size": 6, "max_width": 220, "max_lines": 4},
                "q2": {"x": 334, "y": 168, "size": 6, "max_width": 220, "max_lines": 4},
                "q3": {"x": 334, "y": 205, "size": 6, "max_width": 220, "max_lines": 4},
                "q4": {"x": 334, "y": 239, "size": 6, "max_width": 220, "max_lines": 4},
                "q5": {"x": 334, "y": 278, "size": 6, "max_width": 220, "max_lines": 4},
                "q6": {"x": 334, "y": 313, "size": 6, "max_width": 220, "max_lines": 4},
                "q7": {"x": 334, "y": 351, "size": 6, "max_width": 220, "max_lines": 4},
                "q8": {"x": 334, "y": 389, "size": 6, "max_width": 220, "max_lines": 4},
                "q9": {"x": 334, "y": 426, "size": 6, "max_width": 220, "max_lines": 4},
                "q10": {"x": 334, "y": 465, "size": 6, "max_width": 220, "max_lines": 4},
                "q11": {"x": 334, "y": 500, "size": 6, "max_width": 220, "max_lines": 4},
                "q12": {"x": 334, "y": 537, "size": 6, "max_width": 220, "max_lines": 4},
                "q13": {"x": 334, "y": 573, "size": 6, "max_width": 220, "max_lines": 4},
                "investment_term": {"x": 334, "y": 611, "size": 6, "max_width": 220, "max_lines": 4},

                # Discussion points section
                "discussion_points": {"x": 36, "y": 670, "size": 7, "max_width": 520},
            },
            "page_7": {  # Your attitude to risk result page (NO CHANGE)
                "risk_level": {"x": 43, "y": 73, "size": 9, "max_width": 500}
            },
            "page_8": {  # Adjusted attitude for risk page (MINIMAL CHANGE)
                "adjusted_level": {"x": 39, "y": 69, "size": 9, "max_width": 500}
            }
        }

    def fill_template(self, data: RiskProfileData, source_pdf_bytes: bytes = None,
                     discussion_points: str = None) -> bytes:
        """
        Fill template with extracted data

        Args:
            data: RiskProfileData object
            source_pdf_bytes: Optional source PDF bytes for extracting charts

        Returns:
            PDF as bytes
        """
        try:
            # Open template
            if not self.template_path.exists():
                raise FileNotFoundError(f"Template not found: {self.template_path}")

            doc = fitz.open(str(self.template_path))

            # Extract pie charts from source if provided
            pie_chart_page4 = None
            pie_chart_page6 = None
            if source_pdf_bytes:
                pie_chart_page4, pie_chart_page6 = self._extract_pie_charts(source_pdf_bytes)

            # Fill each page
            self._fill_page_1(doc, data)
            self._fill_page_4(doc, data, discussion_points)
            self._fill_page_6(doc, data, discussion_points)
            self._fill_page_7(doc, data, pie_chart_page4)  # Risk profile result

            # If adjusted risk profile exists, fill page 8
            if data.adjusted_risk_profile:
                self._fill_page_8(doc, data, pie_chart_page6)

            # Save to bytes
            output_bytes = doc.write()
            doc.close()

            logger.info(f"Successfully filled template for {data.client_info.full_name}")
            return output_bytes

        except Exception as e:
            logger.error(f"Error filling template: {e}", exc_info=True)
            raise

    def _fill_page_1(self, doc: fitz.Document, data: RiskProfileData):
        """Fill cover page with adviser name"""
        page = doc[0]  # Page 1 (0-indexed)
        coords = self.coordinates.get("page_1", {})

        if "prepared_by" in coords:
            c = coords["prepared_by"]
            self._insert_text(page, data.client_info.created_by, c["x"], c["y"], c.get("size", 11))

    def _fill_page_4(self, doc: fitz.Document, data: RiskProfileData, discussion_points: str = None):
        """Fill page 4 - Understanding your risk profile"""
        page = doc[3]  # Page 4 (0-indexed = 3)
        coords = self.coordinates.get("page_4", {})

        # Investment experience
        if "experience_q1" in coords:
            c = coords["experience_q1"]
            self._insert_text(page, data.knowledge_experience.relevant_profession,
                            c["x"], c["y"], c.get("size", 10), c.get("max_width"), c.get("max_lines", 1))

        if "experience_q2" in coords:
            c = coords["experience_q2"]
            self._insert_text(page, data.knowledge_experience.past_investments,
                            c["x"], c["y"], c.get("size", 10), c.get("max_width"), c.get("max_lines", 1))

        # Capacity for loss
        capacity_data = [
            ("capacity_q1", data.capacity_for_loss.emergency_expenses),
            ("capacity_q2", data.capacity_for_loss.daily_living_expenses),
            ("capacity_q3", data.capacity_for_loss.significant_proportion),
            ("capacity_q4", data.capacity_for_loss.major_commitments),
            ("capacity_q5", data.capacity_for_loss.dependants),
        ]

        for key, value in capacity_data:
            if key in coords:
                c = coords[key]
                self._insert_text(page, value, c["x"], c["y"], c.get("size", 10), c.get("max_width"), c.get("max_lines", 1))

        # Discussion points
        if discussion_points and "discussion_points" in coords:
            c = coords["discussion_points"]
            self._insert_multiline_text(page, discussion_points, c["x"], c["y"], c.get("size", 7), c.get("max_width"))

    def _fill_page_6(self, doc: fitz.Document, data: RiskProfileData, discussion_points: str = None):
        """Fill page 6 - Your attitude for risk (13 questions)"""
        page = doc[5]  # Page 6 (0-indexed = 5)
        coords = self.coordinates.get("page_6", {})

        # Map questionnaire answers
        answers = [
            ("q1", data.questionnaire_answers.q1_explore_opportunities),
            ("q2", data.questionnaire_answers.q2_best_return),
            ("q3", data.questionnaire_answers.q3_typical_attitude),
            ("q4", data.questionnaire_answers.q4_past_risk),
            ("q5", data.questionnaire_answers.q5_safe_steady),
            ("q6", data.questionnaire_answers.q6_high_growth),
            ("q7", data.questionnaire_answers.q7_willing_to_invest),
            ("q8", data.questionnaire_answers.q8_friend_describe),
            ("q9", data.questionnaire_answers.q9_highs_and_lows),
            ("q10", data.questionnaire_answers.q10_two_products),
            ("q11", data.questionnaire_answers.q11_small_certain),
            ("q12", data.questionnaire_answers.q12_losses_or_gains),
            ("q13", data.questionnaire_answers.q13_money_safe),
            ("investment_term", data.questionnaire_answers.investment_term),
        ]

        for key, value in answers:
            if key in coords:
                c = coords[key]
                self._insert_text(page, value, c["x"], c["y"], c.get("size", 10), c.get("max_width"), c.get("max_lines", 1))

        # Discussion points
        if discussion_points and "discussion_points" in coords:
            c = coords["discussion_points"]
            self._insert_multiline_text(page, discussion_points, c["x"], c["y"], c.get("size", 7), c.get("max_width"))

    def _fill_page_7(self, doc: fitz.Document, data: RiskProfileData, pie_chart_bytes: bytes = None):
        """Fill page 7 - Your attitude to risk result"""
        if len(doc) <= 6:
            logger.warning("Template doesn't have page 7")
            return

        page = doc[6]  # Page 7 (0-indexed = 6)
        coords = self.coordinates.get("page_7", {})

        # Create formatted content block
        if "risk_level" in coords:
            c = coords["risk_level"]
            y_offset = c["y"]
            line_height = 13

            # Risk level as bold/larger heading
            self._insert_text(page, data.risk_profile_result.risk_level, c["x"], y_offset, 11, None)
            y_offset += line_height + 3

            # Description paragraph
            desc_lines = self._wrap_text(data.risk_profile_result.description, 75)
            for line in desc_lines:
                self._insert_text(page, line, c["x"], y_offset, 9, None)
                y_offset += line_height
            y_offset += 5  # Extra spacing

            # Investment Term section
            self._insert_text(page, "Investment Term:", c["x"], y_offset, 10, None)
            y_offset += line_height
            self._insert_text(page, f"  {data.risk_profile_result.investment_term}", c["x"], y_offset, 9, None)
            y_offset += line_height + 5

            # Historic Growth Rates section
            self._insert_text(page, "Historic Growth Rates:", c["x"], y_offset, 10, None)
            y_offset += line_height
            if data.risk_profile_result.min_growth_rate is not None:
                self._insert_text(page, f"  Minimum: {data.risk_profile_result.min_growth_rate}%", c["x"], y_offset, 9, None)
                y_offset += line_height
            if data.risk_profile_result.max_growth_rate is not None:
                self._insert_text(page, f"  Maximum: {data.risk_profile_result.max_growth_rate}%", c["x"], y_offset, 9, None)
                y_offset += line_height
            if data.risk_profile_result.avg_growth_rate is not None:
                self._insert_text(page, f"  Average: {data.risk_profile_result.avg_growth_rate}%", c["x"], y_offset, 9, None)
                y_offset += line_height + 10

            # Insert pie chart if available
            if pie_chart_bytes:
                # Place large chart below text, centered (480x480 - 50% bigger)
                chart_rect = fitz.Rect(58, 280, 538, 760)  # x0, y0, x1, y1 (480x480, centered)
                page.insert_image(chart_rect, stream=pie_chart_bytes)

    def _fill_page_8(self, doc: fitz.Document, data: RiskProfileData, pie_chart_bytes: bytes = None):
        """Fill page 8 - Adjusted attitude for risk"""
        if len(doc) <= 7:
            logger.warning("Template doesn't have page 8")
            return

        page = doc[7]  # Page 8 (0-indexed = 7)
        coords = self.coordinates.get("page_8", {})

        # Create formatted content block
        if "adjusted_level" in coords and data.adjusted_risk_profile:
            c = coords["adjusted_level"]
            y_offset = c["y"]
            line_height = 13

            # Adjusted risk level as bold/larger heading
            self._insert_text(page, data.adjusted_risk_profile.adjusted_level, c["x"], y_offset, 11, None)
            y_offset += line_height + 3

            # Description paragraph
            desc_lines = self._wrap_text(data.adjusted_risk_profile.description, 75)
            for line in desc_lines:
                self._insert_text(page, line, c["x"], y_offset, 9, None)
                y_offset += line_height
            y_offset += 5  # Extra spacing

            # Investment Term section
            self._insert_text(page, "Investment Term:", c["x"], y_offset, 10, None)
            y_offset += line_height
            self._insert_text(page, f"  {data.adjusted_risk_profile.adjusted_term}", c["x"], y_offset, 9, None)
            y_offset += line_height + 5

            # Historic Growth Rates section
            self._insert_text(page, "Historic Growth Rates:", c["x"], y_offset, 10, None)
            y_offset += line_height
            if data.adjusted_risk_profile.min_growth_rate is not None:
                self._insert_text(page, f"  Minimum: {data.adjusted_risk_profile.min_growth_rate}%", c["x"], y_offset, 9, None)
                y_offset += line_height
            if data.adjusted_risk_profile.max_growth_rate is not None:
                self._insert_text(page, f"  Maximum: {data.adjusted_risk_profile.max_growth_rate}%", c["x"], y_offset, 9, None)
                y_offset += line_height
            if data.adjusted_risk_profile.avg_growth_rate is not None:
                self._insert_text(page, f"  Average: {data.adjusted_risk_profile.avg_growth_rate}%", c["x"], y_offset, 9, None)
                y_offset += line_height + 5

            # Adviser Notes section (if present)
            if data.adjusted_risk_profile.adviser_notes:
                self._insert_text(page, "Adviser Notes:", c["x"], y_offset, 10, None)
                y_offset += line_height
                notes_lines = self._wrap_text(data.adjusted_risk_profile.adviser_notes, 75)
                for line in notes_lines:
                    self._insert_text(page, f"  {line}", c["x"], y_offset, 9, None)
                    y_offset += line_height
                y_offset += 5

            # Insert pie chart if available
            if pie_chart_bytes:
                # Place large chart below text, centered (480x480 - 50% bigger)
                chart_rect = fitz.Rect(58, 280, 538, 760)  # x0, y0, x1, y1 (480x480, centered)
                page.insert_image(chart_rect, stream=pie_chart_bytes)

    def _wrap_text(self, text: str, max_chars: int = 80) -> list:
        """
        Wrap text into multiple lines based on character count

        Args:
            text: Text to wrap
            max_chars: Maximum characters per line

        Returns:
            List of wrapped lines
        """
        if not text:
            return []

        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length <= max_chars:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _insert_text(self, page: fitz.Page, text: str, x: float, y: float,
                    font_size: int = 10, max_width: float = None, max_lines: int = 1):
        """
        Insert text at specified coordinates with intelligent fitting

        Args:
            page: PyMuPDF page object
            text: Text to insert
            x: X coordinate
            y: Y coordinate
            font_size: Font size
            max_width: Maximum width (for text wrapping)
            max_lines: Maximum number of lines to wrap (default 1)
        """
        try:
            # Ensure text is string
            text = str(text) if text else ""

            if not text:
                return

            # If no width constraint, insert as-is
            if not max_width:
                point = fitz.Point(x, y)
                page.insert_text(
                    point,
                    text,
                    fontname=self.default_font,
                    fontsize=font_size,
                    color=self.default_color
                )
                return

            # Try intelligent fitting strategies
            fitted_text = self._fit_text_to_width(text, max_width, font_size, max_lines)

            # Insert fitted text (may be single or multiple lines)
            line_height = font_size * 1.2  # 1.2 line spacing
            for i, line in enumerate(fitted_text):
                point = fitz.Point(x, y + (i * line_height))
                page.insert_text(
                    point,
                    line,
                    fontname=self.default_font,
                    fontsize=font_size,
                    color=self.default_color
                )

        except Exception as e:
            logger.error(f"Error inserting text at ({x}, {y}): {e}")

    def _fit_text_to_width(self, text: str, max_width: float, font_size: int,
                          max_lines: int = 1) -> list:
        """
        Fit text to specified width using intelligent strategies

        Strategies (in order):
        1. Try original text - if it fits, use it
        2. Try with smaller font size (down to 7pt minimum)
        3. Wrap text across multiple lines (if max_lines > 1)
        4. Truncate with ellipsis as last resort

        Args:
            text: Text to fit
            max_width: Maximum width in points
            font_size: Desired font size
            max_lines: Maximum number of lines allowed

        Returns:
            List of text lines that fit within constraints
        """
        # Strategy 1: Check if original text fits
        text_width = fitz.get_text_length(text, fontname=self.default_font, fontsize=font_size)
        if text_width <= max_width:
            return [text]

        # Strategy 2: Try smaller font sizes (only if single line)
        if max_lines == 1:
            for smaller_size in range(font_size - 1, 6, -1):  # Try down to 7pt
                text_width = fitz.get_text_length(text, fontname=self.default_font, fontsize=smaller_size)
                if text_width <= max_width:
                    # Update font size for this text
                    logger.debug(f"Reduced font size to {smaller_size}pt to fit text")
                    # Note: Caller needs to handle font size change
                    return [text]

        # Strategy 3: Word wrapping across multiple lines
        if max_lines > 1:
            wrapped_lines = self._wrap_text_to_width(text, max_width, font_size, max_lines)
            if wrapped_lines:
                return wrapped_lines

        # Strategy 4: Truncate with ellipsis (last resort)
        truncated = text
        while len(truncated) > 3:
            test_text = truncated[:-1] + "..."
            text_width = fitz.get_text_length(test_text, fontname=self.default_font, fontsize=font_size)
            if text_width <= max_width:
                logger.warning(f"Truncated text to fit: '{text}' -> '{test_text}'")
                return [test_text]
            truncated = truncated[:-1]

        return ["..."]  # Extreme fallback

    def _wrap_text_to_width(self, text: str, max_width: float, font_size: int,
                           max_lines: int) -> list:
        """
        Wrap text across multiple lines to fit width constraint

        Args:
            text: Text to wrap
            max_width: Maximum width per line in points
            font_size: Font size
            max_lines: Maximum number of lines

        Returns:
            List of wrapped lines, or None if can't fit
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            # Try adding word to current line
            test_line = ' '.join(current_line + [word])
            test_width = fitz.get_text_length(test_line, fontname=self.default_font, fontsize=font_size)

            if test_width <= max_width:
                current_line.append(word)
            else:
                # Word doesn't fit, start new line
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, truncate it
                    truncated_word = word
                    while len(truncated_word) > 0:
                        test_width = fitz.get_text_length(truncated_word, fontname=self.default_font, fontsize=font_size)
                        if test_width <= max_width:
                            lines.append(truncated_word)
                            break
                        truncated_word = truncated_word[:-1]

                # Check if we've exceeded max lines
                if len(lines) >= max_lines:
                    # Truncate last line with ellipsis
                    if lines:
                        last_line = lines[-1]
                        while len(last_line) > 3:
                            test_text = last_line[:-1] + "..."
                            text_width = fitz.get_text_length(test_text, fontname=self.default_font, fontsize=font_size)
                            if text_width <= max_width:
                                lines[-1] = test_text
                                break
                            last_line = last_line[:-1]
                    return lines

        # Add remaining words
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))

        return lines if lines else None

    def _insert_multiline_text(self, page: fitz.Page, text: str, x: float, y: float,
                               font_size: int = 7, max_width: float = None):
        """
        Insert multiline text with proper line breaks and formatting

        Args:
            page: PyMuPDF page object
            text: Text to insert (can contain \n for line breaks)
            x: X coordinate
            y: Y coordinate
            font_size: Font size
            max_width: Maximum width for wrapping
        """
        if not text:
            return

        line_height = font_size * 1.3  # Line spacing
        current_y = y

        # Split by line breaks first
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                # Empty line = spacing
                current_y += line_height * 0.5
                continue

            # Wrap if needed
            if max_width:
                wrapped = self._wrap_text_to_width(line, max_width, font_size, max_lines=10)
                if wrapped:
                    for wrapped_line in wrapped:
                        point = fitz.Point(x, current_y)
                        page.insert_text(
                            point,
                            wrapped_line,
                            fontname=self.default_font,
                            fontsize=font_size,
                            color=self.default_color
                        )
                        current_y += line_height
            else:
                point = fitz.Point(x, current_y)
                page.insert_text(
                    point,
                    line,
                    fontname=self.default_font,
                    fontsize=font_size,
                    color=self.default_color
                )
                current_y += line_height

    def calibrate_coordinates(self, output_path: str = "calibration_output.pdf"):
        """
        Helper function to calibrate coordinates by drawing grid on template
        Useful for finding exact positions for text placement
        """
        doc = fitz.open(str(self.template_path))

        # Draw grid on each page for calibration
        for page_num in range(len(doc)):
            page = doc[page_num]
            rect = page.rect

            # Draw vertical lines every 50 points
            for x in range(0, int(rect.width), 50):
                page.draw_line((x, 0), (x, rect.height), color=(0.8, 0.8, 0.8), width=0.5)
                # Add coordinate label
                page.insert_text((x, 20), str(x), fontsize=8, color=(0.5, 0.5, 0.5))

            # Draw horizontal lines every 50 points
            for y in range(0, int(rect.height), 50):
                page.draw_line((0, y), (rect.width, y), color=(0.8, 0.8, 0.8), width=0.5)
                # Add coordinate label
                page.insert_text((10, y), str(y), fontsize=8, color=(0.5, 0.5, 0.5))

        doc.save(output_path)
        doc.close()
        logger.info(f"Calibration PDF saved to {output_path}")
