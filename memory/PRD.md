# WhatsApp Business API + CRM + Inbox UI - PRD

## Original Problem Statement
1. **WhatsApp Business API Service**: Connect multiple WhatsApp numbers, handle webhooks, store messages, send messages via API
2. **CRM Module**: Auto-create leads from WhatsApp messages, manage agents, track lead stages
3. **Inbox UI**: WhatsApp-style chat interface with conversation list, chat panel, and lead sidebar

## User Choices
- **WhatsApp Provider**: Meta's official WhatsApp Cloud API
- **Authentication**: API Key-based (auto-created on first load)
- **Message Types**: Text + Media (images, documents, videos)
- **Database**: MongoDB
- **Lead Creation**: Auto-create from incoming WhatsApp messages
- **Agent Management**: Full CRUD system
- **Frontend**: React with polling for real-time updates
- **Access**: Open (no login required)

## Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: React + TailwindCSS
- **Database**: MongoDB
- **Real-time**: Polling (5s conversations, 3s messages)

## What's Been Implemented

### Phase 1: WhatsApp Integration (2026-03-26)
- ✅ Multi-number WhatsApp support
- ✅ Webhook verification & message receiver
- ✅ Message sending (text, image, document, video, template)
- ✅ Message storage with status tracking

### Phase 2: CRM Module (2026-03-26)
- ✅ Agent management (create, list, update, deactivate)
- ✅ Lead management (create, list, update, delete)
- ✅ Lead stages: New → Contacted → Interested → Converted/Lost
- ✅ Auto-lead creation from WhatsApp messages
- ✅ Lead assignment to agents
- ✅ Lead status history tracking

### Phase 3: Inbox UI (2026-03-26)
- ✅ 3-panel WhatsApp-style layout
- ✅ Conversation list with search & status filter
- ✅ Chat interface with message display
- ✅ Lead details sidebar
- ✅ Agent assignment dropdown
- ✅ Status update dropdown
- ✅ Tag management
- ✅ Real-time polling updates

## UI Components

### Conversation List Panel
- Search by name/phone
- Filter by lead status
- Show contact name, last message, status indicator
- Active conversation highlighting

### Chat Message Interface
- WhatsApp-style bubbles (green for outbound, white for inbound)
- Date separators
- Message timestamps
- Status indicators (sent, delivered, read)
- Message input with send button

### Lead Details Sidebar
- Contact information
- Lead status with dropdown
- Agent assignment with dropdown
- Tag management (add/remove)
- First message display
- Notes section

## Tech Stack
- **Frontend**: React 19, TailwindCSS, Phosphor Icons
- **Backend**: FastAPI, Motor (MongoDB async driver)
- **Fonts**: Chivo (headings), IBM Plex Sans (body)
- **Colors**: Green primary (#22C55E), gray backgrounds

## Prioritized Backlog

### P0 (Done)
- [x] WhatsApp API integration
- [x] CRM with leads & agents
- [x] Inbox UI with 3-panel layout

### P1 (Future)
- [ ] WebSocket for true real-time
- [ ] Message read receipts
- [ ] Quick reply templates
- [ ] Agent performance dashboard

### P2 (Nice to have)
- [ ] Mobile responsive design
- [ ] Dark mode
- [ ] Message search
- [ ] File upload for media messages

## Next Tasks
1. Configure real Meta WhatsApp credentials
2. Test end-to-end message flow with real WhatsApp number
3. Add WebSocket for instant message updates
