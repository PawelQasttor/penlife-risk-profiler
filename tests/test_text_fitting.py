"""
Test script for PDF text fitting functionality
Tests the intelligent text fitting strategies with various text lengths
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.pdf_filler import PDFFiller
from app.models.schemas import (
    RiskProfileData, ClientInfo, KnowledgeExperience,
    CapacityForLoss, RiskQuestionnaireAnswers, RiskProfileResult
)
import fitz


def print_section(title: str):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_text_fitting_logic():
    """Test the text fitting logic without generating PDF"""
    print_section("Testing Text Fitting Logic")

    filler = PDFFiller()

    # Test cases with different text lengths
    test_cases = [
        {
            "name": "Short text (fits easily)",
            "text": "Yes",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 1
        },
        {
            "name": "Medium text (fits in one line)",
            "text": "I have some experience with investments",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 1
        },
        {
            "name": "Long text (needs wrapping)",
            "text": "Yes, I have over 10 years of experience working in financial services and investment banking",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 2
        },
        {
            "name": "Very long text (needs wrapping, may truncate)",
            "text": "Yes, I have extensive experience managing investment portfolios, working with pension funds, and advising high-net-worth individuals on complex financial planning strategies over the past 15 years",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 2
        },
        {
            "name": "Extremely long text (will truncate)",
            "text": "Yes, I have been working in the financial services industry for over 20 years, specializing in investment management, portfolio diversification, risk assessment, financial planning, pension fund management, and providing comprehensive advisory services to both individual and institutional clients across various market conditions",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 2
        },
        {
            "name": "Single line constraint (forces truncation)",
            "text": "This is a moderately long answer that would normally wrap but is constrained to a single line",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 1
        },
        {
            "name": "Three line wrapping",
            "text": "Yes, I have extensive experience managing investment portfolios and working with pension funds over the past 15 years",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 3
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print(f"   Input: \"{test['text']}\"")
        print(f"   Length: {len(test['text'])} characters")
        print(f"   Constraints: max_width={test['max_width']}pt, font_size={test['font_size']}pt, max_lines={test['max_lines']}")

        # Get fitted text
        fitted_lines = filler._fit_text_to_width(
            test['text'],
            test['max_width'],
            test['font_size'],
            test['max_lines']
        )

        print(f"   Result: {len(fitted_lines)} line(s)")
        for j, line in enumerate(fitted_lines, 1):
            # Calculate actual width
            width = fitz.get_text_length(line, fontname="helv", fontsize=test['font_size'])
            fits = "[OK]" if width <= test['max_width'] else "[X]"
            print(f"     Line {j} [{fits}]: \"{line}\" ({len(line)} chars, {width:.1f}pt wide)")

        # Check if truncated
        original_text = ' '.join(fitted_lines).replace('...', '')
        if len(original_text) < len(test['text']) - 3:  # Account for ellipsis
            print(f"   [!]  Text was truncated!")


def test_wrap_text_to_width():
    """Test the word wrapping functionality"""
    print_section("Testing Word Wrapping")

    filler = PDFFiller()

    test_cases = [
        {
            "text": "Short text",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 2
        },
        {
            "text": "This is a longer piece of text that should wrap across multiple lines nicely",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 3
        },
        {
            "text": "Supercalifragilisticexpialidocious",  # Single long word
            "max_width": 100,
            "font_size": 9,
            "max_lines": 1
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Input: \"{test['text']}\"")
        wrapped = filler._wrap_text_to_width(
            test['text'],
            test['max_width'],
            test['font_size'],
            test['max_lines']
        )

        if wrapped:
            print(f"   Result: {len(wrapped)} line(s)")
            for j, line in enumerate(wrapped, 1):
                width = fitz.get_text_length(line, fontname="helv", fontsize=test['font_size'])
                fits = "[OK]" if width <= test['max_width'] else "[X]"
                print(f"     Line {j} [{fits}]: \"{line}\" ({width:.1f}pt)")
        else:
            print("   Result: Could not wrap (None)")


def create_sample_data(text_length: str = "medium") -> RiskProfileData:
    """
    Create sample data with different text lengths

    Args:
        text_length: "short", "medium", "long", or "very_long"
    """
    text_samples = {
        "short": {
            "profession": "Yes",
            "investments": "Stocks and bonds",
            "expenses": "3-6 months",
            "q1": "Agree",
            "q2": "Moderately",
        },
        "medium": {
            "profession": "I have 5 years experience in finance",
            "investments": "Stocks, bonds, mutual funds, and property",
            "expenses": "I have 3-6 months of expenses saved",
            "q1": "I agree with this statement",
            "q2": "I am moderately comfortable with risk",
        },
        "long": {
            "profession": "Yes, I have over 10 years of experience working in financial services and investment banking",
            "investments": "I have invested in stocks, bonds, mutual funds, ETFs, property, and alternative investments over the years",
            "expenses": "I maintain an emergency fund covering 6-12 months of living expenses in easily accessible savings accounts",
            "q1": "I strongly agree - I actively look for opportunities to explore new investment options that could grow my wealth",
            "q2": "I believe in seeking the best possible returns even if it means accepting some additional volatility in my portfolio",
        },
        "very_long": {
            "profession": "Yes, I have extensive experience managing investment portfolios, working with pension funds, and advising high-net-worth individuals on complex financial planning strategies over the past 15 years in the investment banking sector",
            "investments": "Throughout my career, I have personally invested in a diverse range of assets including equities, fixed income securities, real estate investment trusts, commodities, foreign exchange, hedge funds, private equity, and various alternative investment vehicles",
            "expenses": "I maintain a comprehensive emergency fund that covers 12-18 months of living expenses, held in high-interest savings accounts and short-term government bonds to ensure liquidity while preserving capital value during market downturns",
            "q1": "I strongly agree with this statement as I have consistently demonstrated a proactive approach to identifying and pursuing new investment opportunities that align with my long-term financial goals and risk tolerance throughout my investment journey",
            "q2": "I am very comfortable accepting higher levels of volatility and market risk in pursuit of potentially superior long-term returns, as I have both the knowledge and emotional fortitude to weather short-term market fluctuations without panic selling",
        }
    }

    samples = text_samples.get(text_length, text_samples["medium"])

    return RiskProfileData(
        client_info=ClientInfo(
            full_name="Test Client",
            completion_date="2024-01-15",
            created_by="Test Advisor"
        ),
        knowledge_experience=KnowledgeExperience(
            relevant_profession=samples["profession"],
            past_investments=samples["investments"]
        ),
        capacity_for_loss=CapacityForLoss(
            emergency_expenses=samples["expenses"],
            daily_living_expenses="Yes, adequately covered",
            significant_proportion="No",
            major_commitments="None planned",
            dependants="No dependants"
        ),
        questionnaire_answers=RiskQuestionnaireAnswers(
            q1_explore_opportunities=samples["q1"],
            q2_best_return=samples["q2"],
            q3_typical_attitude="Balanced approach",
            q4_past_risk="Moderate risk",
            q5_safe_steady="Somewhat agree",
            q6_high_growth="Moderately interested",
            q7_willing_to_invest="50-75%",
            q8_friend_describe="Cautious but willing",
            q9_highs_and_lows="Somewhat comfortable",
            q10_two_products="Product A",
            q11_small_certain="Depends on timeframe",
            q12_losses_or_gains="Balanced",
            q13_money_safe="Moderately agree",
            investment_term="5-10 years"
        ),
        risk_profile_result=RiskProfileResult(
            risk_level="Moderate Risk Profile",
            risk_number=4,
            description="This is a balanced approach suitable for medium-term goals",
            investment_term="5-10 years",
            min_growth_rate=2.5,
            max_growth_rate=8.5,
            avg_growth_rate=5.5
        )
    )


def test_pdf_generation():
    """Test actual PDF generation with different text lengths"""
    print_section("Testing PDF Generation with Different Text Lengths")

    filler = PDFFiller()

    # Check if template exists
    if not filler.template_path.exists():
        print(f"[ERROR] Template not found at: {filler.template_path}")
        print("   Please ensure the template PDF exists before running this test.")
        return

    print(f"[OK] Template found at: {filler.template_path}")

    test_lengths = ["short", "medium", "long", "very_long"]
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    for length in test_lengths:
        print(f"\n{length.upper()} Text Test:")
        print("-" * 40)

        # Create sample data
        data = create_sample_data(length)

        # Show sample text
        print(f"Sample profession answer: \"{data.knowledge_experience.relevant_profession}\"")
        print(f"Length: {len(data.knowledge_experience.relevant_profession)} characters")

        try:
            # Generate PDF
            pdf_bytes = filler.fill_template(data)

            # Save to file
            output_path = output_dir / f"test_fitting_{length}.pdf"
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

            print(f"[OK] PDF generated successfully: {output_path}")

            # Analyze the PDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            print(f"  Pages: {len(doc)}")
            doc.close()

        except Exception as e:
            print(f"[ERROR] Error generating PDF: {e}")
            import traceback
            traceback.print_exc()


def test_edge_cases():
    """Test edge cases and special scenarios"""
    print_section("Testing Edge Cases")

    filler = PDFFiller()

    edge_cases = [
        {
            "name": "Empty string",
            "text": "",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 2
        },
        {
            "name": "None value",
            "text": None,
            "max_width": 165,
            "font_size": 9,
            "max_lines": 2
        },
        {
            "name": "Very wide field (no constraint needed)",
            "text": "This should fit easily",
            "max_width": 500,
            "font_size": 9,
            "max_lines": 1
        },
        {
            "name": "No max_width (unrestricted)",
            "text": "This text has no width constraint",
            "max_width": None,
            "font_size": 9,
            "max_lines": 1
        },
        {
            "name": "Special characters",
            "text": "Test with special chars: $@ & symbols: #%",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 2
        },
        {
            "name": "Multiple spaces",
            "text": "Text    with    multiple    spaces",
            "max_width": 165,
            "font_size": 9,
            "max_lines": 2
        },
    ]

    for i, test in enumerate(edge_cases, 1):
        print(f"\n{i}. {test['name']}")
        if test['text'] is not None:
            print(f"   Input: \"{test['text']}\"")
        else:
            print(f"   Input: None")

        try:
            # Convert None to empty string (as done in _insert_text)
            text = str(test['text']) if test['text'] else ""

            if test['max_width']:
                fitted_lines = filler._fit_text_to_width(
                    text,
                    test['max_width'],
                    test['font_size'],
                    test['max_lines']
                )
                print(f"   Result: {len(fitted_lines)} line(s)")
                for j, line in enumerate(fitted_lines, 1):
                    print(f"     Line {j}: \"{line}\"")
            else:
                print(f"   Result: No width constraint - text used as-is")

        except Exception as e:
            print(f"   [ERROR] Error: {e}")


def run_all_tests():
    """Run all test suites"""
    print("\n")
    print("=" * 80)
    print(" " * 20 + "PDF TEXT FITTING TEST SUITE")
    print("=" * 80)

    try:
        # Test 1: Text fitting logic
        test_text_fitting_logic()

        # Test 2: Word wrapping
        test_wrap_text_to_width()

        # Test 3: Edge cases
        test_edge_cases()

        # Test 4: PDF generation (requires template)
        test_pdf_generation()

        print_section("Test Summary")
        print("[OK] All tests completed!")
        print("\nCheck the 'tests/output' directory for generated PDF samples.")
        print("\nReview the console output above for:")
        print("  • Text fitting strategy results")
        print("  • Line wrapping behavior")
        print("  • Truncation warnings")
        print("  • Edge case handling")

    except Exception as e:
        print(f"\n[ERROR] Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
