from fastapi import APIRouter
from pydantic import BaseModel

from backend.core.version import get_version

version_router = APIRouter(prefix="/api/version", tags=["Version"])


class VersionResponse(BaseModel):
    version: str


@version_router.get(
    "",
    response_model=VersionResponse,
    summary="Obter a versão do app",
    description="Retorna a versão do Simulador Financeiro em execução (SemVer).",
)
def get_app_version():
    return VersionResponse(version=get_version())
