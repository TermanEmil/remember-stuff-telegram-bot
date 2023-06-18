import json
from dataclasses import dataclass, asdict
from typing import Optional, Tuple, TypedDict

from pymongo.collection import Collection
from telegram.ext._utils.types import ConversationKey

import configs
from db import get_db


class ConversationData(TypedDict):
    user_id: int
    conversation_name: str
    conversation_key: str
    conversation_state: str


def _get_collection() -> Collection[ConversationData]:
    return get_db()[configs.db_name][configs.conversations_collection_name]


def update_or_create_conversation_data(
        user_id: int,
        conversation_key: ConversationKey,
        conversation_name: str,
        conversation_state: Optional[object]
) -> None:
    if conversation_state is None:
        actual_state = None
    else:
        actual_state = json.dumps(conversation_state)

    data = ConversationData(
        user_id=user_id,
        conversation_name=conversation_name,
        conversation_key=json.dumps(conversation_key, sort_keys=True),
        conversation_state=actual_state
    )

    _get_collection().update_one(
        filter={'user_id': user_id, 'conversation_name': conversation_name},
        update={"$set": data},
        upsert=True
    )


def get_conversation_data(
        user_id: int,
        conversation_name: str
) -> dict:
    conversation = _get_collection().find_one({'user_id': user_id, 'conversation_name': conversation_name})
    if conversation is None:
        return {}

    key = _array_as_string_to_int_tuple(conversation['conversation_key'])

    state_str = conversation['conversation_state']
    state = int(state_str) if state_str else None

    return {key: state}


def _array_as_string_to_int_tuple(value: str) -> Tuple[int]:
    array_of_strings = value.replace('[', '').replace(']', '').split(', ')
    return tuple(int(num) for num in array_of_strings)
