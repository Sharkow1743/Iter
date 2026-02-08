from requests import Response
from iter.models.base import Error
from iter.request import fetch
from typing import Optional
from iter.models.post import Comment
from iter.models.responses import CommentsResponse, LikeResponse, RepliesResponse
from uuid import UUID

def add_comment(token: str, post_id: UUID, content: str, attachment_ids: Optional[list[str]] = None) -> Comment | Error:
    data = {'content': content}
    if attachment_ids:
        data['attachmentIds'] = attachment_ids
    return fetch(token, 'post', f'posts/{post_id}/comments', data, response_schema=Comment)

def add_reply_comment(token: str, comment_id: UUID, content: str, attachment_ids: Optional[list[str]]  = None) -> Comment | Error:
    data = {'content': content}
    if attachment_ids:
        data['attachmentIds'] = attachment_ids
    return fetch(token, 'post', f'comments/{comment_id}/replies', data, response_schema=Comment)

def get_comments(token: str, post_id: UUID, limit: int = 20, cursor: int = 0, sort: str = 'popular') -> CommentsResponse | Error:
    return fetch(token, 'get', f'posts/{post_id}/comments', {'limit': limit, 'sort': sort, 'cursor': cursor}, response_schema=CommentsResponse)

def like_comment(token: str, comment_id: UUID) -> LikeResponse | Error:
    return fetch(token, 'post', f'comments/{comment_id}/like', response_schema=LikeResponse)

def unlike_comment(token: str, comment_id: UUID) -> LikeResponse | Error:
    return fetch(token, 'delete', f'comments/{comment_id}/like', response_schema=LikeResponse)

def delete_comment(token: str, comment_id: UUID) -> Response:
    return fetch(token, 'delete', f'comments/{comment_id}')

def get_replies(token: str, comment_id: UUID, page: int = 1, limit: int = 50, sort: str = 'oldest') -> RepliesResponse | Error:
    return fetch(token, 'get', f'comments/{comment_id}/replies', {'page': page, 'limit': limit, 'sort': sort}, response_schema=RepliesResponse)