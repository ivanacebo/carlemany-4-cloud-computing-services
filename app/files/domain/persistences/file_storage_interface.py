from abc import ABC, abstractmethod


class FileStorageInterface(ABC):
    @abstractmethod
    async def put_file(self, local_path: str, remote_identifier: str) -> str:
        """Upload a file to storage

        Returns:
            The effective remote identifier under which the file was stored,
            which may differ from the requested one if the implementation
            normalises or namespaces it.
        """

    @abstractmethod
    async def get_file(self, remote_path: str, local_folder: str) -> str:
        """Download a file from storage

        Returns:
            The local path the file was written to, inside local_folder.

        Raises:
            FileNotFoundException: if remote_path does not exist in storage
        """

    @abstractmethod
    async def remove_file(self, remote_identifier: str):
        """Delete a file from storage

        Raises:
            FileNotFoundException: if remote_identifier does not exist in storage
        """
