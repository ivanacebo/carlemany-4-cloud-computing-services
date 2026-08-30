from app.authentication.domain.bo.user_bo import UserBO
from app.authentication.domain.persistences.token_interface import TokenInterface
from app.authentication.domain.persistences.user_bo_interface import UserBOInterface


class IntrospectController:
    def __init__(self, token_persistence: TokenInterface, user_bo_persistence: UserBOInterface):
        self.token_persistence = token_persistence
        self.user_bo_persistence = user_bo_persistence

    async def execute(self, token: str) -> UserBO:
        username = self.token_persistence.get_username(token)
        return await self.user_bo_persistence.get_by_username(username)
