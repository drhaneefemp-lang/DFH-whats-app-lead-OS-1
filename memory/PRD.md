# WhatsApp Business API + CRM + Inbox + Automation - PRD

## Original Problem Statement
1. **WhatsApp Business API Service**: Connect multiple WhatsApp numbers, handle webhooks, store messages
2. **CRM Module**: Auto-create leads, manage agents, track lead stages
3. **Inbox UI**: WhatsApp-style chat interface with conversation list, chat panel, lead sidebar
4. **Automation Engine**: Rule-based triggers, scheduled actions, automated follow-ups

## User Choices
- **WhatsApp Provider**: Meta WhatsApp Cloud API
- **Authentication**: API Key-based
- **Database**: MongoDB
- **Real-time**: Polling
- **Scheduler**: APScheduler (in-process)
- **Rule Execution**: All matching rules execute

## Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: React + TailwindCSS
- **Database**: MongoDB
- **Scheduler**: APScheduler (AsyncIO)

## What's Been Implemented

### Phase 1: WhatsApp Integration (2026-03-26)
- ✅ Multi-number WhatsApp support
- ✅ Webhook handling
- ✅ Message sending (text, image, document, video, template)

### Phase 2: CRM Module (2026-03-26)
- ✅ Agent management
- ✅ Lead management with auto-creation
- ✅ Lead stages: New → Contacted → Interested → Converted/Lost

### Phase 3: Inbox UI (2026-03-26)
- ✅ 3-panel WhatsApp-style layout
- ✅ Conversation list, chat interface, lead sidebar
- ✅ Agent assignment and status updates

### Phase 4: Automation Engine (2026-03-26)
- ✅ Rule engine with condition evaluation
- ✅ 5 Trigger types: new_message, new_lead, no_reply, lead_status_change, scheduled
- ✅ 5 Action types: send_message, assign_lead, update_status, add_tag, send_template
- ✅ APScheduler with 3 jobs:
  - Execute Scheduled Tasks (every minute)
  - Check No Reply Leads (hourly)
  - Run Cron Rules (hourly)
- ✅ Delayed actions with scheduling
- ✅ Frontend rule management UI

## Automation API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/automation/triggers | List trigger types |
| GET | /api/automation/actions | List action types |
| POST | /api/automation/rules | Create rule |
| GET | /api/automation/rules | List rules |
| GET | /api/automation/rules/{id} | Get rule |
| PATCH | /api/automation/rules/{id} | Update rule |
| POST | /api/automation/rules/{id}/toggle | Toggle active |
| DELETE | /api/automation/rules/{id} | Delete rule |
| GET | /api/automation/logs | Execution logs |
| GET | /api/automation/scheduler/status | Scheduler status |

## Example Automation Rules

### Welcome New Leads
```json
{
  "trigger_type": "new_lead",
  "actions": [{
    "action_type": "send_message",
    "config": {"message_text": "Welcome! Thanks for reaching out."}
  }]
}
```

### 24h Follow-up
```json
{
  "trigger_type": "no_reply",
  "trigger_config": {"hours": 24},
  "conditions": [{"field": "lead.status", "operator": "equals", "value": "new"}],
  "actions": [{
    "action_type": "send_message",
    "config": {"message_text": "Just checking in..."}
  }]
}
```

## Frontend Routes
- `/` - Inbox (conversations, chat, lead details)
- `/automation` - Automation rules management

## Prioritized Backlog

### P0 (Done)
- [x] WhatsApp API integration
- [x] CRM with leads & agents
- [x] Inbox UI
- [x] Automation engine with rule builder UI

### P1 (Future)
- [ ] WebSocket for real-time messages
- [ ] Webhook signature verification
- [ ] Bulk message campaigns
- [ ] Analytics dashboard

### P2 (Nice to have)
- [ ] Mobile responsive design
- [ ] Dark mode
- [ ] Message templates library
- [ ] A/B testing for automation rules

## Next Tasks
1. Configure real Meta WhatsApp credentials
2. Test end-to-end automation flow with real messages
3. Add webhook signature verification for security
