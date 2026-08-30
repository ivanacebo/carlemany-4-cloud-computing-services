from dependency_injector import containers, providers

from app.files.domain.controllers.delete_file_controller import DeleteFileController


class DeleteFileControllerContainer(containers.DeclarativeContainer):
    file_bo_persistences = providers.DependenciesContainer()
    file_storage_persistences = providers.DependenciesContainer()

    delete_file_controller = providers.Singleton(
        DeleteFileController,
        file_bo_persistence=file_bo_persistences.default,
        file_storage_persistence=file_storage_persistences.default,
    )
