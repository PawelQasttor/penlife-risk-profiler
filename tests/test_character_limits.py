"""
Test to determine exact character limits for 2-line text at 7pt
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import fitz
from app.services.pdf_filler import PDFFiller


def test_character_limits():
    """Test how many characters fit in 2 lines at 7pt before truncation"""

    print("=" * 80)
    print("  Character Limit Test - 7pt Font, 2 Lines")
    print("=" * 80)

    filler = PDFFiller()

    # Test configuration
    max_width = 165  # Points
    font_size = 7    # Points
    max_lines = 2    # Lines

    print(f"\nConfiguration:")
    print(f"  Font size: {font_size}pt")
    print(f"  Max width: {max_width}pt")
    print(f"  Max lines: {max_lines}")
    print(f"  Font: Helvetica")

    # Test different text lengths
    test_cases = [
        # Short texts
        ("No", "Very short"),
        ("I agree with this statement", "Short"),
        ("I have 5 years of experience in finance", "Medium short"),

        # Testing the limits
        ("Yes, I have over 10 years of experience working in financial services", "~70 chars"),
        ("Yes, I have over 10 years of experience working in financial services and investment", "~85 chars"),
        ("Yes, I have over 10 years of experience working in financial services and investment banking", "~95 chars"),
        ("Yes, I have over 10 years of experience working in financial services and investment banking sector", "~105 chars"),
        ("Yes, I have over 10 years of experience working in financial services and investment banking and pension funds", "~115 chars"),
        ("Yes, I have over 10 years of experience working in financial services and investment banking and pension funds management", "~125 chars"),
        ("Yes, I have extensive experience managing investment portfolios, working with pension funds, and advising high-net-worth individuals", "~135 chars"),
        ("Yes, I have extensive experience managing investment portfolios, working with pension funds, and advising high-net-worth individuals on financial", "~150 chars"),
        ("Yes, I have extensive experience managing investment portfolios, working with pension funds, and advising high-net-worth individuals on financial planning", "~160 chars"),
        ("Yes, I have extensive experience managing investment portfolios, working with pension funds, and advising high-net-worth individuals on financial planning strategies", "~170 chars"),
    ]

    print("\n" + "=" * 80)
    print("Testing Character Limits:")
    print("=" * 80)

    truncation_point = None

    for text, description in test_cases:
        char_count = len(text)

        # Get fitted text
        fitted_lines = filler._fit_text_to_width(text, max_width, font_size, max_lines)

        # Check if truncated
        fitted_text = ' '.join(fitted_lines)
        was_truncated = '...' in fitted_text

        # Calculate widths
        if len(fitted_lines) > 0:
            line1_width = fitz.get_text_length(fitted_lines[0], fontname="helv", fontsize=font_size)
            line2_width = fitz.get_text_length(fitted_lines[1], fontname="helv", fontsize=font_size) if len(fitted_lines) > 1 else 0
        else:
            line1_width = 0
            line2_width = 0

        status = "[!] TRUNCATED" if was_truncated else "[OK] FITS"

        print(f"\n{description}: {char_count} chars - {status}")
        print(f"  Input: \"{text[:80]}{'...' if len(text) > 80 else ''}\"")
        print(f"  Result: {len(fitted_lines)} line(s)")

        for i, line in enumerate(fitted_lines, 1):
            width = fitz.get_text_length(line, fontname="helv", fontsize=font_size)
            print(f"    Line {i}: \"{line}\"")
            print(f"            ({len(line)} chars, {width:.1f}pt wide)")

        # Track first truncation point
        if was_truncated and truncation_point is None:
            truncation_point = char_count

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if truncation_point:
        print(f"\n✓ Characters fit WITHOUT truncation: ~{truncation_point - 10}-{truncation_point - 1}")
        print(f"✗ Truncation starts at: ~{truncation_point}+ characters")

    # Calculate average character width
    sample_text = "The quick brown fox jumps over the lazy dog 1234567890"
    sample_width = fitz.get_text_length(sample_text, fontname="helv", fontsize=font_size)
    avg_char_width = sample_width / len(sample_text)

    # Calculate theoretical limits
    chars_per_line = int(max_width / avg_char_width)
    chars_per_2_lines = chars_per_line * 2

    print(f"\nTheoretical Calculation:")
    print(f"  Average character width at 7pt: {avg_char_width:.2f}pt")
    print(f"  Characters per line (165pt ÷ {avg_char_width:.2f}pt): ~{chars_per_line}")
    print(f"  Characters in 2 lines: ~{chars_per_2_lines}")

    print(f"\nPractical Limit (with word wrapping):")
    print(f"  Safe limit: ~{chars_per_2_lines - 20} characters")
    print(f"  Maximum before truncation: ~{chars_per_2_lines} characters")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_character_limits()
