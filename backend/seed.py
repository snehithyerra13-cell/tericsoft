import json
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models import Product

SEED_PRODUCTS = [
    {
        "name": "CRM Automation Suite",
        "category": "Sales & CRM",
        "description": "Enterprise-grade customer relationship management software with automated pipeline tracking, contact enrichment, and deal velocity tracking.",
        "features": [
            "Automated contact and deal lifecycle management",
            "Bi-directional email and calendar synchronization",
            "Smart lead routing based on territory and rep expertise",
            "Pipeline forecasting with weighted probability stages",
            "Native integrations with Slack, Gmail, and Microsoft 365"
        ],
        "solution": "Eliminates manual CRM data entry for B2B sales teams, accelerates deal closing cycles, and gives revenue leaders accurate pipeline forecasts."
    },
    {
        "name": "AI Customer Support Platform",
        "category": "Customer Support",
        "description": "Next-generation generative AI customer service platform providing automated omnichannel ticket resolution, sentiment detection, and agent co-pilot.",
        "features": [
            "24/7 automated resolution for tier-1 customer inquiries across chat, email, and social",
            "Real-time agent co-pilot with context-aware response suggestions",
            "Multilingual instant translation in over 50 languages",
            "Customer sentiment and escalation risk scoring",
            "Deep integrations with Zendesk, Freshdesk, and Salesforce Service Cloud"
        ],
        "solution": "Reduces customer wait times by 80%, deflects routine repetitive support queries, and lowers overall contact center operational costs."
    },
    {
        "name": "Sales Analytics Dashboard",
        "category": "Analytics & BI",
        "description": "Predictive sales intelligence and executive dashboard software delivering real-time revenue KPIs, rep activity attribution, and quota attainment models.",
        "features": [
            "Real-time ARR, MRR, churn, and expansion revenue tracking",
            "Sales rep quota performance tracking and win/loss breakdown",
            "Predictive pipeline health scoring powered by historical cohort metrics",
            "Interactive drill-down reports with CSV and automated executive PDF exports",
            "Native connectors for Snowflake, BigQuery, Postgres, and Salesforce"
        ],
        "solution": "Provides sales leadership and CFOs with a unified single source of truth for revenue forecasting, eliminating spreadsheet chaos."
    },
    {
        "name": "Marketing Automation Platform",
        "category": "Marketing Tech",
        "description": "Multi-channel marketing automation engine enabling behavioral email nurturing, automated lead scoring, dynamic landing pages, and campaign ROI tracking.",
        "features": [
            "Drag-and-drop customer journey builder for automated email and SMS sequences",
            "Predictive behavioral lead scoring based on website interactions and content downloads",
            "Dynamic audience segmentation and ABM (Account-Based Marketing) targeting",
            "A/B testing for landing pages, forms, and email subject lines",
            "Multi-touch campaign attribution modeling for paid advertising channels"
        ],
        "solution": "Enables demand generation teams to convert website visitors into qualified pipeline through personalized automated nurture sequences."
    },
    {
        "name": "Document Intelligence System",
        "category": "Artificial Intelligence",
        "description": "AI-powered optical character recognition (OCR) and document extraction engine designed for unstructured PDFs, contracts, invoices, and financial reports.",
        "features": [
            "Zero-shot key-value pair extraction from invoices, receipts, and POs",
            "Automated legal contract clause comparison and risk flagging",
            "Multi-format ingestion supporting PDF, TIFF, DOCX, and scanned image formats",
            "Human-in-the-loop review interface with confidence threshold controls",
            "Enterprise compliance with HIPAA, SOC2 Type II, and GDPR"
        ],
        "solution": "Automates accounts payable, compliance audits, and mortgage processing, reducing document processing times from days to seconds."
    },
    {
        "name": "Fraud Detection Platform",
        "category": "Risk & Security",
        "description": "Real-time payment fraud prevention and identity verification engine combining graph analytics, device fingerprinting, and behavioral anomaly detection.",
        "features": [
            "Sub-100ms real-time transaction risk scoring and instant decisioning",
            "Synthetic identity and account takeover (ATO) defense",
            "Device fingerprinting, proxy detection, and geo-velocity anomaly alerts",
            "Configurable rule builder with machine learning fallback models",
            "Chargeback dispute management and fraud pattern visualization"
        ],
        "solution": "Protects online merchants, neo-banks, and fintech platforms from payment fraud and unauthorized transactions while minimizing false declines."
    },
    {
        "name": "Cloud Data Platform",
        "category": "Data Infrastructure",
        "description": "Serverless unified data warehouse and streaming analytics platform for large-scale ETL pipelines, real-time querying, and data cataloging.",
        "features": [
            "Fully managed serverless query engine with auto-scaling compute and storage",
            "Real-time streaming ingestion from Kafka, Kinesis, and IoT endpoints",
            "Built-in data catalog with automated metadata discovery and lineage",
            "Role-based access control (RBAC) and column-level encryption",
            "Seamless compatibility with standard SQL, dbt, Apache Spark, and Python"
        ],
        "solution": "Breaks down internal data silos, allowing engineering and data science teams to query petabyte-scale datasets with sub-second latency."
    },
    {
        "name": "Workflow Automation Suite",
        "category": "Productivity & Ops",
        "description": "Low-code enterprise integration platform as a service (iPaaS) connecting hundreds of SaaS tools with event-driven webhooks and logic triggers.",
        "features": [
            "Visual workflow canvas with conditional branching, loops, and error handling",
            "Pre-built connectors for over 400 popular SaaS applications and databases",
            "Custom webhook listeners and scheduled cron-based background jobs",
            "Encrypted credential vault with fine-grained API token management",
            "Detailed execution audit logs and automatic retry policies on API failures"
        ],
        "solution": "Empowers operations, IT, and product teams to automate cross-functional business processes without writing custom integration glue code."
    },
    {
        "name": "Cybersecurity Monitoring Platform",
        "category": "Cybersecurity",
        "description": "Cloud-native SIEM and extended detection and response (XDR) platform delivering continuous endpoint monitoring, zero-trust telemetry, and threat hunting.",
        "features": [
            "Continuous 24/7 security event log ingestion across cloud workloads and endpoints",
            "AI-driven anomaly detection identifying unauthorized privilege escalations and lateral movement",
            "Automated incident response playbooks for isolating compromised devices",
            "Vulnerability scanner and compliance benchmarking against CIS and NIST guidelines",
            "Unified SecOps console with prioritized MITRE ATT&CK mapping"
        ],
        "solution": "Guards enterprise infrastructure against ransomware, unauthorized intrusions, and data breaches with automated rapid threat containment."
    },
    {
        "name": "Enterprise AI Assistant",
        "category": "Artificial Intelligence",
        "description": "Secure internal conversational AI assistant that connects to enterprise knowledge bases, code repositories, and intranets with strict permission boundaries.",
        "features": [
            "Retrieval-Augmented Generation (RAG) over Notion, Confluence, Google Drive, and Jira",
            "Strict enterprise data privacy with zero model retention on customer queries",
            "Role-based access control ensuring employees only see authorized documents",
            "Code generation, technical documentation search, and internal HR policy Q&A",
            "Available as desktop app, browser extension, and Slack/Teams bot"
        ],
        "solution": "Accelerates employee productivity and internal knowledge discovery, saving hours each week spent searching through disparate internal documents."
    }
]

def seed_products(db: Session) -> int:
    """Populates the database with default enterprise SaaS products if table is empty."""
    existing_count = db.query(Product).count()
    if existing_count > 0:
        return existing_count

    for item in SEED_PRODUCTS:
        product = Product(
            name=item["name"],
            category=item["category"],
            description=item["description"],
            features=json.dumps(item["features"]),
            solution=item["solution"]
        )
        db.add(product)
    
    db.commit()
    return len(SEED_PRODUCTS)

if __name__ == "__main__":
    print("Initializing database tables and seeding products...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = seed_products(db)
        print(f"Database successfully seeded with {count} products.")
    finally:
        db.close()
