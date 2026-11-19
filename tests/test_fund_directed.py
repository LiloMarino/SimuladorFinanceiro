"""Emissão dirigida pela fachada da partida, com banco: preço, teto, taxa a pagar, bloqueios, expiração e queda da oferta."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.fund import FundDirectedIssuanceRequest
from backend.core.dto.user import UserDTO
from backend.core.enum import FundDirectedIssuanceStatus, PendingType
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.features.funds.fund_book import ISSUANCE_LIMIT
from backend.features.funds.fund_comanagers import INVITE_DAYS
from backend.features.funds.fund_directed import cap_room, directed_price
from backend.features.simulation.simulation import Simulation
from tests.test_fund_comanagers import active_comanager
from tests.test_fund_flow import book_of, fund_with_cash, player
from tests.test_fund_simulation import TICKER, empty_match
from tests.test_simulation_loader import started  # noqa: F401

PRICE_AT_NAV = Decimal(100)


def request(quotas: int, buyer: str | None = None) -> FundDirectedIssuanceRequest:
    return FundDirectedIssuanceRequest(quotas=quotas, buyer_nickname=buyer)


def offers(sim: Simulation, user: UserDTO):
    return [
        p
        for p in sim.get_pending(user)
        if p.type is PendingType.DIRECTED_ISSUANCE_OFFER
    ]


@pytest.fixture
def match(started):  # noqa: F811
    """A gestora da Ana listada, sem oferta aberta: 57 cotas ao PL de R$ 100, 50 delas da Ana; Bruno e Carla são jogadores."""
    sim, ana = empty_match("Bruno", "Carla")
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)
    sim.close_fund_offer(ana, fund_id)
    return sim, ana, player(sim, "Bruno"), fund_id


def run_until(sim: Simulation, day: date) -> None:
    while sim._engine.current_date < day:
        sim.next_tick()


def set_ranking_price(sim: Simulation, price: str) -> None:
    sim._engine.ranking_prices[TICKER] = Decimal(price)


# =========================
# Regras de preço e de teto
# =========================


def test_the_price_is_the_higher_of_the_nav_and_the_ranking_price_to_the_cent():
    assert directed_price(Decimal(100), Decimal(120)) == Decimal("120.00")
    assert directed_price(Decimal("130.004"), Decimal(120)) == Decimal("130.00")


def test_the_room_is_what_keeps_the_combined_stake_under_the_cap():
    # 19.590 de 35.740 cotas com teto de 70%: (0,7 x 35.740 - 19.590) / 0,3 = 18.093,3
    assert cap_room(Decimal(19590), Decimal(35740), Decimal("0.7")) == 18093
    assert cap_room(Decimal(30000), Decimal(35740), Decimal("0.7")) == 0
    assert cap_room(Decimal(1), Decimal(10), Decimal(1)) == Decimal("Infinity")


# =========================
# Emissão para si
# =========================


def test_issuing_to_oneself_pays_the_ranking_price_without_commission(match):
    sim, ana, _bruno, fund_id = match
    set_ranking_price(sim, "120")
    fund = book_of(sim).get(TICKER)
    cash_before = sim._engine.get_cash(ana.client_id)
    fund_cash = sim._engine.get_cash(fund.account.client_id)

    assert sim.issue_fund_directed(ana, fund_id, request(10)) is None

    assert sim._engine.get_cash(ana.client_id) == cash_before - 1200
    assert sim._engine.get_cash(fund.account.client_id) == fund_cash + 1200
    held = sim._engine.broker.get_positions(ana.client_id)[TICKER]
    assert (held.size, held.avg_price) == (60, Decimal(6200) / 60)
    assert fund.account.quotas == 67
    movements = [m for m in sim.get_fund(ana, fund_id).movements]
    [movement] = [m for m in movements if m.type == "directed_issuance"]
    assert (movement.quotas, movement.price, movement.amount) == (10, 120, 1200)


def test_the_nav_is_the_price_when_it_is_above_the_ranking(match):
    sim, ana, _bruno, fund_id = match
    set_ranking_price(sim, "90")
    cash_before = sim._engine.get_cash(ana.client_id)

    sim.issue_fund_directed(ana, fund_id, request(10))

    assert sim._engine.get_cash(ana.client_id) == cash_before - 1000


def test_the_payable_fee_is_settled_by_the_new_money_at_once(match):
    sim, ana, _bruno, fund_id = match
    set_ranking_price(sim, "100")
    fund = book_of(sim).get(TICKER)
    client = fund.account.client_id
    fund.terms = fund.terms.model_copy(update={"management_fee_payable": Decimal(500)})
    sim._engine.fund_fee_payable[client] = Decimal(500)
    fund_cash = sim._engine.get_cash(client)
    ana_cash = sim._engine.get_cash(ana.client_id)

    sim.issue_fund_directed(ana, fund_id, request(10))

    assert fund.terms.fee_payable == 0
    assert sim._engine.fund_fee_payable[client] == 0
    # O PL por cota já descontava a taxa (R$ 90); o preço é o do ranking, de R$ 100
    assert sim._engine.get_cash(client) == fund_cash + 1000 - 500
    # A taxa vai ao gestor principal, que é dono de toda a parte
    assert sim._engine.get_cash(ana.client_id) == ana_cash - 1000 + 500


def test_without_the_hostile_takeover_mode_the_room_is_the_issuance_limit(match):
    sim, _ana, _bruno, _fund_id = match
    book = book_of(sim)
    fund = book.get(TICKER)

    assert book.manager_cap is None
    assert book.directed_room(fund) == fund.account.quotas * ISSUANCE_LIMIT


def test_the_cap_counts_the_principal_and_the_active_comanagers_together(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    book = book_of(sim)
    book._manager_cap = Decimal("0.97")
    fund = book.get(TICKER)
    alone = book.directed_room(fund)

    sim._engine.broker.receive_position(
        bruno.client_id, TICKER, Decimal(5), PRICE_AT_NAV
    )

    # 57 cotas, 55 nas mãos de quem gere: (0,97 x 57 - 55) / 0,03 = 9,67
    assert book.directed_room(fund) == 9
    assert alone > 9
    with pytest.raises(UnprocessableEntityError, match="até 9 cotas"):
        sim.issue_fund_directed(ana, fund_id, request(10))
    sim.issue_fund_directed(ana, fund_id, request(9))


# =========================
# Bloqueios
# =========================


def test_an_unlisted_fund_does_not_issue_directed_quotas(started):  # noqa: F811
    sim, ana = empty_match()
    fund_id = fund_with_cash(sim, ana)

    with pytest.raises(ConflictError, match="depois da oferta pública"):
        sim.issue_fund_directed(ana, fund_id, request(10))


def test_an_open_offer_blocks_the_directed_issuance(started):  # noqa: F811
    sim, ana = empty_match()
    fund_id = fund_with_cash(sim, ana)
    sim.open_fund_offer(ana, fund_id, 20)

    with pytest.raises(ConflictError, match="oferta ou emissão"):
        sim.issue_fund_directed(ana, fund_id, request(10))


def test_only_the_principal_issues_and_the_buyer_must_be_an_active_comanager(match):
    sim, ana, bruno, fund_id = match

    with pytest.raises(ForbiddenError):
        sim.issue_fund_directed(bruno, fund_id, request(10))
    with pytest.raises(UnprocessableEntityError, match="co-gestor ativo"):
        sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))
    with pytest.raises(UnprocessableEntityError, match="jogador"):
        sim.issue_fund_directed(ana, fund_id, request(10, "Ninguém"))


def test_a_pending_offer_blocks_a_second_one_and_the_issuance_to_oneself(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))

    with pytest.raises(ConflictError, match="esperando resposta"):
        sim.issue_fund_directed(ana, fund_id, request(5, "Bruno"))
    with pytest.raises(ConflictError, match="esperando resposta"):
        sim.issue_fund_directed(ana, fund_id, request(5))


def test_the_principal_without_cash_is_refused(match):
    sim, ana, _bruno, fund_id = match
    sim._engine.add_cash(ana.client_id, -sim._engine.get_cash(ana.client_id) + 99)

    with pytest.raises(ConflictError, match="Caixa insuficiente"):
        sim.issue_fund_directed(ana, fund_id, request(1))


# =========================
# Oferta ao co-gestor
# =========================


def test_the_offer_keeps_only_the_quantity_and_settles_at_the_price_of_the_acceptance(
    match,
):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    cash_before = sim._engine.get_cash(bruno.client_id)

    offer = sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))

    assert offer is not None
    assert (offer.quotas, offer.price) == (10, None)
    [pending] = offers(sim, bruno)
    assert pending.fund_id == fund_id
    page = sim.get_fund(ana, fund_id)
    assert page.directed_issuance is not None
    assert page.directed_issuance.buyer_nickname == "Bruno"
    assert page.directed_issuance.expires_on == sim._current_date + timedelta(
        days=INVITE_DAYS
    )

    set_ranking_price(sim, "120")
    sim.accept_fund_directed(bruno, fund_id)

    assert sim._engine.get_cash(bruno.client_id) == cash_before - 1200
    held = sim._engine.broker.get_positions(bruno.client_id)[TICKER]
    assert (held.size, held.avg_price) == (10, 120)
    assert offers(sim, bruno) == []
    assert sim.get_fund(ana, fund_id).directed_issuance is None
    [stored] = repository.fund_directed_issuance.settled_of_fund(
        book_of(sim).get(TICKER).terms.id
    )
    assert (stored.price, stored.status) == (120, FundDirectedIssuanceStatus.ACCEPTED)


def test_the_acceptance_without_cash_is_refused_and_the_offer_stays(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))
    sim._engine.add_cash(bruno.client_id, -sim._engine.get_cash(bruno.client_id) + 100)

    with pytest.raises(ConflictError, match="Caixa insuficiente"):
        sim.accept_fund_directed(bruno, fund_id)

    assert len(offers(sim, bruno)) == 1


def test_the_acceptance_is_refused_when_the_cap_closed_meanwhile(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))
    book_of(sim)._manager_cap = Decimal("0.5")

    with pytest.raises(ConflictError, match="vai até"):
        sim.accept_fund_directed(bruno, fund_id)


def test_only_the_buyer_answers(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))

    with pytest.raises(NotFoundError):
        sim.decline_fund_directed(player(sim, "Carla"), fund_id)


def test_the_refusal_and_the_cancellation_close_the_offer(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    fund = book_of(sim).get(TICKER)

    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))
    sim.decline_fund_directed(bruno, fund_id)
    assert fund.directed is None
    assert offers(sim, bruno) == []

    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))
    sim.cancel_fund_directed(ana, fund_id)
    assert fund.directed is None
    with pytest.raises(NotFoundError):
        sim.cancel_fund_directed(ana, fund_id)


def test_the_unanswered_offer_expires_after_seven_days(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))

    offered_on = sim._engine.current_date
    run_until(sim, offered_on + timedelta(days=INVITE_DAYS - 1))
    assert book_of(sim).get(TICKER).directed is not None
    run_until(sim, offered_on + timedelta(days=INVITE_DAYS + 1))

    assert book_of(sim).get(TICKER).directed is None
    assert offers(sim, bruno) == []
    with pytest.raises(NotFoundError):
        sim.accept_fund_directed(bruno, fund_id)


def test_removing_or_losing_the_comanager_drops_the_offer(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    fund = book_of(sim).get(TICKER)

    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))
    sim.remove_fund_comanager(ana, fund_id, bruno.id)
    assert fund.directed is None

    active_comanager(sim, ana, fund_id, bruno)
    sim.issue_fund_directed(ana, fund_id, request(10, "Bruno"))
    sim.leave_fund_comanagement(bruno, fund_id)
    assert fund.directed is None
    assert offers(sim, bruno) == []


def test_the_preview_is_the_view_of_the_buyer_who_asks(match):
    sim, ana, bruno, fund_id = match
    set_ranking_price(sim, "120")

    preview = sim.preview_fund_directed(ana, fund_id, 10)

    assert (preview.nav, preview.ranking_price, preview.price) == (100, 120, 120)
    assert preview.cost == 1200
    assert preview.cash_enough is True
    with pytest.raises(ForbiddenError):
        sim.preview_fund_directed(bruno, fund_id, 10)
