from iter.request import fetch

def get_notifications(token: str, limit: int = 20, offset: int = 0, type: str | None = None):
    data = {'limit': str(limit), 'cursor': str(offset)}
    if type:
        data['type'] = type
    return fetch(token, 'get', 'notifications', data)

def mark_as_read(token: str, id: str):
    return fetch(token, 'post', f'notifications/{id}/read')

def mark_batch_as_read(token: str, ids: list[str]):
    data = {'ids': ids}
    return fetch(token, 'post', 'notifications/read-batch', data)

def get_unread_notifications_count(token: str):
    return fetch(token, 'get', 'notifications/count')