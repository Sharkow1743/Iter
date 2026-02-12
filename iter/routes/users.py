from iter.request import fetch
from iter.models.user import UserFull, UserPrivacyData
from iter.models.responses import ProfileUpdateResponse, PrivacyUpdateResponse, FollowResponse, UserListResponse
from iter.models.base import Error
from uuid import UUID


def get_user(token: str, username: str) -> UserFull | Error:
    return fetch(token, 'get', f'users/{username}', response_schema=UserFull)

def update_profile(token: str, bio: str | None = None, display_name: str | None = None, username: str | None = None, banner_id: UUID | None = None) -> ProfileUpdateResponse:
    data = {}
    if bio:
        data['bio'] = bio
    if display_name:
        data['displayName'] = display_name
    if username:
        data['username'] = username
    if banner_id:
        data['bannerId'] = str(banner_id)
    return fetch(token, 'put', 'users/me', data, response_schema=ProfileUpdateResponse)

def update_privacy(token: str, privacy: UserPrivacyData) -> PrivacyUpdateResponse | Error:
    return fetch(token, 'put', 'users/me/privacy', privacy.to_dict(), response_schema=PrivacyUpdateResponse)

def follow(token: str, username: str) -> FollowResponse | Error:
    return fetch(token, 'post', f'users/{username}/follow', response_schema=FollowResponse)

def unfollow(token: str, username: str) -> FollowResponse | Error:
    return fetch(token, 'delete', f'users/{username}/follow', response_schema=FollowResponse)

def get_followers(token: str, username: str, limit: int = 30, page: int = 1) -> UserListResponse | Error:
    return fetch(token, 'get', f'users/{username}/followers', {'limit': limit, 'page': page}, response_schema=UserListResponse)

def get_following(token: str, username: str, limit: int = 30, page: int = 1) -> UserListResponse | Error:
    return fetch(token, 'get', f'users/{username}/following', {'limit': limit, 'page': page}, response_schema=UserListResponse)

