from iter.request import fetch
from iter.models.responses import ReportResponse
from uuid import UUID

def report(token: str, id: UUID, type: str = 'post', reason: str = 'other', description: str = '') -> ReportResponse:
    return fetch(token, 'post', 'reports', {'targetId': id, 'targetType': type, 'reason': reason, 'description': description}, response_schema=ReportResponse)