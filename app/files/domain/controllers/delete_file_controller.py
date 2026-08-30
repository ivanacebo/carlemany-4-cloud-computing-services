from app.files.domain.persistences.exceptions import (
    FileNotFoundException,
    FileOwnershipException,
)
from app.files.domain.persistences.file_bo_interface import FileBOInterface
from app.files.domain.persistences.file_storage_interface import FileStorageInterface


class DeleteFileController:
    def __init__(
        self,
        file_bo_persistence: FileBOInterface,
        file_storage_persistence: FileStorageInterface,
    ):
        self.file_bo_persistence = file_bo_persistence
        self.file_storage_persistence = file_storage_persistence

    async def execute(self, external_id: int, owner_external_id: int):
        file = await self.file_bo_persistence.get_by_external_id(external_id)
        if not file.is_owned_by(owner_external_id):
            raise FileOwnershipException(external_id)

        # Metadata first. The two stores share no transaction, so one of the two possible
        # inconsistencies is unavoidable: losing the call below leaves content that
        # nothing references, which a sweep comparing storage against metadata can
        # collect. The opposite order would leave the file listed and broken for its
        # owner, which is the same amount of garbage but visible.
        await self.file_bo_persistence.delete(external_id)

        if file.remote_identifier is None:
            # Created by POST /files and never uploaded, so there is no content to remove.
            # This has to be checked here and not caught below: handing None to the
            # storage does not raise FileNotFoundException, it breaks inside path handling.
            return

        try:
            await self.file_storage_persistence.remove_file(file.remote_identifier)
        except FileNotFoundException:
            # Already gone. What the request asks for is that the content does not exist,
            # and it does not, so a retry converges instead of failing again.
            pass
