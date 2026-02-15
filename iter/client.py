from datetime import datetime
from requests import Response
import logging, verboselogs
from uuid import UUID

from iter.models.user import UserPrivacyData
from iter.request import get_cookies_string, set_cookies
from iter.routes.polls import vote
from iter.models.media import Attachment, PollData
from iter.routes.pins import get_pins, remove_pin, set_pin
logger = verboselogs.VerboseLogger(__name__)

import json
import os
from _io import BufferedReader
from typing import cast, Optional

from requests.exceptions import ConnectionError, HTTPError
# Import your routes
from iter.routes.users import get_user, update_profile, follow, unfollow, get_followers, get_following, update_privacy
from iter.routes.etc import get_top_clans, get_who_to_follow, get_platform_status
from iter.routes.comments import get_comments, add_comment, add_reply_comment, delete_comment, get_replies, like_comment, unlike_comment
from iter.routes.hashtags import get_hashtags, get_posts_by_hashtag
from iter.routes.notifications import get_notifications, mark_all_as_read, mark_as_read, get_unread_notifications_count
from iter.routes.posts import create_post, get_posts, get_post, edit_post, delete_post, pin_post, repost, restore_post, view_post, get_liked_posts, get_user_posts, like_post, unlike_post
from iter.routes.reports import report
from iter.routes.search import search
from iter.routes.files import delete_file, get_file, upload_file
from iter.routes.auth import refresh_token, change_password, logout
from iter.routes.verification import verify, get_verification_status

from iter.manual_auth import auth

from iter.enums import PostsTab, ReportTargetType, ReportTargetReason
from iter.exceptions import (
    NoCookie, NoAuthData, NotFoundOrForbidden, SamePassword, InvalidOldPassword, NotFound, ValidationError, UserBanned,
    PendingRequestExists, Forbidden, UsernameTaken, CantFollowYourself, Unauthorized,
    CantRepostYourPost, AlreadyReposted, AlreadyReported, TooLarge, PinNotOwned, InvalidToken,
    InvalidRefreshToken, NoContent, NotVerified
)

from iter.models.base import Error

def refresh_on_error(func):
    def wrapper(self, *args, **kwargs):
        if self.cookies:
            try:
                return func(self, *args, **kwargs)
            except (Unauthorized, ConnectionError, HTTPError):
                logger.notice("Access token expired, attempting refresh")
                self.refresh_auth()
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return wrapper


class Client:
    def __init__(self, token: Optional[str] = None, cookies: Optional[str] = None, session_file: Optional[str] = "session.json", email: Optional[str] = None, password: Optional[str] = None, use_manual_login: bool = True):
        self.token = token.replace('Bearer ', '') if token else None
        self.cookies = cookies

        self.use_manual_login = use_manual_login
        self.session_file = session_file

        self.email = email
        self.password = password

        is_auth = self.auth()
        if not is_auth:
            raise NoAuthData
        
        me = self.get_me()
        self.me = None if isinstance(me, Error) else me

    def auth(self):
        if (self.session_file 
            and not self.token 
            and not self.cookies):
            self._load_session()

        if (self.use_manual_login 
            and not self.token 
            and not self.cookies):
            self._manual_login()

        return self.token and self.cookies

    def _save_session(self):
        """Saves current credentials to a JSON file."""
        data = {
            "token": self.token,
            "cookies": self.cookies
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def _load_session(self):
        """Loads credentials from the session file."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.token = data.get("token")
                    self.cookies = data.get("cookies")
                    set_cookies(self.cookies)
            except Exception as e:
                logger.warning(f"Failed to load session file: {e}")

    def _manual_login(self):
        """Triggers the manual authentication flow."""
        if not self.use_manual_login:
            logger.info('Manual login canceled')
            return None
        logger.info("Starting manual login")
        new_data = auth(self.email, self.password)
        if new_data:
            self.token = new_data.get('token', '').replace('Bearer ', '')
            self.cookies = new_data.get('cookies')

            if isinstance(self.cookies, list):
                self.cookies = "; ".join([f"{c['name']}={c['value']}" for c in self.cookies])

            self._save_session()
            return self.token
        logger.warning("Manual login failed")

    def refresh_auth(self):
        """Refresh access token and update the rotated refresh cookie"""
        if self.use_manual_login and not self.cookies:
            return self._manual_login()

        try:
            logger.info("Refreshing access token")

            set_cookies(self.cookies)

            new_token: str = refresh_token(self.cookies)
            self.token = new_token.replace('Bearer ', '')

            self.cookies = get_cookies_string()

            self._save_session()
            
            return self.token
        except HTTPError as e:
            if self.use_manual_login and e.response is not None and e.response.status_code in [401, 403]:
                logger.info("Refresh token expired or revoked. Manual login required")
                return self._manual_login()
            raise e
        
    @refresh_on_error
    def logout(self) -> dict:
        """Выход из аккаунта

        Raises:
            NoCookie: Нет cookie

        Returns:
            dict: Ответ API
        """
        if not self.cookies:
            raise NoCookie()

        res = logout(self.cookies)

        return res
    
    @refresh_on_error
    def change_password(self, old: str, new: str) -> dict:
        """Change password

        Args:
            old (str): Old password
            new (str): New password

        Raises:
            NoCookie: No cookie
            SamePassword: Same passwords
            InvalidOldPassword: Invalid old password

        Returns:
            dict: API response `{'message': 'Password changed successfully'}`
        """
        if not self.cookies:
            raise NoCookie()

        res = change_password(self.cookies, self.token, old, new)
        if isinstance(res, Error):
            match res.code:
                case 'SAME_PASSWORD':
                    raise SamePassword()
                case 'INVALID_OLD_PASSWORD':
                    raise InvalidOldPassword()

        return res


# --- API methods ---

    @refresh_on_error
    def get_user(self, username: str):
        """Get user

        Args:
            username (str): username or "me"

        Raises:
            NotFound: User not found
            UserBanned: User banned
        """
        user = get_user(self.token, username)
        if isinstance(user, Error):
            match user.code:
                case 'NOT_FOUND':
                    raise NotFound('User')
                case 'USER_BLOCKED':
                    raise UserBanned()

        return user

    @refresh_on_error
    def get_me(self):
        """Get current user (me)
        """
        return self.get_user('me')

    @refresh_on_error
    def update_profile(self, username: str | None = None, display_name: str | None = None, bio: str | None = None, banner_id: UUID | None = None):
        """Update profile

        Args:
            username (str | None, optional): username. Defaults to None.
            display_name (str | None, optional): Display name. Defaults to None.
            bio (str | None, optional): Biography (about). Defaults to None.
            banner_id (UUID | None, optional): Banner UUID. Defaults to None.

        Raises:
            ValidationError: Validation error
            UsernameTaken: Username is already taken
        """
        res = update_profile(self.token, bio, display_name, username, banner_id)
        if isinstance(res, Error):
            match res.code:
                case 'VALIDATION_ERROR':
                    # Assuming res.data contains the validation details
                    if hasattr(res, 'data') and 'found' in res.data:
                         raise ValidationError(*list(res.data['found'].items())[0])
                case 'USERNAME_TAKEN':
                    raise UsernameTaken()
                case 'PHONE_VERIFICATION_REQUIRED':
                    raise NotVerified(self.me.id if self.me else None)
        
        return res

    @refresh_on_error
    def update_privacy(self, privacy: UserPrivacyData):
        """Update privacy settings

        Args:
            wall_closed (bool, optional): Close wall. Defaults to False.
            private (bool, optional): Privacy. Functionality currently unknown. Defaults to False.
        """
        res = update_privacy(self.token, privacy)
        if isinstance(res, Error):
            res.raise_for_status() # Fallback for unexpected errors

        return res

    @refresh_on_error
    def follow(self, username: str):
        """Follow user

        Args:
            username (str): username

        Raises:
            NotFound: User not found
            CantFollowYourself: Cannot follow yourself
        """
        res = follow(self.token, username)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('User')
                case 'VALIDATION_ERROR':
                    raise CantFollowYourself()
        
        return res

    @refresh_on_error
    def unfollow(self, username: str):
        """Unfollow user

        Args:
            username (str): username

        Raises:
            NotFound: User not found
        """
        res = unfollow(self.token, username)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('User')

        return res

    @refresh_on_error
    def get_followers(self, username: str, limit: int = 30, page: int = 1):
        """Get user followers

        Args:
            username (str): username
            limit (int, optional): Limit. Defaults to 30.
            page (int, optional): Page (increment by 1 for pagination). Defaults to 1.

        Raises:
            NotFound: User not found
        """
        res = get_followers(self.token, username, limit, page)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('User')

        return res

    @refresh_on_error
    def get_following(self, username: str, limit: int = 30, page: int = 1):
        """Get user followings

        Args:
            username (str): username
            limit (int, optional): Limit. Defaults to 30.
            page (int, optional): Page (increment by 1 for pagination). Defaults to 1.

        Raises:
            NotFound: User not found
        """
        res = get_following(self.token, username, limit, page)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('User')

        return res

    @refresh_on_error
    def verify(self, file_url: str):
        """Send verification request

        Args:
            file_url (str): Video URL

        Raises:
            PendingRequestExists: Request already pending
        """
        res = verify(self.token, file_url)
        if isinstance(res, Error):
            match res.code:
                case 'PENDING_REQUEST_EXISTS':
                    raise PendingRequestExists()
        
        return res

    @refresh_on_error
    def get_verification_status(self):
        """Get verification status
        """
        res = get_verification_status(self.token)

        return res

    @refresh_on_error
    def get_who_to_follow(self):
        """Get list of popular users (who to follow)
        """
        res = get_who_to_follow(self.token)          

        return res

    @refresh_on_error
    def get_top_clans(self):
        """Get top clans
        """
        res = get_top_clans(self.token)

        return res

    @refresh_on_error
    def get_platform_status(self):
        """Get platform status
        """
        res = get_platform_status(self.token)

        return res

    @refresh_on_error
    def add_comment(self, post_id: UUID, content: str, attachment_ids: list[UUID] = []):
        """Add comment

        Args:
            post_id (str): Post UUID
            content (str): Content
            attachment_ids (list[UUID]): List of attached file UUIDs
            reply_comment_id (UUID | None, optional): Reply comment ID. Defaults to None.

        Raises:
            ValidationError: Validation error
            NotFound: Post not found
        """
        res = add_comment(self.token, post_id, content, attachment_ids)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Post')
                case 'VALIDATION_ERROR':
                    if hasattr(res, 'data') and 'found' in res.data:
                         raise ValidationError(*list(res.data['found'].items())[0])
                case 'PHONE_VERIFICATION_REQUIRED':
                    raise NotVerified(self.me.id if self.me else None)

        return res

    @refresh_on_error
    def add_reply_comment(self, comment_id: UUID, content: str, author_id: UUID | None = None, attachment_ids: list[UUID] = []):
        """Add reply comment

        Args:
            comment_id (str): Comment UUID
            content (str): Content
            author_id (UUID | None, optional): ID of the user who sent the comment. Defaults to None.
            attachment_ids (list[UUID]): List of attached file UUIDs

        Raises:
            ValidationError: Validation error
            NotFound: User or Comment not found
            NoContent: Validation error resulting in no content
        """
        res = add_reply_comment(self.token, comment_id, content, author_id, attachment_ids)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Comment')
                case 'VALIDATION_ERROR':
                    if hasattr(res, 'data') and 'found' in res.data:
                         raise ValidationError(*list(res.data['found'].items())[0])
                    raise NoContent()
                case 'FAILED_QUERY':
                    raise NotFound('User')
                case 'PHONE_VERIFICATION_REQUIRED':
                    raise NotVerified(self.me.id if self.me else None)
        
        return res

    @refresh_on_error
    def get_comments(self, post_id: UUID, limit: int = 20, cursor: int = 0, sort: str = 'popular'):
        """Get list of comments

        Args:
            post_id (UUID): Post UUID
            limit (int, optional): Limit. Defaults to 20.
            cursor (int, optional): Cursor (how many to skip). Defaults to 0.
            sort (str, optional): Sorting. Defaults to 'popular'.

        Raises:
            NotFound: Post not found
        """
        res = get_comments(self.token, post_id, limit, cursor, sort)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("Post")

        return res

    @refresh_on_error
    def get_replies(self, comment_id: UUID, limit: int = 50, page: int = 1, sort: str = 'oldest'):
        """Get list of replies

        Args:
            comment_id (UUID): Comment UUID
            limit (int, optional): Limit. Defaults to 50.
            page (int, optional): Page. Defaults to 1.
            sort (str, optional): Sorting. Defaults to 'oldest'.

        Raises:
            NotFound: Comment not found
        """
        res = get_replies(self.token, comment_id, page, limit, sort)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("User")

        return res

    @refresh_on_error
    def like_comment(self, id: UUID):
        """Like comment

        Args:
            id (UUID): Comment UUID

        Raises:
            NotFound: Comment not found
        """
        res = like_comment(self.token, id)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("Comment")

        return res

    @refresh_on_error
    def unlike_comment(self, id: UUID):
        """Unlike comment

        Args:
            id (UUID): Comment UUID

        Raises:
            NotFound: Comment not found
        """
        res = unlike_comment(self.token, id)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("Comment")


        return res

    @refresh_on_error
    def delete_comment(self, id: UUID):
        """Delete comment

        Args:
            id (UUID): Comment UUID

        Raises:
            NotFound: Comment not found
            Forbidden: No permission to delete
        """
        res = delete_comment(self.token, id)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Comment')
                case 'FORBIDDEN':
                    raise Forbidden('delete comment')

    @refresh_on_error
    def get_hashtags(self, limit: int = 10):
        """Get list of popular hashtags

        Args:
            limit (int, optional): Limit. Defaults to 10.
        """
        res = get_hashtags(self.token, limit)

        return res

    @refresh_on_error
    def get_posts_by_hashtag(self, hashtag: str, limit: int = 20, cursor: UUID | None = None):
        """Get posts by hashtag

        Args:
            hashtag (str): Hashtag (without #)
            limit (int, optional): Limit. Defaults to 20.
            cursor (UUID | None, optional): Cursor (UUID of the last post to fetch data after). Defaults to None.
        """
        res = get_posts_by_hashtag(self.token, hashtag, limit, cursor)

        return res

    @refresh_on_error
    def get_notifications(self, limit: int = 20, offset: int = 0):
        """Get notifications

        Args:
            limit (int, optional): Limit. Defaults to 20.
            offset (int, optional): Offset. Defaults to 0.
        """
        res = get_notifications(self.token, limit, offset)

        return res

    @refresh_on_error
    def mark_as_read(self, id: UUID):
        """Mark notification as read

        Args:
            id (UUID): Notification UUID
        """
        res = mark_as_read(self.token, id)
        return res

    @refresh_on_error
    def mark_all_as_read(self):
        """Mark all notifications as read"""
        mark_all_as_read(self.token)

    @refresh_on_error
    def get_unread_notifications_count(self):
        """Get unread notifications count
        """
        res = get_unread_notifications_count(self.token)

        return res

    @refresh_on_error
    def create_post(self, content: str, wall_recipient_id: UUID | None = None, attach_ids: list[UUID] = [], poll: PollData | None = None):
        """Create post

        Args:
            content (str): Content
            wall_recipient_id (UUID | None, optional): UUID of the user (to create a post on their wall). Defaults to None.
            attach_ids (list[UUID], optional): UUIDs of attachments. Defaults to [].

        Raises:
            NotFound: User not found
            ValidationError: Validation error
        """
        res = create_post(self.token, content, wall_recipient_id, attach_ids, poll.poll if poll else None)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Wall recipient')
                case 'VALIDATION_ERROR':
                    if hasattr(res, 'data') and 'found' in res.data:
                         raise ValidationError(*list(res.data['found'].items())[0])
                case 'PHONE_VERIFICATION_REQUIRED':
                    raise NotVerified(self.me.id if self.me else None)
        
        return res

    @refresh_on_error
    def get_posts(self, cursor: int = 0, tab: PostsTab = PostsTab.POPULAR):
        """Get list of posts

        Args:
            cursor (int, optional): Page. Defaults to 0.
            tab (PostsTab, optional): Tab (popular or following). Defaults to PostsTab.POPULAR.
        """
        res = get_posts(self.token, cursor=cursor, tab=tab.value)

        return res

    @refresh_on_error
    def get_post(self, id: UUID):
        """Get post

        Args:
            id (UUID): Post UUID

        Raises:
            NotFound: Post not found
        """
        res = get_post(self.token, id)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Post')

        return res

    @refresh_on_error
    def edit_post(self, id: UUID, content: str):
        """Edit post

        Args:
            id (UUID): Post UUID
            content (str): Content

        Raises:
            NotFound: Post not found
            Forbidden: No access
            ValidationError: Validation error
        """
        res = edit_post(self.token, id, content)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Post')
                case 'FORBIDDEN':
                    raise Forbidden('edit post')
                case 'VALIDATION_ERROR':
                    if hasattr(res, 'found'):
                         raise ValidationError(*list(res.found.items())[0])

        return res

    @refresh_on_error
    def delete_post(self, id: UUID):
        """Delete post

        Args:
            id (UUID): Post UUID

        Raises:
            NotFound: Post not found
            Forbidden: No access
        """
        res = delete_post(self.token, id)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Post')
                case 'FORBIDDEN':
                    raise Forbidden('delete post')

    @refresh_on_error
    def pin_post(self, id: UUID):
        """Pin post

        Args:
            id (UUID): Post UUID

        Raises:
            NotFound: Post not found
            Forbidden: No access
        """
        res = pin_post(self.token, id)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Post')
                case 'FORBIDDEN':
                    raise Forbidden('pin post')

    @refresh_on_error
    def repost(self, id: UUID, content: str | None = None):
        """Repost post

        Args:
            id (UUID): Post UUID
            content (str | None, optional): Content (additional comment). Defaults to None.

        Raises:
            NotFound: Post not found
            AlreadyReposted: Post already reposted
            CantRepostYourPost: Cannot repost your own post
            ValidationError: Validation error
        """
        res = repost(self.token, id, content)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('Post')
                case 'CONFLICT':
                    raise AlreadyReposted()
                case 'VALIDATION_ERROR':
                    if hasattr(res, 'message') and res.message == 'Cannot repost your own post':
                        raise CantRepostYourPost()
                    if hasattr(res, 'data') and 'found' in res.data:
                         raise ValidationError(*list(res.data['found'].items())[0])
                case 'PHONE_VERIFICATION_REQUIRED':
                    raise NotVerified(self.me.id if self.me else None)

        return res

    @refresh_on_error
    def view_post(self, id: UUID):
        """View post

        Args:
            id (UUID): Post UUID

        Raises:
            NotFound: Post not found
        """
        res = view_post(self.token, id)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("Post")

    @refresh_on_error
    def get_user_posts(self, username_or_id: str | UUID, limit: int = 20, cursor: datetime | None = None):
        """Get user posts

        Args:
            username_or_id (str | UUID): UUID or username of the user
            limit (int, optional): Limit. Defaults to 20.
            cursor (datetime | None, optional): Offset (next_cursor). Defaults to None.

        Raises:
            NotFound: User not found
        """
        res = get_user_posts(self.token, username_or_id, limit, cursor)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("User")

        return res

    @refresh_on_error
    def get_liked_posts(self, username_or_id: str | UUID, limit: int = 20, cursor: datetime | None = None):
        """Get liked posts by user

        Args:
            username_or_id (str | UUID): UUID or username of the user
            limit (int, optional): Limit. Defaults to 20.
            cursor (datetime | None, optional): Offset (next_cursor). Defaults to None.

        Raises:
            NotFound: User not found
        """
        res = get_liked_posts(self.token, username_or_id, limit, cursor)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("User")

        return res

    @refresh_on_error
    def report(self, id: UUID, type: ReportTargetType = ReportTargetType.POST, reason: ReportTargetReason = ReportTargetReason.OTHER, description: str | None = None):
        """Send report

        Args:
            id (UUID): Target UUID
            type (ReportTargetType, optional): Target type (post/user/comment). Defaults to ReportTargetType.POST.
            reason (ReportTargetReason, optional): Reason. Defaults to ReportTargetReason.OTHER.
            description (str | None, optional): Description. Defaults to None.

        Raises:
            NotFound: Target not found
            AlreadyReported: Report already sent
            ValidationError: Validation error
        """
        res = report(self.token, id, type.value, reason.value, description)
        if isinstance(res, Error):
            match res.code:
                case 'VALIDATION_ERROR':
                    # Heuristics based on error message if precise code isn't available
                    msg = getattr(res, 'message', '') or ''
                    if 'не найден' in msg or 'not found' in msg:
                        raise NotFound(type.value.title())
                    if 'Вы уже отправляли жалобу' in msg or 'already reported' in msg:
                        raise AlreadyReported(type.value.title())
                    
                    if hasattr(res, 'data') and 'found' in res.data:
                         raise ValidationError(*list(res.data['found'].items())[-1])
        
        return res

    @refresh_on_error
    def search(self, query: str, user_limit: int = 5, hashtag_limit: int = 5):
        """Search users and hashtags

        Args:
            query (str): Query
            user_limit (int, optional): User limit. Defaults to 5.
            hashtag_limit (int, optional): Hashtag limit. Defaults to 5.

        Raises:
            TooLarge: Query too long
        """
        res = search(self.token, query, user_limit, hashtag_limit)
        if isinstance(res, Error):
            match res.code:
                case 'URI_TOO_LONG': # or appropriate code for 414
                    raise TooLarge()
        
        return res

    @refresh_on_error
    def search_user(self, query: str, limit: int = 5):
        """Search users

        Args:
            query (str): Query
            limit (int, optional): Limit. Defaults to 5.
        """
        return self.search(query, limit, 1)

    @refresh_on_error
    def search_hashtag(self, query: str, limit: int = 5):
        """Search hashtags

        Args:
            query (str): Query
            limit (int, optional): Limit. Defaults to 5.
        """
        return self.search(query, 1, limit)

    @refresh_on_error
    def upload_file(self, name: str, data: BufferedReader):
        """Upload file

        Args:
            name (str): Filename
            data (BufferedReader): Content (open('name', 'rb'))
        """
        res = upload_file(self.token, name, data)

        return res

    def update_banner(self, name: str):
        """Update banner (shortcut for upload_file + update_profile)

        Args:
            name (str): Filename
        """
        file_id = self.upload_file(name, cast(BufferedReader, open(name, 'rb'))).id
        return self.update_profile(banner_id=file_id)

    @refresh_on_error
    def restore_post(self, post_id: UUID):
        """Restore deleted post

        Args:
            post_id: Post UUID
        """
        restore_post(self.token, post_id)

    @refresh_on_error
    def like_post(self, post_id: UUID):
        """Like post

        Args:
            post_id (UUID): Post UUID

        Raises:
            NotFound: Post not found
        """
        res = like_post(self.token, post_id)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("Post")

        return res

    @refresh_on_error
    def unlike_post(self, post_id: UUID):
        """Unlike post

        Args:
            post_id (UUID): Post UUID

        Raises:
            NotFound: Post not found
        """
        res = unlike_post(self.token, post_id)
        if ((isinstance(res, Error) and res.code == 'NOT_FOUND')
            or (isinstance(res, Response) and res.status_code == 404)): raise NotFound("Post")

        return res

    @refresh_on_error
    def get_pins(self):
        """Get list of pins
        """
        res = get_pins(self.token)

        return res

    @refresh_on_error
    def remove_pin(self):
        """Remove pin"""
        remove_pin(self.token)

    @refresh_on_error
    def set_pin(self, slug: str):
        """Set pin

        Args:
            slug (str): Pin slug

        Raises:
            ValidationError: Validation error
            PinNotOwned: Pin not owned
        """
        res = set_pin(self.token, slug)
        if isinstance(res, Error):
            match res.code:
                case 'VALIDATION_ERROR':
                    if hasattr(res, 'found'):
                        raise ValidationError(*list(res.found.items())[0])
                case 'PIN_NOT_OWNED':
                    raise PinNotOwned(slug)
        
        return res
    
    @refresh_on_error
    def vote(self, ids: list[UUID]):
        """Vote for options in poll

        Args:
            ids (list[UUID]): UUIDs of options in poll
        """

        return vote(self.token, ids)
    
    @refresh_on_error
    def get_file(self, id: UUID) -> Attachment:
        """Получить файл

        Args:
            id (UUID): UUID файла

        Raises:
            NotFoundOrForbidden: Файл не найден или нет доступа

        Returns:
            File: Файл
        """
        res = get_file(self.token, id)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFoundOrForbidden('File')

        return res

    @refresh_on_error
    def delete_file(self, id: UUID) -> Attachment:
        """Удалить файл

        Args:
            id (UUID): UUID файла

        Raises:
            NotFound: Файл не найден
        """
        res = delete_file(self.token, id)
        if isinstance(res, Error):
            match res.code:
                case 'NOT_FOUND':
                    raise NotFound('File')

        return res