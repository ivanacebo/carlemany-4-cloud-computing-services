from dependency_injector import containers, providers

from app.files.persistence.memory.file_bo import FileBOMemoryService


class FileBOPersistences(containers.DeclarativeContainer):
    """Available implementations of FileBOInterface, plus the one currently in use."""

    memory = providers.Singleton(FileBOMemoryService)

    # The implementation the rest of the application receives. Switching to
    # Postgres is a one line change here.
    default = memory
