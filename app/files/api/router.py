import os
import tempfile
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, Header, HTTPException, UploadFile
from pydantic import BaseModel

from app.authentication.domain.bo.user_bo import UserBO
from app.authentication.domain.controllers.introspect_controller import IntrospectController
from app.authentication.domain.persistences.exceptions import TokenNotFound, UserNotFoundException
from app.files.dependency_injection import FilesContainer
from app.files.domain.controllers.create_file_controller import CreateFileController
from app.files.domain.controllers.delete_file_controller import DeleteFileController
from app.files.domain.controllers.get_file_controller import GetFileController
from app.files.domain.controllers.list_files_controller import ListFilesController
from app.files.domain.controllers.merge_files_controller import MergeFilesController
from app.files.domain.controllers.update_file_controller import UpdateFileController
from app.files.domain.bo.file_bo import FileBO
from app.files.domain.persistences.exceptions import (
    FileBONotFoundException,
    FileContentNotUploadedException,
    FileNotFoundException,
    FileOwnershipException,
)

router = APIRouter(tags=["files"])


class FileOutput(BaseModel):
    id: int
    owner_external_id: int
    title: str
    author: str
    remote_identifier: Optional[str] = None


def to_output(file: FileBO) -> FileOutput:
    return FileOutput(
        id=file.external_id,
        owner_external_id=file.owner_external_id,
        title=file.title,
        author=file.author,
        remote_identifier=file.remote_identifier,
    )


# Every endpoint below reaches its controller through @inject plus Provide[...]. Both halves
# are needed: without @inject the parameter keeps the Provide marker as its value and the
# endpoint fails deep inside the controller instead of at startup, with no wiring error.
@inject
async def get_current_user(
    auth: str = Header(),
    introspect_controller: IntrospectController = Depends(
        Provide[FilesContainer.introspect_controller]
    ),
) -> UserBO:
    try:
        return await introspect_controller.execute(auth)
    except (TokenNotFound, UserNotFoundException):
        # 401 and not 403: the caller has no usable identity, so presenting a different
        # token is exactly what would fix it.
        raise HTTPException(status_code=401, detail="Unauthorized")


def raise_not_found():
    """Answer for a file that does not exist and for one that belongs to somebody else.

    Both FileBONotFoundException and FileOwnershipException answer 404 with the same body.
    Telling them apart would let any authenticated user walk the sequential ids and learn
    which ones exist and how many files the rest of the users own, without reading a single
    one of them. The domain keeps the two exceptions separate so that the distinction
    survives in the logs, where it is useful and not reachable from outside.

    The authentication router does not do this: POST /login answers 404 for an unknown user
    and 403 for a wrong password, which is the same oracle and a worse one, since it needs no
    token at all. It is left as it is on purpose. That behaviour comes from the template and
    the status codes are part of the specification of a previous activity, so changing it
    from here would silently modify a deliverable that was already assessed.

    The correct mitigation, if it is ever revisited, is a single answer for both cases, 401
    with a body such as "invalid credentials", never naming which half failed, plus hashing
    the password even when the user does not exist, so that the response time does not
    reintroduce by timing the same distinction the status code stopped making.
    """
    raise HTTPException(status_code=404, detail="File not found")


class PostFilesMerge(BaseModel):
    file_id_1: int
    file_id_2: int


# Declared before /{id} on purpose: FastAPI matches routes in declaration order, and the
# other way round "merge" would be parsed as an id and answered with a 422.
@router.post("/merge")
@inject
async def merge_files(
    input: PostFilesMerge = Body(),
    user: UserBO = Depends(get_current_user),
    merge_files_controller: MergeFilesController = Depends(
        Provide[FilesContainer.merge_files.merge_files_controller]
    ),
) -> int:
    try:
        merged = await merge_files_controller.execute(
            origin_external_id=input.file_id_1,
            addition_external_id=input.file_id_2,
            owner_external_id=user.external_id,
        )
    except (FileBONotFoundException, FileOwnershipException):
        raise_not_found()
    except FileContentNotUploadedException:
        raise HTTPException(status_code=409, detail="File has no content uploaded yet")
    except FileNotFoundException:
        # The metadata says the content is stored and the storage disagrees. Nothing the
        # client sent is wrong, so this is a 500 and not a 4xx.
        raise HTTPException(status_code=500, detail="Stored file content is missing")
    return merged.external_id


@router.get("")
@inject
async def list_files(
    user: UserBO = Depends(get_current_user),
    list_files_controller: ListFilesController = Depends(
        Provide[FilesContainer.list_files.list_files_controller]
    ),
) -> list[FileOutput]:
    files = await list_files_controller.execute(owner_external_id=user.external_id)
    return [to_output(file) for file in files]


class FilesPostInput(BaseModel):
    author: str
    title: str


@router.post("")
@inject
async def create_file(
    input: FilesPostInput = Body(),
    user: UserBO = Depends(get_current_user),
    create_file_controller: CreateFileController = Depends(
        Provide[FilesContainer.create_file.create_file_controller]
    ),
) -> int:
    file = await create_file_controller.execute(
        title=input.title,
        author=input.author,
        owner_external_id=user.external_id,
    )
    return file.external_id


@router.get("/{id}")
@inject
async def get_file(
    id: int,
    user: UserBO = Depends(get_current_user),
    get_file_controller: GetFileController = Depends(
        Provide[FilesContainer.get_file.get_file_controller]
    ),
) -> FileOutput:
    try:
        file = await get_file_controller.execute(
            external_id=id, owner_external_id=user.external_id
        )
    except (FileBONotFoundException, FileOwnershipException):
        raise_not_found()
    return to_output(file)


@router.post("/{id}")
@inject
async def update_file(
    id: int,
    file_content: UploadFile = File(),
    user: UserBO = Depends(get_current_user),
    update_file_controller: UpdateFileController = Depends(
        Provide[FilesContainer.update_file.update_file_controller]
    ),
) -> dict[str, str]:
    # The upload is spooled to a temporary directory that goes away with the request, so a
    # failed upload leaves nothing behind. Turning the multipart body into a local path is
    # the API's job: the controller only knows about paths.
    with tempfile.TemporaryDirectory() as workspace:
        local_path = os.path.join(workspace, "upload.pdf")
        with open(local_path, "wb") as buffer:
            while chunk := await file_content.read(8192):
                buffer.write(chunk)
        try:
            await update_file_controller.execute(
                external_id=id,
                owner_external_id=user.external_id,
                local_path=local_path,
            )
        except (FileBONotFoundException, FileOwnershipException):
            raise_not_found()
    return {}


@router.delete("/{id}")
@inject
async def delete_file(
    id: int,
    user: UserBO = Depends(get_current_user),
    delete_file_controller: DeleteFileController = Depends(
        Provide[FilesContainer.delete_file.delete_file_controller]
    ),
) -> dict[str, str]:
    try:
        await delete_file_controller.execute(
            external_id=id, owner_external_id=user.external_id
        )
    except (FileBONotFoundException, FileOwnershipException):
        raise_not_found()
    return {}
