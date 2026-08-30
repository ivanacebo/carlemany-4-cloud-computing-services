import dataclasses

from app.files.domain.bo.file_bo import FileBO
from app.files.domain.persistences.exceptions import FileBONotFoundException
from app.files.domain.persistences.file_bo_interface import FileBOInterface


class FileBOMemoryService(FileBOInterface):
    def __init__(self):
        self.files: dict[int, FileBO] = {}
        self.next_external_id = 1

    async def create(self, file: FileBO) -> FileBO:
        stored = dataclasses.replace(file, external_id=self.next_external_id)
        self.next_external_id += 1
        self.files[stored.external_id] = stored
        return dataclasses.replace(stored)

    async def get_by_external_id(self, external_id: int) -> FileBO:
        if external_id not in self.files:
            raise FileBONotFoundException(external_id)
        # A copy, so that mutating what a caller received does not silently change
        # what is stored. A database backed implementation cannot behave any other
        # way, and callers must go through update() with either of them.
        return dataclasses.replace(self.files[external_id])

    async def get_by_owner(self, owner_external_id: int) -> list[FileBO]:
        return [
            dataclasses.replace(file)
            for file in self.files.values()
            if file.is_owned_by(owner_external_id)
        ]

    async def update(self, file: FileBO) -> FileBO:
        if file.external_id not in self.files:
            raise FileBONotFoundException(file.external_id)
        stored = dataclasses.replace(file)
        self.files[stored.external_id] = stored
        return dataclasses.replace(stored)

    async def delete(self, external_id: int):
        if external_id not in self.files:
            raise FileBONotFoundException(external_id)
        del self.files[external_id]
