const API_BASE = import.meta.env.VITE_API_URL !== undefined 
  ? import.meta.env.VITE_API_URL 
  : 'http://127.0.0.1:8000';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error(`Health check failed (${res.status})`);
    return await res.json();
  } catch (err) {
    console.error('API health check error:', err);
    throw err;
  }
}

export async function analyzeLead(requirement) {
  try {
    const res = await fetch(`${API_BASE}/api/leads/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ requirement }),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || `Server error (${res.status})`);
    }
    return data;
  } catch (err) {
    console.error('Analyze lead error:', err);
    throw err;
  }
}

export async function getLeadsHistory() {
  try {
    const res = await fetch(`${API_BASE}/api/leads`);
    if (!res.ok) throw new Error(`Failed to load leads history (${res.status})`);
    return await res.json();
  } catch (err) {
    console.error('Get leads history error:', err);
    return [];
  }
}

export async function getProducts() {
  try {
    const res = await fetch(`${API_BASE}/api/products`);
    if (!res.ok) throw new Error(`Failed to load knowledge base (${res.status})`);
    return await res.json();
  } catch (err) {
    console.error('Get products error:', err);
    return [];
  }
}
