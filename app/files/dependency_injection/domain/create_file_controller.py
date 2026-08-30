from dependency_injector import containers, providers

from app.files.domain.controllers.create_file_controller import CreateFileController


class CreateFileControllerContainer(containers.DeclarativeContainer):
    file_bo_persistences = providers.DependenciesContainer()

    create_file_controller = providers.Singleton(
        CreateFileController,
        file_bo_persistence=file_bo_persistences.default,
    )
