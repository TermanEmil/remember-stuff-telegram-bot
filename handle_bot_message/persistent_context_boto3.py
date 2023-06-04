from typing import Dict, Optional

from telegram.ext import BasePersistence, PersistenceInput
from telegram.ext._utils.types import CD, BD, CDCData, ConversationDict, ConversationKey, UD

from models import update_or_create_conversation_data, get_conversation_data


class Boto3ConversationPersistence(BasePersistence[UD, CD, BD]):
    def __init__(
            self,
            user_id: int,
            store_data: PersistenceInput = None,
            update_interval: float = 60
    ):
        super().__init__(
            store_data=store_data,
            update_interval=update_interval
        )
        self.user_id = user_id

    async def get_chat_data(self) -> Dict[int, CD]:
        return {}

    async def get_bot_data(self) -> BD:
        return {}

    async def get_callback_data(self) -> Optional[CDCData]:
        return None

    async def get_conversations(self, name: str) -> ConversationDict:
        return get_conversation_data(self.user_id, name)

    async def update_conversation(self, name: str, key: ConversationKey, new_state: Optional[object]) -> None:
        update_or_create_conversation_data(user_id=self.user_id, key=key, name=name, state=new_state)
        pass

    async def update_user_data(self, user_id: int, data: UD) -> None:
        pass

    async def update_chat_data(self, chat_id: int, data: CD) -> None:
        pass

    async def update_bot_data(self, data: BD) -> None:
        pass

    async def update_callback_data(self, data: CDCData) -> None:
        pass

    async def drop_chat_data(self, chat_id: int) -> None:
        pass

    async def drop_user_data(self, user_id: int) -> None:
        pass

    async def refresh_user_data(self, user_id: int, user_data: UD) -> None:
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data: CD) -> None:
        pass

    async def refresh_bot_data(self, bot_data: BD) -> None:
        pass

    async def flush(self) -> None:
        pass

    async def get_user_data(self) -> Dict[int, UD]:
        return {}

