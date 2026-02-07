from __future__ import annotations
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
class User(BaseModel):
    id: Optional[str] = None
    username: Optional[str] = None
    displayName: str
    avatar: str
    verified: bool = False
    followersCount: Optional[int] = 0

class UserFull(User):
    banner: Optional[str] = None
    bio: Optional[str] = None
    pin: Optional[str] = None
    pinnedPostId: Optional[str] = None
    isPrivate: Optional[bool] = None
    wallClosed: Optional[bool] = None
    followingCount: int = 0
    postsCount: int = 0
    createdAt: PostgresDateTime
    isFollowing: Optional[bool] = None
    isFollowedBy: Optional[bool] = None

class Clan(BaseModel):
    avatar: str
    memberCount: int