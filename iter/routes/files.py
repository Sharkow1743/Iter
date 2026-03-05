from _io import BufferedReader
import mimetypes
from uuid import UUID

from iter.models.base import Error
from iter.request import fetch
from iter.models.media import Attachment


def upload_file(token: str, name: str, data: BufferedReader) -> Attachment | Error:
    mime_type, _ = mimetypes.guess_type(name)

    if not mime_type:
        mime_type = 'application/octet-stream'

    return fetch(
        token, 
        'post', 
        'files/upload', 
        files={'file': (name, data, mime_type)}, 
        response_schema=Attachment
    )

def get_file(token: str, id: UUID) -> Attachment | Error:
    return fetch(token, 'get', f'files/{id}', response_schema=Attachment)

def delete_file(token: str, id: UUID) -> Attachment | Error:
    return fetch(token, 'delete', f'files/{id}', response_schema=Attachment)