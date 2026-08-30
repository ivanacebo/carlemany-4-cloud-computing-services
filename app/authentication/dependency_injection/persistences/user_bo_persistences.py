from dependency_injector import containers, providers

from app.authentication.persistence.memory.user_bo import UserBOMemoryService


class UserBOPersistences(containers.DeclarativeContainer):
    """Available implementations of UserBOInterface, plus the one currently in use."""

    memory = providers.Singleton(UserBOMemoryService)

    # The implementation the rest of the application receives. Switching to
    # Postgres is a one line change here.
    default = memory
