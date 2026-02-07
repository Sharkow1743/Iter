from iter.request import fetch
from iter.types.responses import GetHashtags, HashtagPostsResponse

def get_hastags(token: str, limit: int = 10) -> GetHashtags:
    return fetch(token, 'get', 'hashtags/trending', {'limit': limit}, response_schema=GetHashtags)

def get_posts_by_hastag(token: str, hashtag: str, limit: int = 20, offset: int = 0) -> HashtagPostsResponse:
    return fetch(token, 'get', f'hashtags/{hashtag}/posts', {'limit': limit, 'offset': offset}, response_schema=HashtagPostsResponse)
