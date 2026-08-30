import dataclasses

from app.authentication.domain.bo.user_bo import UserBO
from app.authentication.domain.persistences.exceptions import (
    UsernameAlreadyTakenException,
    UserNotFoundException,
)
from app.authentication.domain.persistences.user_bo_interface import UserBOInterface


class UserBOMemoryService(UserBOInterface):
    def __init__(self):
        self.users: dict[str, UserBO] = {}
        self.next_external_id = 1

    async def create(self, user: UserBO) -> UserBO:
        if user.username in self.users:
            raise UsernameAlreadyTakenException(user.username)
        stored = dataclasses.replace(user, external_id=self.next_external_id)
        self.next_external_id += 1
        self.users[stored.username] = stored
        return stored

    async def get_by_username(self, username: str) -> UserBO:
        if username not in self.users:
            raise UserNotFoundException(username)
        return self.users[username]

    async def get_by_external_id(self, external_id: int) -> UserBO:
        for user in self.users.values():
            if user.external_id == external_id:
                return user
        raise UserNotFoundException(external_id)
