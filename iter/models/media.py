from typing import Optional
from iter.models.base import IterBaseModel, PostgresDateTime
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

class PollOption(IterBaseModel):
    id: UUID
    text: str
    position: int
    votes_count: int
class Poll(IterBaseModel):
    id: UUID
    post_id: UUID
    question: Optional[str] = None
    options: list[PollOption]
    multiple_choise: bool
    total_votes: int
    has_voted: bool
    voted_option_ids: list[UUID]
    created_at: Optional[PostgresDateTime] = None

class NewPollOption(IterBaseModel):
    text: str
class NewPoll(IterBaseModel):
    question: Optional[str] = None
    options: list[NewPollOption]
    multiple_choise: bool