import asyncio
import os
import tempfile
import uuid

from pypdf import PdfMerger

from app.files.domain.bo.file_bo import FileBO
from app.files.domain.persistences.exceptions import (
    FileContentNotUploadedException,
    FileOwnershipException,
)
from app.files.domain.persistences.file_bo_interface import FileBOInterface
from app.files.domain.persistences.file_storage_interface import FileStorageInterface


class MergeFilesController:
    def __init__(
        self,
        file_bo_persistence: FileBOInterface,
        file_storage_persistence: FileStorageInterface,
    ):
        self.file_bo_persistence = file_bo_persistence
        self.file_storage_persistence = file_storage_persistence

    async def execute(
        self, origin_external_id: int, addition_external_id: int, owner_external_id: int
    ) -> FileBO:
        origin = await self._get_mergeable(origin_external_id, owner_external_id)
        addition = await self._get_mergeable(addition_external_id, owner_external_id)

        # One directory per invocation, removed by the context manager even if the merge
        # raises. Writing to the storage folder instead would assume the storage is a local
        # directory, which stops being true as soon as the MinIO adapter is the one wired.
        with tempfile.TemporaryDirectory() as workspace:
            origin_path = await self._download(origin, workspace, "origin")
            addition_path = await self._download(addition, workspace, "addition")
            merged_path = os.path.join(workspace, f"{uuid.uuid4()}.pdf")

            # PdfMerger is blocking, and awaiting it in a thread keeps a merge of two large
            # documents from freezing every other request being served.
            await asyncio.to_thread(self._merge, [origin_path, addition_path], merged_path)

            # Content first, metadata second, as in the delete: a failure between the two
            # leaves content nothing points at, never a file listed and broken.
            remote_identifier = await self.file_storage_persistence.put_file(
                merged_path, f"{uuid.uuid4()}.pdf"
            )

        merged = FileBO(
            title=f"{origin.title}_{addition.title}",
            author=origin.author,
            owner_external_id=owner_external_id,
            remote_identifier=remote_identifier,
        )
        return await self.file_bo_persistence.create(merged)

    async def _get_mergeable(self, external_id: int, owner_external_id: int) -> FileBO:
        file = await self.file_bo_persistence.get_by_external_id(external_id)
        if not file.is_owned_by(owner_external_id):
            raise FileOwnershipException(external_id)
        if file.remote_identifier is None:
            raise FileContentNotUploadedException(external_id)
        return file

    async def _download(self, file: FileBO, workspace: str, folder_name: str) -> str:
        # A folder per operand: get_file names the download after the basename of the
        # remote path, so two identifiers sharing one would silently overwrite each other
        # and the merge would append the same document twice.
        folder = os.path.join(workspace, folder_name)
        os.makedirs(folder)
        return await self.file_storage_persistence.get_file(file.remote_identifier, folder)

    @staticmethod
    def _merge(sources: list[str], destination: str):
        merger = PdfMerger()
        for source in sources:
            merger.append(source)
        merger.write(destination)
        merger.close()
