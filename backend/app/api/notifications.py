from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.auth_service import get_current_user
from app.services.notification_service import NotificationService
from app.models.models import User

router = APIRouter(prefix="/notifications", tags=["In-App Notifications"])

@router.get("", summary="Get Current User Notifications")
def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notifs = NotificationService.get_user_notifications(
        db=db, user_id=current_user.id, limit=limit, unread_only=unread_only
    )
    unread_count = len([n for n in notifs if n.status == "UNREAD"])
    return {
        "unread_count": unread_count,
        "items": [
            {
                "id": n.id,
                "observation_id": n.observation_id,
                "title": n.title,
                "message": n.message,
                "status": n.status,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notifs
        ]
    }

@router.patch("/{notification_id}/read", summary="Mark Notification as Read")
def mark_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = NotificationService.mark_as_read(db=db, notification_id=notification_id, user_id=current_user.id)
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"status": "success", "id": notification_id}

@router.post("/read-all", summary="Mark All Notifications as Read")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = NotificationService.mark_all_as_read(db=db, user_id=current_user.id)
    return {"status": "success", "marked_read_count": count}
