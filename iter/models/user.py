from __future__ import annotations
from typing import Optional
from uuid import UUID
from iter.enums import AccessType
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

class UserPrivacyData:
    def __init__(self, private: bool | None = None, wall_access: AccessType | None = None, likes_visibility: AccessType | None = None, show_last_seen: bool | None = None) -> None:
        self.private = private
        self.wall_access = wall_access
        self.likes_visibility = likes_visibility
        self.show_last_seen = show_last_seen

    def to_dict(self):
        data = {}
        if self.private is not None:
            data['isPrivate'] = self.private
        if self.wall_access is not None:
            data['wallAccess'] = self.wall_access.value
        if self.likes_visibility is not None:
            data['likesVisibility'] = self.likes_visibility.value
        if self.show_last_seen is not None:
            data['showLastSeen'] = self.show_last_seen

        return data