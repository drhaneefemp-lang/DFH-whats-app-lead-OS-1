import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Store API key in localStorage
const getApiKey = () => localStorage.getItem('whatsapp_api_key');
const setApiKey = (key) => localStorage.setItem('whatsapp_api_key', key);

// Axios instance with API key
const apiClient = axios.create({
  baseURL: API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add API key to requests
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
      const response = await axios.post(`${API}/keys`, { name: 'Inbox UI Key' });
      apiKey = response.data.key;
      setApiKey(apiKey);
    } catch (error) {
      console.error('Failed to create API key:', error);
    }
  }
  return apiKey;
};

// Conversations hook - group messages by sender
export const useConversations = (pollInterval = 5000) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchConversations = useCallback(async () => {
    try {
      // Fetch all inbound messages
      const messagesRes = await apiClient.get('/messages', {
        params: { direction: 'inbound', limit: 500 }
      });
      
      // Fetch all leads
      const leadsRes = await apiClient.get('/leads', { params: { limit: 500 } });
      
      const messages = messagesRes.data.messages || [];
      const leads = leadsRes.data.leads || [];
      
      // Create lead lookup by phone
      const leadsByPhone = {};
      leads.forEach(lead => {
        leadsByPhone[lead.phone] = lead;
      });
      
      // Group messages by sender (phone number)
      const conversationMap = {};
      messages.forEach(msg => {
        const phone = msg.sender;
        if (!conversationMap[phone]) {
          conversationMap[phone] = {
            phone,
            messages: [],
            lead: leadsByPhone[phone] || null,
            lastMessage: null,
            unreadCount: 0,
            contactName: msg.contact_name || `User ${phone.slice(-4)}`
          };
        }
        conversationMap[phone].messages.push(msg);
      });
      
      // Process conversations
      const convList = Object.values(conversationMap).map(conv => {
        // Sort messages by date
        conv.messages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
        conv.lastMessage = conv.messages[conv.messages.length - 1];
        return conv;
      });
      
      // Sort by last message date (newest first)
      convList.sort((a, b) => 
        new Date(b.lastMessage?.created_at || 0) - new Date(a.lastMessage?.created_at || 0)
      );
      
      setConversations(convList);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    initializeApiKey().then(() => {
      fetchConversations();
    });
    
    const interval = setInterval(fetchConversations, pollInterval);
    return () => clearInterval(interval);
  }, [fetchConversations, pollInterval]);

  return { conversations, loading, error, refresh: fetchConversations };
};

// Single conversation with all messages (inbound + outbound)
export const useConversationMessages = (phone, pollInterval = 3000) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMessages = useCallback(async () => {
    if (!phone) return;
    
    try {
      const response = await apiClient.get('/messages', {
        params: { phone_number: phone, limit: 200 }
      });
      
      const allMessages = response.data.messages || [];
      // Sort by date ascending
      allMessages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      setMessages(allMessages);
    } catch (err) {
      console.error('Failed to fetch messages:', err);
    } finally {
      setLoading(false);
    }
  }, [phone]);

  useEffect(() => {
    fetchMessages();
    const interval = setInterval(fetchMessages, pollInterval);
    return () => clearInterval(interval);
  }, [fetchMessages, pollInterval]);

  return { messages, loading, refresh: fetchMessages };
};

// Agents hook
export const useAgents = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAgents = useCallback(async () => {
    try {
      // Ensure API key is initialized
      await initializeApiKey();
      const response = await apiClient.get('/agents', { params: { is_active: true } });
      setAgents(response.data.agents || []);
    } catch (err) {
      console.error('Failed to fetch agents:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
  }, [fetchAgents]);

  return { agents, loading, refresh: fetchAgents };
};

// Lead operations
export const useLeadOperations = () => {
  const assignLead = async (leadId, agentId) => {
    const response = await apiClient.post(`/leads/${leadId}/assign`, { agent_id: agentId });
    return response.data;
  };

  const updateLeadStatus = async (leadId, status, notes = null) => {
    const response = await apiClient.post(`/leads/${leadId}/status`, { status, notes });
    return response.data;
  };

  const updateLead = async (leadId, data) => {
    const response = await apiClient.patch(`/leads/${leadId}`, data);
    return response.data;
  };

  return { assignLead, updateLeadStatus, updateLead };
};

// Send message
export const useSendMessage = () => {
  const [sending, setSending] = useState(false);

  const sendTextMessage = async (recipientPhone, messageText, phoneNumberId = null) => {
    setSending(true);
    try {
      const response = await apiClient.post('/messages/text', {
        recipient_phone: recipientPhone,
        message_text: messageText,
        phone_number_id: phoneNumberId
      });
      return response.data;
    } finally {
      setSending(false);
    }
  };

  return { sendTextMessage, sending };
};

// WhatsApp numbers
export const useWhatsAppNumbers = () => {
  const [numbers, setNumbers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNumbers = useCallback(async () => {
    try {
      const response = await apiClient.get('/numbers');
      setNumbers(response.data || []);
    } catch (err) {
      console.error('Failed to fetch WhatsApp numbers:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNumbers();
  }, [fetchNumbers]);

  return { numbers, loading, refresh: fetchNumbers };
};

export default apiClient;
