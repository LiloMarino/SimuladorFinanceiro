from decimal import Decimal

from backend.core.dto.fixed_income_asset import FixedIncomeOfferDTO
from backend.core.dto.fixed_income_projection import (
    FixedIncomeProjectionDTO,
    FixedIncomeQuoteDTO,
    IncomeTaxBracketDTO,
)
from backend.core.dto.simulation import SimulationSettingsDTO


def apply_offer_assistance(
    offer: FixedIncomeOfferDTO, settings: SimulationSettingsDTO
) -> FixedIncomeOfferDTO:
    """A oferta como a partida a mostra: sem a taxa equivalente quando a ajuda está desligada."""
    if settings.show_equivalent_rate:
        return offer
    return offer.model_copy(update={"effective_annual_rate": None})


def build_quote(
    projection: FixedIncomeProjectionDTO,
    settings: SimulationSettingsDTO,
    *,
    cash_before: Decimal,
    cash_after: Decimal,
    max_amount: Decimal,
    cap_used: Decimal | None,
    income_tax_brackets: list[IncomeTaxBracketDTO],
) -> FixedIncomeQuoteDTO:
    """
    A cotação da boleta como a partida a mostra.

    O que a projeção entrega além da taxa e do retorno (valor aplicado, prazo,
    alíquota, caixa e a tabela regressiva) é o que a boleta precisa e fica sempre.
    """
    quote = FixedIncomeQuoteDTO(
        amount=projection.amount,
        index_rate=projection.index_rate,
        business_days=projection.business_days,
        redemption_date=projection.redemption_date,
        income_tax_rate=projection.income_tax_rate,
        effective_annual_rate=projection.effective_annual_rate,
        gross_amount=projection.gross_amount,
        gross_return=projection.gross_return,
        gross_return_pct=projection.gross_return_pct,
        income_tax=projection.income_tax,
        income_tax_pct=projection.income_tax_pct,
        net_amount=projection.net_amount,
        net_return=projection.net_return,
        net_return_pct=projection.net_return_pct,
        cash_before=cash_before,
        cash_after=cash_after,
        max_amount=max_amount,
        cap_used=cap_used,
        income_tax_brackets=income_tax_brackets,
    )
    hidden: dict[str, None] = {}
    if not settings.show_equivalent_rate:
        hidden["effective_annual_rate"] = None
    if not settings.show_maturity_projection:
        hidden.update(
            dict.fromkeys(
                (
                    "gross_amount",
                    "gross_return",
                    "gross_return_pct",
                    "income_tax",
                    "income_tax_pct",
                    "net_amount",
                    "net_return",
                    "net_return_pct",
                )
            )
        )
    return quote.model_copy(update=hidden) if hidden else quote
