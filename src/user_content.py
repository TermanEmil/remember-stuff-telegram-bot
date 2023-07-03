import itertools
import re
from datetime import datetime, timezone
from typing import TypedDict, List, Optional, Iterable, Dict

from pymongo import ASCENDING, DESCENDING
from pymongo.results import UpdateResult
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

import src.auxiliary.db as db


class UserContent(TypedDict):
    user_id: int
    content_id: str
    content_file_id: str
    descriptions: List[str]
    groups: List[str]
    type: str
    title: str
    duration: Optional[int]
    date_created: datetime
    last_updated: datetime


def validate_user_content(content: UserContent) -> Iterable[str]:
    if content['content_id'] is None:
        yield 'Missing content_id'

    if content['content_file_id'] is None:
        yield 'Missing content_file_id'

    if content['groups'] is None or len(content['groups']) == 0:
        yield 'Empty groups are not allowed'

    if content['type'] is None:
        yield 'Missing type'

    if content['type'] not in [STICKER_CONTENT, VOICE_MESSAGE_CONTENT]:
        yield 'Invalid content type'

    if content['descriptions'] is None or len(content['descriptions']) == 0:
        yield 'Empty descriptions are not allowed'


MIN_DESCRIPTION_SIZE = 2
STICKER_CONTENT = 'sticker'
VOICE_MESSAGE_CONTENT = 'voice-message'


def split_descriptions(description: str) -> List[str]:
    split = re.split('[;,!?]+', description)
    filtered = filter(lambda x: x and len(x) > MIN_DESCRIPTION_SIZE, split)
    return list(filtered)


def save_user_content(content: UserContent):
    errors = list(validate_user_content(content))
    if errors:
        raise Exception(f'Failed to save with the following errors: {errors}')

    with db.get_db_client() as client:
        now = datetime.now(timezone.utc)
        content['date_created'] = now
        content['last_updated'] = now
        client[db.DB_NAME][db.USER_CONTENT_NAME].insert_one(content)


def delete_content_description(content_id: int, description: str) -> Optional[UserContent]:
    with db.get_db_client() as client:
        deleted_element = client[db.DB_NAME][db.USER_CONTENT_NAME].find_one_and_update(
            {
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
                },
                '$set': {
                    'last_updated': datetime.now(timezone.utc)
                }
            })

        if deleted_element and len(deleted_element['descriptions']) == 1:
            client[db.DB_NAME][db.USER_CONTENT_NAME].delete_one({'_id': deleted_element['_id']})
        return deleted_element


def user_allowed_to_touch_content(context: dict, user_id: int, content: UserContent) -> bool:
    return f'user-{user_id}' in content['groups']


def find_with_description(content_id: str, description: str) -> Optional[UserContent]:
    with db.get_db_client() as client:
        item = client[db.DB_NAME][db.USER_CONTENT_NAME].find_one({
            'content_id': content_id,
            'descriptions': {
                '$regex': f'^.*{description}.*$',
                '$options': 'i'
            },
        })
        return UserContent(**item) if item else None


def search_user_content(groups: List[str], query: str, content_type: str) -> List[UserContent]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({
            'groups': {
              '$in': groups
            },
            'descriptions': {
                '$regex': f'^.*{query}.*$',
                '$options': 'i'
            },
            'type': content_type
        })
        user_content = [UserContent(**item) for item in items]
        user_content_dict = dict(map(lambda x: (x['content_id'], x), user_content))
        return list(user_content_dict.values())


def get_all_sticker_descriptions(sticker_id: str) -> List[str]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({'content_id': sticker_id})
        descriptions = map(lambda item: item['descriptions'], items)
        return list(sorted(itertools.chain.from_iterable(descriptions)))


def find_content_by_id(content_id: str) -> List[UserContent]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({
            'content_id': content_id,
            'descriptions': {'$exists': True, '$not': {'$size': 0}}
        }).sort([('title', ASCENDING), ('type', ASCENDING), ('last_updated', DESCENDING)])
        return list(items)


# noinspection PyTypeChecker
def get_all_user_described_content(user_id: int, content_type: str) -> Dict[str, List[UserContent]]:
    with db.get_db_client() as client:
        items: List[UserContent]
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({
            'type': content_type,
            'user_id': user_id,
            'descriptions': {
                '$exists': True,
                '$not': {'$size': 0}
            }
        })

        contents: Dict[str, List[UserContent]] = {}
        for item in items:
            contents.setdefault(item['content_id'], []).append(item)

        return contents


def get_all_available_contents(groups: List[str], content_type: str) -> Dict[str, List[UserContent]]:
    with db.get_db_client() as client:
        items = client[db.DB_NAME][db.USER_CONTENT_NAME].find({
            'type': content_type,
            'groups': {
              '$in': groups
            },
            'descriptions': {
                '$exists': True,
                '$not': {'$size': 0}
            }
        }).sort([('last_modified', DESCENDING), ('title', ASCENDING)])
        items = map(lambda x: UserContent(**x), items)

        contents: Dict[str, List[UserContent]] = {}
        for item in items:
            contents.setdefault(item['content_id'], []).append(item)

        return contents
