"""As saídas automáticas da gestora (taxa, taxa a pagar, rendimento) vendem renda fixa antes de debitar."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any, cast

import pytest

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.fixed_income.fixed_broker import CoverSale
from tests.test_fund_book import (
    DATA_COM,
    MANAGER,
    PAY_DAY,
    TICKER,
    MemoryFunds,
    Setup,
    _close_day,
    _earn,
    _holding_setup,
    _owing_setup,
    _setup,
    isolated,
    memory,
)


class FundFixedIncome:
    """Renda fixa de liquidez diária da gestora: vende até `balance` e manda o líquido ao caixa."""

    def __init__(self, engine, balance: str) -> None:
        self.engine = engine
        self.balance = Decimal(balance)
        self.sold = Decimal(0)
        self.asset = FixedIncomeAssetDTO(
            name="CDB da gestora",
            issuer="Banco Teste",
            investment_type=FixedIncomeType.CDB,
            rate_index=RateIndexType.PREFIXADO,
            maturity_date=date(2032, 1, 4),
            interest_rate=Decimal("0.1"),
            daily_liquidity=True,
        )

    def sell_for_cash(
        self, client_id: uuid.UUID, shortfall: Decimal, include_marked: bool
    ) -> list[CoverSale]:
        assert not include_marked
        net = min(shortfall, self.balance)
        if net <= 0:
            return []
        self.balance -= net
        self.sold += net
        self.engine.cash[client_id] += net
        return [CoverSale(self.asset, net)]

    def transfer_all(self, source: uuid.UUID, target: uuid.UUID) -> None:
        """Sem posições a passar."""


@pytest.fixture(autouse=True)
def notices(monkeypatch: pytest.MonkeyPatch) -> list[dict]:
    """Os avisos do resgate automático que o motor mandou."""
    sent: list[dict] = []
    monkeypatch.setattr(
        "backend.features.simulation.simulation_engine.notify",
        lambda name, payload, to=None: sent.append(payload),
    )
    return sent


def _with_fixed_income(setup: Setup, balance: str) -> FundFixedIncome:
    fixed = FundFixedIncome(setup.engine, balance)
    setup.engine.fixed_broker = cast(Any, fixed)
    return fixed


def test_the_management_fee_is_paid_by_selling_fixed_income_before_it_becomes_payable(
    memory: MemoryFunds, notices: list[dict]
):
    """O caixa de R$ 10 não cobre a taxa; o título vende o que falta e o gestor recebe a taxa inteira."""
    setup, fee = _owing_setup(memory)
    fund = setup.book.get(TICKER)
    fixed = _with_fixed_income(setup, "1000000")

    setup.book.on_month(date(2020, 2, 3))

    assert fund.terms.management_fee_payable == 0
    assert setup.engine.cash[MANAGER] == fee
    assert setup.engine.cash[setup.fund_client] == 0
    assert fixed.sold == fee - 10
    assert [n["reason"] for n in notices] == ["a taxa de administração"]


def test_the_fee_is_paid_in_part_when_the_fixed_income_is_not_enough(
    memory: MemoryFunds,
):
    """Com R$ 10 em caixa e R$ 50 em renda fixa, a gestora paga R$ 60 e o resto vira taxa a pagar."""
    setup, fee = _owing_setup(memory)
    fund = setup.book.get(TICKER)
    _with_fixed_income(setup, "50")

    setup.book.on_month(date(2020, 2, 3))

    assert setup.engine.cash[MANAGER] == 60
    assert fund.terms.management_fee_payable == fee - 60
    assert setup.engine.cash[setup.fund_client] == 0


def test_the_payable_fee_is_settled_by_selling_fixed_income(memory: MemoryFunds):
    setup, fee = _owing_setup(memory)
    fund = setup.book.get(TICKER)
    setup.book.on_month(date(2020, 2, 3))
    assert fund.terms.management_fee_payable == fee - 10
    fixed = _with_fixed_income(setup, "1000000")

    setup.tick(date(2020, 2, 4))

    assert fund.terms.fee_payable == 0
    assert setup.engine.cash[MANAGER] == fee
    assert fixed.sold == fee - 10


def test_the_yield_is_paid_in_full_by_selling_fixed_income(
    memory: MemoryFunds, notices: list[dict]
):
    """Com R$ 103 em caixa o rendimento pagaria R$ 0,10 por cota; com renda fixa ele paga o apurado inteiro."""
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    _close_day(setup, DATA_COM)
    setup.engine.cash[setup.fund_client] = Decimal(103)
    fixed = _with_fixed_income(setup, "1000000")
    pending = fund.distributions[-1]

    setup.tick(PAY_DAY)

    row = fund.distributions[-1]
    assert row.paid_per_quota == pending.per_quota
    assert row.paid is not None and row.paid > 103
    # Sobram só os centavos do arredondamento por cotista
    assert 0 <= setup.engine.cash[setup.fund_client] < 1
    assert fixed.sold == pending.per_quota * fund.account.outside_quotas - 103
    assert [n["reason"] for n in notices] == ["o rendimento mensal"]


def test_the_yield_pays_what_the_cash_and_the_fixed_income_reach(memory: MemoryFunds):
    setup = _holding_setup(memory)
    fund = setup.book.get(TICKER)
    _earn(setup, "1000")
    _close_day(setup, DATA_COM)
    setup.engine.cash[setup.fund_client] = Decimal(103)
    _with_fixed_income(setup, "100")

    setup.tick(PAY_DAY)

    row = fund.distributions[-1]
    assert row.paid is not None
    assert Decimal(202) < row.paid <= Decimal(203)
    assert 0 <= setup.engine.cash[setup.fund_client] < 1
