import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.models import Lead, Product

def create_lead(
    db: Session,
    requirement: str,
    retrieved_products: List[Dict[str, Any]],
    ai_analysis: Dict[str, Any]
) -> Lead:
    """Stores a qualified lead record into the database."""
    lead = Lead(
        customer_requirement=requirement,
        retrieved_context=json.dumps(retrieved_products),
        ai_analysis=json.dumps(ai_analysis)
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead

def get_leads(db: Session, limit: int = 50) -> List[Lead]:
    """Retrieves previous lead qualifications ordered newest first."""
    return db.query(Lead).order_by(desc(Lead.created_at)).limit(limit).all()

def get_lead_by_id(db: Session, lead_id: int) -> Optional[Lead]:
    """Retrieves a single lead by its primary ID."""
    return db.query(Lead).filter(Lead.id == lead_id).first()

def get_products(db: Session) -> List[Product]:
    """Retrieves all seeded products in the knowledge base."""
    return db.query(Product).order_by(Product.name).all()
