from dependency_injector import containers, providers

from app.files.domain.controllers.list_files_controller import ListFilesController


class ListFilesControllerContainer(containers.DeclarativeContainer):
    file_bo_persistences = providers.DependenciesContainer()

    list_files_controller = providers.Singleton(
        ListFilesController,
        file_bo_persistence=file_bo_persistences.default,
    )
