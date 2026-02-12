from datetime import datetime
from iter.request import fetch
from iter.models.post import Post
from iter.models.responses import PostFeedResponse, Post, PostUpdateResponse, PinResponse
from iter.models.media import NewPoll
from requests import Response
from iter.models.base import Error
from uuid import UUID

def create_post(token: str, content: str, wall_recipient_id: UUID | None = None, attachment_ids: list[str] = [], poll: NewPoll | None = None) -> Post | Error:
    data: dict = {'content': content}
    if wall_recipient_id:
        data['wallRecipientId'] = str(wall_recipient_id)
    if attachment_ids:
        data['attachmentIds'] = list(map(str, attachment_ids))
    if poll:
        data['poll'] = NewPoll.model_dump(poll)

    return fetch(token, 'post', 'posts', data, response_schema=Post)

def get_posts(token: str, username: str | None = None, limit: int = 20, cursor: int = 0, sort: str = '', tab: str = '') -> PostFeedResponse | Error:
    data: dict = {'limit': limit, 'cursor': cursor}
    if username:
        data['username'] = username
    if sort:
        data['sort'] = sort
    if tab:
        data['tab'] = tab

    return fetch(token, 'get', 'posts', data, response_schema=PostFeedResponse)

def get_post(token: str, id: UUID) -> Post | Error:
    return fetch(token, 'get', f'posts/{id}', response_schema=Post)

def edit_post(token: str, id: UUID, content: str) -> PostUpdateResponse | Error:
    return fetch(token, 'put', f'posts/{id}', {'content': content}, response_schema=PostUpdateResponse)

def delete_post(token: str, id: UUID) -> Response | Error:
    return fetch(token, 'delete', f'posts/{id}')

def pin_post(token: str, id: UUID) -> PinResponse | Error:
    return fetch(token, 'post', f'posts/{id}/pin', response_schema=PinResponse)

def repost(token: str, id: UUID, content: str | None = None) -> Post | Error:
    data = {}
    if content:
        data['content'] = content
    return fetch(token, 'post', f'posts/{id}/repost', data, response_schema=Post)

def view_post(token: str, id: UUID) -> Response:
    return fetch(token, 'post', f'posts/{id}/view')

def get_liked_posts(token: str, username: str, limit: int = 20, cursor: int = 0) -> PostFeedResponse | Error:
    return fetch(token, 'get', f'posts/user/{username}/liked', {'limit': limit, 'cursor': cursor}, response_schema=PostFeedResponse)

def get_user_posts(token: str, username_or_id: str | UUID, limit: int = 20, cursor: datetime | None = None) -> PostFeedResponse | Error:
    return fetch(token, 'get', f'posts/user/{username_or_id}', {'limit': limit, 'cursor': cursor}, response_schema=PostFeedResponse)

def restore_post(token: str, post_id: UUID) -> Response:
    return fetch(token, "post", f"posts/{post_id}/restore")

def like_post(token: str, post_id: UUID):
    return fetch(token, "post", f"posts/{post_id}/like")

def unlike_post(token: str, post_id: UUID):
    return fetch(token, "delete", f"posts/{post_id}/like")