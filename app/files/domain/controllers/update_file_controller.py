import uuid

from app.files.domain.bo.file_bo import FileBO
from app.files.domain.persistences.exceptions import (
    FileNotFoundException,
    FileOwnershipException,
)
from app.files.domain.persistences.file_bo_interface import FileBOInterface
from app.files.domain.persistences.file_storage_interface import FileStorageInterface


class UpdateFileController:
    def __init__(
        self,
        file_bo_persistence: FileBOInterface,
        file_storage_persistence: FileStorageInterface,
    ):
        self.file_bo_persistence = file_bo_persistence
        self.file_storage_persistence = file_storage_persistence

    async def execute(self, external_id: int, owner_external_id: int, local_path: str) -> FileBO:
        file = await self.file_bo_persistence.get_by_external_id(external_id)
        if not file.is_owned_by(owner_external_id):
            raise FileOwnershipException(external_id)

        previous_identifier = file.remote_identifier
        # A new identifier on every upload instead of overwriting the previous content:
        # an upload that fails halfway leaves the stored file untouched, and the metadata
        # update below becomes the single point where the new content takes over.
        # The identifier kept is the one the storage returns, not the one requested,
        # because the implementation is free to namespace it.
        remote_identifier = await self.file_storage_persistence.put_file(
            local_path, f"{uuid.uuid4()}.pdf"
        )

        file.remote_identifier = remote_identifier
        updated = await self.file_bo_persistence.update(file)

        if previous_identifier is not None:
            # The metadata no longer points here, so this content is already unreachable.
            # Failing to remove it only wastes space, and the request already succeeded.
            try:
                await self.file_storage_persistence.remove_file(previous_identifier)
            except FileNotFoundException:
                pass

        return updated
