# WhatsApp Business API Backend Service - PRD

## Original Problem Statement
Build a backend service to integrate WhatsApp Business API with:
- Connect multiple WhatsApp numbers
- Handle webhook events for incoming messages
- Store message data in database
- Support message sending via API

## User Choices
- **Provider**: Meta's official WhatsApp Cloud API
- **Authentication**: API Key-based (X-API-Key header)
- **Message Types**: Text + Media (images, documents, videos)
- **Service Type**: Backend-only API service

## Architecture
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **External API**: Meta WhatsApp Cloud API (graph.facebook.com)

## Core Requirements (Static)
1. Multi-number support - connect/disconnect WhatsApp Business numbers
2. Webhook handling for incoming messages and status updates
3. Message storage with full metadata
4. Send text, image, document, video, and template messages
5. API key authentication for all protected endpoints

## What's Been Implemented (2026-03-26)
- ✅ API Key management (create, list, revoke)
- ✅ WhatsApp number management (connect, list, disconnect)
- ✅ Webhook verification endpoint (GET /api/webhook/whatsapp)
- ✅ Webhook receiver (POST /api/webhook/whatsapp)
- ✅ Message sending endpoints (text, image, document, video, template)
- ✅ Message history with filters
- ✅ Health check endpoint
- ✅ MongoDB integration with proper indexes

## API Endpoints
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | /api/health | No | Health check |
| POST | /api/keys | No | Create API key |
| GET | /api/keys | Yes | List API keys |
| DELETE | /api/keys/{id} | Yes | Revoke API key |
| POST | /api/numbers | Yes | Connect WhatsApp number |
| GET | /api/numbers | Yes | List connected numbers |
| DELETE | /api/numbers/{id} | Yes | Disconnect number |
| GET | /api/webhook/whatsapp | No | Webhook verification |
| POST | /api/webhook/whatsapp | No | Receive messages |
| POST | /api/messages/text | Yes | Send text message |
| POST | /api/messages/image | Yes | Send image message |
| POST | /api/messages/document | Yes | Send document |
| POST | /api/messages/video | Yes | Send video |
| POST | /api/messages/template | Yes | Send template |
| GET | /api/messages | Yes | List messages |
| GET | /api/messages/{id} | Yes | Get message details |

## Prioritized Backlog

### P0 (Critical - Done)
- [x] Core API structure
- [x] Authentication middleware
- [x] Webhook handling
- [x] Message storage

### P1 (Important - Future)
- [ ] Webhook signature verification (X-Hub-Signature-256)
- [ ] Rate limiting
- [ ] Message retry logic with exponential backoff
- [ ] Media download/upload functionality

### P2 (Nice to have)
- [ ] Message analytics/stats endpoint
- [ ] Conversation threading
- [ ] Auto-response configuration
- [ ] Batch message sending

## Next Tasks
1. Add Meta WhatsApp credentials to .env (WA_PHONE_NUMBER_ID, CLOUD_API_ACCESS_TOKEN)
2. Configure webhook URL in Meta Developer Console
3. Add webhook signature verification for production security
4. Implement rate limiting for API protection
