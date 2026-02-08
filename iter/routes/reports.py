from iter.models.base import Error
from iter.request import fetch
from iter.models.reports import NewReport
from uuid import UUID

def report(token: str, id: UUID, type: str = 'post', reason: str = 'other', description: str = '') -> NewReport | Error:
    return fetch(token, 'post', 'reports', {'targetId': str(id), 'targetType': type, 'reason': reason, 'description': description}, response_schema=NewReport)