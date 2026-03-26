import { useState, useCallback } from 'react';
import ConversationListPanel from '../components/ConversationListPanel';
import ChatMessageInterface from '../components/ChatMessageInterface';
import LeadDetailsSidebar from '../components/LeadDetailsSidebar';
import { 
  useConversations, 
  useConversationMessages,
  useAgents,
  useLeadOperations,
  useSendMessage
} from '../hooks/useApi';
import '../App.css';

const InboxPage = () => {
  const [selectedConversation, setSelectedConversation] = useState(null);
  
  // Fetch data
  const { conversations, loading: loadingConversations, refresh: refreshConversations } = useConversations(5000);
  const { messages, loading: loadingMessages, refresh: refreshMessages } = useConversationMessages(
    selectedConversation?.phone, 
    3000
  );
  const { agents } = useAgents();
  const { assignLead, updateLeadStatus, updateLead } = useLeadOperations();
  const { sendTextMessage, sending } = useSendMessage();

  const handleSelectConversation = useCallback((conv) => {
    setSelectedConversation(conv);
  }, []);

  const handleSendMessage = useCallback(async (text) => {
    if (!selectedConversation) return;
    
    try {
      await sendTextMessage(selectedConversation.phone, text);
      // Refresh messages after sending
      setTimeout(() => {
        refreshMessages();
        refreshConversations();
      }, 500);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  }, [selectedConversation, sendTextMessage, refreshMessages, refreshConversations]);

  const handleAssignAgent = useCallback(async (leadId, agentId) => {
    try {
      await assignLead(leadId, agentId);
      refreshConversations();
    } catch (error) {
      console.error('Failed to assign agent:', error);
    }
  }, [assignLead, refreshConversations]);

  const handleUpdateStatus = useCallback(async (leadId, status) => {
    try {
      await updateLeadStatus(leadId, status);
      refreshConversations();
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  }, [updateLeadStatus, refreshConversations]);

  const handleUpdateLead = useCallback(async (leadId, data) => {
    try {
      await updateLead(leadId, data);
      refreshConversations();
    } catch (error) {
      console.error('Failed to update lead:', error);
    }
  }, [updateLead, refreshConversations]);

  // Update selected conversation when data refreshes
  const currentConversation = selectedConversation 
    ? conversations.find(c => c.phone === selectedConversation.phone) || selectedConversation
    : null;

  return (
    <div className="inbox-container w-full h-screen grid grid-cols-1 lg:grid-cols-4 overflow-hidden">
      {/* Conversation List */}
      <ConversationListPanel
        conversations={conversations}
        selectedPhone={selectedConversation?.phone}
        onSelectConversation={handleSelectConversation}
        loading={loadingConversations}
      />

      {/* Chat Interface */}
      <ChatMessageInterface
        conversation={currentConversation}
        messages={messages}
        loading={loadingMessages}
        onSendMessage={handleSendMessage}
        sending={sending}
      />

      {/* Lead Details */}
      <LeadDetailsSidebar
        conversation={currentConversation}
        agents={agents}
        onAssignAgent={handleAssignAgent}
        onUpdateStatus={handleUpdateStatus}
        onUpdateLead={handleUpdateLead}
      />
    </div>
  );
};

export default InboxPage;
