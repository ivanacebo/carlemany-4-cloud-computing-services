from dependency_injector import containers, providers

from app.authentication.domain.controllers.register_controller import RegisterController


class RegisterControllerContainer(containers.DeclarativeContainer):
    user_bo_persistences = providers.DependenciesContainer()

    register_controller = providers.Singleton(
        RegisterController,
        user_bo_persistence=user_bo_persistences.default,
    )
