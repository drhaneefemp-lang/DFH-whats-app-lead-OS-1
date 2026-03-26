"""
Scheduler for Automation Engine using APScheduler
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional

from automation_engine import AutomationEngine
from automation_models import TriggerType
from whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class AutomationScheduler:
    """
    Scheduler for running automation tasks
    
    - Checks for no-reply leads periodically
    - Executes delayed/scheduled actions
    - Runs cron-based rules
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.engine = AutomationEngine(db)
        self.scheduler = AsyncIOScheduler()
        self.whatsapp_service: Optional[WhatsAppService] = None
        self._started = False
    
    def set_whatsapp_service(self, service: WhatsAppService):
        """Set WhatsApp service for sending messages"""
        self.whatsapp_service = service
    
    async def _get_whatsapp_service(self) -> Optional[WhatsAppService]:
        """Get a WhatsApp service instance"""
        if self.whatsapp_service:
            return self.whatsapp_service
        
        # Try to get default WhatsApp number
        number = await self.db.whatsapp_numbers.find_one(
            {"is_active": True}, 
            {"_id": 0}
        )
        
        if number:
            return WhatsAppService(
                phone_number_id=number["phone_number_id"],
                access_token=number["access_token"]
            )
        
        return None
    
    async def check_no_reply_job(self):
        """Job to check for leads without reply"""
        logger.info("Running no-reply check job")
        try:
            service = await self._get_whatsapp_service()
            await self.engine.check_no_reply_leads(service)
        except Exception as e:
            logger.error(f"Error in no-reply check job: {e}", exc_info=True)
    
    async def execute_scheduled_tasks_job(self):
        """Job to execute scheduled tasks"""
        logger.debug("Running scheduled tasks job")
        try:
            service = await self._get_whatsapp_service()
            await self.engine.execute_scheduled_tasks(service)
        except Exception as e:
            logger.error(f"Error in scheduled tasks job: {e}", exc_info=True)
    
    async def run_cron_rules_job(self):
        """Job to check and run cron-based rules"""
        logger.info("Running cron rules check")
        try:
            rules = await self.engine.get_active_rules(TriggerType.SCHEDULED)
            service = await self._get_whatsapp_service()
            
            for rule in rules:
                # For scheduled rules, we run them for all active leads
                # that match the conditions
                leads = await self.db.leads.find(
                    {"status": {"$nin": ["converted", "lost"]}},
                    {"_id": 0}
                ).to_list(500)
                
                for lead in leads:
                    context = {
                        "phone": lead["phone"],
                        "lead": lead
                    }
                    
                    if await self.engine.evaluate_conditions(rule.conditions, context):
                        await self.engine.execute_rule(rule, context, service)
        
        except Exception as e:
            logger.error(f"Error in cron rules job: {e}", exc_info=True)
    
    def start(self):
        """Start the scheduler"""
        if self._started:
            return
        
        # Check no-reply leads every hour
        self.scheduler.add_job(
            self.check_no_reply_job,
            IntervalTrigger(hours=1),
            id='check_no_reply',
            name='Check No Reply Leads',
            replace_existing=True
        )
        
        # Execute scheduled tasks every minute
        self.scheduler.add_job(
            self.execute_scheduled_tasks_job,
            IntervalTrigger(minutes=1),
            id='execute_scheduled_tasks',
            name='Execute Scheduled Tasks',
            replace_existing=True
        )
        
        # Run cron rules every hour (rules have their own cron expressions)
        self.scheduler.add_job(
            self.run_cron_rules_job,
            IntervalTrigger(hours=1),
            id='run_cron_rules',
            name='Run Cron Rules',
            replace_existing=True
        )
        
        self.scheduler.start()
        self._started = True
        logger.info("Automation scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self._started:
            self.scheduler.shutdown()
            self._started = False
            logger.info("Automation scheduler stopped")
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in self.scheduler.get_jobs()
        ]


# Global scheduler instance
_scheduler: Optional[AutomationScheduler] = None


def get_scheduler(db: AsyncIOMotorDatabase) -> AutomationScheduler:
    """Get or create the global scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = AutomationScheduler(db)
    return _scheduler
