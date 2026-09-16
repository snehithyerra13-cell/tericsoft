import React, { useState } from 'react';
import { Send, Loader2, Sparkles, AlertCircle } from 'lucide-react';

const PRESETS = [
  {
    label: 'E-commerce Support',
    text: 'We are a fast-growing e-commerce retailer with 20k monthly support tickets. We need an automated AI customer support system that deflects tier-1 inquiries, handles multi-language chat, and integrates with our Zendesk helpdesk.'
  },
  {
    label: 'Fintech Fraud Prevention',
    text: 'Our fintech platform is processing online transactions and we are experiencing synthetic identity fraud and payment chargebacks. We need a real-time risk scoring engine with device fingerprinting and sub-100ms decisioning.'
  },
  {
    label: 'B2B Sales CRM',
    text: 'We are an enterprise B2B sales team of 45 account executives. Our pipeline data is messy and reps waste hours on manual entry. We need CRM automation with bi-directional email sync, smart lead routing, and revenue forecasting.'
  },
  {
    label: 'Document Intelligence',
    text: 'Our accounting and legal teams process thousands of vendor invoices and contracts every month as unstructured PDFs. We need an AI document extraction system with human-in-the-loop review to extract line items directly into our ERP.'
  }
];

export default function LeadInputForm({ onAnalyze, isLoading, error }) {
  const [requirement, setRequirement] = useState(
    'We are a growing e-commerce company and need automated customer support with analytics.'
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!requirement.trim() || isLoading) return;
    onAnalyze(requirement.trim());
  };

  const handleSelectPreset = (presetText) => {
    setRequirement(presetText);
  };

  const isValid = requirement.trim().length >= 5;

  return (
    <div className="card">
      <div className="form-header">
        <h2>Customer Requirement Analysis</h2>
        <p>Enter the prospective customer's pain points, operational needs, or project RFP.</p>
      </div>

      <div className="preset-chips">
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', alignSelf: 'center' }}>
          Sample Presets:
        </span>
        {PRESETS.map((preset, idx) => (
          <button
            key={idx}
            type="button"
            className="preset-chip"
            onClick={() => handleSelectPreset(preset.text)}
            disabled={isLoading}
          >
            {preset.label}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit}>
        <div className="textarea-wrapper">
          <textarea
            className="textarea-input"
            value={requirement}
            onChange={(e) => setRequirement(e.target.value)}
            placeholder="E.g., We are a growing e-commerce company and need automated customer support with analytics..."
            disabled={isLoading}
            rows={5}
          />
          <div className="textarea-footer">
            <span>Minimum 5 characters</span>
            <span>{requirement.length} / 4000</span>
          </div>
        </div>

        {error && (
          <div className="alert-box alert-danger">
            <AlertCircle size={18} style={{ flexShrink: 0 }} />
            <div>
              <strong>Qualification Error: </strong>
              <span>{error}</span>
            </div>
          </div>
        )}

        <button
          type="submit"
          className="btn-primary"
          disabled={!isValid || isLoading}
        >
          {isLoading ? (
            <>
              <Loader2 size={18} className="spinner-inline" style={{ animation: 'spin 1s linear infinite' }} />
              <span>Analyzing Requirement & Searching Knowledge Base...</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>Analyze Lead & Qualify</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
