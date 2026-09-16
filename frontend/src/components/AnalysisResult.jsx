import React, { useState } from 'react';
import {
  FileText,
  PackageCheck,
  CheckCircle,
  ArrowRightCircle,
  HelpCircle,
  Layers,
  ChevronDown,
  ChevronUp,
  Award,
  Zap
} from 'lucide-react';

export default function AnalysisResult({ result }) {
  const [showRetrieved, setShowRetrieved] = useState(false);

  if (!result || !result.analysis) {
    return null;
  }

  const { analysis, retrieved_products, requirement } = result;

  const getPriorityBadgeClass = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'badge-success';
      case 'medium':
        return 'badge-warning';
      case 'low':
        return 'badge-info';
      default:
        return 'badge-info';
    }
  };

  return (
    <div className="analysis-container">
      {/* 1. LEAD SUMMARY */}
      <div className="summary-card">
        <div className="summary-header">
          <div className="section-title" style={{ margin: 0, color: '#a5b4fc' }}>
            <FileText size={16} />
            <span>Lead Summary</span>
          </div>

          <div className="score-badge-group">
            {analysis.priority && (
              <span className={`badge ${getPriorityBadgeClass(analysis.priority)}`}>
                <Zap size={12} />
                {analysis.priority} Priority
              </span>
            )}
            {typeof analysis.lead_score === 'number' && (
              <span className="score-pill">
                <Award size={12} style={{ display: 'inline', marginRight: 4 }} />
                Score: {analysis.lead_score}/100
              </span>
            )}
          </div>
        </div>

        <p className="summary-text">{analysis.lead_summary}</p>
      </div>

      {/* 2. RELEVANT PRODUCTS / FEATURES */}
      <div className="card">
        <div className="section-title">
          <PackageCheck size={16} />
          <span>Relevant Products / Features</span>
        </div>

        <div className="products-grid">
          {analysis.relevant_products?.map((prod, idx) => {
            // Find matched product in retrieved_products for score and category
            const matchInfo = retrieved_products?.find(
              (p) => p.name.toLowerCase() === prod.name.toLowerCase()
            );

            return (
              <div key={idx} className="product-match-card">
                <div>
                  <div className="product-card-top">
                    <h4 className="product-card-title">{prod.name}</h4>
                    {matchInfo?.score && (
                      <span className="match-score-pill">
                        Match: {Math.round(matchInfo.score * 100)}%
                      </span>
                    )}
                  </div>
                  <p className="product-reason">{prod.reason}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. POTENTIAL CUSTOMER NEEDS */}
      <div className="card">
        <div className="section-title">
          <CheckCircle size={16} />
          <span>Potential Customer Needs</span>
        </div>

        <ul className="needs-list">
          {analysis.potential_customer_needs?.map((need, idx) => (
            <li key={idx} className="need-item">
              <span className="need-item-icon">•</span>
              <span>{need}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* 4. RECOMMENDED NEXT STEP */}
      <div className="card" style={{ padding: '1.25rem' }}>
        <div className="section-title" style={{ color: '#34d399' }}>
          <ArrowRightCircle size={16} />
          <span>Recommended Next Step</span>
        </div>

        <div className="next-step-card">
          <div className="next-step-text">
            {analysis.recommended_next_step}
          </div>
        </div>
      </div>

      {/* 5. FOLLOW-UP QUESTIONS */}
      <div className="card">
        <div className="section-title">
          <HelpCircle size={16} />
          <span>Follow-up Discovery Questions</span>
        </div>

        <ul className="questions-list">
          {analysis.follow_up_questions?.map((q, idx) => (
            <li key={idx} className="question-item">
              <span className="question-number">{idx + 1}</span>
              <span>{q}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* 6. RETRIEVED CONTEXT (ACCORDION) */}
      {retrieved_products && retrieved_products.length > 0 && (
        <div className="retrieved-accordion">
          <button
            type="button"
            className="accordion-trigger"
            onClick={() => setShowRetrieved(!showRetrieved)}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={15} />
              <span>Retrieved Knowledge Base Context ({retrieved_products.length} Products Matched via TF-IDF)</span>
            </div>
            {showRetrieved ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {showRetrieved && (
            <div className="accordion-content">
              {retrieved_products.map((p, idx) => (
                <div
                  key={idx}
                  style={{
                    marginBottom: idx !== retrieved_products.length - 1 ? '1rem' : 0,
                    paddingBottom: idx !== retrieved_products.length - 1 ? '1rem' : 0,
                    borderBottom: idx !== retrieved_products.length - 1 ? '1px solid #374151' : 'none'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <strong style={{ color: '#fff' }}>{p.name}</strong>
                    <span style={{ color: '#a5b4fc', fontSize: '0.75rem', fontFamily: 'var(--font-mono)' }}>
                      Relevance Score: {p.score}
                    </span>
                  </div>
                  <div style={{ color: '#9ca3af', marginBottom: 4 }}>{p.description}</div>
                  <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>
                    <strong>Solution:</strong> {p.solution}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
