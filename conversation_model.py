import json
from dataclasses import dataclass, asdict
from typing import Optional, Tuple

from telegram.ext._utils.types import ConversationKey

import configs
from aws import get_db


@dataclass
class ConversationData:
    id: str
    key: str
    user_id: int
    name: str
    state: str

    @staticmethod
    def create_id(name: str, user_id: int):
        return f"{user_id}_{name}"


def update_or_create_conversation_data(
        user_id: int,
        key: ConversationKey,
        name: str,
        state: Optional[object]
) -> None:
    if state is None:
        actual_state = None
    else:
        actual_state = json.dumps(state)

    data = ConversationData(
        id=ConversationData.create_id(name=name, user_id=user_id),
        user_id=user_id,
        name=name,
        key=json.dumps(key, sort_keys=True),
        state=actual_state
    )
    get_db().Table(configs.conversation_table_name).put_item(Item=asdict(data))


def get_conversation_data(
        user_id: int,
        conversation_name: str
) -> dict:
    table = get_db().Table(configs.conversation_table_name)
    item = table.get_item(Key={'id': ConversationData.create_id(name=conversation_name, user_id=user_id)})
    if item and 'Item' in item:
        key = _array_as_string_to_int_tuple(item['Item']['key'])

        state_str = item['Item']['state']
        state = int(state_str) if state_str else None

        return {key: state}
    else:
        return {}


def _array_as_string_to_int_tuple(value: str) -> Tuple[int]:
    array_of_strings = value.replace('[', '').replace(']', '').split(', ')
    return tuple(int(num) for num in array_of_strings)
