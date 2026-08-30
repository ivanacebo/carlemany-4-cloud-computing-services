from dependency_injector import containers, providers

from app.authentication.persistence.memory.token import TokenMemoryService


class TokenPersistences(containers.DeclarativeContainer):
    """Available implementations of TokenInterface, plus the one currently in use."""

    memory = providers.Singleton(TokenMemoryService)

    # The implementation the rest of the application receives. Switching to Redis
    # is a one line change here: nothing outside this container names an
    # implementation.
    default = memory
