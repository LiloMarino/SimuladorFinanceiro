from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from backend import config
from backend.config.paths import app_files_dir
from backend.core import repository
from backend.core.dependencies import ClientID, HostVerified
from backend.core.dto.technical_indicators import IndicatorSettingsDTO
from backend.core.exceptions.http_exceptions import ConflictError, ForbiddenError
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.file_manager import open_in_file_manager

settings_router = APIRouter(prefix="/api/settings", tags=["Settings"])


class OrderNotificationSettings(BaseModel):
    executed: bool
    partial: bool


class PlayerNotificationSettings(BaseModel):
    join_exit: bool


class SettingsRequest(BaseModel):
    orders: OrderNotificationSettings
    players: PlayerNotificationSettings
    # O que o jogador liga no gráfico das ações; quem gravou antes dele nasce com o padrão
    indicators: IndicatorSettingsDTO = IndicatorSettingsDTO()

    model_config = ConfigDict(extra="allow")


class SettingsResponse(SettingsRequest):
    """As preferências do usuário mais o modo debug do servidor, só leitura."""

    debug: bool


DEFAULT_SETTINGS = SettingsRequest(
    orders=OrderNotificationSettings(
        executed=True,
        partial=True,
    ),
    players=PlayerNotificationSettings(join_exit=True),
)


def _with_debug(settings: dict) -> SettingsResponse:
    """Sobrepõe o `debug` do config.toml, mesmo que o banco tenha um valor antigo."""
    return SettingsResponse.model_validate(
        {**settings, "debug": config.toml.debug.enabled}
    )


@settings_router.get(
    "",
    response_model=SettingsResponse,
    summary="Obter configurações do usuário",
    description=(
        "Retorna as configurações pessoais do usuário (notificações de ordens, etc.) "
        "e se o servidor está em modo debug, definido no boot (`--debug` ou config.toml)."
    ),
)
def get_settings(client_id: ClientID):
    """
    Retorna as configurações do usuário.
    """
    settings = repository.settings.get_by_user_id(UserManager.get_user_id(client_id))
    return _with_debug(
        {
            **DEFAULT_SETTINGS.model_dump(),
            **settings,
        }
    )


@settings_router.put(
    "",
    response_model=SettingsResponse,
    summary="Atualizar configurações do usuário",
    description="Atualiza as configurações pessoais do usuário.",
)
def update_settings(client_id: ClientID, data: SettingsRequest):
    """
    Atualiza as configurações do usuário.
    """
    user_id = UserManager.get_user_id(client_id)

    # O debug é do servidor: o cliente não o grava (`extra="allow"` deixaria passar)
    repository.settings.update_by_user_id(user_id, data.model_dump(exclude={"debug"}))
    settings = repository.settings.get_by_user_id(user_id)

    return _with_debug(settings)


LOCAL_HOSTS = {"127.0.0.1", "::1"}


class AppFoldersResponse(BaseModel):
    config: str
    logs: str


def _app_folders() -> dict[Literal["config", "logs"], Path]:
    """A pasta do config.toml e do .env, e a dos logs, sempre em caminho absoluto."""
    return {
        "config": app_files_dir().resolve(),
        "logs": (app_files_dir() / config.toml.logging.logs_path).resolve(),
    }


@settings_router.get(
    "/folders",
    response_model=AppFoldersResponse,
    summary="Caminho das pastas do app",
    description="Onde ficam o config.toml e os logs no computador do host.",
)
def get_app_folders(_: HostVerified):
    return AppFoldersResponse.model_validate(
        {name: str(path) for name, path in _app_folders().items()}
    )


@settings_router.post(
    "/open-folder",
    status_code=204,
    summary="Abrir uma pasta do app no computador do host",
    description=(
        "Abre a pasta de configurações (`target=config`) ou de logs (`target=logs`) no "
        "gerenciador de arquivos. Só atende o próprio computador do host; sem interface "
        "gráfica responde 409 com o caminho."
    ),
)
def open_app_folder(
    _: HostVerified, request: Request, target: Literal["config", "logs"] = "config"
):
    # A janela abre na máquina do servidor: só quem está nela pode pedir
    if request.client is None or request.client.host not in LOCAL_HOSTS:
        raise ForbiddenError("A pasta só abre no computador do host.")

    folder = _app_folders()[target]
    if not open_in_file_manager(folder):
        raise ConflictError(f"Este computador não abriu a pasta. O caminho é {folder}")
