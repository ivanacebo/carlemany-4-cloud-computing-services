from dependency_injector import containers, providers

from app.authentication.dependency_injection.domain.introspect_controller import (
    IntrospectControllerContainer,
)
from app.authentication.dependency_injection.domain.login_controller import LoginControllerContainer
from app.authentication.dependency_injection.domain.logout_controller import (
    LogoutControllerContainer,
)
from app.authentication.dependency_injection.domain.register_controller import (
    RegisterControllerContainer,
)
from app.authentication.dependency_injection.persistences.token_persistences import (
    TokenPersistences,
)
from app.authentication.dependency_injection.persistences.user_bo_persistences import (
    UserBOPersistences,
)


class AuthenticationContainer(containers.DeclarativeContainer):
    """Composition root of the authentication module.

    Instantiating this container also wires the API module, so the endpoints
    receive their controllers. Endpoints only work through a wired container:
    without it they silently receive the Provide marker instead of a controller.
    """

    wiring_config = containers.WiringConfiguration(modules=["app.authentication.api.router"])

    token_persistences = providers.Container(TokenPersistences)
    user_bo_persistences = providers.Container(UserBOPersistences)

    register = providers.Container(
        RegisterControllerContainer,
        user_bo_persistences=user_bo_persistences,
    )
    login = providers.Container(
        LoginControllerContainer,
        user_bo_persistences=user_bo_persistences,
        token_persistences=token_persistences,
    )
    logout = providers.Container(
        LogoutControllerContainer,
        token_persistences=token_persistences,
    )
    introspect = providers.Container(
        IntrospectControllerContainer,
        token_persistences=token_persistences,
        user_bo_persistences=user_bo_persistences,
    )
