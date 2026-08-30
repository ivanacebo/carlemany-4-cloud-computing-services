from typing import Optional

from fastapi import APIRouter, Body, Header, HTTPException
from pydantic import BaseModel

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
from app.authentication.persistence.memory.token import TokenMemoryService
from app.authentication.persistence.memory.user_bo import UserBOMemoryService

router = APIRouter(tags=["authentication"])

# --- Temporary composition root. Replaced by the DI container in the next step. ---
token_persistence = TokenMemoryService()
user_bo_persistence = UserBOMemoryService()

register_controller = RegisterController(user_bo_persistence=user_bo_persistence)
login_controller = LoginController(
    user_bo_persistence=user_bo_persistence, token_persistence=token_persistence
)
logout_controller = LogoutController(token_persistence=token_persistence)
introspect_controller = IntrospectController(
    token_persistence=token_persistence, user_bo_persistence=user_bo_persistence
)


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
async def register_post(input: RegisterInput = Body()) -> dict[str, RegisterOutput]:
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
async def login_post(input: LoginInput = Body()) -> dict[str, str]:
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
async def introspect_get(auth: str = Header()) -> IntrospectOutput:
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
async def logout_post(auth: str = Header()) -> dict[str, str]:
    try:
        await logout_controller.execute(auth)
    except TokenNotFound:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"status": "ok"}
