from typing import Optional, Annotated
from pydantic import BaseModel, BeforeValidator
from datetime import datetime

def validate_datetime(v):
    if isinstance(v, str):
        # Fix +03 -> +03:00
        if "+" in v:
            parts = v.split("+")
            if len(parts[-1]) <= 2:
                v = f"{parts[0]}+{parts[-1].zfill(2)}:00"
        return v
    return v
PostgresDateTime = Annotated[datetime, BeforeValidator(validate_datetime)]

class NotificationActor(BaseModel):
    id: str
    displayName: str
    username: Optional[str] = None
    avatar: str

class Notification(BaseModel):
    id: str
    type: str # "like", "comment", "follow", "repost"
    targetType: Optional[str] = None
    targetId: Optional[str] = None
    preview: Optional[str] = None
    readAt: Optional[PostgresDateTime] = None
    createdAt: PostgresDateTime
    actor: NotificationActor
    read: bool