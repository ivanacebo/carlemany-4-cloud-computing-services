from typing import Optional

from app.authentication.domain.bo.user_bo import UserBO
from app.authentication.domain.password_hasher import hash_password
from app.authentication.domain.persistences.user_bo_interface import UserBOInterface


class RegisterController:
    def __init__(self, user_bo_persistence: UserBOInterface):
        self.user_bo_persistence = user_bo_persistence

    async def execute(
        self, username: str, password: str, mail: str, year_of_birth: Optional[int] = None
    ) -> UserBO:
        user = UserBO(
            username=username,
            password=hash_password(username, password),
            mail=mail,
            year_of_birth=year_of_birth,
        )
        return await self.user_bo_persistence.create(user)
