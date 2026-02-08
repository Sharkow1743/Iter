from _io import BufferedReader

from iter.request import fetch
from iter.models.media import Attachment


def upload_file(token: str, name: str, data: BufferedReader) -> Attachment:
    return fetch(token, 'post', 'files/upload', files={'file': (name, data)}, response_schema=Attachment)