"""
Workflow Scheduler using APScheduler for recurring workflow execution.
"""
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from sqlalchemy.orm import Session

from app.database import get_db


class WorkflowScheduler:
    """
    Manages scheduled workflow execution using APScheduler.
    """
    
    def __init__(self):
        """Initialize the scheduler with memory job store."""
        jobstores = {
            'default': MemoryJobStore()
        }
        self.scheduler = AsyncIOScheduler(jobstores=jobstores)
        self.scheduler.start()
    
    def schedule_workflow(
        self,
        workflow_id: UUID,
        cron_schedule: str,
        orchestrator_factory,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Schedule a workflow to run on a cron schedule.
        
        Args:
            workflow_id: UUID of the workflow to schedule
            cron_schedule: Cron expression (e.g., "0 9 * * *" for daily at 9am)
            orchestrator_factory: Factory function to create orchestrator instance
            context: Optional context to pass to workflow execution
            
        Returns:
            Job ID for the scheduled workflow
        """
        # Parse cron expression
        trigger = CronTrigger.from_crontab(cron_schedule)
        
        # Create job ID
        job_id = f"workflow_{workflow_id}"
        
        # Schedule the job
        self.scheduler.add_job(
            func=self._execute_workflow_job,
            trigger=trigger,
            args=[workflow_id, orchestrator_factory, context],
            id=job_id,
            replace_existing=True,
            name=f"Workflow {workflow_id}"
        )
        
        return job_id
    
    async def _execute_workflow_job(
        self,
        workflow_id: UUID,
        orchestrator_factory,
        context: Optional[Dict[str, Any]]
    ):
        """
        Execute a scheduled workflow.
        
        Args:
            workflow_id: UUID of the workflow to execute
            orchestrator_factory: Factory function to create orchestrator instance
            context: Optional context to pass to workflow execution
        """
        try:
            # Create orchestrator instance with database session
            db = next(get_db())
            orchestrator = orchestrator_factory(db)
            
            # Execute the workflow
            await orchestrator.executeWorkflow(workflow_id, context)
            
        except Exception as e:
            print(f"Error executing scheduled workflow {workflow_id}: {str(e)}")
        finally:
            if db:
                db.close()
    
    def cancel_workflow(self, workflow_id: UUID) -> bool:
        """
        Cancel a scheduled workflow.
        
        Args:
            workflow_id: UUID of the workflow to cancel
            
        Returns:
            True if job was cancelled, False if not found
        """
        job_id = f"workflow_{workflow_id}"
        
        try:
            self.scheduler.remove_job(job_id)
            return True
        except Exception:
            return False
    
    def get_scheduled_jobs(self) -> Dict[str, Any]:
        """
        Get all scheduled jobs.
        
        Returns:
            Dictionary of job information
        """
        jobs = self.scheduler.get_jobs()
        return {
            job.id: {
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            }
            for job in jobs
        }
    
    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> WorkflowScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = WorkflowScheduler()
    return _scheduler_instance
