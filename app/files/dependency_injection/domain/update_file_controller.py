from dependency_injector import containers, providers

from app.files.domain.controllers.update_file_controller import UpdateFileController


class UpdateFileControllerContainer(containers.DeclarativeContainer):
    file_bo_persistences = providers.DependenciesContainer()
    file_storage_persistences = providers.DependenciesContainer()

    update_file_controller = providers.Singleton(
        UpdateFileController,
        file_bo_persistence=file_bo_persistences.default,
        file_storage_persistence=file_storage_persistences.default,
    )
