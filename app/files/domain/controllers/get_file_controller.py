from app.files.domain.bo.file_bo import FileBO
from app.files.domain.persistences.exceptions import FileOwnershipException
from app.files.domain.persistences.file_bo_interface import FileBOInterface


class GetFileController:
    def __init__(self, file_bo_persistence: FileBOInterface):
        self.file_bo_persistence = file_bo_persistence

    async def execute(self, external_id: int, owner_external_id: int) -> FileBO:
        file = await self.file_bo_persistence.get_by_external_id(external_id)
        if not file.is_owned_by(owner_external_id):
            raise FileOwnershipException(external_id)
        return file
