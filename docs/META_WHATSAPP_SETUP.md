# Meta WhatsApp Cloud API Setup Guide

## Overview
This guide walks you through setting up your WhatsApp Business API credentials to enable real message sending and receiving.

---

## Prerequisites
- Facebook Business Account
- Meta Developer Account
- A phone number for WhatsApp Business (not already registered with WhatsApp)

---

## Step 1: Create Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. Select **Business** as the app type
4. Fill in:
   - App name: `Your Company WhatsApp`
   - Contact email: your email
   - Business Account: Select or create one
5. Click **Create App**

---

## Step 2: Add WhatsApp Product

1. In your app dashboard, click **Add Product**
2. Find **WhatsApp** and click **Set Up**
3. You'll be redirected to WhatsApp Getting Started page

---

## Step 3: Get Your Credentials

### A. Phone Number ID
1. Go to **WhatsApp** → **API Setup** in the left sidebar
2. Under "From", you'll see a test phone number
3. Copy the **Phone Number ID** (e.g., `123456789012345`)

### B. Access Token (Temporary)
1. On the same API Setup page
2. Click **Generate** under "Temporary access token"
3. Copy the token (valid for 24 hours)

### C. Access Token (Permanent - Recommended)
1. Go to **Business Settings** → **System Users**
2. Create a new System User with Admin role
3. Click **Generate New Token**
4. Select your WhatsApp app
5. Add permissions:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
6. Generate and copy the token

### D. App Secret (For Webhook Verification)
1. Go to **App Settings** → **Basic**
2. Click **Show** next to App Secret
3. Copy the App Secret

---

## Step 4: Configure Webhook

### Your Webhook URL
```
https://msg-gateway-2.preview.emergentagent.com/api/webhook/whatsapp
```

### Configure in Meta Console
1. Go to **WhatsApp** → **Configuration**
2. Under "Webhook", click **Edit**
3. Enter:
   - **Callback URL**: `https://msg-gateway-2.preview.emergentagent.com/api/webhook/whatsapp`
   - **Verify Token**: `whatsapp_webhook_verify_token_123`
4. Click **Verify and Save**
5. Subscribe to webhook fields:
   - ✅ `messages`
   - ✅ `message_template_status_update` (optional)

---

## Step 5: Update Your .env File

Edit `/app/backend/.env` with your credentials:

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
WEBHOOK_VERIFY_TOKEN="whatsapp_webhook_verify_token_123"

# Meta WhatsApp Cloud API Credentials
WA_PHONE_NUMBER_ID="123456789012345"
CLOUD_API_ACCESS_TOKEN="EAAxxxxxxx..."
META_APP_SECRET="abcd1234..."
```

Then restart the backend:
```bash
sudo supervisorctl restart backend
```

---

## Step 6: Connect Your Number via API

```bash
curl -X POST "https://msg-gateway-2.preview.emergentagent.com/api/numbers" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "phone_number_id": "123456789012345",
    "display_phone_number": "+1234567890",
    "access_token": "EAAxxxxxxx...",
    "department": "support"
  }'
```

---

## Step 7: Register Your Real Phone Number (Production)

For production, you need to register your own phone number:

1. Go to **WhatsApp** → **API Setup**
2. Click **Add phone number**
3. Enter your business phone number
4. Verify via SMS or Voice call
5. Complete business verification if required

---

## Testing Your Setup

### Test Webhook Verification
```bash
curl "https://msg-gateway-2.preview.emergentagent.com/api/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=whatsapp_webhook_verify_token_123"
# Should return: test123
```

### Test Sending a Message
```bash
curl -X POST "https://msg-gateway-2.preview.emergentagent.com/api/messages/text" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "recipient_phone": "1234567890",
    "message_text": "Hello from WhatsApp CRM!"
  }'
```

---

## Important Notes

### Rate Limits
- Test numbers: 1,000 messages/day
- Business verified: Based on your tier (1k, 10k, 100k+)

### Message Templates (Required for Outbound)
- First message to a user requires an approved template
- Users must message you first to open a 24-hour conversation window
- Within 24 hours, you can send free-form messages

### Webhook Security
- Always use HTTPS
- `META_APP_SECRET` enables signature verification
- All webhooks are verified using X-Hub-Signature-256 header

---

## Troubleshooting

### Webhook Not Receiving Messages
1. Check webhook subscription is active
2. Verify callback URL is correct
3. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`

### Messages Not Sending
1. Verify access token is valid (not expired)
2. Check phone number is correctly configured
3. Ensure recipient has WhatsApp and valid number format

### Signature Verification Failed
1. Confirm `META_APP_SECRET` matches your app's secret
2. Check there are no extra spaces in the .env value

---

## Support Links
- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Webhook Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks)
- [Message Templates](https://developers.facebook.com/docs/whatsapp/message-templates)
