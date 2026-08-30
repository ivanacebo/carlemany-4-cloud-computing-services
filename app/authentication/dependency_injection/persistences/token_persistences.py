from dependency_injector import containers, providers

from app.authentication.persistence.memory.token import TokenMemoryService
from app.authentication.persistence.redis.token import TokenRedisService
from app.config import redis_settings


class TokenPersistences(containers.DeclarativeContainer):
    """Available implementations of TokenInterface, plus the one currently in use."""

    memory = providers.Singleton(TokenMemoryService)
    redis = providers.Singleton(
        TokenRedisService,
        host=redis_settings.host,
        port=redis_settings.port,
        db=redis_settings.db,
        expiration_time=redis_settings.token_expiration_time,
    )

    # The implementation the rest of the application receives. Redis now, so that sessions
    # expire on their own and survive a restart of the application. Going back to memory is
    # a one line change here: nothing outside this container names an implementation.
    default = redis
