import logging, verboselogs
from _io import BufferedReader
from requests import Session, Response, PreparedRequest, Request, JSONDecodeError
from typing import Optional, Union, Dict, Any, Tuple
from pydantic import BaseModel, ValidationError
from urllib.parse import urljoin

from iter.exceptions import InvalidToken, InvalidCookie, RateLimitExceeded, Unauthorized
from iter.models.base import Error

# Use a named logger for this module
logger = verboselogs.VerboseLogger(__name__)
s = Session()

def dump_res(res: Response, err: Error | None = None):
    return f'Request dump:\n> {res.request.method} {res.request.url}\n> {str(res.request.body) if len(str(res.request.body)) < 1000 else str(res.request.body)[:1000] + '...'}\n> {res.reason} {res.status_code} {res.text if len(res.text) < 1000 else res.text[:1000] + '...'}\n> {err.code + ': ' + err.message if err else ''}'
def dump_req(req: PreparedRequest):
    body = str(req.body) if req.body is not None else ""
    return (
        f'Request dump:\n'
        f'> {req.method} {req.url}\n'
        f'> {body if len(body) < 1000 else body[:1000] + "..."}'
    )

def fetch(
    token: str,
    method: str,
    endpoint: str, 
    params: Optional[Dict[str, Any]] = None, 
    files: Optional[Dict[str, Tuple[str, Any]]] = None, 
    response_schema: Optional[type[BaseModel]] = None
) -> Union[BaseModel, Response]:
    
    base_url = 'https://xn--d1ah4a.com/api/'
    url = urljoin(base_url, endpoint.lstrip('/'))

    headers = {
        "Authorization": f'Bearer {token}',
        "Accept": "application/json",
        "User-Agent": "Iter-Python-Client/1.0"
    }

    is_get = method.upper() == "GET"

    request = Request(
        method=method.upper(),
        url=url,
        headers=headers,
        params=params if is_get else None,
        json=params if not is_get else None,
        files=files
    )

    prepared = s.prepare_request(request)
    error_obj = None

    response = None

    try:
        response = s.send(
            prepared, 
            timeout=120 if files else 20
        )
        
        try:
            data = response.json()
            if isinstance(data, dict) and data.get('error'):
                
                error_obj = Error.model_validate_json(response.text)
                
                match error_obj.code:
                    case 'RATE_LIMIT_EXCEEDED':
                        raise RateLimitExceeded(error_obj.retry_after)
                    case 'UNAUTHORIZED':
                        raise Unauthorized()
                    case _:
                        return error_obj
                        
        except (JSONDecodeError, ValidationError):
            pass

        response.raise_for_status()

        if response_schema:
            try:
                return response_schema.model_validate_json(response.text)
            except ValidationError as e:
                logger.error(f"Response did not match schema {response_schema.__name__}")
                raise e

        return response

    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
    finally:
        dump = dump_req(prepared)
        if response: dump = dump_res(response, error_obj)
        logger.debug(dump)


def set_cookies(cookies: str):
    for cookie in cookies.split('; '):
        s.cookies.set(cookie.split('=')[0], cookie.split('=')[-1], path='/', domain='xn--d1ah4a.com.com')

def auth_fetch(cookies: str | list, method: str, url: str, params: dict = {}, token: str | None = None):
    base = 'https://xn--d1ah4a.com/api/'
    if isinstance(cookies, list):
        cookies = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    headers = {
        "Host": "xn--d1ah4a.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://xn--d1ah4a.com/",
        "Content-Type": "application/json",
        "Origin": "https://xn--d1ah4a.com",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Cookie": cookies,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Content-Length": "0",
        "TE": "trailers",
    }
    if token:
        headers['Authorization'] = 'Bearer ' + token

    req = Request(
        method=method.upper(),
        url=base + url,
        headers=headers,
        params=params if method.upper() == "GET" else None,
        json=params if method.upper() != "GET" else None
    )
    res = None
    err = None

    prepared = s.prepare_request(req)

    try:
        res = s.send(
            prepared, 
            timeout=20
        )

        # 204 No Content has no body, so we return immediately
        if res.status_code == 204:
            return None

        if res.text == 'UNAUTHORIZED':
            raise InvalidToken()
        try:
            res.json()['error']
            err = Error.model_validate_json(res.text)
            match err.code:
                case 'RATE_LIMIT_EXCEEDED':
                    raise RateLimitExceeded(err.retry_after)
                case 'UNAUTHORIZED':
                    raise Unauthorized()
        except (KeyError, JSONDecodeError):
            pass # not an error

        res.raise_for_status()
        return res.json()
    except Exception as e:
        logger.error(f'Auth request failed: {e}')
        raise
    finally:
        dump = dump_req(prepared)
        if res: dump = dump_res(res, err)

        logger.debug(dump)
