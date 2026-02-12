from typing import Optional
from iter.models.base import IterBaseModel, PostgresDateTime
from uuid import UUID
from iter.enums import AttachType

class Attachment(IterBaseModel):
    id: UUID
    type: Optional[AttachType] = None
    url: str
    thumbnailUrl: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    filename: Optional[str] = None
    mimeType: Optional[str] = None
    size: Optional[int] = None
    created_at: Optional[PostgresDateTime] = None

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
    multiple_choice: bool
    total_votes: int
    has_voted: bool
    voted_option_ids: list[UUID]
    created_at: Optional[PostgresDateTime] = None

class NewPollOption(IterBaseModel):
    text: str
class NewPoll(IterBaseModel):
    question: Optional[str] = None
    options: list[NewPollOption]
    multiple_choice: bool

class PollData:
    def __init__(self, question: str, options: list[str], multiple: bool = False):
        self.poll = NewPoll(question=question, options=[NewPollOption(text=option) for option in options], multipleChoice=multiple)