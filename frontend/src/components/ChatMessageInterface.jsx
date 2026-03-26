import { useState, useRef, useEffect } from 'react';
import { 
  PaperPlaneRight, 
  Image, 
  File,
  Smiley,
  Check,
  Checks,
  Clock,
  Warning
} from '@phosphor-icons/react';
import { format } from 'date-fns';

const ChatMessageInterface = ({ 
  conversation, 
  messages, 
  loading,
  onSendMessage,
  sending
}) => {
  const [messageText, setMessageText] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!messageText.trim() || sending) return;
    
    await onSendMessage(messageText);
    setMessageText('');
    inputRef.current?.focus();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatMessageTime = (dateString) => {
    try {
      return format(new Date(dateString), 'HH:mm');
    } catch {
      return '';
    }
  };

  const formatMessageDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMMM d, yyyy');
    } catch {
      return '';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'sent':
        return <Check size={14} className="text-gray-400" />;
      case 'delivered':
        return <Checks size={14} className="text-gray-400" />;
      case 'read':
        return <Checks size={14} className="text-blue-500" />;
      case 'failed':
        return <Warning size={14} className="text-red-500" />;
      default:
        return <Clock size={14} className="text-gray-300" />;
    }
  };

  const getMessageTypeIcon = (type) => {
    switch (type) {
      case 'image':
        return <Image size={16} className="text-gray-500" />;
      case 'document':
        return <File size={16} className="text-gray-500" />;
      default:
        return null;
    }
  };

  // Group messages by date
  const groupedMessages = messages.reduce((groups, msg) => {
    const date = formatMessageDate(msg.created_at);
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(msg);
    return groups;
  }, {});

  if (!conversation) {
    return (
      <div 
        data-testid="chat-message-interface"
        className="col-span-2 border-r border-gray-200 bg-white flex flex-col h-full items-center justify-center"
      >
        <div className="empty-state">
          <div className="w-24 h-24 rounded-full bg-gray-100 flex items-center justify-center mb-4">
            <Smiley size={48} className="text-gray-300" />
          </div>
          <p className="text-gray-400 text-sm">Select a conversation to start chatting</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      data-testid="chat-message-interface"
      className="col-span-2 border-r border-gray-200 bg-white flex flex-col h-full overflow-hidden"
    >
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200 bg-white flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white font-bold">
          {conversation.contactName?.charAt(0)?.toUpperCase() || '?'}
        </div>
        <div className="flex-1">
          <h2 className="font-bold text-gray-900 font-[Chivo]">
            {conversation.contactName}
          </h2>
          <p className="text-xs text-gray-500">
            {conversation.phone}
          </p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="loading-spinner w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full" />
          </div>
        ) : (
          <>
            {Object.entries(groupedMessages).map(([date, dateMessages]) => (
              <div key={date}>
                {/* Date separator */}
                <div className="flex items-center justify-center my-4">
                  <span className="px-3 py-1 bg-white border border-gray-200 rounded-sm text-xs text-gray-500">
                    {date}
                  </span>
                </div>

                {/* Messages */}
                {dateMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`chat-bubble mb-4 flex ${
                      msg.direction === 'outbound' ? 'justify-end' : 'justify-start'
                    }`}
                    data-testid={`message-${msg.id}`}
                  >
                    <div
                      className={`max-w-[70%] px-4 py-3 ${
                        msg.direction === 'outbound'
                          ? 'bg-green-500 text-white rounded-tl-lg rounded-tr-sm rounded-bl-lg rounded-br-lg'
                          : 'bg-white border border-gray-200 text-gray-900 rounded-tl-sm rounded-tr-lg rounded-bl-lg rounded-br-lg'
                      }`}
                    >
                      {/* Media indicator */}
                      {msg.message_type !== 'text' && (
                        <div className={`flex items-center gap-1 mb-1 ${
                          msg.direction === 'outbound' ? 'text-green-100' : 'text-gray-400'
                        }`}>
                          {getMessageTypeIcon(msg.message_type)}
                          <span className="text-xs capitalize">{msg.message_type}</span>
                        </div>
                      )}

                      {/* Message content */}
                      <p className="text-sm whitespace-pre-wrap break-words">
                        {msg.content || `[${msg.message_type} message]`}
                      </p>

                      {/* Time and status */}
                      <div className={`flex items-center justify-end gap-1 mt-1 ${
                        msg.direction === 'outbound' ? 'text-green-100' : 'text-gray-400'
                      }`}>
                        <span className="text-[10px]">
                          {formatMessageTime(msg.created_at)}
                        </span>
                        {msg.direction === 'outbound' && getStatusIcon(msg.status)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Message Input */}
      <div 
        className="p-4 border-t border-gray-200 bg-white flex items-end gap-2"
        data-testid="message-input-container"
      >
        <textarea
          ref={inputRef}
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type a message..."
          rows={1}
          className="flex-1 resize-none p-3 border border-gray-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-green-500 focus:border-green-500 text-sm"
          data-testid="message-input"
          disabled={sending}
        />
        <button
          onClick={handleSend}
          disabled={!messageText.trim() || sending}
          className="bg-green-500 hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-sm px-4 py-3 font-medium transition-colors flex items-center gap-2"
          data-testid="send-button"
        >
          {sending ? (
            <div className="loading-spinner w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
          ) : (
            <PaperPlaneRight size={20} weight="fill" />
          )}
        </button>
      </div>
    </div>
  );
};

export default ChatMessageInterface;
