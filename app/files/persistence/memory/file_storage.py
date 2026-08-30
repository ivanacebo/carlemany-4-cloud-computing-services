import os
import shutil

from app.files.domain.persistences.exceptions import FileNotFoundException
from app.files.domain.persistences.file_storage_interface import FileStorageInterface


class FileStorageMemoryService(FileStorageInterface):
    def __init__(self, base_folder: str = "files"):
        self.base_folder = os.path.abspath(base_folder)
        os.makedirs(self.base_folder, exist_ok=True)

    def _resolve(self, identifier: str) -> str:
        path = os.path.abspath(os.path.join(self.base_folder, identifier))
        # Identifiers reach us from the request, so without this an id like "../../etc/passwd"
        # would read or delete files outside base_folder.
        if os.path.commonpath([self.base_folder, path]) != self.base_folder:
            raise ValueError("Invalid remote identifier: " + identifier)
        return path

    async def put_file(self, local_path: str, remote_identifier: str) -> str:
        destination = self._resolve(remote_identifier)
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        shutil.copyfile(local_path, destination)
        return remote_identifier

    async def get_file(self, remote_path: str, local_folder: str) -> str:
        source = self._resolve(remote_path)
        if not os.path.isfile(source):
            raise FileNotFoundException(remote_path)
        destination = os.path.join(local_folder, os.path.basename(remote_path))
        shutil.copyfile(source, destination)
        return destination

    async def remove_file(self, remote_identifier: str):
        path = self._resolve(remote_identifier)
        if not os.path.isfile(path):
            raise FileNotFoundException(remote_identifier)
        os.remove(path)
