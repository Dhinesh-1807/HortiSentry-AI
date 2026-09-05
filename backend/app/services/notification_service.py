import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.models import Notification
from app.core.constants import NotificationStatus

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        title: str,
        message: str,
        observation_id: Optional[str] = None
    ) -> Notification:
        try:
            notif = Notification(
                user_id=user_id,
                observation_id=observation_id,
                title=title,
                message=message,
                status=NotificationStatus.UNREAD,
                created_at=datetime.utcnow()
            )
            db.add(notif)
            db.commit()
            return notif
        except Exception as e:
            logger.error(f"Failed to create notification for user {user_id}: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.status == NotificationStatus.UNREAD)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def mark_as_read(db: Session, notification_id: str, user_id: str) -> Optional[Notification]:
        notif = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        if notif:
            notif.status = NotificationStatus.READ
            db.commit()
        return notif

    @staticmethod
    def mark_all_as_read(db: Session, user_id: str) -> int:
        updated = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.status == NotificationStatus.UNREAD
        ).update({"status": NotificationStatus.READ})
        db.commit()
        return updated
