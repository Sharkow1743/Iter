from requests import Response
from iter.request import fetch
from iter.models.responses import NotificationListResponse, NotificationCountResponse, StatusResponse
from uuid import UUID

def get_notifications(token: str, limit: int = 20, offset: int = 0, type: str | None = None) -> NotificationListResponse:
    data = {'limit': str(limit), 'cursor': str(offset)}
    if type:
        data['type'] = type
    return fetch(token, 'get', 'notifications', data, response_schema=NotificationListResponse)

def mark_as_read(token: str, id: UUID) -> Response:
    return fetch(token, 'post', f'notifications/{id}/read')

def mark_batch_as_read(token: str, ids: list[UUID]) -> Response:
    data = {'ids': ids}
    return fetch(token, 'post', 'notifications/read-batch', data)

def mark_all_as_read(token: str) ->Response:
    return fetch(token, 'post', 'notifications/read-all')

def get_unread_notifications_count(token: str) -> NotificationCountResponse:
    return fetch(token, 'get', 'notifications/count', response_schema=NotificationCountResponse)