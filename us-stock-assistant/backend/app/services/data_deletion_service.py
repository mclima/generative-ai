"""
Data Deletion Service for processing scheduled account deletions.
Runs as a background task to delete accounts after the 30-day grace period.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
import asyncio
from typing import List

from app.database import SessionLocal
from app.models import User, DataDeletionRequest
from app.logging_config import get_logger
from app.audit import log_action

logger = get_logger(__name__)


class DataDeletionService:
    """
    Service for processing scheduled data deletions.
    Runs periodically to check for and execute pending deletions.
    """
    
    def __init__(self):
        self.is_running = False
        self.task = None
    
    async def start(self):
        """Start the data deletion service."""
        if self.is_running:
            logger.warning("Data deletion service is already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._run_deletion_loop())
        logger.info("Data deletion service started")
    
    async def stop(self):
        """Stop the data deletion service."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Data deletion service stopped")
    
    async def _run_deletion_loop(self):
        """
        Main loop that checks for and processes deletions.
        Runs every hour.
        """
        while self.is_running:
            try:
                await self.process_pending_deletions()
            except Exception as e:
                logger.error(f"Error in deletion loop: {str(e)}", exc_info=True)
            
            # Wait 1 hour before next check
            await asyncio.sleep(3600)
    
    async def process_pending_deletions(self):
        """
        Process all pending deletions that have reached their scheduled date.
        """
        db = SessionLocal()
        try:
            # Find all pending deletions that are due
            now = datetime.utcnow()
            pending_deletions = db.query(DataDeletionRequest).filter(
                and_(
                    DataDeletionRequest.status == "pending",
                    DataDeletionRequest.scheduled_deletion_date <= now
                )
            ).all()
            
            if not pending_deletions:
                logger.debug("No pending deletions to process")
                return
            
            logger.info(f"Processing {len(pending_deletions)} pending deletions")
            
            for deletion_request in pending_deletions:
                try:
                    await self._delete_user_data(db, deletion_request)
                except Exception as e:
                    logger.error(
                        f"Failed to delete user {deletion_request.user_email}: {str(e)}",
                        exc_info=True
                    )
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Error processing deletions: {str(e)}", exc_info=True)
            db.rollback()
        finally:
            db.close()
    
    async def _delete_user_data(self, db: Session, deletion_request: DataDeletionRequest):
        """
        Delete all data for a user.
        
        Args:
            db: Database session
            deletion_request: The deletion request to process
        """
        user_id = deletion_request.user_id
        user_email = deletion_request.user_email
        
        if not user_id:
            logger.warning(f"User ID not found for deletion request {deletion_request.id}")
            deletion_request.status = "completed"
            deletion_request.completed_at = datetime.utcnow()
            return
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"User {user_email} not found, marking deletion as completed")
            deletion_request.status = "completed"
            deletion_request.completed_at = datetime.utcnow()
            return
        
        # Log audit event before deletion
        log_action(
            db=db,
            user_id=user_id,
            action="DELETE_USER_DATA",
            resource_type="user_account",
            resource_id=str(user_id),
            details={
                "email": user_email,
                "deletion_date": datetime.utcnow().isoformat()
            },
            ip_address=None
        )
        
        # Delete user (cascade will delete all related data)
        # The database foreign keys are set up with CASCADE delete
        db.delete(user)
        
        # Mark deletion as completed
        deletion_request.status = "completed"
        deletion_request.completed_at = datetime.utcnow()
        
        logger.info(f"Successfully deleted user data for {user_email}")


# Singleton instance
_data_deletion_service = None


def get_data_deletion_service() -> DataDeletionService:
    """Get the singleton data deletion service instance."""
    global _data_deletion_service
    if _data_deletion_service is None:
        _data_deletion_service = DataDeletionService()
    return _data_deletion_service
