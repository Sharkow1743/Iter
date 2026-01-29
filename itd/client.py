from itd.users import get_user
from itd.comments import get_comments, add_comment, delete_comment, like_comment, unlike_comment, update_comment
from itd.hashtags import get_hastags, get_posts_by_hastag

class Client:
    def __init__(self, token: str):
        self.token = token.replace('Bearer ', '')

    def get_user(self, username: str) -> dict:
        return get_user(self.token, username)

    def get_me(self) -> dict:
        return self.get_user('me')


    def add_comment(self, post_id: str, content: str, reply_comment_id: str | None = None):
        return add_comment(self.token, post_id, content, reply_comment_id)

    def get_comments(self, post_id: str, limit: int = 20, cursor: int = 0, sort: str = 'popular'):
        return get_comments(self.token, post_id, limit, cursor, sort)

    def like_comment(self, id: str):
        return like_comment(self.token, id)

    def unlike_comment(self, id: str):
        return unlike_comment(self.token, id)

    def delete_comment(self, id: str):
        return delete_comment(self.token, id)

    def update_comment(self, id: str, content: str):
        return update_comment(self.token, id, content)


    def get_hastags(self, limit: int = 10):
        return get_hastags(self.token, limit)

    def get_posts_by_hashtag(self, hashtag: str, limit: int = 20, cursor: int = 0):
        return get_posts_by_hastag(self.token, hashtag, limit, cursor)