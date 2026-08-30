from dependency_injector import containers, providers

from app.authentication.domain.controllers.introspect_controller import IntrospectController


class IntrospectControllerContainer(containers.DeclarativeContainer):
    token_persistences = providers.DependenciesContainer()
    user_bo_persistences = providers.DependenciesContainer()

    introspect_controller = providers.Singleton(
        IntrospectController,
        token_persistence=token_persistences.default,
        user_bo_persistence=user_bo_persistences.default,
    )
