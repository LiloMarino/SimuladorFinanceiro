from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.preset import PresetDTO
from backend.core.models.models import Preset


class PresetRepository:
    """Os presets de partida: os prontos do app e os que o host salvou."""

    @transactional
    def list(self, session: Session) -> list[PresetDTO]:
        statement = select(Preset).order_by(
            Preset.built_in.desc(), Preset.created_at, Preset.id
        )
        return [PresetDTO.model_validate(p) for p in session.scalars(statement)]

    @transactional
    def get(self, session: Session, preset_id: int) -> PresetDTO | None:
        preset = session.get(Preset, preset_id)
        return PresetDTO.model_validate(preset) if preset is not None else None

    @transactional
    def name_taken(
        self, session: Session, name: str, except_id: int | None = None
    ) -> bool:
        statement = select(Preset.id).where(func.lower(Preset.name) == name.lower())
        if except_id is not None:
            statement = statement.where(Preset.id != except_id)
        return session.scalar(statement) is not None

    @transactional
    def create(self, session: Session, name: str, config: dict[str, Any]) -> PresetDTO:
        preset = Preset(name=name, built_in=False, config=config)
        session.add(preset)
        session.flush()
        session.refresh(preset)
        return PresetDTO.model_validate(preset)

    @transactional
    def rename(self, session: Session, preset_id: int, name: str) -> None:
        preset = session.get(Preset, preset_id)
        if preset is not None:
            preset.name = name

    @transactional
    def update_config(
        self, session: Session, preset_id: int, config: dict[str, Any]
    ) -> None:
        preset = session.get(Preset, preset_id)
        if preset is not None:
            preset.config = config

    @transactional
    def delete(self, session: Session, preset_id: int) -> None:
        preset = session.get(Preset, preset_id)
        if preset is not None:
            session.delete(preset)
