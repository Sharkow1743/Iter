from typing import Optional
from iter.models.base import IterBaseModel
from uuid import UUID

class Hashtag(IterBaseModel):
    id: UUID
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

class Pagination(IterBaseModel):
    page: int | None = 1
    limit: int = 20
    total: int | None = None
    has_more: bool = True
    next_cursor: UUID | None = None