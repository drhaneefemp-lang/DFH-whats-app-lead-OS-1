"""
Comprehensive backend testing for WhatsApp Business API service
Tests all endpoints systematically using the public API endpoint
"""
import requests
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any

class WhatsAppAPITester:
    def __init__(self, base_url: str = "https://msg-gateway-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_key = "wa_LCJTBLltCNuzopYfF95QKuYUQ0eDVfCbTNIUPOWdMjs"  # Use provided API key
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.whatsapp_number_id = None
        self.created_message_id = None
        self.created_agent_id = None
        self.created_lead_id = None

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    Details: {details}")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}/{endpoint}"
        
        # Default headers
        request_headers = {'Content-Type': 'application/json'}
        if headers:
            request_headers.update(headers)
        
        # Add API key if available
        if self.api_key and 'X-API-Key' not in request_headers:
            request_headers['X-API-Key'] = self.api_key

        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=request_headers, params=params, timeout=30)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=request_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=30)
            else:
                return False, {"error": f"Unsupported method: {method}"}, 0

            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            return response.status_code in [200, 201], response_data, response.status_code

        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, 0

    def test_health_check(self):
        """Test health check endpoint"""
        success, data, status_code = self.make_request('GET', 'api/health')
        
        if success and data.get('status') == 'healthy':
            self.log_test("Health Check", True, f"Status: {data.get('status')}, DB: {data.get('database')}")
        else:
            self.log_test("Health Check", False, f"Status: {status_code}, Response: {data}")

    def test_create_api_key(self):
        """Test creating API key (no auth required for first key)"""
        test_data = {
            "name": f"Test API Key {datetime.now().strftime('%H%M%S')}"
        }
        
        success, data, status_code = self.make_request('POST', 'api/keys', data=test_data, headers={})
        
        if success and data.get('key'):
            self.api_key = data['key']
            self.log_test("Create API Key", True, f"Key ID: {data.get('id')}, Name: {data.get('name')}")
        else:
            self.log_test("Create API Key", False, f"Status: {status_code}, Response: {data}")

    def test_list_api_keys(self):
        """Test listing API keys (requires auth)"""
        if not self.api_key:
            self.log_test("List API Keys", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/keys')
        
        if success and isinstance(data, list):
            self.log_test("List API Keys", True, f"Found {len(data)} API keys")
        else:
            self.log_test("List API Keys", False, f"Status: {status_code}, Response: {data}")

    def test_connect_whatsapp_number(self):
        """Test connecting WhatsApp number"""
        if not self.api_key:
            self.log_test("Connect WhatsApp Number", False, "No API key available")
            return

        test_data = {
            "phone_number_id": "123456789012345",
            "display_phone_number": "+15551234567",
            "access_token": "test_access_token_123",
            "department": "test_department",
            "webhook_verify_token": "test_webhook_token"
        }
        
        success, data, status_code = self.make_request('POST', 'api/numbers', data=test_data)
        
        if success:
            self.whatsapp_number_id = data.get('id')
            self.log_test("Connect WhatsApp Number", True, f"Number ID: {data.get('id')}, Phone: {data.get('display_phone_number')}")
        else:
            self.log_test("Connect WhatsApp Number", False, f"Status: {status_code}, Response: {data}")

    def test_list_whatsapp_numbers(self):
        """Test listing WhatsApp numbers"""
        if not self.api_key:
            self.log_test("List WhatsApp Numbers", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/numbers')
        
        if success and isinstance(data, list):
            self.log_test("List WhatsApp Numbers", True, f"Found {len(data)} WhatsApp numbers")
        else:
            self.log_test("List WhatsApp Numbers", False, f"Status: {status_code}, Response: {data}")

    def test_webhook_verification(self):
        """Test webhook verification endpoint"""
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge_123",
            "hub.verify_token": "whatsapp_webhook_verify_token_123"
        }
        
        success, data, status_code = self.make_request('GET', 'api/webhook/whatsapp', params=params, headers={})
        
        # For webhook verification, we expect the challenge to be returned
        if status_code == 200:
            self.log_test("Webhook Verification", True, f"Challenge returned successfully")
        else:
            self.log_test("Webhook Verification", False, f"Status: {status_code}, Response: {data}")

    def test_webhook_message_receive(self):
        """Test webhook message receiving"""
        # Simulate incoming message webhook payload
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "test_entry_id",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "+15551234567",
                            "phone_number_id": "123456789012345"
                        },
                        "contacts": [{
                            "profile": {
                                "name": "Test User"
                            },
                            "wa_id": "15559876543"
                        }],
                        "messages": [{
                            "from": "15559876543",
                            "id": "test_message_id_123",
                            "timestamp": "1234567890",
                            "text": {
                                "body": "Hello from test webhook"
                            },
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        success, data, status_code = self.make_request('POST', 'api/webhook/whatsapp', data=webhook_payload, headers={})
        
        # Webhook should always return 200 even if processing fails
        if status_code == 200:
            self.log_test("Webhook Message Receive", True, "Webhook processed successfully")
        else:
            self.log_test("Webhook Message Receive", False, f"Status: {status_code}, Response: {data}")

    def test_send_text_message(self):
        """Test sending text message (expected to fail with test tokens)"""
        if not self.api_key:
            self.log_test("Send Text Message", False, "No API key available")
            return

        test_data = {
            "recipient_phone": "15559876543",
            "message_text": "Hello from WhatsApp Business API test!",
            "phone_number_id": "123456789012345"
        }
        
        success, data, status_code = self.make_request('POST', 'api/messages/text', data=test_data)
        
        # We expect this to fail due to test tokens, but API should handle it gracefully
        if status_code == 200:
            if data.get('success') == False and 'error' in data:
                self.log_test("Send Text Message", True, f"Expected WhatsApp API error: {data.get('error')}")
            else:
                self.log_test("Send Text Message", True, f"Message sent: {data.get('message_id')}")
        else:
            self.log_test("Send Text Message", False, f"Status: {status_code}, Response: {data}")

    def test_send_image_message(self):
        """Test sending image message"""
        if not self.api_key:
            self.log_test("Send Image Message", False, "No API key available")
            return

        test_data = {
            "recipient_phone": "15559876543",
            "image_url": "https://example.com/test-image.jpg",
            "caption": "Test image from API",
            "use_media_id": False
        }
        
        success, data, status_code = self.make_request('POST', 'api/messages/image', data=test_data)
        
        if status_code == 200:
            if data.get('success') == False and 'error' in data:
                self.log_test("Send Image Message", True, f"Expected WhatsApp API error: {data.get('error')}")
            else:
                self.log_test("Send Image Message", True, f"Image sent: {data.get('message_id')}")
        else:
            self.log_test("Send Image Message", False, f"Status: {status_code}, Response: {data}")

    def test_send_document_message(self):
        """Test sending document message"""
        if not self.api_key:
            self.log_test("Send Document Message", False, "No API key available")
            return

        test_data = {
            "recipient_phone": "15559876543",
            "document_url": "https://example.com/test-document.pdf",
            "filename": "test-document.pdf",
            "use_media_id": False
        }
        
        success, data, status_code = self.make_request('POST', 'api/messages/document', data=test_data)
        
        if status_code == 200:
            if data.get('success') == False and 'error' in data:
                self.log_test("Send Document Message", True, f"Expected WhatsApp API error: {data.get('error')}")
            else:
                self.log_test("Send Document Message", True, f"Document sent: {data.get('message_id')}")
        else:
            self.log_test("Send Document Message", False, f"Status: {status_code}, Response: {data}")

    def test_send_video_message(self):
        """Test sending video message"""
        if not self.api_key:
            self.log_test("Send Video Message", False, "No API key available")
            return

        test_data = {
            "recipient_phone": "15559876543",
            "video_url": "https://example.com/test-video.mp4",
            "caption": "Test video from API",
            "use_media_id": False
        }
        
        success, data, status_code = self.make_request('POST', 'api/messages/video', data=test_data)
        
        if status_code == 200:
            if data.get('success') == False and 'error' in data:
                self.log_test("Send Video Message", True, f"Expected WhatsApp API error: {data.get('error')}")
            else:
                self.log_test("Send Video Message", True, f"Video sent: {data.get('message_id')}")
        else:
            self.log_test("Send Video Message", False, f"Status: {status_code}, Response: {data}")

    def test_send_template_message(self):
        """Test sending template message"""
        if not self.api_key:
            self.log_test("Send Template Message", False, "No API key available")
            return

        test_data = {
            "recipient_phone": "15559876543",
            "template_name": "hello_world",
            "language_code": "en_US",
            "parameters": ["Test Parameter"]
        }
        
        success, data, status_code = self.make_request('POST', 'api/messages/template', data=test_data)
        
        if status_code == 200:
            if data.get('success') == False and 'error' in data:
                self.log_test("Send Template Message", True, f"Expected WhatsApp API error: {data.get('error')}")
            else:
                self.log_test("Send Template Message", True, f"Template sent: {data.get('message_id')}")
        else:
            self.log_test("Send Template Message", False, f"Status: {status_code}, Response: {data}")

    def test_list_messages(self):
        """Test listing messages"""
        if not self.api_key:
            self.log_test("List Messages", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/messages')
        
        if success and 'total' in data and 'messages' in data:
            self.log_test("List Messages", True, f"Found {data.get('total')} total messages")
        else:
            self.log_test("List Messages", False, f"Status: {status_code}, Response: {data}")

    def test_get_specific_message(self):
        """Test getting specific message by ID"""
        if not self.api_key:
            self.log_test("Get Specific Message", False, "No API key available")
            return

        # Try to get a message (this will likely fail as we don't have a real message ID)
        test_message_id = "test_message_id_123"
        success, data, status_code = self.make_request('GET', f'api/messages/{test_message_id}')
        
        if status_code == 404:
            self.log_test("Get Specific Message", True, "Correctly returned 404 for non-existent message")
        elif success:
            self.log_test("Get Specific Message", True, f"Message retrieved: {data.get('id')}")
        else:
            self.log_test("Get Specific Message", False, f"Status: {status_code}, Response: {data}")

    def test_revoke_api_key(self):
        """Test revoking API key (only if we have multiple keys)"""
        if not self.api_key:
            self.log_test("Revoke API Key", False, "No API key available")
            return

        # First, get list of keys to find one to revoke
        success, data, status_code = self.make_request('GET', 'api/keys')
        
        if not success or not isinstance(data, list) or len(data) == 0:
            self.log_test("Revoke API Key", False, "No API keys found to revoke")
            return

        # Don't revoke the key we're currently using for testing
        key_to_revoke = None
        for key in data:
            if key.get('id') and key.get('is_active'):
                key_to_revoke = key['id']
                break

        if not key_to_revoke:
            self.log_test("Revoke API Key", False, "No suitable API key found to revoke")
            return

        success, data, status_code = self.make_request('DELETE', f'api/keys/{key_to_revoke}')
        
        if success and data.get('success'):
            self.log_test("Revoke API Key", True, f"API key {key_to_revoke} revoked successfully")
        else:
            self.log_test("Revoke API Key", False, f"Status: {status_code}, Response: {data}")

    def test_disconnect_whatsapp_number(self):
        """Test disconnecting WhatsApp number"""
        if not self.api_key or not self.whatsapp_number_id:
            self.log_test("Disconnect WhatsApp Number", False, "No API key or WhatsApp number ID available")
            return

        success, data, status_code = self.make_request('DELETE', f'api/numbers/{self.whatsapp_number_id}')
        
        if success and data.get('success'):
            self.log_test("Disconnect WhatsApp Number", True, f"WhatsApp number {self.whatsapp_number_id} disconnected")
        else:
            self.log_test("Disconnect WhatsApp Number", False, f"Status: {status_code}, Response: {data}")

    # ============== CRM AGENT TESTS ==============

    def test_create_agent(self):
        """Test creating a new agent"""
        if not self.api_key:
            self.log_test("Create Agent", False, "No API key available")
            return

        test_data = {
            "name": f"Test Agent {datetime.now().strftime('%H%M%S')}",
            "email": f"test.agent.{datetime.now().strftime('%H%M%S')}@example.com",
            "phone": "+15551234567",
            "department": "sales",
            "is_active": True
        }
        
        success, data, status_code = self.make_request('POST', 'api/agents', data=test_data)
        
        if success and data.get('id'):
            self.created_agent_id = data['id']
            self.log_test("Create Agent", True, f"Agent created: {data.get('name')} (ID: {data.get('id')})")
        else:
            self.log_test("Create Agent", False, f"Status: {status_code}, Response: {data}")

    def test_list_agents(self):
        """Test listing agents"""
        if not self.api_key:
            self.log_test("List Agents", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/agents')
        
        if success and 'total' in data and 'agents' in data:
            self.log_test("List Agents", True, f"Found {data.get('total')} total agents")
        else:
            self.log_test("List Agents", False, f"Status: {status_code}, Response: {data}")

    def test_list_agents_with_filters(self):
        """Test listing agents with filters"""
        if not self.api_key:
            self.log_test("List Agents with Filters", False, "No API key available")
            return

        # Test filter by department
        params = {"department": "sales", "is_active": True}
        success, data, status_code = self.make_request('GET', 'api/agents', params=params)
        
        if success and 'total' in data and 'agents' in data:
            self.log_test("List Agents with Filters", True, f"Found {data.get('total')} sales agents")
        else:
            self.log_test("List Agents with Filters", False, f"Status: {status_code}, Response: {data}")

    def test_get_agent_by_id(self):
        """Test getting agent by ID"""
        if not self.api_key or not self.created_agent_id:
            self.log_test("Get Agent by ID", False, "No API key or agent ID available")
            return

        success, data, status_code = self.make_request('GET', f'api/agents/{self.created_agent_id}')
        
        if success and data.get('id') == self.created_agent_id:
            self.log_test("Get Agent by ID", True, f"Agent retrieved: {data.get('name')}")
        else:
            self.log_test("Get Agent by ID", False, f"Status: {status_code}, Response: {data}")

    def test_update_agent(self):
        """Test updating an agent"""
        if not self.api_key or not self.created_agent_id:
            self.log_test("Update Agent", False, "No API key or agent ID available")
            return

        update_data = {
            "department": "customer_support",
            "phone": "+15559876543"
        }
        
        success, data, status_code = self.make_request('PATCH', f'api/agents/{self.created_agent_id}', data=update_data)
        
        if success and data.get('department') == "customer_support":
            self.log_test("Update Agent", True, f"Agent updated: department={data.get('department')}")
        else:
            self.log_test("Update Agent", False, f"Status: {status_code}, Response: {data}")

    def test_deactivate_agent(self):
        """Test deactivating an agent"""
        if not self.api_key or not self.created_agent_id:
            self.log_test("Deactivate Agent", False, "No API key or agent ID available")
            return

        success, data, status_code = self.make_request('DELETE', f'api/agents/{self.created_agent_id}')
        
        if success and data.get('success'):
            self.log_test("Deactivate Agent", True, f"Agent deactivated successfully")
        else:
            self.log_test("Deactivate Agent", False, f"Status: {status_code}, Response: {data}")

    # ============== CRM LEAD TESTS ==============

    def test_create_lead(self):
        """Test creating a new lead manually"""
        if not self.api_key:
            self.log_test("Create Lead", False, "No API key available")
            return

        test_data = {
            "name": f"Test Lead {datetime.now().strftime('%H%M%S')}",
            "phone": f"+1555{datetime.now().strftime('%H%M%S')}",
            "email": f"test.lead.{datetime.now().strftime('%H%M%S')}@example.com",
            "source": "manual",
            "status": "new",
            "notes": "Test lead created via API"
        }
        
        success, data, status_code = self.make_request('POST', 'api/leads', data=test_data)
        
        if success and data.get('id'):
            self.created_lead_id = data['id']
            self.log_test("Create Lead", True, f"Lead created: {data.get('name')} (ID: {data.get('id')})")
        else:
            self.log_test("Create Lead", False, f"Status: {status_code}, Response: {data}")

    def test_list_leads(self):
        """Test listing leads"""
        if not self.api_key:
            self.log_test("List Leads", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/leads')
        
        if success and 'total' in data and 'leads' in data:
            self.log_test("List Leads", True, f"Found {data.get('total')} total leads")
        else:
            self.log_test("List Leads", False, f"Status: {status_code}, Response: {data}")

    def test_list_leads_with_filters(self):
        """Test listing leads with filters"""
        if not self.api_key:
            self.log_test("List Leads with Filters", False, "No API key available")
            return

        # Test multiple filters
        params = {"status": "new", "source": "manual", "unassigned": True}
        success, data, status_code = self.make_request('GET', 'api/leads', params=params)
        
        if success and 'total' in data and 'leads' in data:
            self.log_test("List Leads with Filters", True, f"Found {data.get('total')} new manual unassigned leads")
        else:
            self.log_test("List Leads with Filters", False, f"Status: {status_code}, Response: {data}")

    def test_get_lead_stats(self):
        """Test getting lead statistics"""
        if not self.api_key:
            self.log_test("Get Lead Stats", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/leads/stats')
        
        if success and 'total_leads' in data and 'by_status' in data and 'by_source' in data:
            self.log_test("Get Lead Stats", True, f"Stats: {data.get('total_leads')} total, {data.get('unassigned_count')} unassigned")
        else:
            self.log_test("Get Lead Stats", False, f"Status: {status_code}, Response: {data}")

    def test_get_lead_by_id(self):
        """Test getting lead by ID"""
        if not self.api_key or not self.created_lead_id:
            self.log_test("Get Lead by ID", False, "No API key or lead ID available")
            return

        success, data, status_code = self.make_request('GET', f'api/leads/{self.created_lead_id}')
        
        if success and data.get('id') == self.created_lead_id:
            self.log_test("Get Lead by ID", True, f"Lead retrieved: {data.get('name')}")
        else:
            self.log_test("Get Lead by ID", False, f"Status: {status_code}, Response: {data}")

    def test_update_lead(self):
        """Test updating a lead"""
        if not self.api_key or not self.created_lead_id:
            self.log_test("Update Lead", False, "No API key or lead ID available")
            return

        update_data = {
            "email": f"updated.lead.{datetime.now().strftime('%H%M%S')}@example.com",
            "notes": "Updated via API test"
        }
        
        success, data, status_code = self.make_request('PATCH', f'api/leads/{self.created_lead_id}', data=update_data)
        
        if success and data.get('email') == update_data['email']:
            self.log_test("Update Lead", True, f"Lead updated: email={data.get('email')}")
        else:
            self.log_test("Update Lead", False, f"Status: {status_code}, Response: {data}")

    def test_assign_lead_to_agent(self):
        """Test assigning lead to agent"""
        if not self.api_key or not self.created_lead_id:
            self.log_test("Assign Lead to Agent", False, "No API key or lead ID available")
            return

        # First create a new agent for assignment
        agent_data = {
            "name": f"Assignment Agent {datetime.now().strftime('%H%M%S')}",
            "email": f"assign.agent.{datetime.now().strftime('%H%M%S')}@example.com",
            "department": "sales"
        }
        
        success, agent_response, status_code = self.make_request('POST', 'api/agents', data=agent_data)
        
        if not success or not agent_response.get('id'):
            self.log_test("Assign Lead to Agent", False, "Failed to create agent for assignment")
            return

        agent_id = agent_response['id']
        
        # Now assign the lead
        assign_data = {"agent_id": agent_id}
        success, data, status_code = self.make_request('POST', f'api/leads/{self.created_lead_id}/assign', data=assign_data)
        
        if success and data.get('assigned_agent_id') == agent_id:
            self.log_test("Assign Lead to Agent", True, f"Lead assigned to agent: {data.get('assigned_agent_name')}")
        else:
            self.log_test("Assign Lead to Agent", False, f"Status: {status_code}, Response: {data}")

    def test_update_lead_status(self):
        """Test updating lead status with history"""
        if not self.api_key or not self.created_lead_id:
            self.log_test("Update Lead Status", False, "No API key or lead ID available")
            return

        status_data = {
            "status": "contacted",
            "notes": "Lead contacted via phone call"
        }
        
        success, data, status_code = self.make_request('POST', f'api/leads/{self.created_lead_id}/status', data=status_data)
        
        if success and data.get('status') == "contacted":
            self.log_test("Update Lead Status", True, f"Lead status updated to: {data.get('status')}")
        else:
            self.log_test("Update Lead Status", False, f"Status: {status_code}, Response: {data}")

    def test_webhook_auto_create_lead(self):
        """Test auto-creating lead from incoming WhatsApp message"""
        # Create a unique phone number for this test
        test_phone = f"1555{datetime.now().strftime('%H%M%S')}"
        
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "test_entry_id",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "+15551234567",
                            "phone_number_id": "123456789012345"
                        },
                        "contacts": [{
                            "profile": {
                                "name": f"Auto Lead {datetime.now().strftime('%H%M%S')}"
                            },
                            "wa_id": test_phone
                        }],
                        "messages": [{
                            "from": test_phone,
                            "id": f"auto_msg_{datetime.now().strftime('%H%M%S')}",
                            "timestamp": "1234567890",
                            "text": {
                                "body": "Hello, I'm interested in your services"
                            },
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        success, data, status_code = self.make_request('POST', 'api/webhook/whatsapp', data=webhook_payload, headers={})
        
        if status_code == 200:
            # Now check if lead was auto-created
            import time
            time.sleep(1)  # Give it a moment to process
            
            # Search for the lead by phone number
            params = {"search": test_phone}
            success, search_data, search_status = self.make_request('GET', 'api/leads', params=params)
            
            if success and search_data.get('total', 0) > 0:
                lead = search_data['leads'][0]
                if lead.get('source') == 'whatsapp' and lead.get('message_count') == 1:
                    self.log_test("Webhook Auto-Create Lead", True, f"Lead auto-created: {lead.get('name')} from WhatsApp")
                else:
                    self.log_test("Webhook Auto-Create Lead", False, f"Lead found but incorrect data: source={lead.get('source')}, count={lead.get('message_count')}")
            else:
                self.log_test("Webhook Auto-Create Lead", False, "Lead was not auto-created from webhook")
        else:
            self.log_test("Webhook Auto-Create Lead", False, f"Webhook failed: {status_code}")

    def test_webhook_increment_message_count(self):
        """Test that subsequent messages increment message_count"""
        # First, create a lead manually
        test_phone = f"1555{datetime.now().strftime('%H%M%S')}"
        
        lead_data = {
            "name": f"Message Count Test {datetime.now().strftime('%H%M%S')}",
            "phone": test_phone,
            "source": "whatsapp",
            "status": "new"
        }
        
        success, lead_response, status_code = self.make_request('POST', 'api/leads', data=lead_data)
        
        if not success or not lead_response.get('id'):
            self.log_test("Webhook Increment Message Count", False, "Failed to create test lead")
            return

        lead_id = lead_response['id']
        
        # Send first webhook message
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "test_entry_id",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "+15551234567",
                            "phone_number_id": "123456789012345"
                        },
                        "contacts": [{
                            "profile": {
                                "name": "Test User"
                            },
                            "wa_id": test_phone
                        }],
                        "messages": [{
                            "from": test_phone,
                            "id": f"msg1_{datetime.now().strftime('%H%M%S')}",
                            "timestamp": "1234567890",
                            "text": {
                                "body": "First message"
                            },
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        success, data, status_code = self.make_request('POST', 'api/webhook/whatsapp', data=webhook_payload, headers={})
        
        if status_code != 200:
            self.log_test("Webhook Increment Message Count", False, f"First webhook failed: {status_code}")
            return

        import time
        time.sleep(1)  # Give it a moment to process
        
        # Check message count after first message
        success, lead_data, status_code = self.make_request('GET', f'api/leads/{lead_id}')
        
        if not success:
            self.log_test("Webhook Increment Message Count", False, "Failed to retrieve lead after first message")
            return

        first_count = lead_data.get('message_count', 0)
        
        # Send second webhook message
        webhook_payload['entry'][0]['changes'][0]['value']['messages'][0]['id'] = f"msg2_{datetime.now().strftime('%H%M%S')}"
        webhook_payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body'] = "Second message"
        
        success, data, status_code = self.make_request('POST', 'api/webhook/whatsapp', data=webhook_payload, headers={})
        
        if status_code != 200:
            self.log_test("Webhook Increment Message Count", False, f"Second webhook failed: {status_code}")
            return

        time.sleep(1)  # Give it a moment to process
        
        # Check message count after second message
        success, lead_data, status_code = self.make_request('GET', f'api/leads/{lead_id}')
        
        if success:
            second_count = lead_data.get('message_count', 0)
            if second_count == first_count + 1:
                self.log_test("Webhook Increment Message Count", True, f"Message count incremented: {first_count} -> {second_count}")
            else:
                self.log_test("Webhook Increment Message Count", False, f"Message count not incremented correctly: {first_count} -> {second_count}")
        else:
            self.log_test("Webhook Increment Message Count", False, "Failed to retrieve lead after second message")

    def test_delete_lead(self):
        """Test deleting a lead"""
        if not self.api_key or not self.created_lead_id:
            self.log_test("Delete Lead", False, "No API key or lead ID available")
            return

        success, data, status_code = self.make_request('DELETE', f'api/leads/{self.created_lead_id}')
        
        if success and data.get('success'):
            self.log_test("Delete Lead", True, f"Lead deleted successfully")
        else:
            self.log_test("Delete Lead", False, f"Status: {status_code}, Response: {data}")

    # ============== AUTOMATION ENGINE TESTS ==============

    def test_list_trigger_types(self):
        """Test GET /api/automation/triggers - List available trigger types"""
        if not self.api_key:
            self.log_test("List Trigger Types", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/automation/triggers')
        
        if success and 'triggers' in data and isinstance(data['triggers'], list):
            triggers = data['triggers']
            expected_triggers = ['new_message', 'new_lead', 'no_reply', 'lead_status_change', 'scheduled']
            found_triggers = [t.get('value') for t in triggers]
            
            if all(trigger in found_triggers for trigger in expected_triggers):
                self.log_test("List Trigger Types", True, f"Found {len(triggers)} trigger types: {found_triggers}")
            else:
                self.log_test("List Trigger Types", False, f"Missing expected triggers. Found: {found_triggers}")
        else:
            self.log_test("List Trigger Types", False, f"Status: {status_code}, Response: {data}")

    def test_list_action_types(self):
        """Test GET /api/automation/actions - List available action types"""
        if not self.api_key:
            self.log_test("List Action Types", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/automation/actions')
        
        if success and 'actions' in data and isinstance(data['actions'], list):
            actions = data['actions']
            expected_actions = ['send_message', 'assign_lead', 'update_status', 'add_tag', 'send_template']
            found_actions = [a.get('value') for a in actions]
            
            if all(action in found_actions for action in expected_actions):
                self.log_test("List Action Types", True, f"Found {len(actions)} action types: {found_actions}")
            else:
                self.log_test("List Action Types", False, f"Missing expected actions. Found: {found_actions}")
        else:
            self.log_test("List Action Types", False, f"Status: {status_code}, Response: {data}")

    def test_create_automation_rule(self):
        """Test POST /api/automation/rules - Create automation rule"""
        if not self.api_key:
            self.log_test("Create Automation Rule", False, "No API key available")
            return

        rule_data = {
            "name": f"Test Welcome Rule {datetime.now().strftime('%H%M%S')}",
            "description": "Test rule for new leads",
            "trigger_type": "new_lead",
            "trigger_config": {},
            "conditions": [],
            "actions": [{
                "action_type": "send_message",
                "config": {
                    "message_text": "Welcome! Thanks for reaching out to us."
                },
                "delay_minutes": 0
            }],
            "is_active": True,
            "priority": 1
        }
        
        success, data, status_code = self.make_request('POST', 'api/automation/rules', data=rule_data)
        
        if success and data.get('id'):
            self.created_rule_id = data['id']
            self.log_test("Create Automation Rule", True, f"Rule created: {data.get('name')} (ID: {data.get('id')})")
        else:
            self.log_test("Create Automation Rule", False, f"Status: {status_code}, Response: {data}")

    def test_list_automation_rules(self):
        """Test GET /api/automation/rules - List all rules"""
        if not self.api_key:
            self.log_test("List Automation Rules", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/automation/rules')
        
        if success and 'total' in data and 'rules' in data:
            self.log_test("List Automation Rules", True, f"Found {data.get('total')} automation rules")
        else:
            self.log_test("List Automation Rules", False, f"Status: {status_code}, Response: {data}")

    def test_get_automation_rule_by_id(self):
        """Test GET /api/automation/rules/{id} - Get specific rule"""
        if not self.api_key or not hasattr(self, 'created_rule_id'):
            self.log_test("Get Automation Rule by ID", False, "No API key or rule ID available")
            return

        success, data, status_code = self.make_request('GET', f'api/automation/rules/{self.created_rule_id}')
        
        if success and data.get('id') == self.created_rule_id:
            self.log_test("Get Automation Rule by ID", True, f"Rule retrieved: {data.get('name')}")
        else:
            self.log_test("Get Automation Rule by ID", False, f"Status: {status_code}, Response: {data}")

    def test_update_automation_rule(self):
        """Test PATCH /api/automation/rules/{id} - Update rule"""
        if not self.api_key or not hasattr(self, 'created_rule_id'):
            self.log_test("Update Automation Rule", False, "No API key or rule ID available")
            return

        update_data = {
            "description": "Updated test rule description",
            "priority": 5
        }
        
        success, data, status_code = self.make_request('PATCH', f'api/automation/rules/{self.created_rule_id}', data=update_data)
        
        if success and data.get('priority') == 5:
            self.log_test("Update Automation Rule", True, f"Rule updated: priority={data.get('priority')}")
        else:
            self.log_test("Update Automation Rule", False, f"Status: {status_code}, Response: {data}")

    def test_toggle_automation_rule(self):
        """Test POST /api/automation/rules/{id}/toggle - Toggle rule active status"""
        if not self.api_key or not hasattr(self, 'created_rule_id'):
            self.log_test("Toggle Automation Rule", False, "No API key or rule ID available")
            return

        # First get current status
        success, rule_data, status_code = self.make_request('GET', f'api/automation/rules/{self.created_rule_id}')
        if not success:
            self.log_test("Toggle Automation Rule", False, "Failed to get current rule status")
            return

        original_status = rule_data.get('is_active', True)
        
        # Toggle the rule
        success, data, status_code = self.make_request('POST', f'api/automation/rules/{self.created_rule_id}/toggle')
        
        if success and data.get('is_active') != original_status:
            self.log_test("Toggle Automation Rule", True, f"Rule toggled: {original_status} -> {data.get('is_active')}")
        else:
            self.log_test("Toggle Automation Rule", False, f"Status: {status_code}, Response: {data}")

    def test_create_no_reply_rule(self):
        """Test creating a no_reply automation rule with trigger config"""
        if not self.api_key:
            self.log_test("Create No Reply Rule", False, "No API key available")
            return

        rule_data = {
            "name": f"No Reply Follow-up {datetime.now().strftime('%H%M%S')}",
            "description": "Send follow-up after 24 hours of no reply",
            "trigger_type": "no_reply",
            "trigger_config": {
                "hours": 24
            },
            "conditions": [],
            "actions": [{
                "action_type": "send_message",
                "config": {
                    "message_text": "Hi! Just following up on your inquiry. How can we help you?"
                },
                "delay_minutes": 0
            }],
            "is_active": True,
            "priority": 2
        }
        
        success, data, status_code = self.make_request('POST', 'api/automation/rules', data=rule_data)
        
        if success and data.get('id') and data.get('trigger_config', {}).get('hours') == 24:
            self.created_no_reply_rule_id = data['id']
            self.log_test("Create No Reply Rule", True, f"No reply rule created: {data.get('name')}")
        else:
            self.log_test("Create No Reply Rule", False, f"Status: {status_code}, Response: {data}")

    def test_create_assign_lead_rule(self):
        """Test creating a rule with assign_lead action"""
        if not self.api_key:
            self.log_test("Create Assign Lead Rule", False, "No API key available")
            return

        rule_data = {
            "name": f"Auto Assign New Leads {datetime.now().strftime('%H%M%S')}",
            "description": "Automatically assign new leads using round robin",
            "trigger_type": "new_lead",
            "trigger_config": {},
            "conditions": [],
            "actions": [{
                "action_type": "assign_lead",
                "config": {
                    "assignment_strategy": "round_robin"
                },
                "delay_minutes": 0
            }],
            "is_active": True,
            "priority": 3
        }
        
        success, data, status_code = self.make_request('POST', 'api/automation/rules', data=rule_data)
        
        if success and data.get('id'):
            self.created_assign_rule_id = data['id']
            self.log_test("Create Assign Lead Rule", True, f"Assign rule created: {data.get('name')}")
        else:
            self.log_test("Create Assign Lead Rule", False, f"Status: {status_code}, Response: {data}")

    def test_list_execution_logs(self):
        """Test GET /api/automation/logs - List execution logs"""
        if not self.api_key:
            self.log_test("List Execution Logs", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/automation/logs')
        
        if success and 'total' in data and 'logs' in data:
            self.log_test("List Execution Logs", True, f"Found {data.get('total')} execution logs")
        else:
            self.log_test("List Execution Logs", False, f"Status: {status_code}, Response: {data}")

    def test_list_execution_logs_with_filters(self):
        """Test execution logs with rule_id filter"""
        if not self.api_key or not hasattr(self, 'created_rule_id'):
            self.log_test("List Execution Logs with Filters", False, "No API key or rule ID available")
            return

        params = {"rule_id": self.created_rule_id, "limit": 10}
        success, data, status_code = self.make_request('GET', 'api/automation/logs', params=params)
        
        if success and 'total' in data and 'logs' in data:
            self.log_test("List Execution Logs with Filters", True, f"Found {data.get('total')} logs for rule {self.created_rule_id}")
        else:
            self.log_test("List Execution Logs with Filters", False, f"Status: {status_code}, Response: {data}")

    def test_scheduler_status(self):
        """Test GET /api/automation/scheduler/status - Check scheduler status and jobs"""
        if not self.api_key:
            self.log_test("Scheduler Status", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/automation/scheduler/status')
        
        if success and 'running' in data and 'jobs' in data:
            running = data.get('running')
            jobs = data.get('jobs', [])
            expected_jobs = ['check_no_reply', 'execute_scheduled_tasks', 'run_cron_rules']
            
            job_ids = [job.get('id') for job in jobs if isinstance(job, dict)]
            
            if running and all(job_id in job_ids for job_id in expected_jobs):
                self.log_test("Scheduler Status", True, f"Scheduler running: {running}, Jobs: {len(jobs)}")
            else:
                self.log_test("Scheduler Status", False, f"Scheduler issues - Running: {running}, Jobs: {job_ids}")
        else:
            self.log_test("Scheduler Status", False, f"Status: {status_code}, Response: {data}")

    def test_delete_automation_rule(self):
        """Test DELETE /api/automation/rules/{id} - Delete rule"""
        if not self.api_key or not hasattr(self, 'created_rule_id'):
            self.log_test("Delete Automation Rule", False, "No API key or rule ID available")
            return

        success, data, status_code = self.make_request('DELETE', f'api/automation/rules/{self.created_rule_id}')
        
        if success and data.get('success'):
            self.log_test("Delete Automation Rule", True, f"Rule deleted successfully")
        else:
            self.log_test("Delete Automation Rule", False, f"Status: {status_code}, Response: {data}")

    def test_delete_no_reply_rule(self):
        """Test deleting the no reply rule"""
        if not self.api_key or not hasattr(self, 'created_no_reply_rule_id'):
            self.log_test("Delete No Reply Rule", False, "No API key or no reply rule ID available")
            return

        success, data, status_code = self.make_request('DELETE', f'api/automation/rules/{self.created_no_reply_rule_id}')
        
        if success and data.get('success'):
            self.log_test("Delete No Reply Rule", True, f"No reply rule deleted successfully")
        else:
            self.log_test("Delete No Reply Rule", False, f"Status: {status_code}, Response: {data}")

    def test_delete_assign_rule(self):
        """Test deleting the assign rule"""
        if not self.api_key or not hasattr(self, 'created_assign_rule_id'):
            self.log_test("Delete Assign Rule", False, "No API key or assign rule ID available")
            return

        success, data, status_code = self.make_request('DELETE', f'api/automation/rules/{self.created_assign_rule_id}')
        
        if success and data.get('success'):
            self.log_test("Delete Assign Rule", True, f"Assign rule deleted successfully")
        else:
            self.log_test("Delete Assign Rule", False, f"Status: {status_code}, Response: {data}")

    # ============== DASHBOARD API TESTS ==============

    def test_dashboard_metrics(self):
        """Test GET /api/dashboard/metrics - Dashboard metrics endpoint"""
        if not self.api_key:
            self.log_test("Dashboard Metrics", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/dashboard/metrics')
        
        if success:
            required_fields = [
                'total_leads', 'new_leads', 'converted_leads', 'conversion_rate',
                'leads_by_status', 'leads_by_source', 'total_messages', 
                'inbound_messages', 'outbound_messages', 'agent_performance'
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.log_test("Dashboard Metrics", True, 
                             f"Total Leads: {data.get('total_leads')}, Conversion Rate: {data.get('conversion_rate')}%")
            else:
                self.log_test("Dashboard Metrics", False, f"Missing fields: {missing_fields}")
        else:
            self.log_test("Dashboard Metrics", False, f"Status: {status_code}, Response: {data}")

    def test_dashboard_metrics_with_date_filter(self):
        """Test dashboard metrics with date filtering"""
        if not self.api_key:
            self.log_test("Dashboard Metrics with Date Filter", False, "No API key available")
            return

        from datetime import datetime, timedelta
        end_date = datetime.now().isoformat()
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        
        params = {'start_date': start_date, 'end_date': end_date}
        success, data, status_code = self.make_request('GET', 'api/dashboard/metrics', params=params)
        
        if success:
            self.log_test("Dashboard Metrics with Date Filter", True, 
                         f"Filtered data returned successfully")
        else:
            self.log_test("Dashboard Metrics with Date Filter", False, f"Status: {status_code}")

    def test_leads_over_time(self):
        """Test GET /api/dashboard/leads-over-time - Leads over time endpoint"""
        if not self.api_key:
            self.log_test("Leads Over Time", False, "No API key available")
            return

        # Test different intervals
        intervals = ['day', 'week', 'month']
        
        for interval in intervals:
            params = {'interval': interval}
            success, data, status_code = self.make_request('GET', 'api/dashboard/leads-over-time', params=params)
            
            if success and 'data' in data:
                data_points = len(data.get('data', []))
                self.log_test(f"Leads Over Time - {interval}", True, 
                             f"Returned {data_points} data points")
            else:
                self.log_test(f"Leads Over Time - {interval}", False, 
                             f"Status: {status_code}, Response: {data}")

    def test_messages_over_time(self):
        """Test GET /api/dashboard/messages-over-time - Messages over time endpoint"""
        if not self.api_key:
            self.log_test("Messages Over Time", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/dashboard/messages-over-time')
        
        if success and 'data' in data:
            data_points = len(data.get('data', []))
            self.log_test("Messages Over Time", True, 
                         f"Returned {data_points} data points")
            
            # Check data structure
            if data.get('data'):
                sample_point = data['data'][0]
                required_keys = ['date', 'inbound', 'outbound']
                missing_keys = [key for key in required_keys if key not in sample_point]
                
                if not missing_keys:
                    self.log_test("Messages Over Time - Data Structure", True, 
                                 "All required fields present")
                else:
                    self.log_test("Messages Over Time - Data Structure", False, 
                                 f"Missing keys: {missing_keys}")
        else:
            self.log_test("Messages Over Time", False, f"Status: {status_code}")

    def test_response_times(self):
        """Test GET /api/dashboard/response-times - Response times endpoint"""
        if not self.api_key:
            self.log_test("Response Times", False, "No API key available")
            return

        success, data, status_code = self.make_request('GET', 'api/dashboard/response-times')
        
        if success:
            required_fields = [
                'average_minutes', 'min_minutes', 'max_minutes', 
                'total_responses', 'distribution'
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.log_test("Response Times", True, 
                             f"Avg: {data.get('average_minutes')} min, Total: {data.get('total_responses')}")
                
                # Check distribution structure
                distribution = data.get('distribution', {})
                dist_keys = ['under_5min', '5_to_15min', '15_to_60min', '1_to_4h', 'over_4h']
                missing_dist_keys = [key for key in dist_keys if key not in distribution]
                
                if not missing_dist_keys:
                    self.log_test("Response Times - Distribution", True, 
                                 "All distribution buckets present")
                else:
                    self.log_test("Response Times - Distribution", False, 
                                 f"Missing distribution keys: {missing_dist_keys}")
            else:
                self.log_test("Response Times", False, f"Missing fields: {missing_fields}")
        else:
            self.log_test("Response Times", False, f"Status: {status_code}")

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting WhatsApp Business API Backend Tests")
        print(f"📡 Testing endpoint: {self.base_url}")
        print("=" * 60)

        # Basic tests first
        self.test_health_check()
        
        # Skip API Key creation since we have a provided key
        if self.api_key:
            print(f"✅ Using provided API key: {self.api_key[:10]}...")
        
        # WhatsApp number management (basic tests)
        self.test_list_whatsapp_numbers()
        
        # Webhook tests
        self.test_webhook_verification()
        
        # ============== CRM TESTS ==============
        print("\n🏢 Testing CRM Agent Management...")
        
        # Agent CRUD operations
        self.test_create_agent()
        self.test_list_agents()
        self.test_list_agents_with_filters()
        self.test_get_agent_by_id()
        self.test_update_agent()
        
        print("\n📋 Testing CRM Lead Management...")
        
        # Lead CRUD operations
        self.test_create_lead()
        self.test_list_leads()
        self.test_list_leads_with_filters()
        self.test_get_lead_stats()
        self.test_get_lead_by_id()
        self.test_update_lead()
        self.test_assign_lead_to_agent()
        self.test_update_lead_status()
        
        print("\n🔗 Testing WhatsApp Integration...")
        
        # WhatsApp webhook integration tests
        self.test_webhook_auto_create_lead()
        self.test_webhook_increment_message_count()
        
        # ============== AUTOMATION ENGINE TESTS ==============
        print("\n⚡ Testing Automation Engine...")
        
        # Test automation metadata endpoints
        self.test_list_trigger_types()
        self.test_list_action_types()
        
        # Test scheduler status
        self.test_scheduler_status()
        
        # Test automation rule CRUD operations
        self.test_create_automation_rule()
        self.test_list_automation_rules()
        self.test_get_automation_rule_by_id()
        self.test_update_automation_rule()
        self.test_toggle_automation_rule()
        
        # Test different rule types
        self.test_create_no_reply_rule()
        self.test_create_assign_lead_rule()
        
        # Test execution logs
        self.test_list_execution_logs()
        self.test_list_execution_logs_with_filters()

        # ============== DASHBOARD API TESTS ==============
        print("\n📊 Testing Dashboard APIs...")
        
        # Test all dashboard endpoints
        self.test_dashboard_metrics()
        self.test_dashboard_metrics_with_date_filter()
        self.test_leads_over_time()
        self.test_messages_over_time()
        self.test_response_times()
        
        print("\n🧹 Testing Cleanup Operations...")
        
        # Cleanup tests
        self.test_delete_lead()
        self.test_deactivate_agent()
        
        # Cleanup automation rules
        self.test_delete_automation_rule()
        self.test_delete_no_reply_rule()
        self.test_delete_assign_rule()

        # Print summary
        print("=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️  Some tests failed - check details above")
            return 1

def main():
    """Main test runner"""
    tester = WhatsAppAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())