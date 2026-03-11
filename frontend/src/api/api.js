import axios from 'axios';

// Fallback to localhost if deployed to Render without an explicit ENV var
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: API_URL,
});

export const predictEmissions = async (data, token = null) => {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const response = await api.post('/predict', data, { headers });
  return response.data;
};

export const getHistory = async (token) => {
  const response = await api.get('/history', {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};

export default api;
