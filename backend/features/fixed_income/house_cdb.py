"""
CDB da casa do Bancário: todo mês o banco emite, só para ele, três CDBs prefixados de 1, 2 e
3 anos pagando um ponto a mais que o prefixado do Tesouro do mesmo prazo. Sem liquidez
diária, com teto de aplicação de um salário líquido do mês por CDB.

A regra não guarda estado: a oferta de um mês sai da SELIC do dia 1º, do salário líquido do
dono nesse dia e do mês, e o UUID dela é o mesmo em qualquer retomada da partida.
"""

import calendar
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal
from uuid import NAMESPACE_URL, UUID, uuid5

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.core.rates import STORED_RATE_STEP
from backend.features.fixed_income import treasury

ISSUER = "Banco da casa"

# Prazos emitidos todo mês, em anos, do mais curto ao mais longo
HOUSE_CDB_YEARS = (1, 2, 3)

# O que o CDB da casa paga acima do prefixado do Tesouro de mesmo prazo, em fração ao ano
HOUSE_CDB_SPREAD = Decimal("0.01")


def house_uuid(simulation_id: int, owner: UUID, years: int, first: date) -> UUID:
    """O mesmo CDB do mesmo dono no mesmo mês é sempre o mesmo UUID: a retomada mostra a mesma oferta."""
    key = f"house-cdb/{simulation_id}/{owner}/{years}/{first:%Y-%m}"
    return uuid5(NAMESPACE_URL, key)


def house_rate(years: int, selic: Decimal, ipca: Decimal) -> Decimal:
    """A taxa do CDB da casa: o prefixado do Tesouro do prazo mais `HOUSE_CDB_SPREAD`."""
    rate = (
        treasury.base_rate(RateIndexType.PREFIXADO, Decimal(years), selic, ipca)
        + HOUSE_CDB_SPREAD
    )
    return rate.quantize(STORED_RATE_STEP, ROUND_HALF_EVEN)


def issue(
    simulation_id: int, owner: UUID, on: date, cap: Decimal
) -> dict[int, FixedIncomeAssetDTO]:
    """
    Os CDBs do mês de `on` para `owner`, por prazo em anos, cada um com a taxa travada e o
    teto `cap`. A oferta vale até o fim do mês; o título comprado vence `years` anos depois.
    """
    first = treasury.month_start(on)
    rates = treasury.MarketRates.on(first)
    until = first.replace(day=calendar.monthrange(first.year, first.month)[1])
    return {
        years: FixedIncomeAssetDTO(
            asset_uuid=house_uuid(simulation_id, owner, years, first),
            name=f"CDB da casa {years} {'ano' if years == 1 else 'anos'}",
            issuer=ISSUER,
            investment_type=FixedIncomeType.CDB,
            rate_index=RateIndexType.PREFIXADO,
            maturity_date=first.replace(year=first.year + years),
            interest_rate=house_rate(years, rates.selic, rates.ipca),
            player_cap=cap,
            offered_until=until,
        )
        for years in HOUSE_CDB_YEARS
    }
