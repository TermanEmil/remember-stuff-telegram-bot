from dataclasses import dataclass, asdict

import configs
from aws import get_db


@dataclass
class UserData:
    user_id: int
    conversation_sticker_id: str


def _get_table():
    return get_db().Table(configs.user_data_table_name)


def update_or_create_user_data(user_id: int, data: dict) -> None:
    if 'conversation_sticker_id' in data:
        user_data = UserData(user_id=user_id, conversation_sticker_id=data['conversation_sticker_id'])
        _get_table().put_item(Item=asdict(user_data))


def get_user_data(user_id: int) -> dict:
    item = _get_table().get_item(Key={'user_id': user_id})
    if item and 'Item' in item:
        return item['Item']
    else:
        return {}
