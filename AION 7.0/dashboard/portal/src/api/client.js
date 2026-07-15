const API_BASE = import.meta.env.VITE_API_URL || '';

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: { message: res.statusText } }));
    throw new Error(err.error?.message || err.detail || 'Erro na requisicao');
  }
  return res.json();
}

export const api = {
  health: () => request('/health'),
  agents: () => request('/api/agents/health'),
  plans: () => request('/api/subscriptions/plans'),
  getPlan: (id) => request(`/api/subscriptions/plans/${id}`),
  createCheckout: (planId, successUrl, cancelUrl) =>
    request('/api/subscriptions/checkout', {
      method: 'POST',
      body: JSON.stringify({
        plan_id: planId,
        success_url: successUrl || window.location.origin + '/subscription?success=true',
        cancel_url: cancelUrl || window.location.origin + '/subscription?canceled=true',
      }),
    }),
  executeTask: (data) =>
    request('/api/agents/execute', {
      method: 'POST', body: JSON.stringify(data),
    }),
  agentStatus: (agentId) =>
    request(`/api/agents/${agentId}/status`),
  initializeAgents: (tenant, clusters) =>
    request('/api/agents/initialize', {
      method: 'POST',
      body: JSON.stringify({ tenant, clusters }),
    }),
};
