import React from 'react';
import { History, Clock, ArrowRight, RefreshCw } from 'lucide-react';

export default function LeadHistory({
  history,
  onSelectLead,
  selectedLeadId,
  onRefresh,
  isLoading
}) {
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const d = new Date(dateStr);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  return (
    <div className="card history-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="card-title" style={{ margin: 0 }}>
          <History size={18} />
          <span>Lead History</span>
        </div>
        <button
          onClick={onRefresh}
          className="btn-secondary"
          style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
          title="Refresh History"
          disabled={isLoading}
        >
          <RefreshCw size={12} className={isLoading ? 'spinner-inline' : ''} />
          <span>Refresh</span>
        </button>
      </div>

      {(!history || history.length === 0) ? (
        <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          No previous leads analyzed yet.
        </div>
      ) : (
        <div className="history-list">
          {history.map((item) => {
            const isSelected = selectedLeadId === item.id;
            const priority = item.analysis?.priority || 'Medium';
            const score = item.analysis?.lead_score;

            return (
              <div
                key={item.id}
                className={`history-item ${isSelected ? 'active' : ''}`}
                onClick={() => onSelectLead(item)}
              >
                <div className="history-item-header">
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Clock size={11} />
                    {formatDate(item.created_at)}
                  </span>
                  <span style={{ fontWeight: 600 }}>Lead #{item.id}</span>
                </div>

                <div className="history-item-req">
                  {item.customer_requirement}
                </div>

                <div className="history-meta" style={{ justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                    <span
                      style={{
                        fontSize: '0.7rem',
                        padding: '0.15rem 0.4rem',
                        borderRadius: '4px',
                        background: priority === 'High' ? 'rgba(52, 211, 153, 0.2)' : 'rgba(251, 191, 36, 0.2)',
                        color: priority === 'High' ? '#34d399' : '#fbbf24'
                      }}
                    >
                      {priority}
                    </span>
                    {typeof score === 'number' && (
                      <span style={{ fontSize: '0.7rem', color: '#9ca3af' }}>
                        {score}/100
                      </span>
                    )}
                  </div>
                  <ArrowRight size={13} style={{ color: 'var(--text-muted)' }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
