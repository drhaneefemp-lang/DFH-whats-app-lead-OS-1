import { useState } from 'react';
import { 
  MagnifyingGlass, 
  Funnel,
  ChatCircleDots,
  Circle
} from '@phosphor-icons/react';
import { formatDistanceToNow } from 'date-fns';

const ConversationListPanel = ({ 
  conversations, 
  selectedPhone, 
  onSelectConversation,
  loading 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  // Filter conversations
  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = 
      conv.contactName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conv.phone?.includes(searchQuery);
    
    const matchesStatus = statusFilter === 'all' || 
      (conv.lead?.status === statusFilter);
    
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    const colors = {
      new: 'bg-blue-500',
      contacted: 'bg-yellow-500',
      interested: 'bg-emerald-500',
      converted: 'bg-green-600',
      lost: 'bg-red-500'
    };
    return colors[status] || 'bg-gray-400';
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return '';
    }
  };

  const truncateMessage = (content, maxLength = 40) => {
    if (!content) return 'Media message';
    return content.length > maxLength ? content.slice(0, maxLength) + '...' : content;
  };

  return (
    <div 
      data-testid="conversation-list-panel"
      className="col-span-1 border-r border-gray-200 bg-gray-50 flex flex-col h-full overflow-hidden"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <h1 className="text-lg font-bold tracking-tight text-gray-900 font-[Chivo]">
          Inbox
        </h1>
        <p className="text-xs text-gray-500 mt-1">
          {conversations.length} conversations
        </p>
      </div>

      {/* Search */}
      <div className="p-3 border-b border-gray-200 bg-white">
        <div className="relative">
          <MagnifyingGlass 
            className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" 
            size={16} 
          />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500"
            data-testid="conversation-search"
          />
        </div>
      </div>

      {/* Filter */}
      <div className="px-3 py-2 border-b border-gray-200 bg-white flex items-center gap-2">
        <Funnel size={14} className="text-gray-500" />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="text-xs border border-gray-300 rounded-sm px-2 py-1 focus:outline-none focus:ring-1 focus:ring-green-500"
          data-testid="whatsapp-number-filter"
        >
          <option value="all">All Status</option>
          <option value="new">New</option>
          <option value="contacted">Contacted</option>
          <option value="interested">Interested</option>
          <option value="converted">Converted</option>
          <option value="lost">Lost</option>
        </select>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="loading-spinner w-6 h-6 border-2 border-green-500 border-t-transparent rounded-full" />
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="empty-state p-8">
            <ChatCircleDots size={48} className="text-gray-300 mb-3" />
            <p className="text-sm text-gray-400">No conversations yet</p>
          </div>
        ) : (
          filteredConversations.map((conv) => (
            <div
              key={conv.phone}
              onClick={() => onSelectConversation(conv)}
              className={`conversation-item p-4 border-b border-gray-200 cursor-pointer ${
                selectedPhone === conv.phone ? 'active' : ''
              }`}
              data-testid={`conversation-item-${conv.phone}`}
            >
              <div className="flex items-start gap-3">
                {/* Avatar */}
                <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                  {conv.contactName?.charAt(0)?.toUpperCase() || '?'}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-medium text-sm text-gray-900 truncate">
                      {conv.contactName}
                    </span>
                    <span className="text-xs text-gray-400 flex-shrink-0">
                      {formatTime(conv.lastMessage?.created_at)}
                    </span>
                  </div>

                  <p className="text-xs text-gray-500 truncate mt-1">
                    {truncateMessage(conv.lastMessage?.content)}
                  </p>

                  {/* Status indicator */}
                  {conv.lead && (
                    <div className="flex items-center gap-2 mt-2">
                      <Circle 
                        weight="fill" 
                        size={8} 
                        className={getStatusColor(conv.lead.status).replace('bg-', 'text-')} 
                      />
                      <span className="text-[10px] uppercase tracking-wider text-gray-500 font-medium">
                        {conv.lead.status}
                      </span>
                      {conv.lead.assigned_agent_name && (
                        <span className="text-[10px] text-gray-400">
                          &bull; {conv.lead.assigned_agent_name}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ConversationListPanel;
