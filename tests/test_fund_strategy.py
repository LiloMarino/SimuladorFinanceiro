"""O automático da gestora, pela fachada da partida, com banco: opera pela carteira dela, convive com a presidência e some com a troca do principal."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.events.strategy import StrategyEventDTO
from backend.core.dto.fund import FundContributionRequest, FundFeesRequest
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    FundComanagerStatus,
    StrategyLogKind,
    StrategyOrderStatus,
)
from backend.core.exceptions.http_exceptions import ConflictError, ForbiddenError
from backend.core.runtime.event_manager import EventManager
from backend.features.simulation.simulation import Simulation
from backend.features.strategy.intents import buy
from backend.features.strategy.runner import StrategyAccount
from tests.test_fund_comanagers import (
    active_comanager,
    comanager_of,
    heir_match,
    invite,
    match,  # noqa: F401
)
from tests.test_fund_flow import book_of, governing, player
from tests.test_fund_simulation import TICKER
from tests.test_simulation_loader import started  # noqa: F401

KEY = "cdi_100"
TERM_END = date(2004, 12, 31)


def fund_client(sim: Simulation, fund_id: int):
    return book_of(sim).by_id(fund_id).account.client_id


def turn_on(sim: Simulation, user: UserDTO, fund_id: int, key: str = KEY) -> None:
    sim.set_fund_strategy(user, fund_id, key, {})


def active_key(sim: Simulation, user: UserDTO, fund_id: int) -> str | None:
    active = sim.get_fund_strategy(user, fund_id).active
    return active.key if active else None


def last_log(sim: Simulation, user: UserDTO, fund_id: int):
    return sim.get_fund_strategy_log(user, fund_id, "all", None, 10).items[0]


# =========================
# Opera pela carteira da gestora
# =========================


def test_the_strategy_orders_go_out_through_the_fund_account(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match
    turn_on(sim, ana, fund_id)
    account = StrategyAccount(ana.id, fund_client(sim, fund_id), fund_id, ana.nickname)
    intent = buy("BANK_A", 1, "teste", limit=0.01)
    row = StrategyEventDTO(
        simulation_id=sim.settings.id,
        user_id=ana.id,
        fund_id=fund_id,
        event_date=sim._current_date,
        kind=StrategyLogKind.ORDER,
        strategy_key=KEY,
        action=intent.action,
        ticker=intent.ticker,
        quantity=intent.quantity,
        reason="teste",
        status=StrategyOrderStatus.REFUSED,
    )

    sim._strategies._submit(account, intent, row)

    book = sim._engine.matching_engine.order_book
    assert book.orders_of(fund_client(sim, fund_id)) != []
    assert book.orders_of(ana.client_id) == []
    EventManager.flush()


def test_the_fund_strategy_is_independent_from_the_personal_account(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match

    turn_on(sim, ana, fund_id)

    assert active_key(sim, ana, fund_id) == KEY
    assert sim.get_my_strategy(ana).active is None
    # Cada conta trava só as próprias boletas
    sim._ensure_can_operate(ana.client_id)
    with pytest.raises(ConflictError, match="automático"):
        sim._ensure_can_operate(fund_client(sim, fund_id))
    sim.set_my_strategy(ana, KEY, {})
    sim.set_fund_strategy(ana, fund_id, None, {})
    assert sim.get_my_strategy(ana).active is not None
    sim._ensure_can_operate(fund_client(sim, fund_id))
    with pytest.raises(ConflictError, match="automático"):
        sim._ensure_can_operate(ana.client_id)


def test_the_fund_strategy_log_has_its_own_rows(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match

    turn_on(sim, ana, fund_id)

    assert last_log(sim, ana, fund_id).strategy_key == KEY
    assert sim.get_strategy_log(ana, "all", None, 10).items == []
    assert sim.get_fund_strategy(ana, fund_id).active is not None


# =========================
# Quem liga
# =========================


def test_the_principal_and_the_active_comanagers_turn_it_on_switch_and_off(match):  # noqa: F811
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)

    turn_on(sim, ana, fund_id)
    assert active_key(sim, bruno, fund_id) == KEY
    sim.set_fund_strategy(bruno, fund_id, None, {})
    assert active_key(sim, ana, fund_id) is None
    turn_on(sim, bruno, fund_id)
    assert active_key(sim, ana, fund_id) == KEY


def test_who_does_not_manage_the_fund_cannot_use_its_strategy(match):  # noqa: F811
    sim, ana, bruno, fund_id = match
    invite(sim, ana, fund_id, "Bruno")

    with pytest.raises(ForbiddenError):
        turn_on(sim, bruno, fund_id)
    with pytest.raises(ForbiddenError):
        sim.get_fund_strategy(player(sim, "Carla"), fund_id)


def test_the_fund_list_has_no_fund_quotas(match):  # noqa: F811
    sim, _ana, _bruno, _fund_id = match

    personal = {info.key for info in sim.get_strategies()}
    for_fund = {info.key for info in sim.get_strategies(for_fund=True)}

    assert "fund_quotas" in personal
    assert "fund_quotas" not in for_fund
    assert for_fund < personal


def test_the_fund_refuses_the_strategy_without_fund_account(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match

    with pytest.raises(Exception, match=r"(?i)cotas|fund|gestora|estratégia"):
        turn_on(sim, ana, fund_id, "fund_quotas")
    assert active_key(sim, ana, fund_id) is None


# =========================
# Presidência
# =========================


def test_taking_office_with_the_strategy_on_keeps_the_portfolio_running(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match
    turn_on(sim, ana, fund_id)
    governing(sim, ana, TERM_END)

    sim._take_office(ana, sim._current_date)

    fund = book_of(sim).get(TICKER)
    assert fund.terms.manager_user_id == ana.id
    assert active_key(sim, ana, fund_id) == KEY
    assert book_of(sim).automatic(fund)
    assert book_of(sim).portfolio_frozen_until(fund) is None
    page = sim.get_fund(ana, fund_id)
    assert page.automatic is True
    assert page.frozen_until == TERM_END
    # A carteira opera pela estratégia: a ordem do robô passa, a boleta à mão não
    sim._ensure_can_trade(fund_client(sim, fund_id))
    with pytest.raises(ConflictError, match="automático"):
        sim._ensure_can_operate(fund_client(sim, fund_id))


def test_taking_office_without_the_strategy_freezes_the_portfolio(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match
    governing(sim, ana, TERM_END)

    sim._take_office(ana, sim._current_date)

    fund = book_of(sim).get(TICKER)
    assert book_of(sim).portfolio_frozen_until(fund) == TERM_END
    assert sim.get_fund(ana, fund_id).automatic is False
    with pytest.raises(ConflictError, match="congelada"):
        sim._ensure_can_trade(fund_client(sim, fund_id))


def test_turning_it_on_during_the_presidency_unfreezes_only_the_portfolio(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match
    governing(sim, ana, TERM_END)
    sim._take_office(ana, sim._current_date)

    turn_on(sim, ana, fund_id)

    fund = book_of(sim).get(TICKER)
    assert book_of(sim).portfolio_frozen_until(fund) is None
    sim._ensure_can_trade(fund_client(sim, fund_id))
    # As decisões do gestor seguem congeladas, e as taxas também
    assert sim.get_fund(ana, fund_id).frozen_until == TERM_END
    with pytest.raises(ConflictError, match="congelada"):
        sim.contribute_to_fund(ana, fund_id, FundContributionRequest(cash=Decimal(100)))
    with pytest.raises(ConflictError, match="congelada"):
        sim.open_fund_offer(ana, fund_id, 10)
    with pytest.raises(ConflictError, match="congelada"):
        sim.set_fund_fees(
            ana,
            fund_id,
            FundFeesRequest(
                management_fee=Decimal("0.02"), performance_fee=Decimal("0.20")
            ),
        )
    assert book_of(sim)._manager_frozen_until(ana.id) == TERM_END


def test_turning_it_off_during_the_presidency_freezes_the_portfolio_again(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match
    governing(sim, ana, TERM_END)
    sim._take_office(ana, sim._current_date)
    turn_on(sim, ana, fund_id)

    sim.set_fund_strategy(ana, fund_id, None, {})

    fund = book_of(sim).get(TICKER)
    assert book_of(sim).portfolio_frozen_until(fund) == TERM_END
    with pytest.raises(ConflictError, match="congelada"):
        sim._ensure_can_trade(fund_client(sim, fund_id))


def test_the_president_who_governs_does_not_use_the_strategy_of_a_fund_he_does_not_hold(
    match,  # noqa: F811
):
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    governing(sim, bruno, TERM_END)

    with pytest.raises(ConflictError, match="governa"):
        turn_on(sim, bruno, fund_id)
    turn_on(sim, ana, fund_id)


def test_the_strategy_ends_with_the_term_without_reelection(match):  # noqa: F811
    sim, ana, _bruno, fund_id = match
    state = governing(sim, ana, TERM_END)
    sim._take_office(ana, sim._current_date)
    turn_on(sim, ana, fund_id)
    state["on"] = False

    sim._leave_office(ana, sim._current_date)

    assert active_key(sim, ana, fund_id) is None
    assert book_of(sim).automatic(book_of(sim).get(TICKER)) is False
    assert "mandato" in (last_log(sim, ana, fund_id).reason or "")
    sim._ensure_can_operate(fund_client(sim, fund_id))


def test_the_heir_takes_over_with_the_manager_and_the_strategy_goes_off(match):  # noqa: F811
    sim, ana, bruno, carla, fund_id = heir_match(match)
    turn_on(sim, ana, fund_id)
    governing(sim, ana, TERM_END)

    sim._take_office(ana, sim._current_date)

    assert book_of(sim).get(TICKER).terms.manager_user_id == bruno.id
    assert active_key(sim, bruno, fund_id) is None
    assert book_of(sim).automatic(book_of(sim).get(TICKER)) is False
    assert carla.id in book_of(sim).operators(book_of(sim).get(TICKER))


def test_the_strategy_goes_off_when_the_assembly_changes_the_principal(match):  # noqa: F811
    sim, ana, bruno, fund_id = match
    turn_on(sim, ana, fund_id)
    book = book_of(sim)

    book._replace_manager(book.get(TICKER), bruno.id)

    assert book.automatic(book.get(TICKER)) is False
    assert active_key(sim, bruno, fund_id) is None
    assert "mãos" in (last_log(sim, bruno, fund_id).reason or "")


def test_the_strategy_goes_off_when_the_principal_is_eliminated(match):  # noqa: F811
    sim, ana, bruno, fund_id = match
    active_comanager(sim, ana, fund_id, bruno)
    turn_on(sim, ana, fund_id)
    book = book_of(sim)

    book._replace_manager(book.get(TICKER), bruno.id)

    assert book.automatic(book.get(TICKER)) is False


# =========================
# Co-gestor na presidência
# =========================


def test_the_comanager_who_accepts_during_the_presidency_takes_over_at_once(match):  # noqa: F811
    sim, ana, bruno, fund_id = match
    turn_on(sim, ana, fund_id)
    governing(sim, ana, TERM_END)
    sim._take_office(ana, sim._current_date)
    assert book_of(sim).get(TICKER).terms.manager_user_id == ana.id
    invite(sim, ana, fund_id, "Bruno")

    sim.answer_fund_comanager_invite(bruno, fund_id, True)

    fund = book_of(sim).get(TICKER)
    assert fund.terms.manager_user_id == bruno.id
    assert fund.terms.leave_manager_user_id == ana.id
    # O automático do presidente sai com a troca, e a carteira segue com o novo principal
    assert active_key(sim, bruno, fund_id) is None
    assert book_of(sim).frozen_until(fund) is None
    sim._ensure_can_operate(fund_client(sim, fund_id))
    assert sim.get_fund(bruno, fund_id).my_role == "manager"


def test_the_comanager_who_accepts_without_the_presidency_stays_a_comanager(match):  # noqa: F811
    sim, ana, bruno, fund_id = match
    turn_on(sim, ana, fund_id)
    invite(sim, ana, fund_id, "Bruno")

    sim.answer_fund_comanager_invite(bruno, fund_id, True)

    assert book_of(sim).get(TICKER).terms.manager_user_id == ana.id
    assert active_key(sim, ana, fund_id) == KEY
    row = comanager_of(sim, bruno)
    assert row is not None
    assert row.status is FundComanagerStatus.ACTIVE


def test_the_president_invites_and_withdraws_the_invite_during_the_freeze(match):  # noqa: F811
    sim, ana, bruno, fund_id = match
    governing(sim, ana, TERM_END)
    sim._take_office(ana, sim._current_date)

    invite(sim, ana, fund_id, "Bruno")
    assert comanager_of(sim, bruno) is not None
    sim.remove_fund_comanager(ana, fund_id, bruno.id)

    row = comanager_of(sim, bruno)
    assert row is None or row.status is not FundComanagerStatus.INVITED
    # Convidar e retirar são as únicas decisões liberadas: o resto segue congelado
    with pytest.raises(ConflictError, match="congelada"):
        sim.open_fund_offer(ana, fund_id, 10)
