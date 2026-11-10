"""
O capital político: os pontos que decidem a vitória política. Só partidos de jogador pontuam.
Cada parcela chega em pontos inteiros, arredondados uma vez por partido (meio para cima).
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from backend.core.dto.political_capital import PoliticalCapitalDTO
from backend.features.government import congress
from backend.features.government.state import GovernmentState, Party

# Pontos de cada promessa cumprida por inteiro no balanço do mandato
PROMISE_POINTS = 100
# A fração da pontuação da presidência que o impeachment tira daquele mandato
IMPEACHMENT_LOSS = Decimal("0.5")


def party_capital(state: GovernmentState) -> list[tuple[Party, PoliticalCapitalDTO]]:
    """
    O capital de cada partido de jogador, do maior para o menor; empata pela bancada da
    casa em exercício e depois pelo id do partido.
    """
    today = state.today
    if today is None:
        return []
    parties = state.player_parties()
    seats = _seat_points(state, parties, today)
    current = state.house_on(today)

    ranked = []
    for party in parties:
        presidency = sum(
            m.approval for m in state.governed_months if m.party_id == party.id
        )
        promises = _promise_points(state, party)
        impeachment = -_impeachment_loss(state, party)
        capital = PoliticalCapitalDTO(
            total=seats[party.id] + presidency + promises + impeachment,
            seats=seats[party.id],
            presidency=presidency,
            promises=promises,
            impeachment=impeachment,
        )
        bloc = current.of_party(party.id)
        ranked.append((party, capital, bloc.seats if bloc else 0))
    ranked.sort(key=lambda item: (-item[1].total, -item[2], item[0].id))
    return [(party, capital) for party, capital, _ in ranked]


def _seat_points(
    state: GovernmentState, parties: list[Party], today: date
) -> dict[int, int]:
    """Uma cadeira vale 1 ponto por fechamento de mês (o último dia útil) desde a posse da 1ª casa eleita."""
    points = {party.id: 0 for party in parties}
    if not state.houses:
        return points
    first = state.houses[0].takes_office
    year, month = first.year, first.month
    while date(year, month, 1) <= today:
        closing = congress.last_business_day(year, month)
        if first <= closing <= today:
            current = state.house_on(closing)
            for party in parties:
                bloc = current.of_party(party.id)
                points[party.id] += bloc.seats if bloc else 0
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    return points


def _promise_points(state: GovernmentState, party: Party) -> int:
    """Cada promessa do balanço rende `PROMISE_POINTS` pela fração cumprida; fração negativa vale 0."""
    done = sum(
        (
            max(Decimal(0), item.done)
            for balance in state.balances
            if balance.party_id == party.id
            for item in balance.items
        ),
        Decimal(0),
    )
    return _rounded(done * PROMISE_POINTS)


def _impeachment_loss(state: GovernmentState, party: Party) -> int:
    """O que a presidência rendeu nos mandatos derrubados do partido, na fração `IMPEACHMENT_LOSS`."""
    earned = sum(
        m.approval
        for impeachment in state.impeachments
        if impeachment.party_id == party.id
        for m in state.governed_months
        if m.party_id == party.id and m.term_start == impeachment.term_start
    )
    return _rounded(earned * IMPEACHMENT_LOSS)


def _rounded(value: Decimal | int) -> int:
    return int(Decimal(value).to_integral_value(rounding=ROUND_HALF_UP))
