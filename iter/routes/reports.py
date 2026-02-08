from iter.request import fetch
from iter.models.responses import ReportResponse

def report(token: str, id: str, type: str = 'post', reason: str = 'other', description: str = '') -> ReportResponse:
    return fetch(token, 'post', 'reports', {'targetId': id, 'targetType': type, 'reason': reason, 'description': description}, response_schema=ReportResponse)