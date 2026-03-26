import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const getApiKey = () => localStorage.getItem('whatsapp_api_key');

const apiClient = axios.create({
  baseURL: API,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const apiKey = getApiKey();
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

// Initialize API key
export const initializeApiKey = async () => {
  let apiKey = getApiKey();
  if (!apiKey) {
    try {
      const response = await axios.post(`${API}/keys`, { name: 'Dashboard Key' });
      apiKey = response.data.key;
      localStorage.setItem('whatsapp_api_key', apiKey);
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  }
  return apiKey;
};

// Dashboard Metrics Hook
export const useDashboardMetrics = (startDate, endDate) => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setLoading(true);
      await initializeApiKey();
      
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await apiClient.get('/dashboard/metrics', { params });
      setMetrics(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch metrics:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  return { metrics, loading, error, refresh: fetchMetrics };
};

// Leads Over Time Hook
export const useLeadsOverTime = (startDate, endDate, interval = 'day') => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      await initializeApiKey();
      
      const params = { interval };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await apiClient.get('/dashboard/leads-over-time', { params });
      setData(response.data.data || []);
    } catch (err) {
      console.error('Failed to fetch leads over time:', err);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, interval]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, refresh: fetchData };
};

// Messages Over Time Hook
export const useMessagesOverTime = (startDate, endDate, interval = 'day') => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      await initializeApiKey();
      
      const params = { interval };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await apiClient.get('/dashboard/messages-over-time', { params });
      setData(response.data.data || []);
    } catch (err) {
      console.error('Failed to fetch messages over time:', err);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate, interval]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, refresh: fetchData };
};

// Response Times Hook
export const useResponseTimes = (startDate, endDate) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      await initializeApiKey();
      
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await apiClient.get('/dashboard/response-times', { params });
      setData(response.data);
    } catch (err) {
      console.error('Failed to fetch response times:', err);
    } finally {
      setLoading(false);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, refresh: fetchData };
};

export default apiClient;
