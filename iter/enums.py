ERROR_CODE_TO_EXCEPTION = {
    'SAME_PASSWORD': SamePassword,
    'INVALID_OLD_PASSWORD': InvalidOldPassword,
    'NOT_FOUND': NotFound,
    'USER_BLOCKED': UserBanned,
    'USERNAME_TAKEN': UsernameTaken,
    'VALIDATION_ERROR': ValidationError,
    'PENDING_REQUEST_EXISTS': PendingRequestExists,
    'FORBIDDEN': Forbidden,
    'PIN_NOT_OWNED': PinNotOwned
}

from enum import Enum
from iter.exceptions import (
    NoCookie, NoAuthData, SamePassword, InvalidOldPassword, NotFound, ValidationError, UserBanned,
    PendingRequestExists, Forbidden, UsernameTaken, CantFollowYourself, Unauthorized,
    CantRepostYourPost, AlreadyReposted, AlreadyReported, TooLarge, PinNotOwned
)

class NotificationType(Enum):
    WALL_POST = 'wall_post'
    REPLY = 'reply'
    REPOST = 'repost'
    COMMENT = 'comment'
    FOLLOW = 'follow'
    LIKE = 'like'

class NotificationTargetType(Enum):
    POST = 'post'

class ReportTargetType(Enum):
    POST = 'post'
    USER = 'user'
    COMMENT = 'comment'

class ReportTargetReason(Enum):
    SPAM = 'spam' # спам
    VIOLENCE = 'violence' # насилие
    HATE = 'hate' # ненависть
    ADULT = 'adult' # 18+
    FRAUD = 'fraud' # обман\мошенничество
    OTHER = 'other' # другое

class AttachType(Enum):
    AUDIO = 'audio'
    IMAGE = 'image'
    VIDEO = 'video'
    FILE = 'file'

class PostsTab(Enum):
    FOLLOWING = 'following'
    POPULAR = 'popular'
