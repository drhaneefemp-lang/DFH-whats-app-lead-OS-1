import { useState } from 'react';
import { 
  User, 
  Phone, 
  EnvelopeSimple, 
  Tag,
  Clock,
  ChatCircleDots,
  UserCirclePlus,
  CaretDown,
  X,
  Plus,
  Check
} from '@phosphor-icons/react';
import { format } from 'date-fns';

const LEAD_STATUSES = [
  { value: 'new', label: 'New', color: 'bg-blue-100 text-blue-800' },
  { value: 'contacted', label: 'Contacted', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'interested', label: 'Interested', color: 'bg-emerald-100 text-emerald-800' },
  { value: 'converted', label: 'Converted', color: 'bg-green-100 text-green-800' },
  { value: 'lost', label: 'Lost', color: 'bg-red-100 text-red-800' }
];

const LeadDetailsSidebar = ({ 
  conversation, 
  agents,
  onAssignAgent,
  onUpdateStatus,
  onUpdateLead
}) => {
  const [showAgentDropdown, setShowAgentDropdown] = useState(false);
  const [showStatusDropdown, setShowStatusDropdown] = useState(false);
  const [newTag, setNewTag] = useState('');
  const [isAddingTag, setIsAddingTag] = useState(false);

  const lead = conversation?.lead;

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return format(new Date(dateString), 'MMM d, yyyy HH:mm');
    } catch {
      return 'N/A';
    }
  };

  const getStatusStyle = (status) => {
    const found = LEAD_STATUSES.find(s => s.value === status);
    return found?.color || 'bg-gray-100 text-gray-800';
  };

  const handleAssignAgent = async (agentId) => {
    if (lead) {
      await onAssignAgent(lead.id, agentId);
      setShowAgentDropdown(false);
    }
  };

  const handleStatusChange = async (status) => {
    if (lead) {
      await onUpdateStatus(lead.id, status);
      setShowStatusDropdown(false);
    }
  };

  const handleAddTag = async () => {
    if (!newTag.trim() || !lead) return;
    
    const currentTags = lead.tags || [];
    if (!currentTags.includes(newTag.trim())) {
      await onUpdateLead(lead.id, { tags: [...currentTags, newTag.trim()] });
    }
    setNewTag('');
    setIsAddingTag(false);
  };

  const handleRemoveTag = async (tagToRemove) => {
    if (!lead) return;
    const currentTags = lead.tags || [];
    await onUpdateLead(lead.id, { tags: currentTags.filter(t => t !== tagToRemove) });
  };

  if (!conversation) {
    return (
      <div 
        data-testid="lead-details-sidebar"
        className="col-span-1 bg-gray-50 flex flex-col h-full items-center justify-center"
      >
        <div className="empty-state">
          <User size={48} className="text-gray-300 mb-3" />
          <p className="text-sm text-gray-400">Select a conversation</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      data-testid="lead-details-sidebar"
      className="col-span-1 bg-gray-50 flex flex-col h-full overflow-y-auto"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center text-white font-bold text-lg">
            {conversation.contactName?.charAt(0)?.toUpperCase() || '?'}
          </div>
          <div>
            <h2 className="font-bold text-gray-900 font-[Chivo]">
              {conversation.contactName}
            </h2>
            {lead && (
              <span className={`inline-block px-2 py-0.5 text-[10px] uppercase tracking-wider font-bold rounded-sm mt-1 ${getStatusStyle(lead.status)}`}>
                {lead.status}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Contact Info */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
          Contact Information
        </h3>
        
        <div className="space-y-3">
          <div className="flex items-center gap-3 text-sm">
            <Phone size={16} className="text-gray-400" />
            <span className="text-gray-700">{conversation.phone}</span>
          </div>
          
          {lead?.email && (
            <div className="flex items-center gap-3 text-sm">
              <EnvelopeSimple size={16} className="text-gray-400" />
              <span className="text-gray-700">{lead.email}</span>
            </div>
          )}
          
          <div className="flex items-center gap-3 text-sm">
            <ChatCircleDots size={16} className="text-gray-400" />
            <span className="text-gray-700">
              {lead?.message_count || conversation.messages?.length || 0} messages
            </span>
          </div>
          
          <div className="flex items-center gap-3 text-sm">
            <Clock size={16} className="text-gray-400" />
            <span className="text-gray-700">
              {formatDate(lead?.created_at || conversation.lastMessage?.created_at)}
            </span>
          </div>
        </div>
      </div>

      {/* Lead Status */}
      {lead && (
        <div className="p-4 border-b border-gray-200 bg-white">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Lead Status
          </h3>
          
          <div className="relative">
            <button
              onClick={() => setShowStatusDropdown(!showStatusDropdown)}
              className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-sm text-sm hover:bg-gray-50 transition-colors"
              data-testid="lead-status-update"
            >
              <span className={`px-2 py-0.5 rounded-sm text-xs font-bold uppercase ${getStatusStyle(lead.status)}`}>
                {lead.status}
              </span>
              <CaretDown size={14} className="text-gray-400" />
            </button>
            
            {showStatusDropdown && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-sm shadow-lg z-10">
                {LEAD_STATUSES.map((status) => (
                  <button
                    key={status.value}
                    onClick={() => handleStatusChange(status.value)}
                    className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
                    data-testid={`status-option-${status.value}`}
                  >
                    <span className={`px-2 py-0.5 rounded-sm text-xs font-bold uppercase ${status.color}`}>
                      {status.label}
                    </span>
                    {lead.status === status.value && (
                      <Check size={14} className="text-green-500" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Assigned Agent */}
      {lead && (
        <div className="p-4 border-b border-gray-200 bg-white">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Assigned Agent
          </h3>
          
          <div className="relative">
            <button
              onClick={() => setShowAgentDropdown(!showAgentDropdown)}
              className="w-full flex items-center justify-between p-3 border border-gray-300 rounded-sm text-sm hover:bg-gray-50 transition-colors"
              data-testid="agent-assignment-dropdown"
            >
              {lead.assigned_agent_name ? (
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold">
                    {lead.assigned_agent_name.charAt(0)}
                  </div>
                  <span>{lead.assigned_agent_name}</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-gray-400">
                  <UserCirclePlus size={18} />
                  <span>Assign agent</span>
                </div>
              )}
              <CaretDown size={14} className="text-gray-400" />
            </button>
            
            {showAgentDropdown && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-sm shadow-lg z-10 max-h-48 overflow-y-auto">
                {agents.length === 0 ? (
                  <div className="px-3 py-2 text-sm text-gray-400">
                    No agents available
                  </div>
                ) : (
                  agents.map((agent) => (
                    <button
                      key={agent.id}
                      onClick={() => handleAssignAgent(agent.id)}
                      className="w-full flex items-center justify-between px-3 py-2 text-sm hover:bg-gray-50 transition-colors"
                      data-testid={`agent-option-${agent.id}`}
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs font-bold">
                          {agent.name.charAt(0)}
                        </div>
                        <div className="text-left">
                          <div>{agent.name}</div>
                          <div className="text-[10px] text-gray-400">{agent.department}</div>
                        </div>
                      </div>
                      {lead.assigned_agent_id === agent.id && (
                        <Check size={14} className="text-green-500" />
                      )}
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tags */}
      {lead && (
        <div className="p-4 border-b border-gray-200 bg-white">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Tags
          </h3>
          
          <div className="flex flex-wrap gap-2" data-testid="tag-management">
            {(lead.tags || []).map((tag) => (
              <span
                key={tag}
                className="lead-tag flex items-center gap-1"
              >
                {tag}
                <button
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-red-500 transition-colors"
                >
                  <X size={10} />
                </button>
              </span>
            ))}
            
            {isAddingTag ? (
              <div className="flex items-center gap-1">
                <input
                  type="text"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                  placeholder="Tag name"
                  className="w-20 px-2 py-1 text-xs border border-gray-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-green-500"
                  autoFocus
                />
                <button
                  onClick={handleAddTag}
                  className="text-green-500 hover:text-green-600"
                >
                  <Check size={14} />
                </button>
                <button
                  onClick={() => { setIsAddingTag(false); setNewTag(''); }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={14} />
                </button>
              </div>
            ) : (
              <button
                onClick={() => setIsAddingTag(true)}
                className="flex items-center gap-1 px-2 py-1 text-xs text-gray-500 border border-dashed border-gray-300 rounded-sm hover:border-green-500 hover:text-green-500 transition-colors"
              >
                <Plus size={10} />
                Add tag
              </button>
            )}
          </div>
        </div>
      )}

      {/* Notes */}
      {lead?.notes && (
        <div className="p-4 border-b border-gray-200 bg-white">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            Notes
          </h3>
          <p className="text-sm text-gray-700">{lead.notes}</p>
        </div>
      )}

      {/* First Message */}
      {lead?.first_message && (
        <div className="p-4 bg-white">
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
            First Message
          </h3>
          <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-sm border border-gray-200">
            "{lead.first_message}"
          </p>
        </div>
      )}
    </div>
  );
};

export default LeadDetailsSidebar;
