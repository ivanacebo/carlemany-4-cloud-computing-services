from dependency_injector import containers, providers

from app.files.persistence.memory.file_storage import FileStorageMemoryService


class FileStoragePersistences(containers.DeclarativeContainer):
    """Available implementations of FileStorageInterface, plus the one currently in use."""

    memory = providers.Singleton(FileStorageMemoryService)

    # MinIO goes here, next to memory, once its adapter is written:
    #     minio = providers.Singleton(MinioFileStorageService, ...)
    # and default switches to it. Nothing outside this container names an
    # implementation, so that is the whole change.
    default = memory
