from uuid import UUID

from iter.models.base import IterBaseModel, PostgresDateTime

class Verification(IterBaseModel):
    id: UUID
    user_id: UUID
    video_url: str
    status: str # should be enum, but we dont know all statuses (what status for accepted?)

    reject_reason: str | None = None
    reviewer: str | None = None
    reviewed_at: PostgresDateTime | None = None

    created_at: PostgresDateTime
    updated_at: PostgresDateTime


class VerificationStatus(IterBaseModel):
    status: str # should be enum, but we dont know all statuses (what status for accepted?)
    request_id: UUID
    submitted_at: PostgresDateTime