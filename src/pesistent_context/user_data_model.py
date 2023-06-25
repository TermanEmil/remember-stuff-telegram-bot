from typing import TypedDict

import src.auxiliary.db as db


class UserData(TypedDict):
    user_id: int
    data: dict


def update_or_create_user_data(user_id: int, data: dict) -> None:
    if len(data) > 0:
        if 'subscribed_groups' not in data:
            data['subscribed_groups'] = [f'user-{user_id}', 'public']

        user_data = UserData(user_id=user_id, data=data)

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
        return item['data']
