from app.files.domain.bo.file_bo import FileBO
from app.files.domain.persistences.file_bo_interface import FileBOInterface


class CreateFileController:
    def __init__(self, file_bo_persistence: FileBOInterface):
        self.file_bo_persistence = file_bo_persistence

    async def execute(self, title: str, author: str, owner_external_id: int) -> FileBO:
        file = FileBO(
            title=title,
            author=author,
            owner_external_id=owner_external_id,
        )
        return await self.file_bo_persistence.create(file)
