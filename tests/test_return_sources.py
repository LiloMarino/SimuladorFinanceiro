"""A decomposição do retorno: as parcelas somam o retorno e a valorização é o resto."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.dto.patrimonial_history import PatrimonialHistoryDTO
from backend.core.dto.return_flows import ReturnFlowsDTO
from backend.features.statistics.return_sources import build_return_sources


def _last(networth: str, fixed: str = "0", debt: str = "0") -> PatrimonialHistoryDTO:
    return PatrimonialHistoryDTO(
        snapshot_date=date(2021, 1, 4),
        total_equity=Decimal(0),
        total_fixed=Decimal(fixed),
        total_cash=Decimal(0),
        total_networth=Decimal(networth),
        total_contribution=Decimal(0),
        total_debt=Decimal(debt),
    )


def test_sources_sum_to_the_return():
    flows = ReturnFlowsDTO(
        dividends=Decimal(500),
        fixed_bought=Decimal(1000),
        fixed_redeemed=Decimal(300),
        fixed_tax_withheld=Decimal(20),
        loan_proceeds=Decimal(2000),
        loan_payment=Decimal(1200),
        overdraft_interest=Decimal(10),
        campaign=Decimal(100),
    )

    sources = build_return_sources(
        _last("13000", fixed="900", debt="1000"),
        capital_provided=Decimal(10000),
        income_tax=Decimal(80),
        flows=flows,
    )

    # Juro bruto da renda fixa: 900 aplicado hoje + 300 resgatado - 1000 que entrou
    assert sources.fixed_income_interest == Decimal(200)
    # IR: 80 da renda variável + 20 retidos no resgate
    assert sources.taxes == Decimal(-100)
    # Empréstimo: pagou 1200, devolveu 1000 de principal (2000 - 1000 em aberto) e 10 de cheque especial
    assert sources.debt_interest == Decimal(-210)
    assert sources.campaign == Decimal(-100)
    # Retorno de 3000: o que não é provento, juro, imposto nem custo é valorização
    assert sources.appreciation == Decimal(3000) - 500 - 200 + 100 + 210 + 100
    total = (
        sources.appreciation
        + sources.dividends
        + sources.fixed_income_interest
        + sources.taxes
        + sources.debt_interest
        + sources.campaign
    )
    assert total == Decimal(3000)


def test_player_without_flows_has_all_return_as_appreciation():
    sources = build_return_sources(
        _last("10700"),
        capital_provided=Decimal(10000),
        income_tax=Decimal(0),
        flows=ReturnFlowsDTO(),
    )

    assert sources.appreciation == Decimal(700)
    assert sources.dividends == Decimal(0)
    assert sources.debt_interest == Decimal(0)
    assert sources.campaign == Decimal(0)
