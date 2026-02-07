from iter.request import fetch
from iter.types.responses import GetNotifications, GetNotificationCount, MarkAsReadResponse, MarkBatchAsReadResponse

def get_notifications(token: str, limit: int = 20, offset: int = 0, type: str | None = None) -> GetNotifications:
    data = {'limit': str(limit), 'cursor': str(offset)}
    if type:
        data['type'] = type
    return fetch(token, 'get', 'notifications', data, response_schema=GetNotifications)

def mark_as_read(token: str, id: str) -> MarkAsReadResponse:
    return fetch(token, 'post', f'notifications/{id}/read', response_schema=MarkAsReadResponse)

def mark_batch_as_read(token: str, ids: list[str]) -> MarkBatchAsReadResponse:
    data = {'ids': ids}
    return fetch(token, 'post', 'notifications/read-batch', data, response_schema=MarkBatchAsReadResponse)

def get_unread_notifications_count(token: str) -> GetNotificationCount:
    return fetch(token, 'get', 'notifications/count', response_schema=GetNotificationCount)