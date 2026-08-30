import uuid

from app.authentication.domain.persistences.exceptions import TokenNotFound
from app.authentication.domain.persistences.token_interface import TokenInterface


class TokenMemoryService(TokenInterface):
    def __init__(self):
        self.tokens: dict[str, str] = {}

    def generate_token(self, username: str) -> str:
        token = str(uuid.uuid4())
        while token in self.tokens:
            token = str(uuid.uuid4())
        self.tokens[token] = username
        return token

    def delete_token(self, token: str):
        if token not in self.tokens:
            raise TokenNotFound(token)
        del self.tokens[token]

    def get_username(self, token: str) -> str:
        if token not in self.tokens:
            raise TokenNotFound(token)
        return self.tokens[token]
