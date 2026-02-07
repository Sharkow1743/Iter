from typing import List, Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator
from iter.types.user import User, UserFull, Clan
from iter.types.etc import Hashtag
from iter.types.post import Post, Comment
from iter.types.media import Attachment
from iter.types.etc import CursorPagination, PagePagination
from iter.types.notification import Notification
from datetime import datetime

def validate_datetime(v):
    if isinstance(v, str):
        # Fix +03 -> +03:00
        if "+" in v:
            parts = v.split("+")
            if len(parts[-1]) <= 2:
                v = f"{parts[0]}+{parts[-1].zfill(2)}:00"
        return v
    return v
PostgresDateTime = Annotated[datetime, BeforeValidator(validate_datetime)]

class SearchResults(BaseModel):
    users: List[User] = Field(default_factory=list)
    hashtags: List[Hashtag] = Field(default_factory=list)

class GetCommentsResults(BaseModel):
    comments: List[Comment]
    total: int
    hasMore: bool
    nextCursor: Optional[int]

class HashtagFeedData(BaseModel):
    hashtag: Hashtag
    posts: List[Post]
    pagination: CursorPagination

class GetPlatformStatus(BaseModel):
    readOnly: bool

class GetTopClans(BaseModel):
    clans: List[Clan]

class GetWhoToFollow(BaseModel):
    users: List[User]

class GetHashtags(BaseModel):
    data: SearchResults

class GetNotificationCount(BaseModel):
    count: int

class GetNotifications(BaseModel):
    notifications: List[Notification]
    hasMore: bool

class MarkAsReadResponse(BaseModel):
    success: bool

class MarkBatchAsReadResponse(BaseModel):
    # TODO
    pass

class GetComments(BaseModel):
    data: GetCommentsResults

class SearchResponse(BaseModel):
    data: SearchResults

class HashtagPostsResponse(BaseModel):
    data: HashtagFeedData

class UserFeedResponse(BaseModel):
    data: List[User]
    pagination: PagePagination

class PostFeedData(BaseModel):
    posts: list[Post]
    pagination: CursorPagination

class PostFeedResponse(BaseModel):
    data: PostFeedData

class PinPostResponse(BaseModel):
    success: bool
    pinnedPostId: Optional[str] = None

class LikeResponse(BaseModel):
    liked: bool
    likesCount: int

class FollowResponse(BaseModel):
    following: bool
    followersCount: int

class GetPostResponse(BaseModel):
    data: Post

class EditPostResponse(BaseModel):
    id: str
    content: str
    updatedAt: PostgresDateTime

class GetLikedPostsData(BaseModel):
    posts: list[Post]
    pagination: CursorPagination

class GetLikedPostsResponse(BaseModel):
    data: GetLikedPostsData

class UpdateProfileResponse(BaseModel):
    id: str
    username: str
    displayName: str
    bio: str
    updatedAt: PostgresDateTime

class UpdatePrivacyResponse(BaseModel):
    isPrivate: bool
    wallClosed: bool

class GetFollowersData(BaseModel):
    users: list[User]
    pagination: PagePagination

class GetFollowersResponse(BaseModel):
    data: GetFollowersData

class ReportResponse(BaseModel):
    pass # TODO

class VerificateResponse(BaseModel):
    pass # TODO

class GetVerificationStatusResponse(BaseModel):
    pass # TODO