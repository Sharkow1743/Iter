from __future__ import annotations
from typing import List, Optional, Annotated
from pydantic import BaseModel
from iter.types.user import User
from iter.types.media import Attachment
from pydantic import BeforeValidator
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

class Comment(BaseModel):
    id: str
    content: str
    author: User
    likesCount: int = 0
    repliesCount: int = 0
    isLiked: bool = False
    createdAt: PostgresDateTime
    attachments: List[Attachment] = []
    replies: List[Comment] = []

class Post(BaseModel):
    id: str
    content: str
    author: User
    attachments: List[Attachment] = []
    likesCount: int = 0
    commentsCount: int = 0
    repostsCount: int = 0
    viewsCount: int = 0
    createdAt: PostgresDateTime
    isLiked: bool = False
    isReposted: bool = False
    isOwner: bool = False
    isViewed: bool = False
    wallRecipientId: Optional[str] = None
    wallRecipient: Optional[User] = None
    originalPost: Optional[Post] = None
    comments: Optional[List[Comment]] = None

# Rebuild recursive models
Post.model_rebuild()
Comment.model_rebuild()