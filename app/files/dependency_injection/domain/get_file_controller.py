from dependency_injector import containers, providers

from app.files.domain.controllers.get_file_controller import GetFileController


class GetFileControllerContainer(containers.DeclarativeContainer):
    file_bo_persistences = providers.DependenciesContainer()

    get_file_controller = providers.Singleton(
        GetFileController,
        file_bo_persistence=file_bo_persistences.default,
    )
