from app.authentication.domain.password_hasher import hash_password
from app.authentication.domain.persistences.exceptions import WrongPasswordException
from app.authentication.domain.persistences.token_interface import TokenInterface
from app.authentication.domain.persistences.user_bo_interface import UserBOInterface


class LoginController:
    def __init__(self, user_bo_persistence: UserBOInterface, token_persistence: TokenInterface):
        self.user_bo_persistence = user_bo_persistence
        self.token_persistence = token_persistence

    async def execute(self, username: str, password: str) -> str:
        user = await self.user_bo_persistence.get_by_username(username)
        if user.password != hash_password(username, password):
            raise WrongPasswordException(username)
        return self.token_persistence.generate_token(user.username)
