from decimal import Decimal

from backend.core.enum import NewsType
from backend.core.utils import format_quantity
from backend.features.notifications.news import Headline

FEE_DEK = "A taxa nova vale a partir do primeiro dia útil do mês seguinte."


def offer_opened(ticker: str, quotas: Decimal) -> Headline:
    return Headline(
        NewsType.FUND_OFFER_OPENED,
        f"{ticker} abre oferta pública de {format_quantity(quotas)} cotas",
        "As cotas saem ao patrimônio líquido do dia.",
        (ticker,),
    )


def management_fee_changed(ticker: str, rate: Decimal) -> Headline:
    return Headline(
        NewsType.FUND_FEE_CHANGED,
        f"{ticker} muda a taxa de administração para {_percent(rate)} ao ano",
        FEE_DEK,
        (ticker,),
    )


def performance_fee_changed(ticker: str, rate: Decimal) -> Headline:
    return Headline(
        NewsType.FUND_FEE_CHANGED,
        f"{ticker} muda a taxa de performance para {_percent(rate)} do que passar do CDI",
        FEE_DEK,
        (ticker,),
    )


def _percent(rate: Decimal) -> str:
    return format_quantity(rate * 100) + "%"
