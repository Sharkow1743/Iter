from __future__ import annotations
from typing import Optional
from uuid import UUID
from iter.models.base import IterBaseModel, PostgresDateTime
from iter.models.pin import ShortPin

class User(IterBaseModel):
    id: Optional[str] = None
    username: Optional[str] = None
    display_name: str
    avatar: str
    verified: bool = False
    followers_count: Optional[int] = 0

class UserFull(User):
    banner: Optional[str] = None
    bio: Optional[str] = None
    pin: Optional[ShortPin] = None
    pinned_post_id: Optional[UUID] = None
    is_private: Optional[bool] = None
    wall_closed: Optional[bool] = None
    following_count: int = 0
    posts_count: int = 0
    created_at: PostgresDateTime
    is_following: Optional[bool] = None
    is_followed_by: Optional[bool] = None
    online: bool
    lastSeen: Optional[PostgresDateTime] = None

class Clan(IterBaseModel):
    avatar: str
    member_count: int