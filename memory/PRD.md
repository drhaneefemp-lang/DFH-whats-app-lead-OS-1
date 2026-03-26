# WhatsApp Business API + CRM Backend Service - PRD

## Original Problem Statement
1. **WhatsApp Business API Service**: Connect multiple WhatsApp numbers, handle webhooks, store messages, send messages via API
2. **CRM Module**: Auto-create leads from WhatsApp messages, manage agents, track lead stages

## User Choices
- **WhatsApp Provider**: Meta's official WhatsApp Cloud API
- **Authentication**: API Key-based (X-API-Key header)
- **Message Types**: Text + Media (images, documents, videos)
- **Database**: MongoDB (user preferred over PostgreSQL)
- **Lead Creation**: Auto-create from incoming WhatsApp messages
- **Agent Management**: Full CRUD system

## Architecture
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **External API**: Meta WhatsApp Cloud API

## What's Been Implemented

### Phase 1: WhatsApp Integration (2026-03-26)
- ✅ Multi-number WhatsApp support
- ✅ Webhook verification & message receiver
- ✅ Message sending (text, image, document, video, template)
- ✅ Message storage with status tracking
- ✅ API key authentication

### Phase 2: CRM Module (2026-03-26)
- ✅ Agent management (create, list, update, deactivate)
- ✅ Lead management (create, list, update, delete)
- ✅ Lead stages: New → Contacted → Interested → Converted/Lost
- ✅ Lead sources: WhatsApp, Manual, Website, Referral, Other
- ✅ Auto-lead creation from WhatsApp messages
- ✅ Lead assignment to agents
- ✅ Lead status history tracking
- ✅ Lead statistics endpoint

## API Endpoints

### WhatsApp APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/numbers | Connect WhatsApp number |
| GET | /api/numbers | List connected numbers |
| GET/POST | /api/webhook/whatsapp | Webhook handling |
| POST | /api/messages/{type} | Send messages |
| GET | /api/messages | Message history |

### CRM: Agent APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/agents | Create agent |
| GET | /api/agents | List agents |
| GET | /api/agents/{id} | Get agent |
| PATCH | /api/agents/{id} | Update agent |
| DELETE | /api/agents/{id} | Deactivate agent |

### CRM: Lead APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/leads | Create lead |
| GET | /api/leads | List leads (with filters) |
| GET | /api/leads/stats | Lead statistics |
| GET | /api/leads/{id} | Get lead |
| PATCH | /api/leads/{id} | Update lead |
| POST | /api/leads/{id}/assign | Assign to agent |
| POST | /api/leads/{id}/status | Update status |
| DELETE | /api/leads/{id} | Delete lead |

## Lead Stages Flow
```
NEW → CONTACTED → INTERESTED → CONVERTED
                            ↘ LOST
```

## Database Schema (MongoDB Collections)

### agents
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string (unique)",
  "phone": "string",
  "department": "string",
  "is_active": "boolean",
  "leads_count": "integer",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### leads
```json
{
  "id": "uuid",
  "name": "string",
  "phone": "string (unique)",
  "email": "string",
  "source": "whatsapp|manual|website|referral|other",
  "status": "new|contacted|interested|converted|lost",
  "assigned_agent_id": "string",
  "assigned_agent_name": "string",
  "notes": "string",
  "tags": ["string"],
  "first_message": "string",
  "message_count": "integer",
  "last_message_at": "datetime",
  "status_history": [{"status", "changed_at", "notes"}],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Prioritized Backlog

### P0 (Done)
- [x] WhatsApp webhook handling
- [x] Message storage
- [x] Agent CRUD
- [x] Lead CRUD with auto-creation
- [x] Lead assignment & status tracking

### P1 (Future)
- [ ] Webhook signature verification (X-Hub-Signature-256)
- [ ] Lead assignment rules (auto-assign based on round-robin)
- [ ] Agent performance metrics
- [ ] Lead scoring system

### P2 (Nice to have)
- [ ] Email notifications on new leads
- [ ] Lead follow-up reminders
- [ ] Bulk lead import/export
- [ ] Lead conversation history view

## Next Tasks
1. Configure real Meta WhatsApp credentials
2. Add webhook signature verification for security
3. Implement auto-assignment rules
