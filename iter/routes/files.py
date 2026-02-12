from _io import BufferedReader
from uuid import UUID

from iter.models.base import Error
from iter.request import fetch
from iter.models.media import Attachment


def upload_file(token: str, name: str, data: BufferedReader) -> Attachment | Error:
    return fetch(token, 'post', 'files/upload', files={'file': (name, data)}, response_schema=Attachment)

def get_file(token: str, id: UUID) -> Attachment | Error:
    return fetch(token, 'get', f'files/{id}', response_schema=Attachment)

def delete_file(token: str, id: UUID) -> Attachment | Error:
    return fetch(token, 'delete', f'files/{id}', response_schema=Attachment)