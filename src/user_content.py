import itertools
import re

from typing import TypedDict, List
import src.auxiliary.db as db


class UserContent(TypedDict):
    user_id: int
    content_id: str
    description: str
    groups: List[str]


MIN_DESCRIPTION_SIZE = 2


def _split_descriptions(description: str) -> List[str]:
    split = re.split('[;,!?]+', description)
    filtered = filter(lambda x: x and len(x) > MIN_DESCRIPTION_SIZE, split)
    return list(filtered)


def save_user_content(content: UserContent):
    with db.get_db_client() as client:
        client[db.DB_NAME][db.USER_CONTENT_NAME].insert_one(content)


def search_user_content(query: str) -> List[UserContent]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({'description': {'$regex': f'.*{query}.*'}})
        return [UserContent(**item) for item in items]


def get_all_sticker_descriptions(sticker_id: str) -> List[str]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({'content_id': sticker_id})
        descriptions = (_split_descriptions(item['description']) for item in items)
        return list(itertools.chain.from_iterable(descriptions))
