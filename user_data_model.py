from dataclasses import dataclass, asdict
from typing import TypedDict

from pymongo.collection import Collection

import configs
from db import get_db


class UserData(TypedDict):
    user_id: int
    conversation_sticker_id: str


def _get_collection() -> Collection[UserData]:
    return get_db()[configs.db_name][configs.user_data_collection_name]


def update_or_create_user_data(user_id: int, data: dict) -> None:
    if 'conversation_sticker_id' in data:
        user_data = UserData(user_id=user_id, conversation_sticker_id=data['conversation_sticker_id'])
        _get_collection().update_one({'matchable_field': 'user_id'}, {"$set": user_data}, upsert=True)


def get_user_data(user_id: int) -> dict:
    item = _get_collection().find_one({'user_id': user_id})
    if item is None:
        return {}
    else:
        return item
