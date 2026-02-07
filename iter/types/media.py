from typing import Optional
from pydantic import BaseModel

class Attachment(BaseModel):
    id: str
    type: Optional[str] = None  # "image" or "video"
    url: str
    thumbnailUrl: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    filename: Optional[str] = None
    mimeType: Optional[str] = None
    size: Optional[int] = None