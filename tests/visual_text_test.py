"""
Visual text fitting comparison tool
Generates a simple PDF showing how different text lengths are handled
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz
from app.services.pdf_filler import PDFFiller


def create_visual_comparison_pdf():
    """
    Create a visual comparison PDF showing text fitting strategies
    Does not require the template - creates a new document
    """
    print("Creating visual text fitting comparison PDF...")

    # Create new PDF document
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 size

    filler = PDFFiller()

    # Title
    page.insert_text(
        fitz.Point(50, 50),
        "Text Fitting Strategy Demonstration",
        fontname="helv",
        fontsize=16,
        color=(0, 0, 0.5)
    )

    # Test scenarios
    scenarios = [
        {
            "title": "Scenario 1: Short text (fits easily)",
            "text": "Yes",
            "max_width": 200,
            "max_lines": 2,
            "y_start": 100
        },
        {
            "title": "Scenario 2: Medium text (fits in one line)",
            "text": "I have 5 years of experience in finance",
            "max_width": 200,
            "max_lines": 2,
            "y_start": 180
        },
        {
            "title": "Scenario 3: Long text (wraps to 2 lines)",
            "text": "Yes, I have over 10 years of experience working in financial services and investment banking",
            "max_width": 200,
            "max_lines": 2,
            "y_start": 260
        },
        {
            "title": "Scenario 4: Very long text (wraps and truncates)",
            "text": "Yes, I have extensive experience managing investment portfolios, working with pension funds, and advising high-net-worth individuals on complex financial planning strategies over the past 15 years",
            "max_width": 200,
            "max_lines": 2,
            "y_start": 360
        },
        {
            "title": "Scenario 5: Single line constraint (truncates)",
            "text": "This is a moderately long answer that would wrap but is forced to single line",
            "max_width": 200,
            "max_lines": 1,
            "y_start": 480
        },
        {
            "title": "Scenario 6: Three lines allowed",
            "text": "Yes, I have extensive experience managing portfolios and working with pension funds over the past years",
            "max_width": 200,
            "max_lines": 3,
            "y_start": 560
        },
    ]

    for scenario in scenarios:
        y = scenario["y_start"]

        # Scenario title
        page.insert_text(
            fitz.Point(50, y),
            scenario["title"],
            fontname="helv",
            fontsize=10,
            color=(0, 0, 0)
        )
        y += 15

        # Original text (in gray)
        page.insert_text(
            fitz.Point(60, y),
            f"Input: \"{scenario['text'][:60]}{'...' if len(scenario['text']) > 60 else ''}\"",
            fontname="helv",
            fontsize=8,
            color=(0.5, 0.5, 0.5)
        )
        y += 12

        # Draw box showing max_width constraint
        box_x = 60
        box_y = y + 5
        box_rect = fitz.Rect(box_x, box_y, box_x + scenario["max_width"], box_y + (scenario["max_lines"] * 12))
        page.draw_rect(box_rect, color=(0.8, 0.8, 1), width=0.5)

        # Get fitted text
        fitted_lines = filler._fit_text_to_width(
            scenario["text"],
            scenario["max_width"],
            9,
            scenario["max_lines"]
        )

        # Draw fitted text inside box
        for i, line in enumerate(fitted_lines):
            page.insert_text(
                fitz.Point(box_x + 5, box_y + 10 + (i * 11)),
                line,
                fontname="helv",
                fontsize=9,
                color=(0, 0, 0)
            )

        # Show info
        info_y = box_y + (scenario["max_lines"] * 12) + 10
        info_text = f"Max width: {scenario['max_width']}pt | Max lines: {scenario['max_lines']} | Result: {len(fitted_lines)} line(s)"
        if '...' in ''.join(fitted_lines):
            info_text += " | [!] TRUNCATED"

        page.insert_text(
            fitz.Point(60, info_y),
            info_text,
            fontname="helv",
            fontsize=7,
            color=(0.6, 0, 0)
        )

    # Add legend
    legend_y = 710
    page.insert_text(
        fitz.Point(50, legend_y),
        "Legend:",
        fontname="helv",
        fontsize=9,
        color=(0, 0, 0.5)
    )
    legend_y += 15
    page.insert_text(
        fitz.Point(60, legend_y),
        "• Blue box = Maximum width and height constraint",
        fontname="helv",
        fontsize=8,
        color=(0, 0, 0)
    )
    legend_y += 12
    page.insert_text(
        fitz.Point(60, legend_y),
        "• Black text = Fitted result",
        fontname="helv",
        fontsize=8,
        color=(0, 0, 0)
    )
    legend_y += 12
    page.insert_text(
        fitz.Point(60, legend_y),
        "• '...' = Text was truncated to fit constraints",
        fontname="helv",
        fontsize=8,
        color=(0, 0, 0)
    )

    # Save PDF
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "text_fitting_visual_comparison.pdf"

    doc.save(str(output_path))
    doc.close()

    print(f"[OK] Visual comparison PDF created: {output_path}")
    return output_path


def create_width_measurement_guide():
    """Create a PDF showing how to measure text widths"""
    print("Creating width measurement guide...")

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # Title
    page.insert_text(
        fitz.Point(50, 50),
        "Text Width Measurement Guide",
        fontname="helv",
        fontsize=16,
        color=(0, 0, 0.5)
    )

    page.insert_text(
        fitz.Point(50, 80),
        "Common text samples at 9pt font size:",
        fontname="helv",
        fontsize=11,
        color=(0, 0, 0)
    )

    # Sample texts with width measurements
    samples = [
        "Yes",
        "No",
        "3-6 months",
        "I have some experience",
        "Yes, I have extensive experience",
        "I have over 10 years of experience in financial services",
        "Yes, I have extensive experience managing investment portfolios over many years",
    ]

    y = 110
    for sample in samples:
        width = fitz.get_text_length(sample, fontname="helv", fontsize=9)

        # Draw the text
        page.insert_text(
            fitz.Point(60, y),
            sample,
            fontname="helv",
            fontsize=9,
            color=(0, 0, 0)
        )

        # Draw measurement line
        line_y = y + 5
        page.draw_line(
            fitz.Point(60, line_y),
            fitz.Point(60 + width, line_y),
            color=(1, 0, 0),
            width=0.5
        )

        # Show width
        page.insert_text(
            fitz.Point(60 + width + 10, y),
            f"{width:.1f}pt",
            fontname="helv",
            fontsize=8,
            color=(1, 0, 0)
        )

        y += 30

    # Add reference boxes
    y = 400
    page.insert_text(
        fitz.Point(50, y),
        "Common box width references:",
        fontname="helv",
        fontsize=11,
        color=(0, 0, 0)
    )
    y += 25

    box_widths = [100, 165, 200, 300, 500]
    for box_width in box_widths:
        # Draw box
        box_rect = fitz.Rect(60, y, 60 + box_width, y + 20)
        page.draw_rect(box_rect, color=(0.9, 0.9, 0.9), width=0.5)

        # Label
        page.insert_text(
            fitz.Point(65, y + 13),
            f"{box_width}pt wide",
            fontname="helv",
            fontsize=8,
            color=(0, 0, 0)
        )

        y += 35

    # Save
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "text_width_measurement_guide.pdf"

    doc.save(str(output_path))
    doc.close()

    print(f"[OK] Width measurement guide created: {output_path}")
    return output_path


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Visual Text Fitting Test Tool")
    print("=" * 60 + "\n")

    try:
        # Create visual comparison
        comparison_pdf = create_visual_comparison_pdf()

        # Create measurement guide
        measurement_pdf = create_width_measurement_guide()

        print("\n" + "=" * 60)
        print("[OK] All visual test PDFs created successfully!")
        print("=" * 60)
        print(f"\n1. Visual Comparison: {comparison_pdf}")
        print(f"2. Measurement Guide: {measurement_pdf}")
        print("\nOpen these PDFs to see how text fitting works visually.")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
