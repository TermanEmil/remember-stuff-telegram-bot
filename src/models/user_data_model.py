from typing import TypedDict

from src.models import names
from src.models.db import get_db


class UserData(TypedDict):
    user_id: int
    conversation_sticker_id: str


def update_or_create_user_data(user_id: int, data: dict) -> None:
    if 'conversation_sticker_id' in data:
        user_data = UserData(user_id=user_id, conversation_sticker_id=data['conversation_sticker_id'])

        with get_db() as db:
            db[names.db][names.user_data].update_one(
                {'matchable_field': 'user_id'},
                {"$set": user_data}, upsert=True
            )


def get_user_data(user_id: int) -> dict:
    with get_db() as db:
        item = db[names.db][names.user_data].find_one({'user_id': user_id})

    if item is None:
        return {}
    else:
        return item
