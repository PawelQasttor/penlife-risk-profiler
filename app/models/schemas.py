"""
Pydantic models for risk profile data
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class ClientInfo(BaseModel):
    """Client identification information"""
    full_name: str = Field(..., description="Client's full name")
    created_by: str = Field(..., description="Adviser who created the report")
    company: str = Field(default="PenLife Associates", description="Company name")
    completion_date: str = Field(..., description="Date questionnaire was completed")


class QuestionAnswer(BaseModel):
    """Single question-answer pair"""
    question_number: int
    question_text: str
    answer: str


class RiskQuestionnaireAnswers(BaseModel):
    """All 13 risk attitude questions"""
    q1_explore_opportunities: str
    q2_best_return: str
    q3_typical_attitude: str
    q4_past_risk: str
    q5_safe_steady: str
    q6_high_growth: str
    q7_willing_to_invest: str
    q8_friend_describe: str
    q9_highs_and_lows: str
    q10_two_products: str
    q11_small_certain: str
    q12_losses_or_gains: str
    q13_money_safe: str
    investment_term: str


class CapacityForLoss(BaseModel):
    """Capacity for loss assessment"""
    emergency_expenses: str
    daily_living_expenses: str
    significant_proportion: str
    major_commitments: str
    dependants: str


class KnowledgeExperience(BaseModel):
    """Investment knowledge and experience"""
    relevant_profession: str
    past_investments: str


class RiskProfileResult(BaseModel):
    """Initial risk profile assessment result"""
    risk_level: str = Field(..., description="e.g., '4 - Moderate to Adventurous'")
    risk_number: int = Field(..., ge=1, le=10, description="Risk level 1-10")
    investment_term: str = Field(..., description="e.g., 'Medium Term (8 - 15 Years)'")
    description: str = Field(..., description="Risk profile description")
    min_growth_rate: Optional[float] = None
    max_growth_rate: Optional[float] = None
    avg_growth_rate: Optional[float] = None


class AdjustedRiskProfile(BaseModel):
    """Adviser-adjusted risk profile"""
    adjusted_level: str = Field(..., description="e.g., 'EValue Risk 5 Long Term (16+ Years)'")
    adjusted_number: int = Field(..., ge=1, le=10)
    adjusted_term: str
    description: str
    min_growth_rate: Optional[float] = None
    max_growth_rate: Optional[float] = None
    avg_growth_rate: Optional[float] = None
    adviser_notes: Optional[str] = None


class RiskProfileData(BaseModel):
    """Complete risk profile data extracted from Cashcalc PDF"""
    client_info: ClientInfo
    questionnaire_answers: RiskQuestionnaireAnswers
    capacity_for_loss: CapacityForLoss
    knowledge_experience: KnowledgeExperience
    risk_profile_result: RiskProfileResult
    adjusted_risk_profile: Optional[AdjustedRiskProfile] = None


class ProcessingResponse(BaseModel):
    """Response model for successful processing"""
    success: bool = True
    message: str = "PDF processed successfully"
    client_name: str
    filename: str


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    message: str
    details: Optional[Dict] = None
