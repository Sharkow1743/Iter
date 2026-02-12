from typing import Optional, Literal
from iter.enums import NotificationType
from iter.models.base import IterBaseModel, PostgresDateTime
from uuid import UUID

class NotificationActor(IterBaseModel):
    id: UUID
    displayName: str
    username: Optional[str] = None
    avatar: str

class Notification(IterBaseModel):
    id: UUID
    type: NotificationType
    targetType: Optional[str] = None
    targetId: Optional[str] = None
    preview: Optional[str] = None
    readAt: Optional[PostgresDateTime] = None
    createdAt: PostgresDateTime
    actor: NotificationActor
    read: bool