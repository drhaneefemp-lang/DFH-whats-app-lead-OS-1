"""
Pydantic models for WhatsApp Business API service and CRM
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


# ============== CRM Enums ==============

class LeadStatus(str, Enum):
    """Lead status stages"""
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(str, Enum):
    """Lead source channels"""
    WHATSAPP = "whatsapp"
    MANUAL = "manual"
    WEBSITE = "website"
    REFERRAL = "referral"
    OTHER = "other"


# ============== Agent Models ==============

class AgentCreate(BaseModel):
    """Request model for creating an agent"""
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., description="Agent email address")
    phone: Optional[str] = Field(None, description="Agent phone number")
    department: str = Field(default="sales", description="Agent department")
    is_active: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Smith",
                "email": "john.smith@company.com",
                "phone": "+15551234567",
                "department": "sales"
            }
        }


class AgentUpdate(BaseModel):
    """Request model for updating an agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class Agent(BaseModel):
    """Agent stored in database"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    department: str = "sales"
    is_active: bool = True
    leads_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentResponse(BaseModel):
    """Response model for agent"""
    id: str
    name: str
    email: str
    phone: Optional[str]
    department: str
    is_active: bool
    leads_count: int
    created_at: datetime
    updated_at: datetime


class AgentListResponse(BaseModel):
    """Response for agent list"""
    total: int
    agents: List[AgentResponse]


# ============== Lead Models ==============

class LeadCreate(BaseModel):
    """Request model for creating a lead manually"""
    name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., description="Lead phone number")
    email: Optional[str] = None
    source: LeadSource = Field(default=LeadSource.MANUAL)
    status: LeadStatus = Field(default=LeadStatus.NEW)
    assigned_agent_id: Optional[str] = Field(None, description="Agent ID to assign")
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "phone": "+15559876543",
                "email": "jane@example.com",
                "source": "manual",
                "notes": "Interested in premium plan"
            }
        }


class LeadUpdate(BaseModel):
    """Request model for updating a lead"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = None
    status: Optional[LeadStatus] = None
    assigned_agent_id: Optional[str] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class LeadAssign(BaseModel):
    """Request model for assigning lead to agent"""
    agent_id: str = Field(..., description="Agent ID to assign")


class LeadStatusUpdate(BaseModel):
    """Request model for updating lead status"""
    status: LeadStatus = Field(..., description="New status")
    notes: Optional[str] = Field(None, description="Status change notes")


class Lead(BaseModel):
    """Lead stored in database"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: Optional[str] = None
    source: LeadSource = LeadSource.WHATSAPP
    status: LeadStatus = LeadStatus.NEW
    assigned_agent_id: Optional[str] = None
    assigned_agent_name: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    first_message: Optional[str] = None
    message_count: int = 0
    last_message_at: Optional[datetime] = None
    status_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LeadResponse(BaseModel):
    """Response model for lead"""
    id: str
    name: str
    phone: str
    email: Optional[str]
    source: LeadSource
    status: LeadStatus
    assigned_agent_id: Optional[str]
    assigned_agent_name: Optional[str]
    notes: Optional[str]
    tags: List[str]
    first_message: Optional[str]
    message_count: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    """Response for lead list"""
    total: int
    leads: List[LeadResponse]


class LeadStats(BaseModel):
    """Lead statistics"""
    total_leads: int
    by_status: Dict[str, int]
    by_source: Dict[str, int]
    unassigned_count: int


# ============== WhatsApp Number Models ==============

class WhatsAppNumberCreate(BaseModel):
    """Request model for connecting a new WhatsApp number"""
    phone_number_id: str = Field(..., description="Meta Phone Number ID")
    display_phone_number: str = Field(..., description="Display phone number (e.g., +1234567890)")
    access_token: str = Field(..., description="WhatsApp Cloud API access token")
    department: str = Field(default="default", description="Department/category for this number")
    webhook_verify_token: Optional[str] = Field(None, description="Custom webhook verify token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number_id": "123456789012345",
                "display_phone_number": "+15551234567",
                "access_token": "EAAx...",
                "department": "customer_support",
                "webhook_verify_token": "my_secure_token"
            }
        }


class WhatsAppNumber(BaseModel):
    """WhatsApp number stored in database"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phone_number_id: str
    display_phone_number: str
    access_token: str
    department: str = "default"
    webhook_verify_token: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WhatsAppNumberResponse(BaseModel):
    """Response model for WhatsApp number (excludes sensitive data)"""
    id: str
    phone_number_id: str
    display_phone_number: str
    department: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ============== Message Models ==============

class TextMessageRequest(BaseModel):
    """Request model for sending text message"""
    recipient_phone: str = Field(..., description="Recipient phone number in international format")
    message_text: str = Field(..., max_length=4096, description="Message content")
    phone_number_id: Optional[str] = Field(None, description="Specific WhatsApp number to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipient_phone": "15551234567",
                "message_text": "Hello from WhatsApp Business API!"
            }
        }


class ImageMessageRequest(BaseModel):
    """Request model for sending image message"""
    recipient_phone: str
    image_url: str = Field(..., description="URL of the image or media ID")
    caption: Optional[str] = Field(None, max_length=1024)
    use_media_id: bool = Field(default=False, description="If True, image_url is treated as media ID")
    phone_number_id: Optional[str] = None


class DocumentMessageRequest(BaseModel):
    """Request model for sending document message"""
    recipient_phone: str
    document_url: str = Field(..., description="URL of the document or media ID")
    filename: str = Field(..., description="Filename to display")
    use_media_id: bool = False
    phone_number_id: Optional[str] = None


class VideoMessageRequest(BaseModel):
    """Request model for sending video message"""
    recipient_phone: str
    video_url: str = Field(..., description="URL of the video or media ID")
    caption: Optional[str] = Field(None, max_length=1024)
    use_media_id: bool = False
    phone_number_id: Optional[str] = None


class TemplateMessageRequest(BaseModel):
    """Request model for sending template message"""
    recipient_phone: str
    template_name: str
    language_code: str = "en_US"
    parameters: Optional[List[str]] = None
    phone_number_id: Optional[str] = None


class MessageResponse(BaseModel):
    """Response model for sent messages"""
    success: bool
    message_id: Optional[str] = None
    recipient: str
    message_type: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None


# ============== Stored Message Model ==============

class StoredMessage(BaseModel):
    """Message stored in database"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wa_message_id: str = Field(..., description="WhatsApp message ID")
    phone_number_id: str = Field(..., description="WhatsApp number that sent/received")
    sender: str = Field(..., description="Sender phone number")
    recipient: Optional[str] = Field(None, description="Recipient (for outbound messages)")
    message_type: str = Field(..., description="text, image, document, video, template")
    direction: str = Field(..., description="inbound or outbound")
    content: Optional[str] = Field(None, description="Message content or media URL")
    media_id: Optional[str] = Field(None, description="Media ID for media messages")
    status: str = Field(default="received", description="received, sent, delivered, read, failed")
    contact_name: Optional[str] = Field(None, description="Contact profile name")
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MessageListResponse(BaseModel):
    """Response model for message list"""
    total: int
    messages: List[StoredMessage]


# ============== Webhook Models ==============

class WebhookPayload(BaseModel):
    """Incoming webhook payload from Meta"""
    object: str
    entry: List[Dict[str, Any]]


# ============== API Key Models ==============

class APIKeyCreate(BaseModel):
    """Request model for creating API key"""
    name: str = Field(..., description="Name/description for the API key")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Production API Key"
            }
        }


class APIKey(BaseModel):
    """API key stored in database"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    key: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: Optional[datetime] = None


class APIKeyResponse(BaseModel):
    """Response model for API key (shows key only on creation)"""
    id: str
    name: str
    key: Optional[str] = None  # Only shown on creation
    is_active: bool
    created_at: datetime


# ============== Health Check Models ==============

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    connected_numbers: int = 0
    database: str = "connected"
