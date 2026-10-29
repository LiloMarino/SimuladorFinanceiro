import uuid
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from backend.core.dto.base import BaseDTO
from backend.core.enum import FixedIncomeType, RateIndexType


class FixedIncomeAssetDTO(BaseDTO):
    asset_uuid: UUID = Field(default_factory=uuid.uuid4)
    name: str
    issuer: str
    investment_type: FixedIncomeType
    rate_index: RateIndexType
    maturity_date: date
    interest_rate: Decimal
    # Resgatável em qualquer pregão pelo valor do dia, e não só no vencimento
    daily_liquidity: bool = False
    # Máximo que cada jogador aplica no título; None é sem teto
    player_cap: Decimal | None = None
    # Último dia em que a oferta aceita aporte; None é sem prazo
    offered_until: date | None = None
    # Quanto o prêmio de risco do país somou à taxa do título na emissão (fração ao ano); só o Tesouro, só com a expansão de governo
    risk_premium: Decimal | None = None


class FixedIncomeOfferDTO(FixedIncomeAssetDTO):
    """O título com o que ele rende hoje e o IR que paga se levado ao vencimento."""

    index_rate: Decimal
    # Taxa do título combinada com o indexador do dia: o que ele rende ao ano hoje.
    # None quando a partida esconde a taxa equivalente
    effective_annual_rate: Decimal | None
    tax_exempt: bool
    income_tax_rate_at_maturity: Decimal
