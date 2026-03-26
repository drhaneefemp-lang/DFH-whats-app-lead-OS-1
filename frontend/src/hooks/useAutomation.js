import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Get API key from localStorage
const getApiKey = () => localStorage.getItem('whatsapp_api_key');

// Axios instance with API key
const apiClient = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const apiKey = getApiKey();
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

// Initialize API key if not exists
export const initializeApiKey = async () => {
  let apiKey = getApiKey();
  if (!apiKey) {
    try {
      const response = await axios.post(`${API}/keys`, { name: 'Automation UI Key' });
      apiKey = response.data.key;
      localStorage.setItem('whatsapp_api_key', apiKey);
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  }
  return apiKey;
};

// Automation Rules Hook
export const useAutomationRules = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRules = useCallback(async () => {
    try {
      await initializeApiKey();
      const response = await apiClient.get('/automation/rules');
      setRules(response.data.rules || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch rules:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRules();
  }, [fetchRules]);

  const createRule = async (ruleData) => {
    const response = await apiClient.post('/automation/rules', ruleData);
    await fetchRules();
    return response.data;
  };

  const updateRule = async (ruleId, ruleData) => {
    const response = await apiClient.patch(`/automation/rules/${ruleId}`, ruleData);
    await fetchRules();
    return response.data;
  };

  const deleteRule = async (ruleId) => {
    await apiClient.delete(`/automation/rules/${ruleId}`);
    await fetchRules();
  };

  const toggleRule = async (ruleId) => {
    const response = await apiClient.post(`/automation/rules/${ruleId}/toggle`);
    await fetchRules();
    return response.data;
  };

  return { rules, loading, error, refresh: fetchRules, createRule, updateRule, deleteRule, toggleRule };
};

// Execution Logs Hook
export const useExecutionLogs = (ruleId = null) => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = useCallback(async () => {
    try {
      await initializeApiKey();
      const params = ruleId ? { rule_id: ruleId, limit: 50 } : { limit: 50 };
      const response = await apiClient.get('/automation/logs', { params });
      setLogs(response.data.logs || []);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    } finally {
      setLoading(false);
    }
  }, [ruleId]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  return { logs, loading, refresh: fetchLogs };
};

// Trigger and Action Types Hook
export const useAutomationMeta = () => {
  const [triggers, setTriggers] = useState([]);
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMeta = useCallback(async () => {
    try {
      await initializeApiKey();
      const [triggersRes, actionsRes] = await Promise.all([
        apiClient.get('/automation/triggers'),
        apiClient.get('/automation/actions')
      ]);
      setTriggers(triggersRes.data.triggers || []);
      setActions(actionsRes.data.actions || []);
    } catch (err) {
      console.error('Failed to fetch automation meta:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMeta();
  }, [fetchMeta]);

  return { triggers, actions, loading };
};

// Scheduler Status Hook
export const useSchedulerStatus = () => {
  const [status, setStatus] = useState({ running: false, jobs: [] });
  const [loading, setLoading] = useState(true);

  const fetchStatus = useCallback(async () => {
    try {
      await initializeApiKey();
      const response = await apiClient.get('/automation/scheduler/status');
      setStatus(response.data);
    } catch (err) {
      console.error('Failed to fetch scheduler status:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return { status, loading, refresh: fetchStatus };
};

// Agents Hook (for assignment actions)
export const useAgentsForAutomation = () => {
  const [agents, setAgents] = useState([]);

  const fetchAgents = useCallback(async () => {
    try {
      await initializeApiKey();
      const response = await apiClient.get('/agents', { params: { is_active: true } });
      setAgents(response.data.agents || []);
    } catch (err) {
      console.error('Failed to fetch agents:', err);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return { agents };
};

export default apiClient;
