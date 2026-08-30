import uuid

from redis import ConnectionError as RedisConnectionError
from redis import Redis, RedisError
from redis import TimeoutError as RedisTimeoutError

from app.authentication.domain.persistences.exceptions import (
    TokenNotFound,
    TokenStorageUnavailable,
)
from app.authentication.domain.persistences.token_interface import TokenInterface


class TokenRedisService(TokenInterface):
    """TokenInterface backed by Redis, where tokens expire on their own.

    That expiry is what this implementation adds over the in memory one: a session ends
    after expiration_time seconds without anybody having to remember to delete it.
    """

    def __init__(
        self,
        host: str,
        port: int,
        expiration_time: int,
        db: int = 0,
        socket_timeout: float = 2.0,
    ):
        self.expiration_time = expiration_time
        # decode_responses=True so that get() answers str and not bytes: the contract of
        # get_username promises a str, and a forgotten .decode() would return bytes that
        # compare unequal to every stored username instead of failing outright.
        # The timeouts bound how long a synchronous call can hold the event loop when
        # Redis stops answering.
        self.client = Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_timeout,
        )

    @staticmethod
    def _key(token: str) -> str:
        # Namespaced so this database can hold something other than sessions later without
        # a token colliding with it.
        return f"token:{token}"

    @staticmethod
    def _call(operation, *args):
        """Run a redis operation, turning its failures into a domain exception.

        Nothing outside this class should ever have to catch a redis exception: that is
        what makes the implementation replaceable.
        """
        try:
            return operation(*args)
        except (RedisConnectionError, RedisTimeoutError) as error:
            raise TokenStorageUnavailable("Cannot reach the token store") from error
        except RedisError as error:
            raise TokenStorageUnavailable("The token store rejected the operation") from error

    def generate_token(self, username: str) -> str:
        token = str(uuid.uuid4())
        while self._call(self.client.exists, self._key(token)):
            token = str(uuid.uuid4())
        self._call(self.client.setex, self._key(token), self.expiration_time, username)
        return token

    def delete_token(self, token: str):
        # delete() answers how many keys it removed, so one round trip tells apart the
        # token that was there from the one that never was.
        if not self._call(self.client.delete, self._key(token)):
            raise TokenNotFound(token)

    def get_username(self, token: str) -> str:
        username = self._call(self.client.get, self._key(token))
        if username is None:
            # Either it never existed or it expired. Both are the same thing to a caller:
            # the token is no longer usable.
            raise TokenNotFound(token)
        return username
