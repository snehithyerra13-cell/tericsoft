import React from 'react';
import { X, Database, Tag } from 'lucide-react';

export default function ProductsModal({ isOpen, onClose, products }) {
  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Database size={20} style={{ color: 'var(--accent-primary)' }} />
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>Knowledge Base Catalog</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Seeded enterprise products stored in SQLite used for local TF-IDF matching
              </p>
            </div>
          </div>
          <button onClick={onClose} className="btn-secondary" style={{ padding: '0.35rem 0.6rem' }}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {products.map((p) => (
            <div key={p.id} className="catalog-item">
              <div className="catalog-item-header">
                <h4 style={{ color: '#fff', fontSize: '1rem', fontWeight: 600 }}>{p.name}</h4>
                <span className="badge badge-info">
                  <Tag size={10} />
                  {p.category}
                </span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
                {p.description}
              </p>
              <div style={{ fontSize: '0.775rem', color: '#9ca3af', marginBottom: '0.4rem' }}>
                <strong style={{ color: '#d1d5db' }}>Target Solution:</strong> {p.solution}
              </div>
              <div className="feature-tag-list">
                {p.features?.map((feat, fIdx) => (
                  <span key={fIdx} className="feature-tag">
                    {feat}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
