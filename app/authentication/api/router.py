from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, Header, HTTPException
from pydantic import BaseModel

from app.authentication.dependency_injection import AuthenticationContainer
from app.authentication.domain.controllers.introspect_controller import IntrospectController
from app.authentication.domain.controllers.login_controller import LoginController
from app.authentication.domain.controllers.logout_controller import LogoutController
from app.authentication.domain.controllers.register_controller import RegisterController
from app.authentication.domain.persistences.exceptions import (
    TokenNotFound,
    UsernameAlreadyTakenException,
    UserNotFoundException,
    WrongPasswordException,
)

router = APIRouter(tags=["authentication"])


class RegisterInput(BaseModel):
    username: str
    password: str
    mail: str
    year_of_birth: int


class RegisterOutput(BaseModel):
    username: str
    mail: str
    year_of_birth: Optional[int] = None


@router.post("/register")
@inject
async def register_post(
    input: RegisterInput = Body(),
    register_controller: RegisterController = Depends(
        Provide[AuthenticationContainer.register.register_controller]
    ),
) -> dict[str, RegisterOutput]:
    try:
        user = await register_controller.execute(
            username=input.username,
            password=input.password,
            mail=input.mail,
            year_of_birth=input.year_of_birth,
        )
    except UsernameAlreadyTakenException:
        raise HTTPException(status_code=409, detail="This username is already taken")
    output = RegisterOutput(
        username=user.username,
        mail=user.mail,
        year_of_birth=user.year_of_birth,
    )
    return {"new_user": output}


class LoginInput(BaseModel):
    username: str
    password: str


@router.post("/login")
@inject
async def login_post(
    input: LoginInput = Body(),
    login_controller: LoginController = Depends(
        Provide[AuthenticationContainer.login.login_controller]
    ),
) -> dict[str, str]:
    try:
        token = await login_controller.execute(username=input.username, password=input.password)
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User not found")
    except WrongPasswordException:
        raise HTTPException(status_code=403, detail="Password is not correct")
    return {"auth": token}


class IntrospectOutput(BaseModel):
    username: str
    mail: str
    year_of_birth: Optional[int] = None


@router.get("/introspect")
@inject
async def introspect_get(
    auth: str = Header(),
    introspect_controller: IntrospectController = Depends(
        Provide[AuthenticationContainer.introspect.introspect_controller]
    ),
) -> IntrospectOutput:
    try:
        user = await introspect_controller.execute(auth)
    except (TokenNotFound, UserNotFoundException):
        raise HTTPException(status_code=403, detail="Forbidden")
    return IntrospectOutput(
        username=user.username,
        mail=user.mail,
        year_of_birth=user.year_of_birth,
    )


@router.post("/logout")
@inject
async def logout_post(
    auth: str = Header(),
    logout_controller: LogoutController = Depends(
        Provide[AuthenticationContainer.logout.logout_controller]
    ),
) -> dict[str, str]:
    try:
        await logout_controller.execute(auth)
    except TokenNotFound:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"status": "ok"}
