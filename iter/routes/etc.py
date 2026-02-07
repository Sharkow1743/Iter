from iter.request import fetch
from iter.types.responses import GetTopClans, GetWhoToFollow, GetPlatformStatus

def get_top_clans(token: str) -> GetTopClans:
    return fetch(token, 'get', 'users/stats/top-clans', response_schema=GetTopClans)

def get_who_to_follow(token: str) -> GetWhoToFollow:
    return fetch(token, 'get', 'users/suggestions/who-to-follow', response_schema=GetWhoToFollow)

def get_platform_status(token: str) -> GetPlatformStatus:
    return fetch(token, 'get', 'platform/status', response_schema=GetPlatformStatus)