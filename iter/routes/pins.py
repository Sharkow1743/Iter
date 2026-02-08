from requests import Response
from iter.models.base import Error
from iter.models.responses import PinsListResponse, SetPinResponse
from iter.request import fetch

def get_pins(token: str) -> PinsListResponse | Error:
    return fetch(token, 'get', 'users/me/pins', response_schema=PinsListResponse)

def remove_pin(token: str) -> Response:
    return fetch(token, 'delete', 'users/me/pin')

def set_pin(token: str, slug: str):
    return fetch(token, 'put', 'users/me/pin', {'slug': slug}, response_schema=SetPinResponse)