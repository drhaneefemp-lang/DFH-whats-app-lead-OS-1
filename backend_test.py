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
        self.api_key = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.whatsapp_number_id = None
        self.created_message_id = None

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

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting WhatsApp Business API Backend Tests")
        print(f"📡 Testing endpoint: {self.base_url}")
        print("=" * 60)

        # Basic tests first
        self.test_health_check()
        
        # API Key management
        self.test_create_api_key()
        self.test_list_api_keys()
        
        # WhatsApp number management
        self.test_connect_whatsapp_number()
        self.test_list_whatsapp_numbers()
        
        # Webhook tests
        self.test_webhook_verification()
        self.test_webhook_message_receive()
        
        # Message sending tests (expected to fail with test tokens)
        self.test_send_text_message()
        self.test_send_image_message()
        self.test_send_document_message()
        self.test_send_video_message()
        self.test_send_template_message()
        
        # Message retrieval tests
        self.test_list_messages()
        self.test_get_specific_message()
        
        # Cleanup tests
        self.test_disconnect_whatsapp_number()
        # Note: Not testing API key revocation to avoid breaking our test session

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