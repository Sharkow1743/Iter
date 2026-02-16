from typing import Optional
from iter.models.base import IterBaseModel
from iter.enums import SpanType

class Span(IterBaseModel):
    type: SpanType
    length: int
    offset: int
    tag: Optional[str] = None