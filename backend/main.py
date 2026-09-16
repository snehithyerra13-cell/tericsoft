import json
import logging
from contextlib import asynccontextmanager
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import engine, Base, get_db
from backend.models import Product, Lead
from backend.seed import seed_products
from backend.schemas import (
    LeadAnalyzeRequest,
    LeadResponse,
    LeadHistoryItem,
    ProductSchema,
    HealthResponse,
    LeadAnalysis,
    RetrievedProduct
)
from backend.retrieval.retriever import retrieve_relevant_products
from backend.ai.groq_client import analyze_lead_with_groq, GroqServiceError
from backend import crud

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sales_lead_assistant")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema exists and seed products if empty
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        count = seed_products(db)
        logger.info(f"Knowledge base ready with {count} products.")
    finally:
        db.close()
    yield

app = FastAPI(
    title="AI-Powered Sales Lead Qualification Assistant API",
    version="1.0.0",
    description="Backend API for local TF-IDF product retrieval, Groq LLM lead qualification, and SQLite persistence.",
    lifespan=lifespan
)

# Configure CORS for local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """Health check returning system status, LLM configuration state, and product count."""
    products_count = db.query(Product).count()
    groq_configured = bool(
        (settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())
        or (settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
    )
    model_name = "gemini-1.5-flash" if (settings.GEMINI_API_KEY and not settings.GROQ_API_KEY) else settings.GROQ_MODEL
    return HealthResponse(
        status="ok",
        groq_configured=groq_configured,
        model=model_name,
        products_count=products_count
    )

@app.get("/api/products", response_model=List[ProductSchema])
def list_products(db: Session = Depends(get_db)):
    """Returns all products in the knowledge base."""
    products = crud.get_products(db)
    result = []
    for p in products:
        try:
            feats = json.loads(p.features) if isinstance(p.features, str) else p.features
        except Exception:
            feats = [p.features]
        result.append(
            ProductSchema(
                id=p.id,
                name=p.name,
                description=p.description,
                features=feats,
                solution=p.solution,
                category=p.category
            )
        )
    return result

@app.post("/api/leads/analyze", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
def analyze_lead(request: LeadAnalyzeRequest, db: Session = Depends(get_db)):
    """
    1. Validates the customer requirement.
    2. Retrieves the top 3 relevant products via local TF-IDF cosine similarity.
    3. Invokes Groq LLM to generate structured lead qualification.
    4. Persists the lead, retrieved context, and analysis to SQLite.
    5. Returns the structured result.
    """
    query = request.requirement.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer requirement cannot be empty."
        )

    # 1. Retrieve relevant products
    retrieved_items = retrieve_relevant_products(query=query, top_k=3, db=db)
    if not retrieved_items:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No products found in the knowledge base to match."
        )

    # 2. AI Lead Qualification via Groq
    try:
        analysis: LeadAnalysis = analyze_lead_with_groq(
            requirement=query,
            retrieved_products=retrieved_items
        )
    except GroqServiceError as gse:
        logger.error(f"Groq service error: {gse.message}")
        raise HTTPException(
            status_code=gse.status_code,
            detail=gse.detail
        )
    except Exception as e:
        logger.error(f"Unexpected error analyzing lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during AI analysis: {str(e)}"
        )

    # 3. Store lead in database
    lead_record = crud.create_lead(
        db=db,
        requirement=query,
        retrieved_products=retrieved_items,
        ai_analysis=analysis.model_dump()
    )

    # 4. Format response
    formatted_retrieved = [
        RetrievedProduct(
            id=item["id"],
            name=item["name"],
            category=item["category"],
            description=item["description"],
            features=item["features"],
            solution=item["solution"],
            score=item["score"]
        )
        for item in retrieved_items
    ]

    return LeadResponse(
        lead_id=lead_record.id,
        requirement=lead_record.customer_requirement,
        retrieved_products=formatted_retrieved,
        analysis=analysis,
        created_at=lead_record.created_at
    )

@app.get("/api/leads", response_model=List[LeadHistoryItem])
def get_leads_history(limit: int = 20, db: Session = Depends(get_db)):
    """Returns previous qualified leads from the database."""
    leads = crud.get_leads(db, limit=limit)
    history = []
    for lead in leads:
        try:
            retrieved = json.loads(lead.retrieved_context)
            analysis_dict = json.loads(lead.ai_analysis)
            analysis_obj = LeadAnalysis.model_validate(analysis_dict)
            formatted_retrieved = [
                RetrievedProduct(
                    id=item.get("id", 0),
                    name=item.get("name", ""),
                    category=item.get("category", ""),
                    description=item.get("description", ""),
                    features=item.get("features", []),
                    solution=item.get("solution", ""),
                    score=item.get("score", 0.0)
                )
                for item in retrieved
            ]
            history.append(
                LeadHistoryItem(
                    id=lead.id,
                    customer_requirement=lead.customer_requirement,
                    retrieved_products=formatted_retrieved,
                    analysis=analysis_obj,
                    created_at=lead.created_at
                )
            )
        except Exception as e:
            logger.warning(f"Error parsing historical lead record #{lead.id}: {e}")
            continue
    return history
