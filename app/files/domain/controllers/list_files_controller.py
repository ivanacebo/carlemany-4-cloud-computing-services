from app.files.domain.bo.file_bo import FileBO
from app.files.domain.persistences.file_bo_interface import FileBOInterface


class ListFilesController:
    def __init__(self, file_bo_persistence: FileBOInterface):
        self.file_bo_persistence = file_bo_persistence

    async def execute(self, owner_external_id: int) -> list[FileBO]:
        return await self.file_bo_persistence.get_by_owner(owner_external_id)
