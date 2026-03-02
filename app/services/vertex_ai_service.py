"""
Vertex AI service for data validation and text optimization
Uses Google's Gemini model via Vertex AI to validate and optimize extracted PDF data
"""

import logging
from typing import Optional, Dict, Any
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import json

from app.models.schemas import RiskProfileData

logger = logging.getLogger(__name__)


class VertexAIService:
    """Service for AI-powered data validation and optimization using Vertex AI"""

    def __init__(self, project_id: str, location: str = "us-central1", model_name: str = "gemini-1.5-flash"):
        """
        Initialize Vertex AI service

        Args:
            project_id: GCP project ID
            location: GCP region (default: us-central1)
            model_name: Vertex AI model to use (default: gemini-1.5-flash)
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)

        logger.info(f"Initialized Vertex AI service - Project: {project_id}, Location: {location}, Model: {model_name}")

    def validate_and_optimize_data(self, data: RiskProfileData) -> Dict[str, Any]:
        """
        Validate extracted data and optimize text lengths

        Args:
            data: Extracted risk profile data

        Returns:
            Dictionary with validation results and optimized data
        """
        try:
            prompt = self._build_validation_prompt(data)

            # Configure generation settings
            generation_config = GenerationConfig(
                temperature=0.2,  # Low temperature for consistent, factual responses
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )

            # Call Vertex AI
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Parse response
            result = self._parse_validation_response(response.text, data)

            logger.info(f"Validation complete for {data.client_info.full_name}")
            return result

        except Exception as e:
            logger.error(f"Error in Vertex AI validation: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "original_data": data
            }

    def _build_validation_prompt(self, data: RiskProfileData) -> str:
        """Build prompt for Vertex AI validation"""

        prompt = f"""You are a data validation assistant for financial risk profiling documents.

Your tasks:
1. Validate that extracted data is coherent and makes sense
2. Identify any obvious extraction errors or inconsistencies
3. Optimize long text answers to fit within character limits while preserving meaning
4. Ensure professional language and tone

CLIENT DATA:
Client Name: {data.client_info.full_name}
Adviser: {data.client_info.created_by}
Completion Date: {data.client_info.completion_date}

INVESTMENT EXPERIENCE:
Q1 - Relevant Profession: "{data.knowledge_experience.relevant_profession}"
   (Current: {len(data.knowledge_experience.relevant_profession)} chars, Limit: 95 chars)

Q2 - Past Investments: "{data.knowledge_experience.past_investments}"
   (Current: {len(data.knowledge_experience.past_investments)} chars, Limit: 95 chars)

CAPACITY FOR LOSS:
Q1 - Emergency Expenses: "{data.capacity_for_loss.emergency_expenses}"
   (Current: {len(data.capacity_for_loss.emergency_expenses)} chars, Limit: 95 chars)

Q2 - Daily Living Expenses: "{data.capacity_for_loss.daily_living_expenses}"
   (Current: {len(data.capacity_for_loss.daily_living_expenses)} chars, Limit: 95 chars)

Q3 - Significant Proportion: "{data.capacity_for_loss.significant_proportion}"
   (Current: {len(data.capacity_for_loss.significant_proportion)} chars, Limit: 95 chars)

Q4 - Major Commitments: "{data.capacity_for_loss.major_commitments}"
   (Current: {len(data.capacity_for_loss.major_commitments)} chars, Limit: 95 chars)

Q5 - Dependants: "{data.capacity_for_loss.dependants}"
   (Current: {len(data.capacity_for_loss.dependants)} chars, Limit: 95 chars)

RISK QUESTIONNAIRE:
Q1: "{data.questionnaire_answers.q1_explore_opportunities}"
   (Current: {len(data.questionnaire_answers.q1_explore_opportunities)} chars, Limit: 95 chars)

Q2: "{data.questionnaire_answers.q2_best_return}"
   (Current: {len(data.questionnaire_answers.q2_best_return)} chars, Limit: 95 chars)

Q3: "{data.questionnaire_answers.q3_typical_attitude}"
   (Current: {len(data.questionnaire_answers.q3_typical_attitude)} chars, Limit: 95 chars)

Q4: "{data.questionnaire_answers.q4_past_risk}"
   (Current: {len(data.questionnaire_answers.q4_past_risk)} chars, Limit: 95 chars)

Q5: "{data.questionnaire_answers.q5_safe_steady}"
   (Current: {len(data.questionnaire_answers.q5_safe_steady)} chars, Limit: 95 chars)

Q6: "{data.questionnaire_answers.q6_high_growth}"
   (Current: {len(data.questionnaire_answers.q6_high_growth)} chars, Limit: 95 chars)

Q7: "{data.questionnaire_answers.q7_willing_to_invest}"
   (Current: {len(data.questionnaire_answers.q7_willing_to_invest)} chars, Limit: 95 chars)

Q8: "{data.questionnaire_answers.q8_friend_describe}"
   (Current: {len(data.questionnaire_answers.q8_friend_describe)} chars, Limit: 95 chars)

Q9: "{data.questionnaire_answers.q9_highs_and_lows}"
   (Current: {len(data.questionnaire_answers.q9_highs_and_lows)} chars, Limit: 95 chars)

Q10: "{data.questionnaire_answers.q10_two_products}"
   (Current: {len(data.questionnaire_answers.q10_two_products)} chars, Limit: 95 chars)

Q11: "{data.questionnaire_answers.q11_small_certain}"
   (Current: {len(data.questionnaire_answers.q11_small_certain)} chars, Limit: 95 chars)

Q12: "{data.questionnaire_answers.q12_losses_or_gains}"
   (Current: {len(data.questionnaire_answers.q12_losses_or_gains)} chars, Limit: 95 chars)

Q13: "{data.questionnaire_answers.q13_money_safe}"
   (Current: {len(data.questionnaire_answers.q13_money_safe)} chars, Limit: 95 chars)

Investment Term: "{data.questionnaire_answers.investment_term}"
   (Current: {len(data.questionnaire_answers.investment_term)} chars, Limit: 95 chars)

RISK PROFILE RESULT:
Risk Level: {data.risk_profile_result.risk_level}
Risk Number: {data.risk_profile_result.risk_number}
Description: "{data.risk_profile_result.description}"

INSTRUCTIONS:
1. Check for obvious extraction errors (garbled text, missing data, inconsistencies)
2. For any answer over 95 characters, provide a shortened version that:
   - Preserves the core meaning
   - Uses professional financial language
   - Fits within 95 characters
   - Maintains the client's intent

3. Validate consistency:
   - Do answers align with the risk level?
   - Is the professional language appropriate?
   - Are there any contradictions?

4. Return a JSON response with this structure:
{{
  "validation": {{
    "is_valid": true/false,
    "issues": ["list of any issues found"],
    "warnings": ["list of warnings"]
  }},
  "optimizations": {{
    "knowledge_experience": {{
      "relevant_profession": "optimized text if needed",
      "past_investments": "optimized text if needed"
    }},
    "capacity_for_loss": {{
      "emergency_expenses": "optimized text if needed",
      "daily_living_expenses": "optimized text if needed",
      "significant_proportion": "optimized text if needed",
      "major_commitments": "optimized text if needed",
      "dependants": "optimized text if needed"
    }},
    "questionnaire_answers": {{
      "q1_explore_opportunities": "optimized text if needed",
      "q2_best_return": "optimized text if needed",
      "q3_typical_attitude": "optimized text if needed",
      "q4_past_risk": "optimized text if needed",
      "q5_safe_steady": "optimized text if needed",
      "q6_high_growth": "optimized text if needed",
      "q7_willing_to_invest": "optimized text if needed",
      "q8_friend_describe": "optimized text if needed",
      "q9_highs_and_lows": "optimized text if needed",
      "q10_two_products": "optimized text if needed",
      "q11_small_certain": "optimized text if needed",
      "q12_losses_or_gains": "optimized text if needed",
      "q13_money_safe": "optimized text if needed",
      "investment_term": "optimized text if needed"
    }}
  }},
  "summary": "Brief summary of changes made"
}}

Only include fields in "optimizations" that needed changes. If text is under 95 chars and clear, omit it.
Return ONLY valid JSON, no other text.
"""

        return prompt

    def _parse_validation_response(self, response_text: str, original_data: RiskProfileData) -> Dict[str, Any]:
        """Parse and apply Vertex AI validation response"""

        try:
            # Extract JSON from response (handle markdown code blocks)
            json_text = response_text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()

            # Parse JSON
            parsed = json.loads(json_text)

            # Apply optimizations to original data
            optimized_data = original_data.model_copy(deep=True)

            if "optimizations" in parsed:
                opts = parsed["optimizations"]

                # Apply knowledge_experience optimizations
                if "knowledge_experience" in opts:
                    for field, value in opts["knowledge_experience"].items():
                        if value:
                            setattr(optimized_data.knowledge_experience, field, value)

                # Apply capacity_for_loss optimizations
                if "capacity_for_loss" in opts:
                    for field, value in opts["capacity_for_loss"].items():
                        if value:
                            setattr(optimized_data.capacity_for_loss, field, value)

                # Apply questionnaire_answers optimizations
                if "questionnaire_answers" in opts:
                    for field, value in opts["questionnaire_answers"].items():
                        if value:
                            setattr(optimized_data.questionnaire_answers, field, value)

            return {
                "success": True,
                "validation": parsed.get("validation", {}),
                "optimizations_applied": len(parsed.get("optimizations", {})) > 0,
                "summary": parsed.get("summary", "No changes needed"),
                "original_data": original_data,
                "optimized_data": optimized_data
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Vertex AI response as JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            return {
                "success": False,
                "error": "Invalid JSON response from AI",
                "raw_response": response_text,
                "original_data": original_data
            }
        except Exception as e:
            logger.error(f"Error parsing validation response: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "original_data": original_data
            }

    def optimize_single_text(self, text: str, context: str, max_length: int = 95) -> str:
        """
        Optimize a single text field to fit within character limit

        Args:
            text: Text to optimize
            context: Context/description of what this text is
            max_length: Maximum characters allowed

        Returns:
            Optimized text
        """
        if len(text) <= max_length:
            return text

        try:
            prompt = f"""Shorten this text to fit within {max_length} characters while preserving meaning.

Context: {context}
Original text ({len(text)} chars): "{text}"

Requirements:
- Maximum {max_length} characters
- Preserve core meaning
- Use professional financial language
- Maintain client's intent

Return ONLY the shortened text, nothing else."""

            generation_config = GenerationConfig(
                temperature=0.2,
                max_output_tokens=256,
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            optimized = response.text.strip().strip('"').strip("'")

            if len(optimized) <= max_length:
                logger.info(f"Optimized text: {len(text)} -> {len(optimized)} chars")
                return optimized
            else:
                logger.warning(f"AI optimization still too long ({len(optimized)} chars), truncating")
                return optimized[:max_length - 3] + "..."

        except Exception as e:
            logger.error(f"Error optimizing text: {e}")
            # Fallback to simple truncation
            return text[:max_length - 3] + "..."
