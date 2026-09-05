import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    @staticmethod
    def record(
        db: Session,
        action: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Records an audit log entry for security and regulatory traceability.
        """
        try:
            log_entry = AuditLog(
                user_id=user_id,
                user_email=user_email,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details or {},
                timestamp=datetime.utcnow()
            )
            db.add(log_entry)
            db.commit()
            return log_entry
        except Exception as e:
            logger.error(f"Failed to write audit log for action '{action}': {e}")
            db.rollback()
            return None
