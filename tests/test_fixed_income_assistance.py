from __future__ import annotations

from datetime import date
from decimal import Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.simulation import SimulationSettingsDTO
from backend.core.enum import FixedIncomeType, RateIndexType
from backend.features.fixed_income.accrual import income_tax_brackets, offer, project
from backend.features.fixed_income.assistance import (
    apply_offer_assistance,
    build_quote,
)
from tests.fakes import simulation_settings

ON = date(2020, 1, 6)

PROJECTION_FIELDS = (
    "gross_amount",
    "gross_return",
    "gross_return_pct",
    "income_tax",
    "income_tax_pct",
    "net_amount",
    "net_return",
    "net_return_pct",
)


def _asset() -> FixedIncomeAssetDTO:
    return FixedIncomeAssetDTO(
        name="CDB",
        issuer="Banco",
        investment_type=FixedIncomeType.CDB,
        rate_index=RateIndexType.PREFIXADO,
        maturity_date=date(2023, 1, 6),
        interest_rate=Decimal("0.12"),
    )


def _settings(**rules: bool) -> SimulationSettingsDTO:
    return simulation_settings().model_copy(update=rules)


def _quote(settings: SimulationSettingsDTO):
    return build_quote(
        project(_asset(), Decimal(1000), ON),
        settings,
        cash_before=Decimal(5000),
        cash_after=Decimal(4000),
        max_amount=Decimal(5000),
        income_tax_brackets=income_tax_brackets(),
    )


def test_assistances_are_on_by_default():
    settings = simulation_settings()

    assert settings.show_equivalent_rate
    assert settings.show_maturity_projection


def test_offer_keeps_the_equivalent_rate_while_the_assistance_is_on():
    shown = apply_offer_assistance(offer(_asset(), ON), simulation_settings())

    assert shown.effective_annual_rate == Decimal("0.12")


def test_offer_omits_the_equivalent_rate_when_the_assistance_is_off():
    hidden = apply_offer_assistance(
        offer(_asset(), ON), _settings(show_equivalent_rate=False)
    )

    assert hidden.effective_annual_rate is None
    assert hidden.income_tax_rate_at_maturity == Decimal("0.15")
    assert "effective_annual_rate" in hidden.model_dump()


def test_quote_shows_everything_while_the_assistances_are_on():
    quote = _quote(simulation_settings())

    assert quote.effective_annual_rate == Decimal("0.12")
    assert all(getattr(quote, field) is not None for field in PROJECTION_FIELDS)


def test_quote_omits_the_equivalent_rate_and_keeps_the_projection():
    quote = _quote(_settings(show_equivalent_rate=False))

    assert quote.effective_annual_rate is None
    assert all(getattr(quote, field) is not None for field in PROJECTION_FIELDS)


def test_quote_omits_the_maturity_projection_and_keeps_the_rate():
    quote = _quote(_settings(show_maturity_projection=False))

    assert quote.effective_annual_rate == Decimal("0.12")
    assert all(getattr(quote, field) is None for field in PROJECTION_FIELDS)


def test_quote_keeps_what_the_ticket_needs_with_every_assistance_off():
    quote = _quote(
        _settings(show_equivalent_rate=False, show_maturity_projection=False)
    )

    assert quote.effective_annual_rate is None
    assert all(getattr(quote, field) is None for field in PROJECTION_FIELDS)
    assert quote.amount == Decimal(1000)
    assert quote.redemption_date == date(2023, 1, 6)
    assert quote.income_tax_rate == Decimal("0.15")
    assert quote.cash_before == Decimal(5000)
    assert quote.cash_after == Decimal(4000)
    assert quote.max_amount == Decimal(5000)
    assert quote.income_tax_brackets == income_tax_brackets()
