"""
Automation Engine - Rule Evaluation and Execution
"""
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from automation_models import (
    AutomationRule, TriggerType, ActionType, 
    Condition, RuleAction, RuleExecutionLog, ScheduledTask
)
from whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class AutomationEngine:
    """
    Rule-based automation engine for WhatsApp CRM
    
    Evaluates triggers, conditions, and executes actions
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_active_rules(self, trigger_type: TriggerType) -> List[AutomationRule]:
        """Get all active rules for a specific trigger type, sorted by priority"""
        rules = await self.db.automation_rules.find(
            {"trigger_type": trigger_type.value, "is_active": True},
            {"_id": 0}
        ).sort("priority", -1).to_list(100)
        
        return [AutomationRule(**rule) for rule in rules]
    
    async def evaluate_conditions(self, conditions: List[Condition], context: Dict[str, Any]) -> bool:
        """
        Evaluate all conditions against the context
        All conditions must pass (AND logic)
        """
        if not conditions:
            return True
        
        for condition in conditions:
            if not self._evaluate_single_condition(condition, context):
                return False
        
        return True
    
    def _evaluate_single_condition(self, condition: Condition, context: Dict[str, Any]) -> bool:
        """Evaluate a single condition"""
        # Get the field value from context (supports nested fields like 'lead.status')
        field_parts = condition.field.split('.')
        value = context
        
        try:
            for part in field_parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = getattr(value, part, None)
        except Exception:
            value = None
        
        # Evaluate based on operator
        operator = condition.operator
        condition_value = condition.value
        
        if operator == "equals":
            return value == condition_value
        elif operator == "not_equals":
            return value != condition_value
        elif operator == "contains":
            return condition_value in str(value) if value else False
        elif operator == "not_contains":
            return condition_value not in str(value) if value else True
        elif operator == "greater_than":
            return float(value) > float(condition_value) if value else False
        elif operator == "less_than":
            return float(value) < float(condition_value) if value else False
        elif operator == "is_empty":
            return not value
        elif operator == "is_not_empty":
            return bool(value)
        
        return False
    
    async def execute_rule(
        self, 
        rule: AutomationRule, 
        context: Dict[str, Any],
        whatsapp_service: Optional[WhatsAppService] = None
    ) -> RuleExecutionLog:
        """
        Execute a rule's actions
        
        Args:
            rule: The rule to execute
            context: Context data (lead, message, etc.)
            whatsapp_service: WhatsApp service for sending messages
        
        Returns:
            Execution log
        """
        start_time = time.time()
        actions_executed = []
        success = True
        error_message = None
        
        try:
            for action in rule.actions:
                if action.delay_minutes > 0:
                    # Schedule delayed action
                    await self._schedule_action(rule, action, context)
                    actions_executed.append({
                        "action_type": action.action_type.value,
                        "status": "scheduled",
                        "delay_minutes": action.delay_minutes
                    })
                else:
                    # Execute immediately
                    result = await self._execute_action(action, context, whatsapp_service)
                    actions_executed.append({
                        "action_type": action.action_type.value,
                        "status": "executed",
                        "result": result
                    })
        
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Error executing rule {rule.name}: {e}", exc_info=True)
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Create execution log
        log = RuleExecutionLog(
            rule_id=rule.id,
            rule_name=rule.name,
            trigger_type=rule.trigger_type,
            trigger_data={
                "phone": context.get("phone"),
                "lead_id": context.get("lead", {}).get("id") if isinstance(context.get("lead"), dict) else None
            },
            actions_executed=actions_executed,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms
        )
        
        # Save log
        log_doc = log.model_dump()
        log_doc['created_at'] = log_doc['created_at'].isoformat()
        log_doc['trigger_type'] = log_doc['trigger_type'].value
        await self.db.automation_logs.insert_one(log_doc)
        
        # Update rule execution stats
        await self.db.automation_rules.update_one(
            {"id": rule.id},
            {
                "$inc": {"execution_count": 1},
                "$set": {"last_executed_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return log
    
    async def _execute_action(
        self, 
        action: RuleAction, 
        context: Dict[str, Any],
        whatsapp_service: Optional[WhatsAppService] = None
    ) -> Dict[str, Any]:
        """Execute a single action"""
        action_type = action.action_type
        config = action.config
        result = {"success": False}
        
        phone = context.get("phone")
        lead = context.get("lead", {})
        lead_id = lead.get("id") if isinstance(lead, dict) else None
        
        if action_type == ActionType.SEND_MESSAGE:
            if whatsapp_service and phone and config.message_text:
                try:
                    response = await whatsapp_service.send_text_message(phone, config.message_text)
                    result = {"success": True, "message_id": response.get("message_id")}
                except Exception as e:
                    result = {"success": False, "error": str(e)}
            else:
                result = {"success": False, "error": "Missing WhatsApp service or phone"}
        
        elif action_type == ActionType.SEND_TEMPLATE:
            if whatsapp_service and phone and config.template_name:
                try:
                    response = await whatsapp_service.send_template_message(
                        phone, 
                        config.template_name,
                        parameters=config.template_params
                    )
                    result = {"success": True, "message_id": response.get("message_id")}
                except Exception as e:
                    result = {"success": False, "error": str(e)}
        
        elif action_type == ActionType.ASSIGN_LEAD:
            if lead_id:
                agent_id = config.agent_id
                
                if config.assignment_strategy == "round_robin":
                    agent_id = await self._get_round_robin_agent()
                elif config.assignment_strategy == "least_leads":
                    agent_id = await self._get_least_leads_agent()
                
                if agent_id:
                    agent = await self.db.agents.find_one({"id": agent_id, "is_active": True}, {"_id": 0})
                    if agent:
                        await self.db.leads.update_one(
                            {"id": lead_id},
                            {"$set": {
                                "assigned_agent_id": agent_id,
                                "assigned_agent_name": agent["name"],
                                "updated_at": datetime.now(timezone.utc).isoformat()
                            }}
                        )
                        await self.db.agents.update_one({"id": agent_id}, {"$inc": {"leads_count": 1}})
                        result = {"success": True, "agent_id": agent_id, "agent_name": agent["name"]}
                    else:
                        result = {"success": False, "error": "Agent not found"}
                else:
                    result = {"success": False, "error": "No agent available"}
        
        elif action_type == ActionType.UPDATE_STATUS:
            if lead_id and config.new_status:
                status_entry = {
                    "status": config.new_status,
                    "changed_at": datetime.now(timezone.utc).isoformat(),
                    "notes": "Auto-updated by automation rule"
                }
                await self.db.leads.update_one(
                    {"id": lead_id},
                    {
                        "$set": {
                            "status": config.new_status,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        },
                        "$push": {"status_history": status_entry}
                    }
                )
                result = {"success": True, "new_status": config.new_status}
        
        elif action_type == ActionType.ADD_TAG:
            if lead_id and config.tag:
                await self.db.leads.update_one(
                    {"id": lead_id},
                    {
                        "$addToSet": {"tags": config.tag},
                        "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                    }
                )
                result = {"success": True, "tag": config.tag}
        
        return result
    
    async def _schedule_action(self, rule: AutomationRule, action: RuleAction, context: Dict[str, Any]):
        """Schedule a delayed action"""
        scheduled_at = datetime.now(timezone.utc) + timedelta(minutes=action.delay_minutes)
        
        task = ScheduledTask(
            rule_id=rule.id,
            action=action,
            target_phone=context.get("phone", ""),
            lead_id=context.get("lead", {}).get("id") if isinstance(context.get("lead"), dict) else None,
            scheduled_at=scheduled_at
        )
        
        task_doc = task.model_dump()
        task_doc['created_at'] = task_doc['created_at'].isoformat()
        task_doc['scheduled_at'] = task_doc['scheduled_at'].isoformat()
        task_doc['action']['action_type'] = task_doc['action']['action_type'].value
        
        await self.db.scheduled_tasks.insert_one(task_doc)
        logger.info(f"Scheduled action for {scheduled_at}: {action.action_type}")
    
    async def _get_round_robin_agent(self) -> Optional[str]:
        """Get next agent in round-robin order"""
        agents = await self.db.agents.find(
            {"is_active": True}, 
            {"_id": 0, "id": 1}
        ).sort("leads_count", 1).limit(1).to_list(1)
        
        return agents[0]["id"] if agents else None
    
    async def _get_least_leads_agent(self) -> Optional[str]:
        """Get agent with least leads"""
        agents = await self.db.agents.find(
            {"is_active": True},
            {"_id": 0, "id": 1}
        ).sort("leads_count", 1).limit(1).to_list(1)
        
        return agents[0]["id"] if agents else None
    
    async def process_trigger(
        self, 
        trigger_type: TriggerType, 
        context: Dict[str, Any],
        whatsapp_service: Optional[WhatsAppService] = None
    ) -> List[RuleExecutionLog]:
        """
        Process a trigger - find matching rules and execute them
        
        Args:
            trigger_type: Type of trigger
            context: Context data
            whatsapp_service: WhatsApp service for sending messages
        
        Returns:
            List of execution logs
        """
        logs = []
        
        # Get active rules for this trigger type
        rules = await self.get_active_rules(trigger_type)
        logger.info(f"Found {len(rules)} active rules for trigger {trigger_type}")
        
        for rule in rules:
            # Evaluate conditions
            if await self.evaluate_conditions(rule.conditions, context):
                logger.info(f"Executing rule: {rule.name}")
                log = await self.execute_rule(rule, context, whatsapp_service)
                logs.append(log)
            else:
                logger.debug(f"Rule {rule.name} conditions not met")
        
        return logs
    
    async def check_no_reply_leads(self, whatsapp_service: Optional[WhatsAppService] = None):
        """
        Check for leads without reply and trigger no_reply rules
        Called by scheduler
        """
        # Get no_reply rules
        rules = await self.get_active_rules(TriggerType.NO_REPLY)
        
        for rule in rules:
            hours = rule.trigger_config.hours if rule.trigger_config else 24
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            
            # Find leads with last message before cutoff
            leads = await self.db.leads.find({
                "last_message_at": {"$lt": cutoff_time.isoformat()},
                "status": {"$nin": ["converted", "lost"]}
            }, {"_id": 0}).to_list(100)
            
            for lead in leads:
                # Check if we already processed this lead recently
                recent_log = await self.db.automation_logs.find_one({
                    "rule_id": rule.id,
                    "trigger_data.lead_id": lead["id"],
                    "created_at": {"$gt": cutoff_time.isoformat()}
                })
                
                if not recent_log:
                    context = {
                        "phone": lead["phone"],
                        "lead": lead
                    }
                    
                    if await self.evaluate_conditions(rule.conditions, context):
                        await self.execute_rule(rule, context, whatsapp_service)
    
    async def execute_scheduled_tasks(self, whatsapp_service: Optional[WhatsAppService] = None):
        """
        Execute due scheduled tasks
        Called by scheduler
        """
        now = datetime.now(timezone.utc)
        
        # Find due tasks
        tasks = await self.db.scheduled_tasks.find({
            "executed": False,
            "scheduled_at": {"$lte": now.isoformat()}
        }, {"_id": 0}).to_list(100)
        
        for task_doc in tasks:
            try:
                # Reconstruct action
                action_dict = task_doc["action"]
                action_dict["action_type"] = ActionType(action_dict["action_type"])
                action = RuleAction(**action_dict)
                
                context = {
                    "phone": task_doc["target_phone"],
                    "lead": {"id": task_doc.get("lead_id")} if task_doc.get("lead_id") else {}
                }
                
                # Execute the action
                result = await self._execute_action(action, context, whatsapp_service)
                
                # Mark as executed
                await self.db.scheduled_tasks.update_one(
                    {"id": task_doc["id"]},
                    {"$set": {
                        "executed": True,
                        "executed_at": now.isoformat(),
                        "error": None if result.get("success") else result.get("error")
                    }}
                )
                
                logger.info(f"Executed scheduled task {task_doc['id']}")
            
            except Exception as e:
                logger.error(f"Error executing scheduled task: {e}")
                await self.db.scheduled_tasks.update_one(
                    {"id": task_doc["id"]},
                    {"$set": {
                        "executed": True,
                        "executed_at": now.isoformat(),
                        "error": str(e)
                    }}
                )
