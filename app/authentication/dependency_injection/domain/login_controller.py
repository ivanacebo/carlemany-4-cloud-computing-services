from dependency_injector import containers, providers

from app.authentication.domain.controllers.login_controller import LoginController


class LoginControllerContainer(containers.DeclarativeContainer):
    user_bo_persistences = providers.DependenciesContainer()
    token_persistences = providers.DependenciesContainer()

    login_controller = providers.Singleton(
        LoginController,
        user_bo_persistence=user_bo_persistences.default,
        token_persistence=token_persistences.default,
    )
