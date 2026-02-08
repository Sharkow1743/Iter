from iter.models.base import IterBaseModel, PostgresDateTime

class ShortPin(IterBaseModel):
    slug: str
    name: str
    description: str


class Pin(ShortPin):
    granted_at: PostgresDateTime