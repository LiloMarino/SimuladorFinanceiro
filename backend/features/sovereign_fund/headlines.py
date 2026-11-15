"""As manchetes do Fundo Soberano: cada uma leva a sigla do partido do presidente."""

from decimal import Decimal

from backend.core.enum import NewsType
from backend.core.utils import format_billions, format_quantity
from backend.features.notifications.news import Headline

FUND = "Fundo Soberano"


def _government(party: str | None) -> str:
    return f"Governo do {party}" if party else "Governo"


def _abbrs(party: str | None) -> tuple[str, ...]:
    return (party,) if party else ()


def funded(amount: Decimal, party: str | None) -> Headline:
    return Headline(
        NewsType.SOVEREIGN_FUND_FUNDED,
        f"{_government(party)} aporta {format_billions(amount)} no {FUND}",
        "O dinheiro vai para o caixa do fundo, que o presidente usa para comprar ações e cotas de gestora.",
        party_abbrs=_abbrs(party),
    )


def bought(ticker: str, amount: Decimal, party: str | None) -> Headline:
    return Headline(
        NewsType.SOVEREIGN_FUND_BOUGHT,
        f"{FUND} compra {format_billions(amount)} em {ticker}",
        "A ordem do fundo passa pelo livro de ofertas e mexe no preço como qualquer outra.",
        (ticker,),
        party_abbrs=_abbrs(party),
    )


def sold(ticker: str, amount: Decimal, party: str | None) -> Headline:
    return Headline(
        NewsType.SOVEREIGN_FUND_SOLD,
        f"{FUND} vende {ticker} e devolve {format_billions(amount)} ao Tesouro",
        "O valor da venda abate a dívida pública.",
        (ticker,),
        party_abbrs=_abbrs(party),
    )


def favoritism(name: str, ticker: str, stake: Decimal, party: str | None) -> Headline:
    return Headline(
        NewsType.SOVEREIGN_FUND_FAVORITISM,
        f"{FUND} compra {format_quantity((stake * 100).quantize(Decimal('0.1')))}% "
        f"da gestora {name}, de um aliado do governo",
        "O eleitorado rejeita o governo que usa o dinheiro público para favorecer a própria base.",
        (ticker,),
        party_abbrs=_abbrs(party),
    )
