from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.core.models.models import FixedIncomeAsset


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

        return FixedIncomeAssetDTO(
            asset_uuid=asset.asset_uuid,
            name=asset.name,
            issuer=asset.issuer,
            investment_type=FixedIncomeType.from_db(asset.investment_type),
            rate_index=RateIndexType.from_db(asset.rate_type),
            maturity_date=asset.maturity_date,
            interest_rate=(float(asset.interest_rate)),
        )
