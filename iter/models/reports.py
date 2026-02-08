from uuid import UUID

from iter.enums import ReportTargetType, ReportTargetReason
from iter.models.base import IterBaseModel, PostgresDateTime


class NewReport(IterBaseModel):
    id: UUID
    created_at: PostgresDateTime


class Report(NewReport):
    reason: ReportTargetReason
    description: str | None = None

    target_type: ReportTargetType
    target_id: UUID
