import asyncio
import os

from minio import Minio
from minio.error import S3Error
from urllib3.exceptions import HTTPError

from app.files.domain.persistences.exceptions import (
    FileNotFoundException,
    FileStorageUnavailableException,
)
from app.files.domain.persistences.file_storage_interface import FileStorageInterface

# S3 answers a missing object under either of these codes depending on the operation.
MISSING_OBJECT_CODES = ("NoSuchKey", "NoSuchObject")


class MinioFileStorageService(FileStorageInterface):
    """FileStorageInterface backed by MinIO."""

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
    ):
        self.bucket = bucket
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    @staticmethod
    async def _call(operation, *args, identifier: str = None):
        """Run a blocking minio operation off the event loop, translating its failures.

        S3Error carries no object name of its own, so the identifier the caller asked for is
        the one that travels into the domain exception.

        The interface is asynchronous and the client is not, so every call goes to a thread
        the same way MergeFilesController hands PdfMerger to one. Here it matters more: an
        upload moves a whole document across the network, so the block would last as long as
        the transfer and freeze every other request being served meanwhile.
        """
        try:
            return await asyncio.to_thread(operation, *args)
        except S3Error as error:
            if error.code in MISSING_OBJECT_CODES:
                raise FileNotFoundException(identifier) from error
            # A missing bucket or refused credentials are not the file's fault, so they must
            # not reach the caller as "this file does not exist".
            raise FileStorageUnavailableException(error.code) from error
        except HTTPError as error:
            raise FileStorageUnavailableException("Cannot reach the file storage") from error

    async def put_file(self, local_path: str, remote_identifier: str) -> str:
        # A missing local_path raises the native FileNotFoundError from inside minio, which
        # is what the contract asks for: it is a mistake of the caller, not a missing object.
        await self._call(self.client.fput_object, self.bucket, remote_identifier, local_path)
        return remote_identifier

    async def get_file(self, remote_path: str, local_folder: str) -> str:
        # Same naming as the in memory implementation, so both behave alike for a caller:
        # the basename of the identifier inside the folder it was given. A file already
        # sitting there under that name is overwritten, which is why MergeFilesController
        # downloads each of its two operands into a folder of its own.
        destination = os.path.join(local_folder, os.path.basename(remote_path))
        await self._call(
            self.client.fget_object, self.bucket, remote_path, destination, identifier=remote_path
        )
        return destination

    async def remove_file(self, remote_identifier: str):
        # remove_object succeeds on an object that is not there, so its absence has to be
        # asked for separately to keep the FileNotFoundException the contract promises.
        await self._call(
            self.client.stat_object, self.bucket, remote_identifier, identifier=remote_identifier
        )
        await self._call(self.client.remove_object, self.bucket, remote_identifier)
