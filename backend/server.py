"""
WhatsApp Business API Backend Service
- Connect multiple WhatsApp numbers
- Handle webhook events for incoming messages
- Store message data in MongoDB
- Support message sending via API
"""
from fastapi import FastAPI, APIRouter, Request, Response, HTTPException, Depends, Query
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

from models import (
    WhatsAppNumberCreate, WhatsAppNumber, WhatsAppNumberResponse,
    TextMessageRequest, ImageMessageRequest, DocumentMessageRequest,
    VideoMessageRequest, TemplateMessageRequest, MessageResponse,
    StoredMessage, MessageListResponse,
    APIKeyCreate, APIKey, APIKeyResponse,
    HealthCheck
)
from whatsapp_service import WhatsAppService
from auth import generate_api_key, hash_api_key, validate_api_key, api_key_header

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Default webhook verify token (can be overridden per number)
DEFAULT_WEBHOOK_VERIFY_TOKEN = os.environ.get('WEBHOOK_VERIFY_TOKEN', 'whatsapp_webhook_token')

# Create FastAPI app
app = FastAPI(
    title="WhatsApp Business API Service",
    description="Backend service for WhatsApp Business Cloud API integration",
    version="1.0.0"
)

# Create routers
api_router = APIRouter(prefix="/api")
webhook_router = APIRouter()


# ============== Dependencies ==============

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """Verify API key for protected endpoints"""
    await validate_api_key(api_key, db)
    return api_key


async def get_whatsapp_service(phone_number_id: Optional[str] = None) -> WhatsAppService:
    """
    Get WhatsApp service instance for a specific or default number
    
    Args:
        phone_number_id: Specific phone number ID, or None for default
    
    Returns:
        WhatsAppService instance
    """
    query = {"is_active": True}
    if phone_number_id:
        query["phone_number_id"] = phone_number_id
    
    number_doc = await db.whatsapp_numbers.find_one(query, {"_id": 0})
    
    if not number_doc:
        raise HTTPException(
            status_code=404,
            detail="No active WhatsApp number configured" if not phone_number_id 
                   else f"WhatsApp number {phone_number_id} not found"
        )
    
    return WhatsAppService(
        phone_number_id=number_doc["phone_number_id"],
        access_token=number_doc["access_token"]
    )


# ============== Health Check ==============

@api_router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        count = await db.whatsapp_numbers.count_documents({"is_active": True})
        return HealthCheck(
            status="healthy",
            connected_numbers=count,
            database="connected"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheck(
            status="unhealthy",
            database="disconnected"
        )


# ============== API Key Management ==============

@api_router.post("/keys", response_model=APIKeyResponse)
async def create_api_key(request: APIKeyCreate):
    """
    Create a new API key for authentication
    
    Returns the key only once - store it securely!
    """
    raw_key = generate_api_key()
    hashed_key = hash_api_key(raw_key)
    
    api_key_doc = APIKey(
        name=request.name,
        key=hashed_key
    )
    
    doc = api_key_doc.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.api_keys.insert_one(doc)
    
    logger.info(f"Created new API key: {request.name}")
    
    return APIKeyResponse(
        id=api_key_doc.id,
        name=api_key_doc.name,
        key=raw_key,  # Return unhashed key only on creation
        is_active=api_key_doc.is_active,
        created_at=api_key_doc.created_at
    )


@api_router.get("/keys", response_model=List[APIKeyResponse], dependencies=[Depends(verify_api_key)])
async def list_api_keys():
    """List all API keys (without showing the actual keys)"""
    keys = await db.api_keys.find({}, {"_id": 0}).to_list(100)
    
    result = []
    for key in keys:
        if isinstance(key.get('created_at'), str):
            key['created_at'] = datetime.fromisoformat(key['created_at'])
        if isinstance(key.get('last_used_at'), str):
            key['last_used_at'] = datetime.fromisoformat(key['last_used_at'])
        result.append(APIKeyResponse(
            id=key['id'],
            name=key['name'],
            key=None,  # Never expose the key
            is_active=key['is_active'],
            created_at=key['created_at']
        ))
    
    return result


@api_router.delete("/keys/{key_id}", dependencies=[Depends(verify_api_key)])
async def revoke_api_key(key_id: str):
    """Revoke (deactivate) an API key"""
    result = await db.api_keys.update_one(
        {"id": key_id},
        {"$set": {"is_active": False}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="API key not found")
    
    logger.info(f"Revoked API key: {key_id}")
    return {"success": True, "message": "API key revoked"}


# ============== WhatsApp Number Management ==============

@api_router.post("/numbers", response_model=WhatsAppNumberResponse, dependencies=[Depends(verify_api_key)])
async def connect_whatsapp_number(request: WhatsAppNumberCreate):
    """
    Connect a new WhatsApp Business number
    
    Requires Meta Phone Number ID and Access Token from WhatsApp Cloud API
    """
    # Check if number already exists
    existing = await db.whatsapp_numbers.find_one(
        {"phone_number_id": request.phone_number_id},
        {"_id": 0}
    )
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="This phone number ID is already connected"
        )
    
    # Create number document
    number = WhatsAppNumber(
        phone_number_id=request.phone_number_id,
        display_phone_number=request.display_phone_number,
        access_token=request.access_token,
        department=request.department,
        webhook_verify_token=request.webhook_verify_token or DEFAULT_WEBHOOK_VERIFY_TOKEN
    )
    
    doc = number.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.whatsapp_numbers.insert_one(doc)
    
    logger.info(f"Connected WhatsApp number: {request.display_phone_number}")
    
    return WhatsAppNumberResponse(
        id=number.id,
        phone_number_id=number.phone_number_id,
        display_phone_number=number.display_phone_number,
        department=number.department,
        is_active=number.is_active,
        created_at=number.created_at,
        updated_at=number.updated_at
    )


@api_router.get("/numbers", response_model=List[WhatsAppNumberResponse], dependencies=[Depends(verify_api_key)])
async def list_whatsapp_numbers():
    """List all connected WhatsApp numbers"""
    numbers = await db.whatsapp_numbers.find({}, {"_id": 0, "access_token": 0}).to_list(100)
    
    result = []
    for num in numbers:
        if isinstance(num.get('created_at'), str):
            num['created_at'] = datetime.fromisoformat(num['created_at'])
        if isinstance(num.get('updated_at'), str):
            num['updated_at'] = datetime.fromisoformat(num['updated_at'])
        result.append(WhatsAppNumberResponse(**num))
    
    return result


@api_router.delete("/numbers/{number_id}", dependencies=[Depends(verify_api_key)])
async def disconnect_whatsapp_number(number_id: str):
    """Disconnect (deactivate) a WhatsApp number"""
    result = await db.whatsapp_numbers.update_one(
        {"id": number_id},
        {"$set": {"is_active": False, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="WhatsApp number not found")
    
    logger.info(f"Disconnected WhatsApp number: {number_id}")
    return {"success": True, "message": "WhatsApp number disconnected"}


# ============== Message Sending Endpoints ==============

@api_router.post("/messages/text", response_model=MessageResponse, dependencies=[Depends(verify_api_key)])
async def send_text_message(request: TextMessageRequest):
    """Send a text message to a WhatsApp user"""
    try:
        service = await get_whatsapp_service(request.phone_number_id)
        result = await service.send_text_message(request.recipient_phone, request.message_text)
        
        # Store outbound message
        message = StoredMessage(
            wa_message_id=result["message_id"],
            phone_number_id=service.phone_number_id,
            sender=service.phone_number_id,
            recipient=request.recipient_phone,
            message_type="text",
            direction="outbound",
            content=request.message_text,
            status="sent"
        )
        
        doc = message.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.messages.insert_one(doc)
        
        return MessageResponse(
            success=True,
            message_id=result["message_id"],
            recipient=request.recipient_phone,
            message_type="text"
        )
    
    except Exception as e:
        logger.error(f"Failed to send text message: {str(e)}")
        return MessageResponse(
            success=False,
            recipient=request.recipient_phone,
            message_type="text",
            error=str(e)
        )


@api_router.post("/messages/image", response_model=MessageResponse, dependencies=[Depends(verify_api_key)])
async def send_image_message(request: ImageMessageRequest):
    """Send an image message to a WhatsApp user"""
    try:
        service = await get_whatsapp_service(request.phone_number_id)
        result = await service.send_image_message(
            request.recipient_phone,
            request.image_url,
            request.caption,
            request.use_media_id
        )
        
        # Store outbound message
        message = StoredMessage(
            wa_message_id=result["message_id"],
            phone_number_id=service.phone_number_id,
            sender=service.phone_number_id,
            recipient=request.recipient_phone,
            message_type="image",
            direction="outbound",
            content=request.caption,
            media_id=request.image_url if request.use_media_id else None,
            status="sent"
        )
        
        doc = message.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.messages.insert_one(doc)
        
        return MessageResponse(
            success=True,
            message_id=result["message_id"],
            recipient=request.recipient_phone,
            message_type="image"
        )
    
    except Exception as e:
        logger.error(f"Failed to send image message: {str(e)}")
        return MessageResponse(
            success=False,
            recipient=request.recipient_phone,
            message_type="image",
            error=str(e)
        )


@api_router.post("/messages/document", response_model=MessageResponse, dependencies=[Depends(verify_api_key)])
async def send_document_message(request: DocumentMessageRequest):
    """Send a document message to a WhatsApp user"""
    try:
        service = await get_whatsapp_service(request.phone_number_id)
        result = await service.send_document_message(
            request.recipient_phone,
            request.document_url,
            request.filename,
            request.use_media_id
        )
        
        # Store outbound message
        message = StoredMessage(
            wa_message_id=result["message_id"],
            phone_number_id=service.phone_number_id,
            sender=service.phone_number_id,
            recipient=request.recipient_phone,
            message_type="document",
            direction="outbound",
            content=request.filename,
            media_id=request.document_url if request.use_media_id else None,
            status="sent"
        )
        
        doc = message.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.messages.insert_one(doc)
        
        return MessageResponse(
            success=True,
            message_id=result["message_id"],
            recipient=request.recipient_phone,
            message_type="document"
        )
    
    except Exception as e:
        logger.error(f"Failed to send document message: {str(e)}")
        return MessageResponse(
            success=False,
            recipient=request.recipient_phone,
            message_type="document",
            error=str(e)
        )


@api_router.post("/messages/video", response_model=MessageResponse, dependencies=[Depends(verify_api_key)])
async def send_video_message(request: VideoMessageRequest):
    """Send a video message to a WhatsApp user"""
    try:
        service = await get_whatsapp_service(request.phone_number_id)
        result = await service.send_video_message(
            request.recipient_phone,
            request.video_url,
            request.caption,
            request.use_media_id
        )
        
        # Store outbound message
        message = StoredMessage(
            wa_message_id=result["message_id"],
            phone_number_id=service.phone_number_id,
            sender=service.phone_number_id,
            recipient=request.recipient_phone,
            message_type="video",
            direction="outbound",
            content=request.caption,
            media_id=request.video_url if request.use_media_id else None,
            status="sent"
        )
        
        doc = message.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.messages.insert_one(doc)
        
        return MessageResponse(
            success=True,
            message_id=result["message_id"],
            recipient=request.recipient_phone,
            message_type="video"
        )
    
    except Exception as e:
        logger.error(f"Failed to send video message: {str(e)}")
        return MessageResponse(
            success=False,
            recipient=request.recipient_phone,
            message_type="video",
            error=str(e)
        )


@api_router.post("/messages/template", response_model=MessageResponse, dependencies=[Depends(verify_api_key)])
async def send_template_message(request: TemplateMessageRequest):
    """Send a template message to a WhatsApp user"""
    try:
        service = await get_whatsapp_service(request.phone_number_id)
        result = await service.send_template_message(
            request.recipient_phone,
            request.template_name,
            request.language_code,
            request.parameters
        )
        
        # Store outbound message
        message = StoredMessage(
            wa_message_id=result["message_id"],
            phone_number_id=service.phone_number_id,
            sender=service.phone_number_id,
            recipient=request.recipient_phone,
            message_type="template",
            direction="outbound",
            content=f"Template: {request.template_name}",
            status="sent"
        )
        
        doc = message.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.messages.insert_one(doc)
        
        return MessageResponse(
            success=True,
            message_id=result["message_id"],
            recipient=request.recipient_phone,
            message_type="template"
        )
    
    except Exception as e:
        logger.error(f"Failed to send template message: {str(e)}")
        return MessageResponse(
            success=False,
            recipient=request.recipient_phone,
            message_type="template",
            error=str(e)
        )


# ============== Message History ==============

@api_router.get("/messages", response_model=MessageListResponse, dependencies=[Depends(verify_api_key)])
async def get_messages(
    phone_number: Optional[str] = Query(None, description="Filter by phone number"),
    direction: Optional[str] = Query(None, description="Filter by direction (inbound/outbound)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Get message history with optional filters"""
    query = {}
    
    if phone_number:
        query["$or"] = [
            {"sender": phone_number},
            {"recipient": phone_number}
        ]
    
    if direction:
        query["direction"] = direction
    
    total = await db.messages.count_documents(query)
    messages = await db.messages.find(
        query, 
        {"_id": 0}
    ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    result = []
    for msg in messages:
        if isinstance(msg.get('created_at'), str):
            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
        if isinstance(msg.get('updated_at'), str):
            msg['updated_at'] = datetime.fromisoformat(msg['updated_at'])
        result.append(StoredMessage(**msg))
    
    return MessageListResponse(total=total, messages=result)


@api_router.get("/messages/{message_id}", response_model=StoredMessage, dependencies=[Depends(verify_api_key)])
async def get_message(message_id: str):
    """Get a specific message by ID"""
    msg = await db.messages.find_one({"id": message_id}, {"_id": 0})
    
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if isinstance(msg.get('created_at'), str):
        msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    if isinstance(msg.get('updated_at'), str):
        msg['updated_at'] = datetime.fromisoformat(msg['updated_at'])
    
    return StoredMessage(**msg)


# ============== Webhook Endpoints ==============

@webhook_router.get("/api/webhook/whatsapp")
async def verify_webhook(
    request: Request
):
    """
    Webhook verification endpoint for Meta WhatsApp
    
    Meta sends GET request with hub.mode, hub.challenge, hub.verify_token
    """
    params = dict(request.query_params)
    hub_mode = params.get("hub.mode")
    hub_challenge = params.get("hub.challenge")
    hub_verify_token = params.get("hub.verify_token")
    
    logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    if hub_mode != "subscribe":
        return Response(content="Invalid mode", status_code=403)
    
    # Check against default token
    if hub_verify_token == DEFAULT_WEBHOOK_VERIFY_TOKEN:
        logger.info("Webhook verified with default token")
        return Response(content=hub_challenge, status_code=200)
    
    # Check against number-specific tokens
    number = await db.whatsapp_numbers.find_one(
        {"webhook_verify_token": hub_verify_token, "is_active": True},
        {"_id": 0}
    )
    
    if number:
        logger.info(f"Webhook verified for number: {number['display_phone_number']}")
        return Response(content=hub_challenge, status_code=200)
    
    logger.warning("Webhook verification failed - invalid token")
    return Response(content="Invalid verify token", status_code=403)


@webhook_router.post("/api/webhook/whatsapp")
async def receive_webhook(request: Request):
    """
    Receive incoming webhook events from Meta WhatsApp
    
    Handles:
    - Incoming messages (text, image, document, video)
    - Message status updates (sent, delivered, read, failed)
    """
    try:
        body = await request.json()
        logger.info(f"Webhook received: {json.dumps(body, indent=2)}")
        
        if body.get("object") != "whatsapp_business_account":
            return Response(status_code=200)
        
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Get phone number ID from metadata
                phone_number_id = value.get("metadata", {}).get("phone_number_id")
                
                # Process incoming messages
                messages = value.get("messages", [])
                for message in messages:
                    await process_incoming_message(message, value, phone_number_id)
                
                # Process status updates
                statuses = value.get("statuses", [])
                for status in statuses:
                    await process_status_update(status)
        
        return Response(status_code=200)
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        # Always return 200 to prevent Meta from retrying
        return Response(status_code=200)


async def process_incoming_message(message: dict, metadata: dict, phone_number_id: str):
    """Process and store incoming message"""
    try:
        message_id = message.get("id")
        sender = message.get("from")
        message_type = message.get("type")
        timestamp = message.get("timestamp")
        
        # Get contact name
        contacts = metadata.get("contacts", [])
        contact_name = contacts[0].get("profile", {}).get("name") if contacts else None
        
        # Extract content based on message type
        content = None
        media_id = None
        
        if message_type == "text":
            content = message.get("text", {}).get("body")
        
        elif message_type == "image":
            image_data = message.get("image", {})
            media_id = image_data.get("id")
            content = image_data.get("caption")
        
        elif message_type == "document":
            doc_data = message.get("document", {})
            media_id = doc_data.get("id")
            content = doc_data.get("filename")
        
        elif message_type == "video":
            video_data = message.get("video", {})
            media_id = video_data.get("id")
            content = video_data.get("caption")
        
        elif message_type == "audio":
            audio_data = message.get("audio", {})
            media_id = audio_data.get("id")
        
        # Store message
        stored_message = StoredMessage(
            wa_message_id=message_id,
            phone_number_id=phone_number_id,
            sender=sender,
            message_type=message_type,
            direction="inbound",
            content=content,
            media_id=media_id,
            status="received",
            contact_name=contact_name
        )
        
        doc = stored_message.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        
        await db.messages.insert_one(doc)
        
        logger.info(f"Stored incoming {message_type} message from {sender}")
    
    except Exception as e:
        logger.error(f"Error processing incoming message: {str(e)}", exc_info=True)


async def process_status_update(status: dict):
    """Process message status update"""
    try:
        message_id = status.get("id")
        new_status = status.get("status")
        timestamp = status.get("timestamp")
        recipient = status.get("recipient_id")
        
        # Handle errors
        error_code = None
        error_message = None
        errors = status.get("errors", [])
        if errors:
            error_code = errors[0].get("code")
            error_message = errors[0].get("title")
        
        # Update message status in database
        update_data = {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if error_code:
            update_data["error_code"] = error_code
            update_data["error_message"] = error_message
        
        result = await db.messages.update_one(
            {"wa_message_id": message_id},
            {"$set": update_data}
        )
        
        if result.matched_count > 0:
            logger.info(f"Updated message {message_id} status to {new_status}")
        else:
            logger.warning(f"Message {message_id} not found for status update")
    
    except Exception as e:
        logger.error(f"Error processing status update: {str(e)}", exc_info=True)


# ============== Include Routers ==============

app.include_router(api_router)
app.include_router(webhook_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Startup/Shutdown ==============

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("WhatsApp Business API Service starting...")
    
    # Create indexes
    await db.messages.create_index("wa_message_id")
    await db.messages.create_index("sender")
    await db.messages.create_index("recipient")
    await db.messages.create_index("created_at")
    await db.whatsapp_numbers.create_index("phone_number_id", unique=True)
    await db.api_keys.create_index("key", unique=True)
    
    logger.info("Database indexes created")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("WhatsApp Business API Service shutting down...")
    client.close()
