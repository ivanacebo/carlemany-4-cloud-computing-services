from dependency_injector import containers, providers

from app.files.domain.controllers.merge_files_controller import MergeFilesController


class MergeFilesControllerContainer(containers.DeclarativeContainer):
    file_bo_persistences = providers.DependenciesContainer()
    file_storage_persistences = providers.DependenciesContainer()

    merge_files_controller = providers.Singleton(
        MergeFilesController,
        file_bo_persistence=file_bo_persistences.default,
        file_storage_persistence=file_storage_persistences.default,
    )
