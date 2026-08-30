from abc import ABC, abstractmethod

from app.files.domain.bo.file_bo import FileBO


class FileBOInterface(ABC):
    @abstractmethod
    async def create(self, file: FileBO) -> FileBO:
        """Persist the metadata of a new file

        Returns:
            The stored file, with its external_id assigned by the
            implementation. The external_id of the given file is ignored.
        """

    @abstractmethod
    async def get_by_external_id(self, external_id: int) -> FileBO:
        """Retrieve a file by external identifier

        Raises:
            FileBONotFoundException: if no file has that external identifier
        """

    @abstractmethod
    async def get_by_owner(self, owner_external_id: int) -> list[FileBO]:
        """Retrieve every file owned by a user

        Returns:
            The files owned by that user, or an empty list if there is none.
        """

    @abstractmethod
    async def update(self, file: FileBO) -> FileBO:
        """Persist the changes made to an already stored file

        Returns:
            The stored file.

        Raises:
            FileBONotFoundException: if the file external_id is not stored
        """

    @abstractmethod
    async def delete(self, external_id: int):
        """Delete the metadata of a file

        Raises:
            FileBONotFoundException: if no file has that external identifier
        """
