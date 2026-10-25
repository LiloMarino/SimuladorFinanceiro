from typing import Annotated

from fastapi import APIRouter, status
from pydantic import BaseModel, StringConstraints, ValidationError

from backend.core import repository
from backend.core.dependencies import HostVerified
from backend.core.dto.preset import (
    PRESET_NAME_MAX_LENGTH,
    PresetDTO,
    PresetLoadResponse,
)
from backend.core.exceptions.http_exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
)
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import required
from backend.routes.simulation import (
    SimulationRulesRequest,
    notify_preset_changed,
    notify_settings_changed,
)

presets_router = APIRouter(prefix="/api/presets", tags=["Presets"])

PresetName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True, min_length=1, max_length=PRESET_NAME_MAX_LENGTH
    ),
]


class SavePresetRequest(BaseModel):
    name: PresetName
    # As regras que o preset guarda; o nome da partida fica de fora
    rules: SimulationRulesRequest


class RenamePresetRequest(BaseModel):
    name: PresetName


class UpdatePresetRulesRequest(BaseModel):
    rules: SimulationRulesRequest


def _config_of(rules: SimulationRulesRequest) -> dict:
    return rules.model_dump(mode="json", exclude={"name"})


def _editable_preset(preset_id: int) -> PresetDTO:
    preset = repository.preset.get(preset_id)
    if preset is None:
        raise NotFoundError("Preset não encontrado.")
    if preset.built_in:
        raise ConflictError("Os presets prontos não mudam.")
    return preset


def _ensure_name_free(name: str, except_id: int | None = None) -> None:
    if repository.preset.name_taken(name, except_id):
        raise ConflictError("Já existe um preset com esse nome.")


@presets_router.get(
    "",
    response_model=list[PresetDTO],
    summary="Listar os presets",
    description="Os prontos do app primeiro, depois os que o host salvou, do mais antigo ao mais novo. Apenas o host pode executar.",
)
def list_presets(_: HostVerified):
    """Lista os presets de partida."""
    return repository.preset.list()


@presets_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PresetDTO,
    summary="Salvar as regras como preset",
    description="Guarda as regras enviadas com um nome de até 60 letras. Recusa com 409 o nome repetido, sem diferenciar maiúsculas. Sem partida salva selecionada, o novo preset passa a ser o aplicado. Apenas o host pode executar.",
)
def save_preset(payload: SavePresetRequest, _: HostVerified):
    """Salva as regras como um preset do host."""
    _ensure_name_free(payload.name)
    preset = repository.preset.create(payload.name, _config_of(payload.rules))
    if SettingsManager.get_selected_simulation_id() is None:
        SettingsManager.mark_preset(preset.id)
        notify_preset_changed()
    return preset


@presets_router.patch(
    "/{preset_id}",
    response_model=PresetDTO,
    summary="Renomear um preset",
    description="Troca o nome de um preset do host. Recusa com 409 o preset pronto e o nome repetido. Apenas o host pode executar.",
)
def rename_preset(preset_id: int, payload: RenamePresetRequest, _: HostVerified):
    """Renomeia um preset do host."""
    _editable_preset(preset_id)
    _ensure_name_free(payload.name, preset_id)
    repository.preset.rename(preset_id, payload.name)
    notify_preset_changed()
    return required(repository.preset.get(preset_id))


@presets_router.put(
    "/{preset_id}/rules",
    response_model=PresetDTO,
    summary="Gravar as regras por cima de um preset",
    description="Troca as regras guardadas num preset do host pelas enviadas. Recusa com 409 o preset pronto. Sem partida salva selecionada, o preset passa a ser o aplicado. Apenas o host pode executar.",
)
def update_preset_rules(
    preset_id: int, payload: UpdatePresetRulesRequest, _: HostVerified
):
    """Grava as regras de agora por cima de um preset do host."""
    _editable_preset(preset_id)
    repository.preset.update_config(preset_id, _config_of(payload.rules))
    if SettingsManager.get_selected_simulation_id() is None:
        SettingsManager.mark_preset(preset_id)
    notify_preset_changed()
    return required(repository.preset.get(preset_id))


@presets_router.delete(
    "/{preset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Apagar um preset",
    description="Apaga um preset do host; as partidas já criadas não mudam. Se era o aplicado, as regras de agora seguem como estão, sem preset. Recusa com 409 o preset pronto. Apenas o host pode executar.",
)
def delete_preset(preset_id: int, _: HostVerified):
    """Apaga um preset do host."""
    _editable_preset(preset_id)
    repository.preset.delete(preset_id)
    if SettingsManager.applied_preset_id() == preset_id:
        SettingsManager.mark_preset(None)
    notify_preset_changed()


@presets_router.post(
    "/{preset_id}/load",
    response_model=PresetLoadResponse,
    summary="Carregar um preset",
    description="Troca as regras da nova partida pelas do preset, mantendo o nome da partida; o que o preset não traz vem do padrão. Quem muda de modo perde as equipes. Recusa com 409 enquanto uma partida salva está selecionada. Apenas o host pode executar.",
)
def load_preset(preset_id: int, _: HostVerified):
    """Aplica um preset às regras da nova partida."""
    if SettingsManager.get_selected_simulation_id() is not None:
        raise ConflictError(
            "As regras de uma partida salva não mudam. Remova a seleção para carregar um preset."
        )
    preset = repository.preset.get(preset_id)
    if preset is None:
        raise NotFoundError("Preset não encontrado.")

    regrouped_from = SettingsManager.get().player_grouping
    try:
        settings, defaulted = SettingsManager.apply_preset(preset.id, preset.config)
    except ValidationError as error:
        raise BadRequestError("As regras deste preset não valem mais.") from error
    if regrouped_from != settings.player_grouping:
        UserManager.reset_teams()

    notify_settings_changed(settings)
    applied = required(SettingsManager.applied_preset())
    # Os prontos só dizem o essencial de cada jogo: o resto vir do padrão é o desenho deles
    return PresetLoadResponse(
        settings=settings,
        applied=applied,
        defaulted=[] if preset.built_in else defaulted,
    )
