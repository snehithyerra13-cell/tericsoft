from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from datetime import datetime

class LeadAnalyzeRequest(BaseModel):
    requirement: str = Field(
        ...,
        min_length=5,
        max_length=4000,
        description="The potential customer's requirement or inquiry"
    )

    @field_validator("requirement")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Customer requirement cannot be empty or whitespace only.")
        if len(trimmed) < 5:
            raise ValueError("Customer requirement must be at least 5 characters.")
        return trimmed

class RelevantProductItem(BaseModel):
    name: str = Field(..., description="Name of the product from retrieved context")
    reason: str = Field(..., description="Why this product addresses the customer need")

class LeadAnalysis(BaseModel):
    lead_summary: str = Field(..., description="Executive summary of the customer lead")
    relevant_products: List[RelevantProductItem] = Field(
        default_factory=list,
        description="Products from retrieved context that match the lead"
    )
    potential_customer_needs: List[str] = Field(
        default_factory=list,
        description="Key inferred customer pain points or needs"
    )
    recommended_next_step: str = Field(
        ...,
        description="Actionable sales recommendation or proposed engagement"
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="2-3 targeted discovery questions to ask the prospect"
    )
    lead_score: Optional[int] = Field(
        default=75,
        ge=0,
        le=100,
        description="Lead qualification score from 0 to 100"
    )
    priority: Optional[str] = Field(
        default="Medium",
        description="Priority level: High, Medium, or Low"
    )

class RetrievedProduct(BaseModel):
    id: int
    name: str
    category: str
    description: str
    features: List[str]
    solution: str
    score: float

class LeadResponse(BaseModel):
    lead_id: int
    requirement: str
    retrieved_products: List[RetrievedProduct]
    analysis: LeadAnalysis
    created_at: Optional[datetime] = None

class LeadHistoryItem(BaseModel):
    id: int
    customer_requirement: str
    retrieved_products: List[RetrievedProduct]
    analysis: LeadAnalysis
    created_at: Optional[datetime] = None

class ProductSchema(BaseModel):
    id: int
    name: str
    description: str
    features: List[str]
    solution: str
    category: str

class HealthResponse(BaseModel):
    status: str
    groq_configured: bool
    model: str
    products_count: int
