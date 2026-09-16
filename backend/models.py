from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from backend.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    features = Column(Text, nullable=False)  # JSON-encoded string of list of features
    solution = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    customer_requirement = Column(Text, nullable=False)
    retrieved_context = Column(Text, nullable=False)  # JSON-encoded string of top retrieved products
    ai_analysis = Column(Text, nullable=False)  # JSON-encoded structured analysis from Groq
    created_at = Column(DateTime(timezone=True), server_default=func.now())
