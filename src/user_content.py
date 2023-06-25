import itertools
import re
from typing import TypedDict, List, Optional

from pymongo.results import UpdateResult

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


def delete_content_description(user_id: int, content_id: int, description: str) -> Optional[UserContent]:
    with db.get_db_client() as client:
        deleted_element = client[db.DB_NAME][db.USER_CONTENT_NAME].find_one_and_update(
            {
                'user_id': user_id,
                'content_id': content_id,
                'descriptions': {
                    '$regex': f'^{description}$',
                    '$options': 'i'
                }
            },
            {
                '$pull': {
                    'descriptions': {
                        '$regex': f'^{description}$',
                        '$options': 'i'
                    }
                }
            })
        return deleted_element


def search_user_content(groups: List[str], query: str) -> List[UserContent]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({
            'groups': {
              '$in': groups
            },
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
        return list(sorted(itertools.chain.from_iterable(descriptions)))
