"""
WhatsApp Cloud API service for sending messages
"""
import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

META_API_BASE = "https://graph.facebook.com"
API_VERSION = "v18.0"


class WhatsAppService:
    """Service class for WhatsApp Cloud API interactions"""
    
    def __init__(self, phone_number_id: str, access_token: str):
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.base_url = f"{META_API_BASE}/{API_VERSION}/{phone_number_id}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_text_message(self, recipient: str, text: str) -> Dict[str, Any]:
        """
        Send a text message to a WhatsApp user
        
        Args:
            recipient: Phone number in international format (e.g., 15551234567)
            text: Message text (max 4096 characters)
        
        Returns:
            API response with message ID
        """
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {
                "body": text
            }
        }
        
        return await self._post_message(payload)
    
    async def send_image_message(
        self, 
        recipient: str, 
        image_source: str, 
        caption: Optional[str] = None,
        use_media_id: bool = False
    ) -> Dict[str, Any]:
        """
        Send an image message
        
        Args:
            recipient: Phone number
            image_source: URL or media ID
            caption: Optional caption
            use_media_id: If True, image_source is treated as media ID
        """
        image_payload = {"id": image_source} if use_media_id else {"link": image_source}
        
        if caption:
            image_payload["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "image",
            "image": image_payload
        }
        
        return await self._post_message(payload)
    
    async def send_document_message(
        self,
        recipient: str,
        document_source: str,
        filename: str,
        use_media_id: bool = False
    ) -> Dict[str, Any]:
        """
        Send a document message
        
        Args:
            recipient: Phone number
            document_source: URL or media ID
            filename: Display filename
            use_media_id: If True, document_source is treated as media ID
        """
        doc_payload = {"id": document_source} if use_media_id else {"link": document_source}
        doc_payload["filename"] = filename
        
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "document",
            "document": doc_payload
        }
        
        return await self._post_message(payload)
    
    async def send_video_message(
        self,
        recipient: str,
        video_source: str,
        caption: Optional[str] = None,
        use_media_id: bool = False
    ) -> Dict[str, Any]:
        """
        Send a video message
        
        Args:
            recipient: Phone number
            video_source: URL or media ID
            caption: Optional caption
            use_media_id: If True, video_source is treated as media ID
        """
        video_payload = {"id": video_source} if use_media_id else {"link": video_source}
        
        if caption:
            video_payload["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "video",
            "video": video_payload
        }
        
        return await self._post_message(payload)
    
    async def send_template_message(
        self,
        recipient: str,
        template_name: str,
        language_code: str = "en_US",
        parameters: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Send a template message
        
        Args:
            recipient: Phone number
            template_name: Approved template name
            language_code: Template language
            parameters: Dynamic parameters for template variables
        """
        template_payload = {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
        
        if parameters:
            template_payload["components"] = [{
                "type": "body",
                "parameters": [{"type": "text", "text": param} for param in parameters]
            }]
        
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": template_payload
        }
        
        return await self._post_message(payload)
    
    async def _post_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send POST request to WhatsApp messages endpoint
        
        Args:
            payload: Message payload
        
        Returns:
            API response
        
        Raises:
            Exception on API error
        """
        url = f"{self.base_url}/messages"
        headers = self._get_headers()
        
        logger.info(f"Sending message to {payload.get('to')}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )
                
                response_data = response.json()
                
                if response.status_code not in [200, 201]:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    error_code = response_data.get("error", {}).get("code", 0)
                    logger.error(f"WhatsApp API error: {error_code} - {error_msg}")
                    raise Exception(f"WhatsApp API error {error_code}: {error_msg}")
                
                message_id = response_data.get("messages", [{}])[0].get("id")
                logger.info(f"Message sent successfully. ID: {message_id}")
                
                return {
                    "success": True,
                    "message_id": message_id,
                    "response": response_data
                }
        
        except httpx.TimeoutException:
            logger.error("WhatsApp API request timed out")
            raise Exception("WhatsApp API request timed out")
        
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise Exception(f"Request error: {str(e)}")
    
    async def download_media(self, media_id: str) -> Dict[str, Any]:
        """
        Get media download URL from media ID
        
        Args:
            media_id: WhatsApp media ID
        
        Returns:
            Media URL and metadata
        """
        url = f"{META_API_BASE}/{API_VERSION}/{media_id}"
        headers = self._get_headers()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                
                if response.status_code != 200:
                    raise Exception(f"Failed to get media URL: {response.text}")
                
                return response.json()
        
        except Exception as e:
            logger.error(f"Error downloading media: {str(e)}")
            raise
