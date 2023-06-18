from typing import TypedDict, List

from src.models import names
from src.models.db import get_db


class UserContent(TypedDict):
    user_id: int
    content_id: str
    description: str
    groups: List[str]


def save_user_content(content: UserContent):
    with get_db() as db:
        db[names.db][names.user_content].insert_one(content)


def search_user_content(query: str) -> List[UserContent]:
    with get_db() as db:
        items = db[names.db][names.user_content].find({'description': {'$regex': f'.*{query}.*'}})
        return [UserContent(**item) for item in items]
