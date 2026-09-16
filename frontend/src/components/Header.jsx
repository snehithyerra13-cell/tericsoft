import React from 'react';
import { Sparkles, Database, CheckCircle2, AlertTriangle, BookOpen } from 'lucide-react';

export default function Header({ health, onOpenProductsModal }) {
  const isGroqReady = health?.groq_configured;
  const productsCount = health?.products_count || 10;

  return (
    <header className="app-header">
      <div className="header-inner">
        <div className="logo-badge">
          <div className="logo-icon">
            <Sparkles size={22} />
          </div>
          <div className="logo-text">
            <h1>LeadAI Qualification Assistant</h1>
            <p>Local TF-IDF Knowledge Retrieval + Groq LLM</p>
          </div>
        </div>

        <div className="header-actions">
          <div className="badges-group" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            {isGroqReady ? (
              <span className="badge badge-success" title={`Model: ${health?.model}`}>
                <CheckCircle2 size={13} />
                Groq Active ({health?.model?.split('-')[0] || 'LLM'})
              </span>
            ) : (
              <span className="badge badge-warning" title="GROQ_API_KEY is not set in backend/.env">
                <AlertTriangle size={13} />
                API Key Needed
              </span>
            )}

            <button
              onClick={onOpenProductsModal}
              className="btn-secondary"
              title="View the 10 catalog products in SQLite knowledge base"
            >
              <Database size={14} />
              <span>Catalog ({productsCount})</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
