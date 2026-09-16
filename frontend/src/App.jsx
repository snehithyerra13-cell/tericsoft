import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import LeadInputForm from './components/LeadInputForm';
import AnalysisResult from './components/AnalysisResult';
import LeadHistory from './components/LeadHistory';
import ProductsModal from './components/ProductsModal';
import { checkHealth, analyzeLead, getLeadsHistory, getProducts } from './services/api';
import { Sparkles, Check, Database, Cpu, Search } from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState(null);
  const [products, setProducts] = useState([]);
  const [history, setHistory] = useState([]);
  const [currentResult, setCurrentResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isProductsModalOpen, setIsProductsModalOpen] = useState(false);

  // Load initial system data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [healthData, productsData, historyData] = await Promise.all([
        checkHealth().catch(() => null),
        getProducts().catch(() => []),
        getLeadsHistory().catch(() => [])
      ]);

      if (healthData) setHealth(healthData);
      if (productsData) setProducts(productsData);
      if (historyData) {
        setHistory(historyData);
        // If there is existing history, show the latest lead as initial preview
        if (historyData.length > 0 && !currentResult) {
          const latest = historyData[0];
          setCurrentResult({
            lead_id: latest.id,
            requirement: latest.customer_requirement,
            retrieved_products: latest.retrieved_products,
            analysis: latest.analysis,
            created_at: latest.created_at
          });
        }
      }
    } catch (err) {
      console.error('Failed to load initial data:', err);
    }
  };

  const handleAnalyze = async (requirementText) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await analyzeLead(requirementText);
      setCurrentResult(response);
      // Prepend to history
      setHistory((prev) => [
        {
          id: response.lead_id,
          customer_requirement: response.requirement,
          retrieved_products: response.retrieved_products,
          analysis: response.analysis,
          created_at: response.created_at || new Date().toISOString()
        },
        ...prev
      ]);
    } catch (err) {
      setError(err.message || 'An error occurred while qualifying the lead.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectLead = (historyItem) => {
    setCurrentResult({
      lead_id: historyItem.id,
      requirement: historyItem.customer_requirement,
      retrieved_products: historyItem.retrieved_products,
      analysis: historyItem.analysis,
      created_at: historyItem.created_at
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app-container">
      <Header
        health={health}
        onOpenProductsModal={() => setIsProductsModalOpen(true)}
      />

      <main className="main-content">
        <div className="layout-grid">
          {/* Main Column */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <LeadInputForm
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
              error={error}
            />

            {/* Loading Indicator */}
            {isLoading && (
              <div className="card loading-card">
                <div className="spinner" />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#fff', marginBottom: '0.25rem' }}>
                  Analyzing requirement and finding relevant solutions...
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  Matching against knowledge base using TF-IDF and synthesizing sales qualification
                </p>

                <div className="loading-steps">
                  <div className="loading-step-item">
                    <Search size={14} style={{ color: '#6366f1' }} />
                    <span>Extracting requirement keywords & context</span>
                  </div>
                  <div className="loading-step-item">
                    <Database size={14} style={{ color: '#6366f1' }} />
                    <span>Computing TF-IDF cosine similarity scores</span>
                  </div>
                  <div className="loading-step-item">
                    <Cpu size={14} style={{ color: '#6366f1' }} />
                    <span>Synthesizing qualification with Groq LLM</span>
                  </div>
                </div>
              </div>
            )}

            {/* Analysis Result */}
            {!isLoading && currentResult && (
              <AnalysisResult result={currentResult} />
            )}

            {/* Empty State */}
            {!isLoading && !currentResult && !error && (
              <div className="card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem', color: 'var(--text-secondary)' }}>
                <Sparkles size={36} style={{ color: 'var(--accent-primary)', opacity: 0.7, margin: '0 auto 1rem' }} />
                <h3 style={{ color: '#fff', fontSize: '1.1rem', marginBottom: '0.5rem' }}>
                  Ready to Qualify Leads
                </h3>
                <p style={{ fontSize: '0.875rem', maxWidth: '440px', margin: '0 auto' }}>
                  Enter a prospect requirement above or pick one of the sample presets to discover matching products, customer needs, and recommended next sales actions.
                </p>
              </div>
            )}
          </div>

          {/* Sidebar Column: Lead History */}
          <div>
            <LeadHistory
              history={history}
              onSelectLead={handleSelectLead}
              selectedLeadId={currentResult?.lead_id}
              onRefresh={loadInitialData}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>

      {/* Catalog Modal */}
      <ProductsModal
        isOpen={isProductsModalOpen}
        onClose={() => setIsProductsModalOpen(false)}
        products={products}
      />
    </div>
  );
}
