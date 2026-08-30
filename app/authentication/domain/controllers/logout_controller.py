from app.authentication.domain.persistences.token_interface import TokenInterface


class LogoutController:
    def __init__(self, token_persistence: TokenInterface):
        self.token_persistence = token_persistence

    async def execute(self, token: str) -> None:
        self.token_persistence.delete_token(token)
