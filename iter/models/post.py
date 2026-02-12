from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from iter.models.base import IterBaseModel, PostgresDateTime
from iter.models.user import User
from iter.models.media import Attachment, Poll

class Comment(IterBaseModel):
    id: UUID
    content: str
    author: User
    likes_count: int = 0
    replies_count: int = 0
    is_liked: bool = False
    created_at: PostgresDateTime
    attachments: List[Attachment] = []
    replies: List[Comment] = []

class Post(IterBaseModel):
    id: UUID
    content: str
    author: User
    attachments: List[Attachment] = []
    likes_count: int = 0
    comments_count: int = 0
    reposts_count: int = 0
    views_count: int = 0
    created_at: PostgresDateTime
    is_liked: bool = False
    is_reposted: bool = False
    is_owner: bool = False
    is_viewed: bool = False
    wall_recipient_id: Optional[str] = None
    wall_recipient: Optional[User] = None
    original_post: Optional[Post] = None
    comments: Optional[List[Comment]] = None
    poll: Optional[Poll] = None

Post.model_rebuild()
Comment.model_rebuild()