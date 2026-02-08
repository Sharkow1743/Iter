from iter.models.pin import Pin, ShortPin
from iter.models.user import User, Clan
from iter.models.etc import Hashtag, CursorPagination, PagePagination
from iter.models.post import Post, Comment
from iter.models.notification import Notification
from iter.models.base import IterBaseModel, PostgresDateTime
from typing import List, Optional
from pydantic import Field
from uuid import UUID

class PostFeedResponse(IterBaseModel):
    posts: List[Post]
    pagination: CursorPagination

class HashtagFeedResponse(PostFeedResponse):
    hashtag: Hashtag

class UserListResponse(IterBaseModel):
    users: List[User]
    pagination: PagePagination

class SearchResponse(IterBaseModel):
    users: List[User] = Field(default_factory=list)
    hashtags: List[Hashtag] = Field(default_factory=list)

class CommentsResponse(IterBaseModel):
    comments: List[Comment]
    total: int
    has_more: bool
    next_cursor: Optional[int] = None

class WhoToFollowResponse(IterBaseModel):
    users: List[User]

class PostUpdateResponse(IterBaseModel):
    id: UUID
    content: str
    updated_at: PostgresDateTime

class LikeResponse(IterBaseModel):
    liked: bool
    likes_count: int

class FollowResponse(IterBaseModel):
    following: bool
    followers_count: int

class StatusResponse(IterBaseModel):
    success: bool = True

class PinResponse(IterBaseModel):
    success: bool
    pinned_post_id: Optional[str] = None

class ProfileUpdateResponse(IterBaseModel):
    id: UUID
    username: str
    display_name: str
    bio: Optional[str]
    updated_at: PostgresDateTime

class PrivacyUpdateResponse(IterBaseModel):
    is_private: bool
    wall_closed: bool

class NotificationListResponse(IterBaseModel):
    notifications: List[Notification]
    has_more: bool

class NotificationCountResponse(IterBaseModel):
    count: int

class PlatformStatusResponse(IterBaseModel):
    read_only: bool

class ClanListResponse(IterBaseModel):
    clans: List[Clan]
    
class SuccessResponse(IterBaseModel):
    success: bool = True

class RepliesResponse(IterBaseModel):
    replies: list[Comment]
    pagination: PagePagination

class PinsListResponse(IterBaseModel):
    pins: list[Pin]
    activePin: Optional[str]

class SetPinResponse(IterBaseModel):
    pin: ShortPin