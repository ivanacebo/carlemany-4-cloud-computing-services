from dependency_injector import containers, providers

from app.config import minio_settings
from app.files.persistence.memory.file_storage import FileStorageMemoryService
from app.files.persistence.minio.minio_file_storage_service import MinioFileStorageService


class FileStoragePersistences(containers.DeclarativeContainer):
    """Available implementations of FileStorageInterface, plus the one currently in use."""

    memory = providers.Singleton(FileStorageMemoryService)
    minio = providers.Singleton(
        MinioFileStorageService,
        endpoint=minio_settings.endpoint,
        access_key=minio_settings.access_key,
        secret_key=minio_settings.secret_key,
        bucket=minio_settings.bucket,
        secure=minio_settings.secure,
    )

    # The implementation the rest of the application receives. MinIO now, so the content of
    # the files stops living in the local disk of whichever container served the upload.
    # Going back to memory is a one line change here: nothing outside this container names
    # an implementation.
    default = minio
