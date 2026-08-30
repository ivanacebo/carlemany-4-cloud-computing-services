from dependency_injector import containers, providers

from app.files.dependency_injection.domain.create_file_controller import (
    CreateFileControllerContainer,
)
from app.files.dependency_injection.domain.delete_file_controller import (
    DeleteFileControllerContainer,
)
from app.files.dependency_injection.domain.get_file_controller import GetFileControllerContainer
from app.files.dependency_injection.domain.list_files_controller import (
    ListFilesControllerContainer,
)
from app.files.dependency_injection.domain.merge_files_controller import (
    MergeFilesControllerContainer,
)
from app.files.dependency_injection.domain.update_file_controller import (
    UpdateFileControllerContainer,
)
from app.files.dependency_injection.persistences.file_bo_persistences import FileBOPersistences
from app.files.dependency_injection.persistences.file_storage_service import (
    FileStoragePersistences,
)


class FilesContainer(containers.DeclarativeContainer):
    """Composition root of the files module.

    Instantiating this container also wires the API module, so the endpoints
    receive their controllers. Endpoints only work through a wired container:
    without it they silently receive the Provide marker instead of a controller.
    """

    wiring_config = containers.WiringConfiguration(modules=["app.files.api.router"])

    # Resolving who is asking is authentication's business, not this module's, so the
    # IntrospectController is taken from outside instead of built here. Declared as a
    # dependency and bound in main.py, which is the only place that knows both modules
    # exist: importing AuthenticationContainer from here would make files depend on
    # authentication's composition root and give the two modules a fixed order.
    #
    # A single Dependency and not a DependenciesContainer: overriding the latter with a
    # container is broken in dependency_injector 4.41.0, the pinned version, which raises
    # AttributeError on the __self__ provider every container exposes. Declaring only the
    # provider actually needed also keeps the rest of authentication out of reach from here.
    introspect_controller = providers.Dependency()

    file_bo_persistences = providers.Container(FileBOPersistences)
    file_storage_persistences = providers.Container(FileStoragePersistences)

    create_file = providers.Container(
        CreateFileControllerContainer,
        file_bo_persistences=file_bo_persistences,
    )
    get_file = providers.Container(
        GetFileControllerContainer,
        file_bo_persistences=file_bo_persistences,
    )
    list_files = providers.Container(
        ListFilesControllerContainer,
        file_bo_persistences=file_bo_persistences,
    )
    update_file = providers.Container(
        UpdateFileControllerContainer,
        file_bo_persistences=file_bo_persistences,
        file_storage_persistences=file_storage_persistences,
    )
    delete_file = providers.Container(
        DeleteFileControllerContainer,
        file_bo_persistences=file_bo_persistences,
        file_storage_persistences=file_storage_persistences,
    )
    merge_files = providers.Container(
        MergeFilesControllerContainer,
        file_bo_persistences=file_bo_persistences,
        file_storage_persistences=file_storage_persistences,
    )
