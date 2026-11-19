"""Co-gestores da gestora, pela fachada da partida, com banco: convite, partes das taxas, saída e sucessão."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_DOWN, Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from backend.core import repository
from backend.core.dto.fund import (
    FundComanagerInviteRequest,
    FundComanagerShareRequest,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CashflowEventType,
    FundComanagerStatus,
    PendingType,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.core.runtime.realtime_broker_manager import RealtimeBrokerManager
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_month_turn
from backend.features.funds.fees import CENT
from backend.features.funds.fund_comanagers import INVITE_DAYS, MAX_COMANAGERS
from backend.features.simulation.simulation import Simulation
from tests.test_fund_flow import (
    book_of,
    found_request,
    fund_with_cash,
    governing,
    player,
    run_days,
)
from tests.test_fund_simulation import TICKER, empty_match
from tests.test_simulation_loader import started  # noqa: F401

SHARE = Decimal("0.30")


def invite(sim: Simulation, ana: UserDTO, fund_id: int, nickname: str, share=SHARE):
    sim.invite_fund_comanager(
        ana, fund_id, FundComanagerInviteRequest(nickname=nickname, share=share)
    )


def comanager_of(sim: Simulation, user: UserDTO):
    fund = book_of(sim).get(TICKER)
    return next((c for c in fund.comanagers if c.user_id == user.id), None)


def active_comanager(
    sim: Simulation, ana: UserDTO, fund_id: int, guest: UserDTO, share=SHARE
) -> None:
    """O convidado aceita e a parte dele já está em vigor."""
    invite(sim, ana, fund_id, guest.nickname, share)
    sim.answer_fund_comanager_invite(guest, fund_id, True)
    book_of(sim)._comanagers.apply_pending(
        book_of(sim).get(TICKER), sim._current_date + timedelta(days=40)
    )


@pytest.fixture
def match(started):  # noqa: F811
    """Ana gere a gestora (50 cotas em caixa) e Bruno, Carla e Davi são jogadores da sala."""
    sim, ana = empty_match("Bruno", "Carla", "Davi", "Eva")
    return sim, ana, player(sim, "Bruno"), fund_with_cash(sim, ana)


@pytest.fixture
def notices(monkeypatch) -> list[tuple[str, object]]:
    """Os eventos de tempo real da partida com o destinatário de cada um."""
    sent: list[tuple[str, object]] = []
    monkeypatch.setattr(
        RealtimeBrokerManager,
        "get_broker",
        lambda: SimpleNamespace(
            subscribed_clients=lambda _event: set(),
            notify=lambda event, payload, to=None: sent.append((event, to)),
        ),
    )
    return sent


# =========================
# Convite
# =========================


def test_invite_reserves_the_share_and_waits_for_the_answer(match):
    sim, ana, bruno, fund_id = match

    invite(sim, ana, fund_id, "Bruno")

    row = comanager_of(sim, bruno)
    assert row is not None
    assert row.status is FundComanagerStatus.INVITED
    assert (row.share, row.pending_share) == (0, SHARE)
    page = sim.get_fund(ana, fund_id)
    assert page.manager_share == 1
    assert [(c.nickname, c.status) for c in page.comanagers] == [
        ("Bruno", FundComanagerStatus.INVITED)
    ]
    assert page.comanagers[0].expires_on == sim._current_date + timedelta(
        days=INVITE_DAYS
    )
    # O convite não dá acesso à carteira
    with pytest.raises(ForbiddenError):
        sim.acting_client(bruno.client_id, fund_id)


def test_invited_player_sees_a_pending_item_until_he_answers(match):
    sim, ana, bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")

    items = [
        p for p in sim.get_pending(bruno) if p.type is PendingType.COMANAGER_INVITE
    ]

    assert [p.key.endswith(str(fund_id)) for p in items] == [True]
    sim.answer_fund_comanager_invite(bruno, fund_id, False)
    assert not [
        p for p in sim.get_pending(bruno) if p.type is PendingType.COMANAGER_INVITE
    ]


def test_only_the_principal_invites(match):
    sim, _ana, bruno, fund_id = match

    with pytest.raises(ForbiddenError):
        invite(sim, bruno, fund_id, "Carla")


def test_a_bot_is_not_invited(started):  # noqa: F811
    sim, ana = empty_match("Bruno")
    bot = repository.user.create_user(uuid4(), "Robô", is_bot=True)
    UserManager.player_auth(bot.client_id)
    repository.simulation_player.save(
        sim.settings.id, {ana.id: "#111111", bot.id: "#222222"}
    )
    fund_id = fund_with_cash(sim, ana)

    with pytest.raises(UnprocessableEntityError, match="jogador"):
        invite(sim, ana, fund_id, "Robô")


def test_invite_refuses_unknown_nickname_manager_and_duplicates(match):
    sim, ana, _bruno, fund_id = match

    with pytest.raises(UnprocessableEntityError):
        invite(sim, ana, fund_id, "Ninguém")
    with pytest.raises(UnprocessableEntityError, match="gestor"):
        invite(sim, ana, fund_id, "Ana")
    invite(sim, ana, fund_id, "Bruno")
    with pytest.raises(ConflictError):
        invite(sim, ana, fund_id, "Bruno")


def test_shares_must_leave_a_part_for_the_principal(match):
    sim, ana, _bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno", Decimal("0.60"))

    with pytest.raises(UnprocessableEntityError, match="parte"):
        invite(sim, ana, fund_id, "Carla", Decimal("0.40"))
    invite(sim, ana, fund_id, "Carla", Decimal("0.39"))


def test_the_fund_takes_up_to_three_comanagers_counting_the_invites(match):
    sim, ana, _bruno, fund_id = match
    assert MAX_COMANAGERS == 3
    for nickname in ("Bruno", "Carla", "Davi"):
        invite(sim, ana, fund_id, nickname, Decimal("0.10"))

    with pytest.raises(ConflictError, match="até 3"):
        invite(sim, ana, fund_id, "Eva", Decimal("0.10"))


def test_declined_invite_returns_the_reserved_share(match):
    sim, ana, bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")

    sim.answer_fund_comanager_invite(bruno, fund_id, False)

    assert comanager_of(sim, bruno) is None
    assert sim.get_fund(ana, fund_id).comanagers == []


def test_unanswered_invite_expires_after_seven_days(match):
    sim, ana, bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")

    run_days(sim, 4)
    assert comanager_of(sim, bruno) is not None
    run_days(sim, 5)

    assert comanager_of(sim, bruno) is None


def test_the_principal_withdraws_a_pending_invite(match):
    sim, ana, bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")

    sim.remove_fund_comanager(ana, fund_id, bruno.id)

    assert comanager_of(sim, bruno) is None
    assert repository.fund_comanager.events(book_of(sim).get(TICKER).terms.id) == []


# =========================
# Aceite, acesso e partes
# =========================


def test_accepting_gives_access_now_and_the_share_next_month(match):
    sim, ana, bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")

    sim.answer_fund_comanager_invite(bruno, fund_id, True)

    row = comanager_of(sim, bruno)
    assert row is not None
    assert row.status is FundComanagerStatus.ACTIVE
    assert (row.share, row.pending_share) == (0, SHARE)
    assert row.pending_from == next_month_turn(sim._current_date)
    fund = book_of(sim).get(TICKER)
    assert sim.acting_client(bruno.client_id, fund_id) == fund.account.client_id
    page = sim.get_fund(bruno, fund_id)
    assert page.my_role == "comanager"
    assert page.positions is not None
    assert sim.get_fund(ana, fund_id).my_role == "manager"
    assert [a.role for a in sim.get_fund_accounts(bruno)] == [None, "comanager"]


def test_the_comanager_only_operates_the_portfolio(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)

    with pytest.raises(ForbiddenError, match="gestor"):
        sim.invite_fund_comanager(
            bruno, fund_id, FundComanagerInviteRequest(nickname="Carla", share=SHARE)
        )
    with pytest.raises(ForbiddenError):
        sim.remove_fund_comanager(bruno, fund_id, bruno.id)


def test_a_viewer_does_not_see_the_portfolio_nor_operate(match):
    sim, _ana, bruno, fund_id = match

    assert sim.get_fund(bruno, fund_id).my_role == "viewer"
    assert sim.get_fund(bruno, fund_id).positions is None
    with pytest.raises(ForbiddenError):
        sim.acting_client(bruno.client_id, fund_id)


def test_scheduled_share_applies_on_the_next_month_turn(match):
    sim, ana, bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")
    sim.answer_fund_comanager_invite(bruno, fund_id, True)

    run_days(sim, 25)

    row = comanager_of(sim, bruno)
    assert row is not None
    assert (row.share, row.pending_share, row.pending_from) == (SHARE, None, None)
    assert sim.get_fund(ana, fund_id).manager_share == 1 - SHARE
    assert sim.get_fund(bruno, fund_id).my_share == SHARE


def test_changing_a_share_is_scheduled_and_the_current_one_undoes_it(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)

    sim.change_fund_comanager_share(
        ana, fund_id, bruno.id, FundComanagerShareRequest(share=Decimal("0.40"))
    )
    row = comanager_of(sim, bruno)
    assert row is not None
    assert (row.share, row.pending_share) == (SHARE, Decimal("0.40"))
    assert row.pending_from == next_month_turn(sim._current_date)

    sim.change_fund_comanager_share(
        ana, fund_id, bruno.id, FundComanagerShareRequest(share=SHARE)
    )
    row = comanager_of(sim, bruno)
    assert row is not None
    assert (row.pending_share, row.pending_from) == (None, None)


def test_changing_a_share_keeps_the_sum_below_one(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno, Decimal("0.50"))
    invite(sim, ana, fund_id, "Carla", Decimal("0.40"))

    with pytest.raises(UnprocessableEntityError):
        sim.change_fund_comanager_share(
            ana, fund_id, bruno.id, FundComanagerShareRequest(share=Decimal("0.60"))
        )


# =========================
# Saída
# =========================


def test_leaving_drops_the_access_in_the_same_session_and_the_share_goes_back(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)

    sim.leave_fund_comanagement(bruno, fund_id)

    assert comanager_of(sim, bruno) is None
    with pytest.raises(ForbiddenError):
        sim.acting_client(bruno.client_id, fund_id)
    assert sim.get_fund(ana, fund_id).manager_share == 1
    kinds = [m.type for m in sim.get_fund(ana, fund_id).movements]
    assert kinds.count("comanager_joined") == 1
    assert kinds.count("comanager_left") == 1


def test_removing_drops_the_access_in_the_same_session(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)

    sim.remove_fund_comanager(ana, fund_id, bruno.id)

    with pytest.raises(ForbiddenError):
        sim.acting_client(bruno.client_id, fund_id)
    left = [
        m for m in sim.get_fund(ana, fund_id).movements if m.type == "comanager_left"
    ]
    assert [m.nickname for m in left] == ["Bruno"]


def test_only_an_active_comanager_leaves(match):
    sim, ana, bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")

    with pytest.raises(ConflictError):
        sim.leave_fund_comanagement(bruno, fund_id)


# =========================
# Taxas
# =========================


def cash_incomes(sim: Simulation, user: UserDTO) -> list[Decimal]:
    events = repository.event.get_cashflow_events(
        sim.settings.id, UserManager.get_portfolio_id(user.client_id)
    )
    return sorted(
        e.amount
        for e in events
        if e.event_type is CashflowEventType.FUND_MANAGEMENT_FEE_INCOME
    )


def test_the_management_fee_is_split_to_the_cent_between_principal_and_comanager(
    match,
):
    sim, ana, bruno, fund_id = match
    sim.open_fund_offer(ana, fund_id, 20)
    invite(sim, ana, fund_id, "Bruno")
    sim.answer_fund_comanager_invite(bruno, fund_id, True)

    run_days(sim, 45)

    fees = sorted(
        m.amount
        for m in sim.get_fund(ana, fund_id).movements
        if m.type == "management_fee" and m.amount is not None
    )
    assert len(fees) == 2
    to_bruno = sorted((fee * SHARE).quantize(CENT, ROUND_DOWN) for fee in fees)
    assert cash_incomes(sim, bruno) == to_bruno
    assert cash_incomes(sim, ana) == sorted(
        fee - (fee * SHARE).quantize(CENT, ROUND_DOWN) for fee in fees
    )
    assert sum(cash_incomes(sim, bruno)) + sum(cash_incomes(sim, ana)) == sum(fees)


def test_a_comanager_who_left_does_not_receive_the_next_fee(match):
    sim, ana, bruno, fund_id = match
    sim.open_fund_offer(ana, fund_id, 20)
    active_comanager(sim, ana, fund_id, bruno)
    sim.leave_fund_comanagement(bruno, fund_id)

    run_days(sim, 45)

    assert cash_incomes(sim, bruno) == []
    assert len(cash_incomes(sim, ana)) == 2


# =========================
# Sucessão na presidência
# =========================


def heir_match(match):
    """Bruno (30%) e Carla (20%) são co-gestores ativos da gestora da Ana."""
    sim, ana, bruno, fund_id = match
    carla = player(sim, "Carla")
    active_comanager(sim, ana, fund_id, bruno, Decimal("0.30"))
    active_comanager(sim, ana, fund_id, carla, Decimal("0.20"))
    return sim, ana, bruno, carla, fund_id


def test_the_comanager_with_the_largest_share_becomes_principal_when_the_manager_governs(
    match,
):
    sim, ana, bruno, carla, fund_id = heir_match(match)
    governing(sim, ana, date(2004, 12, 31))

    sim._take_office(ana, sim._current_date)

    fund = book_of(sim).get(TICKER)
    assert fund.terms.manager_user_id == bruno.id
    assert fund.terms.manager_since == sim._current_date
    # Ana sai da gestão, a parte de Bruno se soma à do principal e Carla mantém a dela
    assert book_of(sim).operators(fund) == [bruno.id, carla.id]
    assert [c.user_id for c in fund.comanagers] == [carla.id]
    page = sim.get_fund(bruno, fund_id)
    assert page.my_role == "manager"
    assert page.manager_share == 1 - Decimal("0.20")
    assert sim.get_fund(ana, fund_id).my_role == "viewer"
    assert sim.get_fund(ana, fund_id).frozen_until is None
    with pytest.raises(ForbiddenError):
        sim.acting_client(ana.client_id, fund_id)
    left = [m for m in page.movements if m.type == "comanager_left"]
    assert [m.nickname for m in left] == ["Ana"]


def test_a_tie_goes_to_the_oldest_comanager(match):
    sim, ana, bruno, carla, fund_id = heir_match(match)
    same = Decimal("0.25")
    for user in (bruno, carla):
        sim.change_fund_comanager_share(
            ana, fund_id, user.id, FundComanagerShareRequest(share=same)
        )
    book = book_of(sim)
    book._comanagers.apply_pending(
        book.get(TICKER), sim._current_date + timedelta(days=40)
    )
    governing(sim, ana, date(2004, 12, 31))

    sim._take_office(ana, sim._current_date)

    assert book.get(TICKER).terms.manager_user_id == bruno.id


def test_the_heir_takes_over_with_the_manager_on_leave(match):
    sim, ana, bruno, _carla, _fund_id = heir_match(match)
    governing(sim, ana, date(2004, 12, 31))

    sim._take_office(ana, sim._current_date)

    terms = book_of(sim).get(TICKER).terms
    assert (terms.manager_user_id, terms.leave_manager_user_id) == (bruno.id, ana.id)
    assert terms.leave_heir_share == Decimal("0.30")
    # A licença fica gravada, e a lista diz até quando a gestão está com o herdeiro
    [stored] = repository.fund.of_simulation(sim.settings.id)
    assert (stored.leave_manager_user_id, stored.leave_heir_share) == (
        ana.id,
        Decimal("0.30"),
    )
    summary = book_of(sim).summary(book_of(sim).get(TICKER))
    assert summary.leave_until == date(2004, 12, 31)
    assert summary.frozen_until is None


def test_the_manager_resumes_the_fund_when_the_term_ends_without_reelection(match):
    sim, ana, bruno, carla, fund_id = heir_match(match)
    state = governing(sim, ana, date(2004, 12, 31))
    sim._take_office(ana, sim._current_date)
    state["on"] = False

    sim._leave_office(ana, sim._current_date)

    fund = book_of(sim).get(TICKER)
    assert fund.terms.manager_user_id == ana.id
    assert fund.terms.manager_since == sim._current_date
    assert (fund.terms.leave_manager_user_id, fund.terms.leave_heir_share) == (
        None,
        None,
    )
    # Bruno volta a co-gestor com os 30% de antes, e a parte de Ana volta a ser o que sobra
    returned = comanager_of(sim, bruno)
    assert returned is not None
    assert (returned.status, returned.share) == (
        FundComanagerStatus.ACTIVE,
        Decimal("0.30"),
    )
    assert sorted(book_of(sim).operators(fund)) == sorted([ana.id, bruno.id, carla.id])
    page = sim.get_fund(ana, fund_id)
    assert page.my_role == "manager"
    assert page.manager_share == Decimal("0.50")
    assert sim.get_fund(bruno, fund_id).my_role == "comanager"
    [stored] = repository.fund.of_simulation(sim.settings.id)
    assert stored.manager_user_id == ana.id
    assert stored.leave_manager_user_id is None


def test_the_fund_frozen_without_an_heir_needs_no_handover_when_the_term_ends(match):
    sim, ana, _bruno, fund_id = match
    state = governing(sim, ana, date(2004, 12, 31))
    sim._take_office(ana, sim._current_date)
    assert sim.get_fund(ana, fund_id).frozen_until == date(2004, 12, 31)
    state["on"] = False

    sim._leave_office(ana, sim._current_date)

    fund = book_of(sim).get(TICKER)
    assert fund.terms.manager_user_id == ana.id
    assert fund.terms.leave_manager_user_id is None
    assert sim.get_fund(ana, fund_id).frozen_until is None


def test_the_assembly_that_replaced_the_heir_keeps_the_fund_from_the_manager(match):
    sim, ana, _bruno, carla, _fund_id = heir_match(match)
    state = governing(sim, ana, date(2004, 12, 31))
    sim._take_office(ana, sim._current_date)
    book = book_of(sim)
    # A assembleia troca o gestor da gestora durante o mandato
    book._replace_manager(book.get(TICKER), carla.id)
    state["on"] = False

    sim._leave_office(ana, sim._current_date)

    fund = book.get(TICKER)
    assert fund.terms.manager_user_id == carla.id
    assert fund.terms.leave_manager_user_id is None
    assert ana.id not in book.operators(fund)
    assert book.held_by(ana.id) == []


def test_the_heir_does_not_return_as_comanager_when_the_list_is_full(match):
    sim, ana, bruno, _carla, fund_id = heir_match(match)
    state = governing(sim, ana, date(2004, 12, 31))
    sim._take_office(ana, sim._current_date)
    # Bruno gere e completa a lista com Davi e Eva, que ocupam as vagas deixadas por ele
    for guest in (player(sim, "Davi"), player(sim, "Eva")):
        active_comanager(sim, bruno, fund_id, guest, Decimal("0.05"))
    assert len(book_of(sim).get(TICKER).comanagers) == MAX_COMANAGERS
    state["on"] = False

    sim._leave_office(ana, sim._current_date)

    fund = book_of(sim).get(TICKER)
    assert fund.terms.manager_user_id == ana.id
    assert comanager_of(sim, bruno) is None


def test_the_heir_does_not_return_as_comanager_when_the_shares_leave_nothing_for_him(
    match,
):
    sim, ana, bruno, _carla, fund_id = heir_match(match)
    state = governing(sim, ana, date(2004, 12, 31))
    sim._take_office(ana, sim._current_date)
    # Com Carla em 20%, a parte de Davi deixa a soma em 95%: os 30% de Bruno não cabem
    active_comanager(sim, bruno, fund_id, player(sim, "Davi"), Decimal("0.75"))
    state["on"] = False

    sim._leave_office(ana, sim._current_date)

    fund = book_of(sim).get(TICKER)
    assert fund.terms.manager_user_id == ana.id
    assert comanager_of(sim, bruno) is None


def test_the_room_list_names_the_active_comanagers_and_marks_who_is_one(match):
    sim, ana, bruno, fund_id = match
    carla = player(sim, "Carla")
    active_comanager(sim, ana, fund_id, bruno, Decimal("0.30"))
    invite(sim, ana, fund_id, carla.nickname)

    [as_ana] = sim.get_funds(ana)
    [as_bruno] = sim.get_funds(bruno)
    [as_carla] = sim.get_funds(carla)

    # O convite pendente de Carla não a torna co-gestora
    assert as_ana.comanager_nicknames == ["Bruno"]
    assert (as_ana.i_comanage, as_bruno.i_comanage, as_carla.i_comanage) == (
        False,
        True,
        False,
    )


def test_who_has_a_fund_cannot_found_another(match):
    sim, ana, _bruno, _fund_id = match

    with pytest.raises(ConflictError, match="Fundar exige não ter gestora"):
        sim.found_fund(ana, found_request("OMEG11"))


def test_the_president_with_the_fund_frozen_cannot_found_another(match):
    sim, ana, _bruno, _fund_id = match
    governing(sim, ana, date(2004, 12, 31))
    sim._take_office(ana, sim._current_date)

    with pytest.raises(ConflictError, match="Fundar exige não ter gestora"):
        sim.found_fund(ana, found_request("OMEG11"))


def test_the_manager_on_leave_still_has_the_fund_and_cannot_found_another(match):
    sim, ana, _bruno, _carla, _fund_id = heir_match(match)
    governing(sim, ana, date(2004, 12, 31))
    sim._take_office(ana, sim._current_date)

    assert [f.ticker for f in book_of(sim).held_by(ana.id)] == [TICKER]
    with pytest.raises(ConflictError, match="Fundar exige não ter gestora"):
        sim.found_fund(ana, found_request("OMEG11"))


def test_who_lost_the_fund_founds_another(match):
    sim, ana, bruno, _fund_id = match
    book = book_of(sim)
    book._replace_manager(book.get(TICKER), bruno.id)

    founded = sim.found_fund(ana, found_request("OMEG11"))

    assert founded.manager_user_id == ana.id
    assert [f.ticker for f in book.held_by(ana.id)] == ["OMEG11"]


def test_without_a_comanager_the_fund_freezes_with_the_manager(match):
    sim, ana, _bruno, fund_id = match
    governing(sim, ana, date(2004, 12, 31))

    sim._take_office(ana, sim._current_date)

    assert book_of(sim).get(TICKER).terms.manager_user_id == ana.id
    assert sim.get_fund(ana, fund_id).frozen_until == date(2004, 12, 31)


def test_an_invited_player_is_not_the_heir(match):
    sim, ana, _bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")
    governing(sim, ana, date(2004, 12, 31))

    sim._take_office(ana, sim._current_date)

    assert book_of(sim).get(TICKER).terms.manager_user_id == ana.id
    assert sim.get_fund(ana, fund_id).frozen_until == date(2004, 12, 31)


def test_a_comanager_who_governs_does_not_operate_the_fund(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    governing(sim, bruno, date(2004, 12, 31))

    with pytest.raises(ConflictError, match="governa"):
        sim.acting_client(bruno.client_id, fund_id)
    assert sim.acting_client(ana.client_id, fund_id) is not None


# =========================
# Mesmo dono no livro de ofertas
# =========================


def test_the_comanager_account_and_the_fund_share_an_owner(match):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    fund = book_of(sim).get(TICKER)

    assert sim._account_owners(fund.account.client_id) == {ana.id, bruno.id}


# =========================
# Avisos em tempo real
# =========================


def test_the_answer_and_the_invite_notify_the_other_side(match, notices):
    sim, ana, bruno, fund_id = match

    invite(sim, ana, fund_id, "Bruno")
    sim.answer_fund_comanager_invite(bruno, fund_id, True)
    sim.leave_fund_comanagement(bruno, fund_id)

    updates = [to for event, to in notices if event == "comanager_update"]
    assert updates == [bruno.client_id, ana.client_id, ana.client_id]


def test_saved_match_resumes_the_comanagers(match, started):  # noqa: F811
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    fund = book_of(sim).get(TICKER)

    loaded = repository.fund_comanager.of_fund(fund.terms.id)

    assert [(c.user_id, c.share) for c in loaded] == [(bruno.id, SHARE)]
