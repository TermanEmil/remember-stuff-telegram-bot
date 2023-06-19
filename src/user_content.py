from typing import TypedDict, List

import src.auxiliary.db as db


class UserContent(TypedDict):
    user_id: int
    content_id: str
    description: str
    groups: List[str]


def save_user_content(content: UserContent):
    with db.get_db_client() as client:
        client[db.DB_NAME][db.USER_CONTENT_NAME].insert_one(content)


def search_user_content(query: str) -> List[UserContent]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({'description': {'$regex': f'.*{query}.*'}})
        return [UserContent(**item) for item in items]
