import axios from 'axios';

export const API_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
});

export const formatApiError = (error, fallback = 'Something went wrong.') => {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg || JSON.stringify(item)).join(', ');
  }
  if (detail && typeof detail === 'object') {
    const msgs = [];
    if (detail.message) msgs.push(detail.message);
    if (Array.isArray(detail.errors) && detail.errors.length > 0) {
      msgs.push(detail.errors.join('; '));
    }
    return msgs.length > 0 ? msgs.join(' — ') : JSON.stringify(detail);
  }
  return error?.message || fallback;
};

// ============================================================
// PREDICTION OPTIONS & SINGLE PREDICTION
// ============================================================

export const getPredictionOptions = async () => {
  const response = await api.get('/prediction-options');
  return response.data;
};

export const predictEmissions = async (data, token = null) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await api.post('/predict', data, { headers });
  return response.data;
};

// ============================================================
// USER HISTORY
// ============================================================

export const getHistory = async (token) => {
  const response = await api.get('/history', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

// ============================================================
// BATCH CSV UPLOAD
// ============================================================

export const uploadBatchCSV = async (file, token = null) => {
  const formData = new FormData();
  formData.append('file', file);

  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await api.post('/predict/batch', formData, { headers });
  return response.data;
};

// ============================================================
// INSIGHTS & HEALTH
// ============================================================

export const getSectorInsights = async () => {
  const response = await api.get('/sector-insights');
  return response.data;
};

export const getDatasetInsights = async () => {
  const response = await api.get('/dataset-insights');
  return response.data;
};

export const getModelInsights = async () => {
  const response = await api.get('/model-insights');
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const askAI = async (message, prediction = null) => {
  const response = await api.post('/ask-ai', { message, prediction });
  return response.data;
};

// ============================================================
// AI CHATBOT (STREAMING + RAG + PERSISTENT HISTORY)
// ============================================================

export const uploadRagDocument = async (file, token = null) => {
  const formData = new FormData();
  formData.append('file', file);
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await api.post('/api/chat/upload', formData, { headers });
  return response.data;
};

export const getRagDocuments = async (token = null) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await api.get('/api/chat/documents', { headers });
  return response.data;
};

export const getChatHistory = async (sessionId, token = null) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await api.get(`/api/chat/history/${encodeURIComponent(sessionId)}`, {
    headers,
  });
  return response.data;
};

export const streamChat = async ({
  sessionId,
  message,
  currentPrediction = null,
  token = null,
  onStatus,
  onToken,
  onDone,
  onError,
}) => {
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}/api/chat/stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      session_id: sessionId,
      message,
      current_prediction: currentPrediction,
    }),
  });

  if (!response.ok || !response.body) {
    const errText = await response.text();
    throw new Error(errText || `HTTP ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() || '';

    for (const evt of events) {
      const line = evt
        .split('\n')
        .find((l) => l.startsWith('data: '));
      if (!line) continue;

      try {
        const payload = JSON.parse(line.slice(6));
        if (payload.status && onStatus) onStatus(payload.status);
        if (payload.token && onToken) onToken(payload.token);
        if (payload.error && onError) onError(payload.error);
        if (payload.done && onDone) onDone();
      } catch (e) {
        console.error('Failed to parse SSE payload:', line, e);
      }
    }
  }
};

export default api;