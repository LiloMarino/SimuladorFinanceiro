from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from backend import config
from backend.config.paths import app_files_dir
from backend.core import repository
from backend.core.dependencies import ClientID, HostVerified
from backend.core.dto.preparation import PartyIdentityDTO
from backend.core.dto.technical_indicators import IndicatorSettingsDTO
from backend.core.enum import (
    NewsLevel,
    NewsPosition,
    NewsSection,
    NewsType,
    ToastType,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.core.repository.settings import MY_PARTY_KEY
from backend.core.runtime.user_manager import UserManager
from backend.core.utils.file_manager import open_in_file_manager
from backend.features.government import voters
from backend.features.notifications import registry

settings_router = APIRouter(prefix="/api/settings", tags=["Settings"])


class NotificationSettings(BaseModel):
    """Onde o jornal aparece, o nível de cada tipo de manchete e quais avisos sobem."""

    news_position: NewsPosition = registry.DEFAULT_POSITION
    news: dict[NewsType, NewsLevel] = {}
    # Os tipos com filtro que só mostram manchetes de ativos da carteira
    news_held_only: dict[NewsType, bool] = {}
    toasts: dict[ToastType, bool] = {}


class CompleteNotificationSettings(NotificationSettings):
    # A resposta traz todos os tipos do registro, com o padrão onde o jogador não escolheu
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)


class SettingsRequest(BaseModel):
    notifications: NotificationSettings = NotificationSettings()
    # O que o jogador liga no gráfico das ações; quem gravou antes dele nasce com o padrão
    indicators: IndicatorSettingsDTO = IndicatorSettingsDTO()

    model_config = ConfigDict(extra="allow")


class SettingsResponse(BaseModel):
    """As preferências do usuário mais o modo debug do servidor, só leitura."""

    notifications: CompleteNotificationSettings
    indicators: IndicatorSettingsDTO
    debug: bool

    # A resposta sempre traz todas as preferências: o schema de saída as marca como obrigatórias
    model_config = ConfigDict(
        extra="allow", json_schema_serialization_defaults_required=True
    )


DEFAULT_SETTINGS = SettingsRequest()


def _with_debug(settings: dict[str, Any]) -> SettingsResponse:
    """Sobrepõe o `debug` do config.toml, mesmo que o banco tenha um valor antigo, e completa as notificações pelo registro."""
    chosen = SettingsRequest.model_validate(settings).notifications
    complete = CompleteNotificationSettings(
        news_position=chosen.news_position,
        news=registry.news_levels(chosen.news),
        news_held_only=registry.news_held_only(chosen.news_held_only),
        toasts=registry.toasts_on(chosen.toasts),
    )
    return SettingsResponse.model_validate(
        {**settings, "notifications": complete, "debug": config.toml.debug.enabled}
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
            **DEFAULT_SETTINGS.model_dump(mode="json"),
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

    # O debug é do servidor: o cliente não o grava (`extra="allow"` deixaria passar);
    # o Meu partido tem rota própria e atravessa a gravação das preferências
    kept = {
        key: value
        for key, value in repository.settings.get_by_user_id(user_id).items()
        if key == MY_PARTY_KEY
    }
    repository.settings.update_by_user_id(
        user_id, {**data.model_dump(mode="json", exclude={"debug"}), **kept}
    )
    settings = repository.settings.get_by_user_id(user_id)

    return _with_debug(settings)


@settings_router.get(
    "/party",
    response_model=PartyIdentityDTO | None,
    summary="Obter o Meu partido",
    description="A identidade do partido que o jogador funda nas partidas (nome, sigla, cor e 3 bandeiras); nulo enquanto não salvou um.",
)
def get_my_party(client_id: ClientID):
    return repository.settings.get_my_party(UserManager.get_user_id(client_id))


@settings_router.put(
    "/party",
    response_model=PartyIdentityDTO,
    summary="Salvar o Meu partido",
    description="Grava a identidade do partido do jogador no perfil. As bandeiras seguem a regra de fundar um partido: 3 diferentes, sem Mercado livre com Justiça social.",
)
def put_my_party(client_id: ClientID, data: PartyIdentityDTO):
    if not voters.is_valid_flags(data.flags):
        raise UnprocessableEntityError(
            "Escolha 3 bandeiras diferentes; Mercado livre e Justiça social não "
            "andam juntas."
        )
    repository.settings.set_my_party(UserManager.get_user_id(client_id), data)
    return data


class NewsSectionInfo(BaseModel):
    section: NewsSection
    label: str
    note: str | None


class NewsTypeInfo(BaseModel):
    type: NewsType
    section: NewsSection
    label: str
    description: str
    default_level: NewsLevel
    fixed: bool
    portfolio_filter: bool


class ToastTypeInfo(BaseModel):
    type: ToastType
    label: str
    description: str
    default_on: bool


class NotificationCatalogResponse(BaseModel):
    """O registro dos tipos de notificação; as listas vêm na ordem da importância."""

    sections: list[NewsSectionInfo]
    news: list[NewsTypeInfo]
    toasts: list[ToastTypeInfo]
    default_position: NewsPosition


@settings_router.get(
    "/notification-types",
    response_model=NotificationCatalogResponse,
    summary="Tipos de notificação",
    description=(
        "As seções do jornal, os tipos de manchete e os avisos do jogador, com o texto "
        "da configuração e o padrão de cada um."
    ),
)
def get_notification_types():
    return NotificationCatalogResponse(
        sections=[
            NewsSectionInfo(section=s.section, label=s.label, note=s.note)
            for s in registry.SECTIONS
        ],
        news=[
            NewsTypeInfo(
                type=n.type,
                section=n.section,
                label=n.label,
                description=n.description,
                default_level=n.default_level,
                fixed=n.fixed,
                portfolio_filter=n.portfolio_filter,
            )
            for n in registry.NEWS
        ],
        toasts=[
            ToastTypeInfo(
                type=t.type,
                label=t.label,
                description=t.description,
                default_on=t.default_on,
            )
            for t in registry.TOASTS
        ],
        default_position=registry.DEFAULT_POSITION,
    )


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
