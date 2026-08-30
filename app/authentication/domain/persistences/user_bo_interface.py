from abc import ABC, abstractmethod

from app.authentication.domain.bo.user_bo import UserBO


class UserBOInterface(ABC):
    @abstractmethod
    async def create(self, user: UserBO) -> UserBO:
        """Persist a new user

        Returns:
            The stored user, with its external_id assigned by the
            implementation. The external_id of the given user is ignored.

        Raises:
            UsernameAlreadyTakenException: if the username is already registered
        """

    @abstractmethod
    async def get_by_username(self, username: str) -> UserBO:
        """Retrieve a user by username

        Raises:
            UserNotFoundException: if no user has that username
        """

    @abstractmethod
    async def get_by_external_id(self, external_id: int) -> UserBO:
        """Retrieve a user by external identifier

        Raises:
            UserNotFoundException: if no user has that external identifier
        """
