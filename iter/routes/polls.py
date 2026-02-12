from iter.models.base import Error
from iter.request import fetch
from uuid import UUID
from iter.models.media import Poll

def vote(token: str, ids: list[UUID]):
    return fetch(token, 'post', 'poll/vote', {"optionIds": ids}, response_schema=Poll)