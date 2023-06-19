from typing import TypedDict

import src.auxiliary.db as db


class UserData(TypedDict):
    user_id: int
    conversation_sticker_id: str


def update_or_create_user_data(user_id: int, data: dict) -> None:
    if 'conversation_sticker_id' in data:
        user_data = UserData(user_id=user_id, conversation_sticker_id=data['conversation_sticker_id'])

        with db.get_db_client() as client:
            client[db.DB_NAME][db.USER_DATA_NAME].update_one(
                {'matchable_field': 'user_id'},
                {"$set": user_data}, upsert=True
            )


def get_user_data(user_id: int) -> dict:
    with db.get_db_client() as client:
        item = client[db.DB_NAME][db.USER_DATA_NAME].find_one({'user_id': user_id})

    if item is None:
        return {}
    else:
        return item
