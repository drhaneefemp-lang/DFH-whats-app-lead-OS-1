# WhatsApp Business API + CRM + Inbox + Automation + Dashboard - PRD

## Original Problem Statement
1. **WhatsApp Business API Service**: Connect multiple numbers, webhooks, message storage
2. **CRM Module**: Auto-create leads, agents, lead stages
3. **Inbox UI**: WhatsApp-style chat interface
4. **Automation Engine**: Rule-based triggers, scheduled actions
5. **Dashboard**: Analytics, KPIs, charts, agent performance

## User Choices
- **Database**: MongoDB
- **Real-time**: Polling
- **Scheduler**: APScheduler
- **Charts**: Recharts
- **Time Filters**: Today/This Week/This Month + Custom date range

## Architecture
- **Backend**: FastAPI (Python)
- **Frontend**: React + TailwindCSS + Recharts
- **Database**: MongoDB
- **Scheduler**: APScheduler

## What's Been Implemented

### Phase 1-4: WhatsApp + CRM + Inbox + Automation (2026-03-26)
- ✅ WhatsApp API integration
- ✅ CRM with leads & agents
- ✅ 3-panel Inbox UI
- ✅ Automation engine with rule builder

### Phase 5: Dashboard (2026-03-26)
- ✅ 4 KPI Cards: Total Leads, Conversion Rate, Avg Response Time, Total Messages
- ✅ Time filters: Today, This Week, This Month, Custom date range
- ✅ Leads Over Time (line chart)
- ✅ Messages Over Time (bar chart)
- ✅ Leads by Status (pie chart)
- ✅ Leads by Source (bar chart)
- ✅ Response Time Distribution (bar chart)
- ✅ Agent Performance table with progress bars

## Dashboard API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dashboard/metrics | Total leads, conversion rate, by status/source, agent performance |
| GET | /api/dashboard/leads-over-time | Leads grouped by day/week/month |
| GET | /api/dashboard/messages-over-time | Messages grouped by day/week/month |
| GET | /api/dashboard/response-times | Average, min, max response times + distribution |

## Frontend Routes
- `/` - Inbox (conversations, chat, lead details)
- `/dashboard` - Analytics dashboard
- `/automation` - Automation rules management

## Tech Stack
- **Backend**: FastAPI, Motor, APScheduler
- **Frontend**: React 19, TailwindCSS, Recharts, Shadcn UI
- **Fonts**: Chivo (headings), IBM Plex Sans (body)

## Prioritized Backlog

### P0 (Done)
- [x] WhatsApp API integration
- [x] CRM with leads & agents
- [x] Inbox UI
- [x] Automation engine
- [x] Analytics dashboard

### P1 (Future)
- [ ] WebSocket for real-time messages
- [ ] Export reports to CSV/PDF
- [ ] Team performance comparisons
- [ ] Goal tracking

### P2 (Nice to have)
- [ ] Mobile responsive design
- [ ] Dark mode
- [ ] Customizable dashboard widgets
- [ ] Email reports scheduling

## Next Tasks
1. Configure real Meta WhatsApp credentials
2. Test end-to-end flow with real messages
3. Add more detailed agent analytics
