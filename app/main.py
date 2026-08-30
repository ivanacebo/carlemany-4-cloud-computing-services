from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from app.authentication.api.router import router as authentication_router
from app.authentication.dependency_injection import AuthenticationContainer
from app.config import DATABASE_URL, models
from app.files.api.router import router as files_router
from app.files.dependency_injection import FilesContainer

app = FastAPI()

# Instantiating the container also wires app.authentication.api.router, so the
# endpoints receive their controllers.
app.container = AuthenticationContainer()

# Files takes the IntrospectController from authentication instead of building its own, and
# main is the only place that knows both modules exist. Binding it here keeps the files
# module from importing authentication's composition root.
app.files_container = FilesContainer(
    introspect_controller=app.container.introspect.introspect_controller
)


@app.get("/healthcheck")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(authentication_router)
app.include_router(files_router, prefix="/files")

register_tortoise(
    app,
    db_url=DATABASE_URL,
    modules={"models": models},
    generate_schemas=False,
    add_exception_handlers=True,
)
