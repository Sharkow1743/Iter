from iter.request import fetch
from iter.types.responses import SearchResponse

def search(token: str, query: str, user_limit: int = 5, hashtag_limit: int = 5) -> SearchResponse:
    return fetch(token, 'get', 'search', {'userLimit': user_limit, 'hashtagLimit': hashtag_limit, 'q': query}, response_schema=SearchResponse)