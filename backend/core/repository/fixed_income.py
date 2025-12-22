from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.decorators.transactional_method import transactional
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.models.models import FixedIncomeAsset


class FixedIncomeRepository:
    @transactional
    def get_or_create_asset(
        self, session: Session, asset: FixedIncomeAssetDTO
    ) -> FixedIncomeAsset:
        # Verifica se o ativo existe
        stmt = select(FixedIncomeAsset).where(
            FixedIncomeAsset.asset_uuid == asset.asset_uuid
        )
        existing = session.scalar(stmt)
        if existing:
            return existing

        # Cria o ativo e retorna
        db_asset = FixedIncomeAsset(
            asset_uuid=asset.asset_uuid,
            name=asset.name,
            issuer=asset.issuer,
            investment_type=asset.investment_type.value,
            rate_type=asset.rate_index.value,
            maturity_date=asset.maturity_date,
            interest_rate=asset.interest_rate,
        )
        session.add(db_asset)
        return db_asset
