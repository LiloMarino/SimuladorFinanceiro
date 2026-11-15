# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.user import UserDTO
from backend.features.funds.fund_book import maker_stake, takeover_offer_size
from tests.test_fund_assembly import BETO, CAIO, _assemblable, _close_all_sessions
from tests.test_fund_book import (
    BUYER,
    MANAGER,
    MANAGER_USER,
    TICKER,
    TODAY,
    MemoryFunds,
    Setup,
    _setup,
    isolated,
    memory,
)

GESTOR = UserDTO(id=MANAGER_USER, client_id=MANAGER, nickname="Gestor")
ANA = UserDTO(id=1, client_id=BUYER, nickname="Ana")
CAP = Decimal("0.5")
NAV = Decimal(100)
LAST_SESSION = date(2020, 1, 10)


def _held(setup: Setup, client_id=MANAGER) -> Decimal:
    position = setup.engine.broker.get_positions(client_id).get(TICKER)
    return position.size if position is not None else Decimal(0)


def _takeover(memory: MemoryFunds, *, listed: bool) -> Setup:
    """Gestora de 1000 cotas, todas do gestor, com o modo ligado e a carência acabando em TODAY."""
    setup = _setup(memory, participants=lambda: [GESTOR, ANA])
    accounts = {GESTOR.id: GESTOR.client_id, ANA.id: ANA.client_id}
    setup.book._client_of_user = accounts.__getitem__
    if listed:
        # A gestora lista antes do dia em que a carência acaba
        setup.engine.current_date = date(2020, 1, 3)
        setup.book.open_offer(TICKER, Decimal(200))
        setup.book.close_offer(TICKER)
        setup.engine.current_date = TODAY
    fund = setup.book.get(TICKER)
    # As cotas do formador não estão na carteira de ninguém: o gestor tem as demais
    quotas = fund.account.quotas - fund.account.maker_quotas
    setup.engine.cash[MANAGER] += NAV * quotas
    setup.engine.broker.buy_from_fund(MANAGER, TICKER, quotas, NAV)
    setup.book._manager_cap = CAP
    setup.book._assemblies.grace_ends = TODAY
    return setup


def _run_window(setup: Setup) -> None:
    """Os cinco pregões da oferta, com abertura e fechamento de cada um."""
    for day in (6, 7, 8, 9, 10):
        setup.tick(date(2020, 1, day))
        setup.book.on_close(date(2020, 1, day))


def test_takeover_offer_size_reaches_the_cap_counting_the_maker_stake():
    """O gestor com 100 de 100 cotas e limite de 50% precisa de 200 no total, com o formador incluído."""
    size = takeover_offer_size(Decimal(100), Decimal(100), Decimal("0.5"))

    total = Decimal(100) + size
    assert size == 82
    assert total + maker_stake(total) == 200


def test_unlisted_fund_opens_the_offer_when_the_grace_ends(memory: MemoryFunds):
    setup = _takeover(memory, listed=False)
    fund = setup.book.get(TICKER)

    setup.tick(TODAY)

    assert fund.account.offer_remaining is not None
    assert fund.terms.takeover_offer_on == TODAY
    assert memory.funds[fund.terms.id].takeover_offer_on == TODAY


def test_unlisted_fund_has_the_leftover_bought_by_the_maker_at_the_end(
    memory: MemoryFunds,
):
    setup = _takeover(memory, listed=False)
    fund = setup.book.get(TICKER)
    held = _held(setup)

    _run_window(setup)

    assert fund.account.offer_remaining is None
    assert _held(setup) == held
    assert held / fund.account.quotas <= CAP


def test_unlisted_fund_offer_bought_by_a_player_still_respects_the_cap(
    memory: MemoryFunds,
):
    setup = _takeover(memory, listed=False)
    fund = setup.book.get(TICKER)
    setup.tick(TODAY)
    setup.buy(30)
    setup.book.on_close(TODAY)

    for day in (7, 8, 9, 10):
        setup.tick(date(2020, 1, day))
        setup.book.on_close(date(2020, 1, day))

    assert _held(setup) / fund.account.quotas <= CAP


def test_listed_fund_sells_the_excess_to_the_maker_when_nobody_buys(
    memory: MemoryFunds,
):
    setup = _takeover(memory, listed=True)
    fund = setup.book.get(TICKER)
    maker_before = fund.account.maker_quotas

    _run_window(setup)

    assert _held(setup) / fund.account.quotas <= CAP
    assert fund.account.maker_quotas > maker_before


def test_listed_fund_sale_to_a_player_comes_out_of_the_manager_position(
    memory: MemoryFunds,
):
    setup = _takeover(memory, listed=True)
    fund = setup.book.get(TICKER)
    held = _held(setup)

    setup.tick(TODAY)
    setup.buy(100)

    assert _held(setup) == held - 100
    assert _held(setup, BUYER) == 100
    assert fund.terms.takeover_offer_on == TODAY


def test_offer_runs_once_per_fund(memory: MemoryFunds):
    setup = _takeover(memory, listed=True)
    fund = setup.book.get(TICKER)

    _run_window(setup)
    quotas = fund.account.quotas
    setup.tick(date(2020, 1, 13))
    setup.book.on_close(date(2020, 1, 13))

    assert fund.account.quotas == quotas
    assert fund.account.offer_remaining is None
    assert fund.terms.takeover_offer_on == TODAY


def test_fund_within_the_cap_does_not_open_an_offer(memory: MemoryFunds):
    setup = _takeover(memory, listed=True)
    setup.book._manager_cap = Decimal(1)
    fund = setup.book.get(TICKER)

    setup.tick(TODAY)

    assert fund.terms.takeover_offer_on is None


def test_offer_waits_while_an_offer_is_running(memory: MemoryFunds):
    setup = _takeover(memory, listed=False)
    fund = setup.book.get(TICKER)
    setup.book.open_offer(TICKER, Decimal(50))

    setup.tick(TODAY)

    assert fund.terms.takeover_offer_on is None


def test_offer_cancels_the_open_buyback(memory: MemoryFunds):
    setup = _takeover(memory, listed=True)
    fund = setup.book.get(TICKER)
    setup.book.open_buyback(TICKER, Decimal(50), Decimal(100))
    assert fund.buyback is not None

    setup.tick(TODAY)

    assert fund.buyback is None
    assert fund.terms.takeover_offer_on == TODAY


def test_without_the_mode_nothing_happens(memory: MemoryFunds):
    setup = _takeover(memory, listed=True)
    setup.book._manager_cap = None
    fund = setup.book.get(TICKER)
    held = _held(setup)

    _run_window(setup)

    assert fund.terms.takeover_offer_on is None
    assert _held(setup) == held


def test_before_the_grace_ends_nothing_happens(memory: MemoryFunds):
    setup = _takeover(memory, listed=True)
    setup.book._assemblies.grace_ends = date(2020, 7, 1)
    fund = setup.book.get(TICKER)

    setup.tick(TODAY)

    assert fund.terms.takeover_offer_on is None


@pytest.mark.parametrize("listed", [True, False])
def test_reloading_in_the_middle_of_the_window_keeps_the_cap(
    memory: MemoryFunds, listed: bool
):
    setup = _takeover(memory, listed=listed)
    fund = setup.book.get(TICKER)
    setup.tick(TODAY)
    setup.book.on_close(TODAY)
    terms = memory.funds[fund.terms.id]
    assert terms.takeover_offer_on == TODAY

    # Retomada: o livro não guarda ordens, e a abertura do dia refaz o que falta
    setup.book._load(terms)
    reloaded = setup.book.get(TICKER)
    for day in (7, 8, 9, 10):
        setup.tick(date(2020, 1, day))
        setup.book.on_close(date(2020, 1, day))

    assert _held(setup) / reloaded.account.quotas <= CAP


def _lose_the_assembly(memory: MemoryFunds) -> Setup:
    """O gestor fundador perde a votação da própria gestora para a Ana, que tem a maioria."""
    setup = _assemblable(memory)
    setup.book._manager_cap = CAP
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)
    _close_all_sessions(setup)
    return setup


def test_the_founder_who_loses_the_assembly_is_eliminated(memory: MemoryFunds):
    setup = _lose_the_assembly(memory)

    assert set(setup.book.eliminated) == {GESTOR.id}
    assert setup.book.get(TICKER).terms.manager_user_id == ANA.id


def test_losing_the_assembly_without_the_mode_eliminates_nobody(memory: MemoryFunds):
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)
    _close_all_sessions(setup)

    assert setup.book.eliminated == {}


def test_the_eliminated_manager_loses_the_other_fund_to_its_largest_holder(
    memory: MemoryFunds,
):
    setup = _assemblable(memory)
    setup.book._manager_cap = CAP
    # Uma segunda gestora, fundada pela Ana e gerida pelo gestor, com a Caio como maior cotista
    setup.book.found(
        ticker="BETA11",
        name="Beta",
        founder_user_id=ANA.id,
        manager_user_id=GESTOR.id,
        management_fee=Decimal("0.02"),
        performance_fee=Decimal("0.20"),
    )
    beta = setup.book.get("BETA11")
    beta.account.quotas = Decimal(100)
    setup.engine.cash[beta.account.client_id] = Decimal(10000)
    for user, quotas in ((CAIO, 60), (BETO, 30)):
        setup.engine.cash[user.client_id] += NAV * quotas
        setup.engine.broker.buy_from_fund(
            user.client_id, "BETA11", Decimal(quotas), NAV
        )
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)

    _close_all_sessions(setup)

    assert beta.terms.manager_user_id == CAIO.id
    assert setup.book.get(TICKER).terms.manager_user_id == ANA.id
