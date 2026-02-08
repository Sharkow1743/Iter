from typing import Optional
from iter.models.base import IterBaseModel
from uuid import UUID

class Attachment(IterBaseModel):
    id: UUID
    type: Optional[str] = None  # "image" or "video"
    url: str
    thumbnailUrl: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    filename: Optional[str] = None
    mimeType: Optional[str] = None
    size: Optional[int] = None