from datetime import date
from decimal import Decimal

from backend.core.enum import NewsType
from backend.core.utils import format_money, format_quantity
from backend.features.notifications.news import Headline

FEE_DEK = "A taxa nova vale a partir do primeiro dia útil do mês seguinte."


def offer_opened(
    name: str,
    ticker: str,
    manager: str | None,
    quotas: Decimal,
    price: Decimal,
    ends_on: date,
    sessions: int,
) -> Headline:
    who = f"A gestora nova de {manager}" if manager else "A gestora nova"
    return Headline(
        NewsType.FUND_OFFER_OPENED,
        f"{name} abre oferta de {format_quantity(quotas)} cotas a {_whole_money(price)}",
        f"{who} vende cotas a preço fixo por {sessions} pregões, até {ends_on:%d/%m}. Quem compra agora entra com a carteira começando do zero.",
        (ticker,),
    )


def takeover_offer_opened(ticker: str, quotas: Decimal) -> Headline:
    return Headline(
        NewsType.FUND_OFFER_OPENED,
        f"{ticker} abre oferta automática de {format_quantity(quotas)} cotas",
        "A carência acabou e o gestor tinha cotas acima do limite: elas saem ao patrimônio líquido do dia, por 5 pregões. O que não vender o Mercado compra.",
        (ticker,),
    )


def issuance_opened(ticker: str, quotas: Decimal, price: Decimal) -> Headline:
    return Headline(
        NewsType.FUND_ISSUANCE_OPENED,
        f"{ticker} emite {format_quantity(quotas)} cotas a {format_money(price)}",
        "Os cotistas têm preferência nos primeiros pregões; a sobra abre para todos.",
        (ticker,),
    )


def issuance_closed(ticker: str, sold: Decimal, quotas: Decimal) -> Headline:
    return Headline(
        NewsType.FUND_ISSUANCE_CLOSED,
        f"{ticker} encerra a emissão: {format_quantity(sold)} das {format_quantity(quotas)} cotas foram vendidas",
        "As cotas que não venderam não nascem.",
        (ticker,),
    )


def buyback_opened(ticker: str, quantity: Decimal, max_price: Decimal) -> Headline:
    return Headline(
        NewsType.FUND_BUYBACK_OPENED,
        f"{ticker} abre recompra de {format_quantity(quantity)} cotas a até {format_money(max_price)}",
        "A gestora paga com o próprio caixa e as cotas compradas deixam de existir.",
        (ticker,),
    )


def assembly_called(
    ticker: str, convener: str, candidate: str, ends_on: date
) -> Headline:
    proposal = (
        f"{convener} convoca assembleia da {ticker} para trocar o gestor"
        if convener == candidate
        else f"{convener} convoca assembleia da {ticker} e indica {candidate} para a gestão"
    )
    return Headline(
        NewsType.FUND_ASSEMBLY_CALLED,
        proposal,
        f"Os cotistas votam até {ends_on:%d/%m}: vence a maioria das cotas votantes.",
        (ticker,),
    )


def assembly_replaced(ticker: str, previous: str, manager: str) -> Headline:
    return Headline(
        NewsType.FUND_ASSEMBLY_REPLACED,
        f"Assembleia troca o gestor da {ticker}: {manager} assume no lugar de {previous}",
        f"{previous} segue cotista, perde a operação e as taxas futuras.",
        (ticker,),
    )


def assembly_kept(ticker: str, manager: str) -> Headline:
    return Headline(
        NewsType.FUND_ASSEMBLY_KEPT,
        f"Assembleia mantém {manager} na gestão da {ticker}",
        "A troca não reuniu mais cotas a favor do que contra.",
        (ticker,),
    )


def funds_merged(
    mother: str, daughter: str, ratio: Decimal, leaving_quotas: Decimal
) -> Headline:
    leaving = (
        f" {format_quantity(leaving_quotas)} cotas saíram pelo PL por cota."
        if leaving_quotas > 0
        else ""
    )
    return Headline(
        NewsType.FUND_MERGED,
        f"{mother} incorpora a {daughter}: a {daughter} deixa a bolsa",
        f"Cada cota da {daughter} virou {format_quantity(ratio)} da {mother}.{leaving}",
        (mother, daughter),
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


def _whole_money(value: Decimal) -> str:
    """Real sem centavos quando o valor é inteiro: R$ 100; com centavos, R$ 104,30."""
    return format_money(value).removesuffix(",00")


def _percent(rate: Decimal) -> str:
    return format_quantity(rate * 100) + "%"
