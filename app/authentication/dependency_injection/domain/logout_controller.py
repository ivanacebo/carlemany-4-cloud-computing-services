from dependency_injector import containers, providers

from app.authentication.domain.controllers.logout_controller import LogoutController


class LogoutControllerContainer(containers.DeclarativeContainer):
    token_persistences = providers.DependenciesContainer()

    logout_controller = providers.Singleton(
        LogoutController,
        token_persistence=token_persistences.default,
    )
