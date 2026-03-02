"""
Test PDF generation with actual template and different text lengths
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
            full_name=f"Test Client - {text_length.upper()}",
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


def main():
    """Test PDF generation with actual template"""
    print("=" * 80)
    print("  Testing PDF Generation with Actual Template")
    print("=" * 80)

    filler = PDFFiller()

    # Check if template exists
    if not filler.template_path.exists():
        print(f"\n[ERROR] Template not found at: {filler.template_path}")
        print("Please ensure the template PDF exists before running this test.")
        return

    print(f"\n[OK] Template found: {filler.template_path}")

    test_lengths = ["short", "medium", "long", "very_long"]
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\nOutput directory: {output_dir}")
    print("\n" + "-" * 80)

    for length in test_lengths:
        print(f"\n{length.upper()} Text Test:")
        print("-" * 40)

        # Create sample data
        data = create_sample_data(length)

        # Show sample text
        print(f"Profession: \"{data.knowledge_experience.relevant_profession[:80]}{'...' if len(data.knowledge_experience.relevant_profession) > 80 else ''}\"")
        print(f"  Length: {len(data.knowledge_experience.relevant_profession)} chars")

        print(f"Question 1: \"{data.questionnaire_answers.q1_explore_opportunities[:80]}{'...' if len(data.questionnaire_answers.q1_explore_opportunities) > 80 else ''}\"")
        print(f"  Length: {len(data.questionnaire_answers.q1_explore_opportunities)} chars")

        try:
            # Generate PDF
            print(f"\nGenerating PDF...")
            pdf_bytes = filler.fill_template(data)

            # Save to file
            output_path = output_dir / f"test_fitting_{length}.pdf"
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

            # Get file size
            file_size = len(pdf_bytes) / 1024  # KB

            print(f"[OK] Generated: {output_path.name} ({file_size:.1f} KB)")

        except FileNotFoundError as e:
            print(f"[ERROR] Template file not found: {e}")
            break
        except Exception as e:
            print(f"[ERROR] Failed to generate PDF: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print("  Test Complete!")
    print("=" * 80)
    print(f"\nGenerated PDFs are in: {output_dir}")
    print("\nOpen the PDFs to verify:")
    print("  1. Text fits within boxes")
    print("  2. Long text wraps to multiple lines")
    print("  3. No text overlap")
    print("  4. Truncation with '...' where needed")


if __name__ == "__main__":
    main()
