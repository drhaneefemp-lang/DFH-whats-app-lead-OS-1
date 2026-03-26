"""
Automation Engine Models for Rule-Based Triggers and Actions
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timezone
from enum import Enum
import uuid


# ============== Trigger Types ==============

class TriggerType(str, Enum):
    """Types of triggers that can activate a rule"""
    NEW_MESSAGE = "new_message"          # When a new inbound message arrives
    NEW_LEAD = "new_lead"                # When a new lead is created
    NO_REPLY = "no_reply"                # No reply within X hours
    LEAD_STATUS_CHANGE = "lead_status_change"  # When lead status changes
    SCHEDULED = "scheduled"              # Cron-based schedule


class ActionType(str, Enum):
    """Types of actions a rule can perform"""
    SEND_MESSAGE = "send_message"        # Send a WhatsApp message
    ASSIGN_LEAD = "assign_lead"          # Assign lead to an agent
    UPDATE_STATUS = "update_status"      # Update lead status
    ADD_TAG = "add_tag"                  # Add tag to lead
    SEND_TEMPLATE = "send_template"      # Send template message


# ============== Condition Models ==============

class Condition(BaseModel):
    """A single condition for rule evaluation"""
    field: str = Field(..., description="Field to evaluate (e.g., 'lead.status', 'message.content')")
    operator: Literal["equals", "not_equals", "contains", "not_contains", "greater_than", "less_than", "is_empty", "is_not_empty"] = "equals"
    value: Optional[Any] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "lead.status",
                "operator": "equals",
                "value": "new"
            }
        }


# ============== Trigger Configuration ==============

class TriggerConfig(BaseModel):
    """Configuration for different trigger types"""
    # For NO_REPLY trigger
    hours: Optional[int] = Field(None, description="Hours without reply (for no_reply trigger)")
    
    # For SCHEDULED trigger
    cron_expression: Optional[str] = Field(None, description="Cron expression (e.g., '0 9 * * *' for 9 AM daily)")
    
    # For LEAD_STATUS_CHANGE trigger
    from_status: Optional[str] = Field(None, description="Previous status")
    to_status: Optional[str] = Field(None, description="New status")


# ============== Action Configuration ==============

class ActionConfig(BaseModel):
    """Configuration for different action types"""
    # For SEND_MESSAGE action
    message_text: Optional[str] = Field(None, description="Message to send")
    
    # For SEND_TEMPLATE action
    template_name: Optional[str] = Field(None, description="Template name")
    template_params: Optional[List[str]] = Field(None, description="Template parameters")
    
    # For ASSIGN_LEAD action
    agent_id: Optional[str] = Field(None, description="Specific agent ID")
    assignment_strategy: Optional[Literal["specific", "round_robin", "least_leads"]] = Field("specific", description="Assignment strategy")
    
    # For UPDATE_STATUS action
    new_status: Optional[str] = Field(None, description="New status to set")
    
    # For ADD_TAG action
    tag: Optional[str] = Field(None, description="Tag to add")


# ============== Rule Action ==============

class RuleAction(BaseModel):
    """An action to be performed when rule triggers"""
    action_type: ActionType
    config: ActionConfig
    delay_minutes: int = Field(default=0, description="Delay before executing action (in minutes)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "action_type": "send_message",
                "config": {
                    "message_text": "Welcome! How can we help you today?"
                },
                "delay_minutes": 0
            }
        }


# ============== Automation Rule ==============

class AutomationRuleCreate(BaseModel):
    """Request model for creating an automation rule"""
    name: str = Field(..., min_length=1, max_length=200, description="Rule name")
    description: Optional[str] = Field(None, description="Rule description")
    trigger_type: TriggerType
    trigger_config: Optional[TriggerConfig] = None
    conditions: List[Condition] = Field(default_factory=list, description="Additional conditions")
    actions: List[RuleAction] = Field(..., min_length=1, description="Actions to perform")
    is_active: bool = Field(default=True)
    priority: int = Field(default=0, description="Higher priority rules execute first")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Welcome New Leads",
                "description": "Send welcome message to new leads",
                "trigger_type": "new_lead",
                "conditions": [],
                "actions": [{
                    "action_type": "send_message",
                    "config": {"message_text": "Welcome! Thanks for reaching out."},
                    "delay_minutes": 0
                }],
                "is_active": True
            }
        }


class AutomationRuleUpdate(BaseModel):
    """Request model for updating an automation rule"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    trigger_type: Optional[TriggerType] = None
    trigger_config: Optional[TriggerConfig] = None
    conditions: Optional[List[Condition]] = None
    actions: Optional[List[RuleAction]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class AutomationRule(BaseModel):
    """Automation rule stored in database"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    trigger_type: TriggerType
    trigger_config: Optional[TriggerConfig] = None
    conditions: List[Condition] = Field(default_factory=list)
    actions: List[RuleAction]
    is_active: bool = True
    priority: int = 0
    execution_count: int = 0
    last_executed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutomationRuleResponse(BaseModel):
    """Response model for automation rule"""
    id: str
    name: str
    description: Optional[str]
    trigger_type: TriggerType
    trigger_config: Optional[TriggerConfig]
    conditions: List[Condition]
    actions: List[RuleAction]
    is_active: bool
    priority: int
    execution_count: int
    last_executed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class AutomationRuleListResponse(BaseModel):
    """Response for rule list"""
    total: int
    rules: List[AutomationRuleResponse]


# ============== Execution Log ==============

class RuleExecutionLog(BaseModel):
    """Log entry for rule execution"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    rule_name: str
    trigger_type: TriggerType
    trigger_data: Dict[str, Any] = Field(default_factory=dict)
    actions_executed: List[Dict[str, Any]] = Field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None
    execution_time_ms: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExecutionLogResponse(BaseModel):
    """Response for execution log"""
    id: str
    rule_id: str
    rule_name: str
    trigger_type: TriggerType
    trigger_data: Dict[str, Any]
    actions_executed: List[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    execution_time_ms: int
    created_at: datetime


class ExecutionLogListResponse(BaseModel):
    """Response for execution log list"""
    total: int
    logs: List[ExecutionLogResponse]


# ============== Scheduled Task ==============

class ScheduledTask(BaseModel):
    """A scheduled task for delayed actions"""
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    action: RuleAction
    target_phone: str
    lead_id: Optional[str] = None
    scheduled_at: datetime
    executed: bool = False
    executed_at: Optional[datetime] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
