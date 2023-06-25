import itertools
import re
from typing import TypedDict, List, Dict

import src.auxiliary.db as db


class UserContent(TypedDict):
    user_id: int
    content_id: str
    content_file_id: str
    descriptions: List[str]
    groups: List[str]
    type: str


MIN_DESCRIPTION_SIZE = 2
STICKER_CONTENT = 'sticker'
VOICE_MESSAGE_CONTENT = 'voice-message'


def split_descriptions(description: str) -> List[str]:
    split = re.split('[;,!?]+', description)
    filtered = filter(lambda x: x and len(x) > MIN_DESCRIPTION_SIZE, split)
    return list(filtered)


def save_user_content(content: UserContent):
    with db.get_db_client() as client:
        client[db.DB_NAME][db.USER_CONTENT_NAME].insert_one(content)


def search_user_content(query: str) -> List[UserContent]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({
            'descriptions': {
                '$regex': f'^.*{query}.*$',
                '$options': 'i'
            }
        })
        user_content = [UserContent(**item) for item in items]
        user_content_dict = dict(map(lambda x: (x['content_id'], x), user_content))
        return list(user_content_dict.values())


def get_all_sticker_descriptions(sticker_id: str) -> List[str]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({'content_id': sticker_id})
        descriptions = map(lambda item: item['descriptions'], items)
        return list(itertools.chain.from_iterable(descriptions))
