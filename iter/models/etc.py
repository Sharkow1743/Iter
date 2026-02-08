from typing import Optional
from iter.models.base import IterBaseModel

class Hashtag(IterBaseModel):
    id: str
    name: str
    postsCount: int

class CursorPagination(IterBaseModel):
    limit: int
    nextCursor: Optional[str] = None
    hasMore: bool

class PagePagination(IterBaseModel):
    page: int
    limit: int
    total: int
    hasMore: bool