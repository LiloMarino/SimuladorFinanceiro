"""As manchetes das estatais: cada uma leva o ticker e a sigla do partido do presidente."""

from datetime import date
from decimal import Decimal

from backend.core.enum import DividendPolicy, NewsType, StateCompanySize
from backend.core.utils import format_money, format_quantity
from backend.features.notifications.news import Headline
from backend.features.state_companies import payout

BILLION = Decimal(10) ** 9

POLICY_VERBS: dict[DividendPolicy, str] = {
    DividendPolicy.REINVEST: "manda a {ticker} reinvestir",
    DividendPolicy.NORMAL: "volta a {ticker} aos dividendos normais",
    DividendPolicy.SQUEEZE: "manda a {ticker} espremer dividendos",
}


def _government(party: str | None) -> str:
    return f"Governo do {party}" if party else "Governo"


def _abbrs(party: str | None) -> tuple[str, ...]:
    return (party,) if party else ()


def _percent(rate: Decimal) -> str:
    return format_quantity(rate * 100) + "%"


def founded(
    name: str, ticker: str, size: StateCompanySize, share: Decimal, party: str | None
) -> Headline:
    capital = format_quantity(Decimal(size.billions))
    return Headline(
        NewsType.STATE_COMPANY_FOUNDED,
        f"{_government(party)} funda a {name} ({ticker}) com R$ {capital} bi",
        f"O Tesouro fica com {_percent(share)} das ações; o restante vai ao mercado.",
        (ticker,),
        party_abbrs=_abbrs(party),
    )


def not_founded(name: str, ticker: str) -> Headline:
    return Headline(
        NewsType.MEASURE_VOTED,
        f"A fundação da {name} não saiu do papel: o código {ticker} já é de outro ativo",
        tickers=(ticker,),
    )


def privatization_opened(
    ticker: str, shares: int, ends_on: date, party: str | None
) -> Headline:
    return Headline(
        NewsType.STATE_PRIVATIZATION_OPENED,
        f"{ticker} abre oferta de privatização: {_government(party)} vende "
        f"{format_quantity(Decimal(shares))} ações",
        f"Quem quer ações reserva a quantidade até {ends_on:%d/%m}; o caixa só paga no fechamento.",
        (ticker,),
        party_abbrs=_abbrs(party),
    )


def privatized(
    ticker: str,
    price: Decimal,
    proceeds: Decimal,
    prorated: bool,
    party: str | None,
) -> Headline:
    dek = (
        "Os pedidos passaram da oferta e as ações foram rateadas entre os compradores."
        if prorated
        else "Os pedidos couberam na oferta; a sobra vai ao formador de mercado."
    )
    return Headline(
        NewsType.STATE_PRIVATIZATION_CLOSED,
        f"{ticker} é privatizada a {format_money(price)} por ação e o Tesouro recebe "
        f"{format_money(proceeds)}",
        dek,
        (ticker,),
        party_abbrs=_abbrs(party),
    )


def control_in_force(ticker: str, percent: int, party: str | None) -> Headline:
    return Headline(
        NewsType.STATE_CONTROL_IN_FORCE,
        f"{_government(party)} passa a segurar em {percent}% o preço da {ticker}",
        "A inflação fica menor enquanto durar o controle, e o lucro da estatal encolhe.",
        (ticker,),
        party_abbrs=_abbrs(party),
    )


def control_released(
    tickers: tuple[str, ...], points: Decimal | None, party: str | None
) -> Headline:
    names = " e ".join(tickers)
    if points is None:
        return Headline(
            NewsType.STATE_CONTROL_RELEASED,
            f"{_government(party)} solta o preço da {names}",
            "As outras estatais seguem com o preço segurado: a inflação represada ainda não volta.",
            tickers,
            party_abbrs=_abbrs(party),
        )
    return Headline(
        NewsType.STATE_CONTROL_RELEASED,
        f"{_government(party)} solta o preço da {names} e a inflação represada volta: "
        f"{format_quantity(points)} {'ponto' if points <= 1 else 'pontos'} de IPCA",
        "O que o controle segurou nos meses anteriores volta de uma vez aos preços e entra no IPCA de 12 meses.",
        tickers,
        party_abbrs=_abbrs(party),
    )


def dividend_policy_changed(
    ticker: str, policy: DividendPolicy, party: str | None
) -> Headline:
    verb = POLICY_VERBS[policy].format(ticker=ticker)
    return Headline(
        NewsType.STATE_DIVIDEND_POLICY_CHANGED,
        f"{_government(party)} {verb}",
        f"A política passa a pagar {_percent(payout.payout_ratio(policy))} do lucro aos acionistas.",
        (ticker,),
        party_abbrs=_abbrs(party),
    )
