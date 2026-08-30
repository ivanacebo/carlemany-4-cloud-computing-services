from abc import ABC, abstractmethod


class TokenInterface(ABC):
    @abstractmethod
    def generate_token(self, username: str) -> str:
        """Generate a new session token for a user"""

    @abstractmethod
    def delete_token(self, token: str):
        """Delete/invalidate a session token

        Raises:
            TokenNotFound: if the token does not exist
        """

    @abstractmethod
    def get_username(self, token: str) -> str:
        """Retrieve username associated with a token

        Raises:
            TokenNotFound: if the token does not exist
        """
