from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeEventType, FixedIncomeType, RateIndexType
from backend.core.models.models import (
    EventFixedIncome,
    FixedIncomeAsset,
)


def _to_asset_dto(asset: FixedIncomeAsset) -> FixedIncomeAssetDTO:
    return FixedIncomeAssetDTO(
        asset_uuid=asset.asset_uuid,
        name=asset.name,
        issuer=asset.issuer,
        investment_type=FixedIncomeType.from_db(asset.investment_type),
        rate_index=RateIndexType.from_db(asset.rate_type),
        maturity_date=asset.maturity_date,
        interest_rate=asset.interest_rate,
    )


class FixedIncomeRepository:
    @transactional
    def get_or_create_asset(self, session: Session, asset: FixedIncomeAssetDTO) -> int:
        # Verifica se o ativo existe
        stmt = select(FixedIncomeAsset.id).where(
            FixedIncomeAsset.asset_uuid == asset.asset_uuid
        )
        existing_id = session.scalar(stmt)
        if existing_id:
            return existing_id
        # Cria o ativo e retorna
        db_asset = FixedIncomeAsset(
            asset_uuid=asset.asset_uuid,
            name=asset.name,
            issuer=asset.issuer,
            investment_type=asset.investment_type.db_value,
            rate_type=asset.rate_index.db_value,
            maturity_date=asset.maturity_date,
            interest_rate=asset.interest_rate,
        )
        session.add(db_asset)
        session.flush()

        return db_asset.id

    @transactional
    def get_asset_by_uuid(
        self, session: Session, asset_uuid: str
    ) -> FixedIncomeAssetDTO | None:
        stmt = select(FixedIncomeAsset).where(FixedIncomeAsset.asset_uuid == asset_uuid)
        asset = session.scalar(stmt)
        if not asset:
            return None

        return _to_asset_dto(asset)

    @transactional
    def get_events(
        self, session: Session, simulation_id: int, user_id: int
    ) -> list[tuple[FixedIncomeAssetDTO, FixedIncomeEventDTO]]:
        """Eventos de renda fixa do jogador, em ordem cronológica, com o ativo de cada um."""
        rows = session.execute(
            select(EventFixedIncome, FixedIncomeAsset)
            .join(FixedIncomeAsset, FixedIncomeAsset.id == EventFixedIncome.asset_id)
            .where(
                EventFixedIncome.simulation_id == simulation_id,
                EventFixedIncome.user_id == user_id,
            )
            .order_by(EventFixedIncome.event_date, EventFixedIncome.id)
        ).all()

        return [
            (
                _to_asset_dto(asset),
                FixedIncomeEventDTO(
                    simulation_id=event.simulation_id,
                    user_id=event.user_id,
                    asset_id=event.asset_id,
                    event_type=FixedIncomeEventType(event.event_type),
                    amount=event.amount,
                    event_date=event.event_date,
                    created_at=event.created_at,
                ),
            )
            for event, asset in rows
        ]
