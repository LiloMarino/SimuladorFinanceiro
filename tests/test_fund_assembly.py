# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.user import UserDTO
from backend.core.enum import FundAssemblyStatus, NewsType, OrderStatus
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.features.funds.fund_assembly import (
    Tally,
    convene_block,
    stance_of,
    tally,
)
from backend.features.notifications.news import Headline
from tests.fakes import client
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
BETO = UserDTO(id=2, client_id=client("beto"), nickname="Beto")
CAIO = UserDTO(id=3, client_id=client("caio"), nickname="Caio")
ROBOT = UserDTO(id=4, client_id=client("robo"), nickname="Robô", is_bot=True)

NAV = Decimal(100)
FRIDAY = date(2020, 1, 10)
# Pregão 5 da votação aberta em TODAY (segunda, 6/1)
LAST_SESSION = date(2020, 1, 10)


def _give(setup: Setup, user: UserDTO, quotas: int) -> None:
    """Põe `quotas` cotas na carteira do jogador, pagas ao PL da gestora."""
    setup.engine.cash[user.client_id] += NAV * quotas
    setup.engine.broker.buy_from_fund(user.client_id, TICKER, Decimal(quotas), NAV)


def _assemblable(memory: MemoryFunds, published: list[Headline] | None = None) -> Setup:
    """Gestora aberta com o gestor, Ana (a maior fatia entre os votantes), Beto, Caio e um bot com cotas."""
    log = published if published is not None else []
    setup = _setup(
        memory,
        publish=lambda day, headline: log.append(headline),
        participants=lambda: [GESTOR, ANA, BETO, CAIO, ROBOT],
    )
    # Cada usuário paga e recebe na própria conta pessoal
    accounts = {u.id: u.client_id for u in (GESTOR, ANA, BETO, CAIO, ROBOT)}
    setup.book._client_of_user = accounts.__getitem__
    setup.book.open_offer(TICKER, Decimal(200))
    setup.book.close_offer(TICKER)
    _give(setup, GESTOR, 400)
    _give(setup, ANA, 300)
    _give(setup, BETO, 200)
    _give(setup, CAIO, 100)
    _give(setup, ROBOT, 100)
    return setup


def _total(setup: Setup) -> Decimal:
    return setup.book.get(TICKER).account.quotas


def _advance(setup: Setup, day: date) -> None:
    setup.tick(day)
    setup.book.on_close(day)


def _close_all_sessions(setup: Setup) -> None:
    """Fecha os pregões de TODAY até o último da votação, na ordem do tick."""
    day = TODAY
    while day <= LAST_SESSION:
        if day.weekday() < 5:
            _advance(setup, day)
        day = date.fromordinal(day.toordinal() + 1)


def _types(published: list[Headline]) -> list[NewsType]:
    assemblies = (
        NewsType.FUND_ASSEMBLY_CALLED,
        NewsType.FUND_ASSEMBLY_REPLACED,
        NewsType.FUND_ASSEMBLY_KEPT,
    )
    return [h.news_type for h in published if h.news_type in assemblies]


# =========================
# Regra pura
# =========================


def test_tally_counts_the_manager_against_and_the_silent_as_abstention():
    """O gestor não vota (cotas contra); quem não votou e os sem voto (bots, formador) abstêm."""
    result = tally(
        total=Decimal(1000),
        manager_user_id=1,
        holdings={1: Decimal(300), 2: Decimal(200), 3: Decimal(100)},
        votes={2: True},
    )

    assert result == Tally(
        in_favor=Decimal(200),
        against=Decimal(300),
        abstention=Decimal(500),
        non_voting=Decimal(400),
    )
    assert not result.replaces
    assert result.missing_to_replace == Decimal(101)


def test_a_tie_keeps_the_manager():
    result = tally(
        total=Decimal(1000),
        manager_user_id=1,
        holdings={1: Decimal(300), 2: Decimal(300)},
        votes={2: True},
    )

    assert result.in_favor == result.against == Decimal(300)
    assert not result.replaces
    assert result.missing_to_replace == Decimal(1)


def test_one_more_quota_in_favor_replaces():
    result = tally(
        total=Decimal(1000),
        manager_user_id=1,
        holdings={1: Decimal(300), 2: Decimal(301)},
        votes={2: True},
    )

    assert result.replaces
    assert result.missing_to_replace == 0


def test_voters_who_left_the_fund_weigh_nothing():
    """O peso é o das cotas que o votante tem na apuração: quem vendeu tudo sai do placar."""
    result = tally(
        total=Decimal(500),
        manager_user_id=1,
        holdings={1: Decimal(100)},
        votes={2: True, 3: False},
    )

    assert (result.in_favor, result.against) == (Decimal(0), Decimal(100))


def test_stance_of_the_manager_is_always_against():
    assert stance_of(1, 1, {1: True}) == "against"
    assert stance_of(2, 1, {}) == "abstain"
    assert stance_of(2, 1, {2: True}) == "favor"
    assert stance_of(2, 1, {2: False}) == "against"


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"listed": False}, ("unlisted", None)),
        (
            {"listed": False, "grace_ends": date(2020, 7, 1)},
            ("grace", date(2020, 7, 1)),
        ),
        ({"grace_ends": date(2020, 1, 7)}, ("grace", date(2020, 1, 7))),
        ({"grace_ends": date(2020, 1, 6)}, (None, None)),
        ({"is_manager": True}, ("manager", None)),
        ({"active": True}, ("pending", None)),
        ({"quotas": Decimal(99)}, ("share", None)),
        ({"last_end": date(2020, 1, 1)}, ("interval", date(2020, 4, 1))),
        ({"quotas": Decimal(100)}, (None, None)),
        ({"last_end": date(2019, 10, 6)}, (None, None)),
    ],
)
def test_convene_block_reasons(kwargs: dict, expected: tuple):
    """10% convoca; o intervalo de 3 meses conta do fim da assembleia anterior."""
    params = {
        "quotas": Decimal(100),
        "total": Decimal(1000),
        "is_manager": False,
        "listed": True,
        "active": False,
        "last_end": None,
        "today": TODAY,
    } | kwargs

    assert convene_block(**params) == expected


# =========================
# Convocar
# =========================


def test_convening_for_yourself_opens_the_vote_for_five_sessions(memory: MemoryFunds):
    published: list[Headline] = []
    setup = _assemblable(memory, published)

    setup.book.convene_assembly(TICKER, ANA, None)

    assembly = setup.book.get(TICKER).assembly
    assert assembly is not None
    assert assembly.status is FundAssemblyStatus.VOTING
    assert (assembly.candidate_user_id, assembly.started_on) == (ANA.id, TODAY)
    assert assembly.ends_on == LAST_SESSION
    # Quem convocou entra a favor
    assert setup.book.get(TICKER).assembly_votes == {ANA.id: True}
    assert _types(published) == [NewsType.FUND_ASSEMBLY_CALLED]


def test_convening_needs_ten_percent_of_the_quotas(memory: MemoryFunds):
    setup = _assemblable(memory)
    # Caio tem 100 de ~1100: menos de 10%
    _give(setup, CAIO, 0)
    small = UserDTO(id=9, client_id=client("pequeno"), nickname="Pequeno")
    setup.engine.cash[small.client_id] += NAV * 5
    setup.engine.broker.buy_from_fund(small.client_id, TICKER, Decimal(5), NAV)

    with pytest.raises(ConflictError, match="10%"):
        setup.book.convene_assembly(TICKER, small, None)


def test_convening_waits_for_the_end_of_the_grace_period(memory: MemoryFunds):
    setup = _assemblable(memory)
    setup.book._assemblies.grace_ends = date(2020, 7, 1)

    with pytest.raises(ConflictError, match="depois da carência, em 01/07/2020"):
        setup.book.convene_assembly(TICKER, ANA, None)

    # No dia em que a carência acaba a assembleia já abre
    setup.book._assemblies.grace_ends = TODAY
    setup.book.convene_assembly(TICKER, ANA, None)
    assert setup.book.get(TICKER).assembly is not None


def test_the_manager_does_not_convene_against_himself(memory: MemoryFunds):
    setup = _assemblable(memory)

    with pytest.raises(ConflictError, match="contra si mesmo"):
        setup.book.convene_assembly(TICKER, GESTOR, None)


def test_the_candidate_is_a_player_who_is_not_the_manager(memory: MemoryFunds):
    setup = _assemblable(memory)

    with pytest.raises(UnprocessableEntityError, match="jogador"):
        setup.book.convene_assembly(TICKER, ANA, ROBOT.nickname)
    with pytest.raises(UnprocessableEntityError, match="já é o gestor"):
        setup.book.convene_assembly(TICKER, ANA, GESTOR.nickname)


def test_only_one_assembly_at_a_time(memory: MemoryFunds):
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, None)

    with pytest.raises(ConflictError, match="em andamento"):
        setup.book.convene_assembly(TICKER, BETO, None)


# =========================
# Convite ao aliado
# =========================


def test_the_ally_accepts_and_the_vote_opens(memory: MemoryFunds):
    published: list[Headline] = []
    setup = _assemblable(memory, published)
    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)
    fund = setup.book.get(TICKER)
    assert fund.assembly is not None
    assert fund.assembly.status is FundAssemblyStatus.INVITED
    assert [f.terms.id for f, _, _ in setup.book.invites_for(BETO)] == [fund.terms.id]
    assert _types(published) == []

    setup.book.answer_assembly_invite(TICKER, BETO, True)

    assert fund.assembly is not None
    assert fund.assembly.status is FundAssemblyStatus.VOTING
    assert fund.assembly.candidate_user_id == BETO.id
    assert fund.assembly_votes == {ANA.id: True}
    assert setup.book.invites_for(BETO) == []
    assert _types(published) == [NewsType.FUND_ASSEMBLY_CALLED]


def test_only_the_invited_ally_answers(memory: MemoryFunds):
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)

    with pytest.raises(ForbiddenError, match="convite"):
        setup.book.answer_assembly_invite(TICKER, CAIO, True)


def test_refusal_expiry_and_cancellation_do_not_count_for_the_interval(
    memory: MemoryFunds,
):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)

    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)
    setup.book.answer_assembly_invite(TICKER, BETO, False)
    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)
    setup.book.cancel_assembly(TICKER, ANA)
    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)
    # O convite vence ao fim do 5º pregão e cai como recusa
    _close_all_sessions(setup)

    assert fund.assembly is None
    assert fund.last_assembly is None
    assert [a.status for a in memory.assemblies(fund.terms.id)] == [
        FundAssemblyStatus.DECLINED,
        FundAssemblyStatus.CANCELLED,
        FundAssemblyStatus.EXPIRED,
    ]
    setup.book.convene_assembly(TICKER, ANA, None)


def test_only_the_convener_cancels_and_only_while_invited(memory: MemoryFunds):
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)

    with pytest.raises(ForbiddenError, match="convocou"):
        setup.book.cancel_assembly(TICKER, BETO)

    setup.book.answer_assembly_invite(TICKER, BETO, True)
    with pytest.raises(ConflictError, match="convite"):
        setup.book.cancel_assembly(TICKER, ANA)


# =========================
# Votação
# =========================


def test_only_shareholders_vote_and_the_manager_never_does(memory: MemoryFunds):
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, None)
    stranger = UserDTO(id=9, client_id=client("estranho"), nickname="Estranho")

    with pytest.raises(ForbiddenError, match="gestor não vota"):
        setup.book.cast_assembly_vote(TICKER, GESTOR, True)
    with pytest.raises(ForbiddenError, match="tem cotas"):
        setup.book.cast_assembly_vote(TICKER, stranger, True)
    with pytest.raises(ForbiddenError, match="tem cotas"):
        setup.book.cast_assembly_vote(TICKER, ROBOT, True)

    setup.book.cast_assembly_vote(TICKER, BETO, True)
    setup.book.cast_assembly_vote(TICKER, BETO, False)
    assert setup.book.get(TICKER).assembly_votes[BETO.id] is False


def test_voting_needs_an_open_vote(memory: MemoryFunds):
    setup = _assemblable(memory)

    with pytest.raises(ConflictError, match="votação aberta"):
        setup.book.cast_assembly_vote(TICKER, BETO, True)

    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)
    with pytest.raises(ConflictError, match="votação aberta"):
        setup.book.cast_assembly_vote(TICKER, CAIO, True)


def test_the_replacement_wins_by_the_quotas_at_the_close_of_the_last_session(
    memory: MemoryFunds,
):
    """Ana (300) convoca contra o gestor (400); Beto (200) vota a favor: 500 a 400 troca."""
    published: list[Headline] = []
    setup = _assemblable(memory, published)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)

    _close_all_sessions(setup)

    assert fund.terms.manager_user_id == ANA.id
    # O novo gestor conta o "desde" do dia em que a votação fechou
    assert fund.terms.manager_since == LAST_SESSION
    assert fund.assembly is None
    assert fund.last_assembly is not None
    assert fund.last_assembly.status is FundAssemblyStatus.REPLACED
    assert (
        fund.last_assembly.in_favor_quotas,
        fund.last_assembly.against_quotas,
    ) == (Decimal(500), Decimal(400))
    assert _types(published) == [
        NewsType.FUND_ASSEMBLY_CALLED,
        NewsType.FUND_ASSEMBLY_REPLACED,
    ]
    assert memory.funds[fund.terms.id].manager_user_id == ANA.id


def test_buying_quotas_on_the_last_session_changes_the_result(memory: MemoryFunds):
    """Ana sozinha (300) perde para o gestor (400); com mais 150 cotas na última sessão ganha."""
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    for day in (date(2020, 1, 6), date(2020, 1, 7), date(2020, 1, 8), date(2020, 1, 9)):
        _advance(setup, day)
    assert fund.assembly is not None

    _give(setup, ANA, 150)
    _advance(setup, LAST_SESSION)

    assert fund.terms.manager_user_id == ANA.id


def test_a_tie_keeps_the_manager_at_the_close(memory: MemoryFunds):
    """Ana com 400 a favor empata com o gestor (400): fica o gestor."""
    published: list[Headline] = []
    setup = _assemblable(memory, published)
    fund = setup.book.get(TICKER)
    _give(setup, ANA, 100)
    setup.book.convene_assembly(TICKER, ANA, None)

    _close_all_sessions(setup)

    assert fund.terms.manager_user_id == MANAGER_USER
    assert fund.last_assembly is not None
    assert fund.last_assembly.status is FundAssemblyStatus.KEPT
    assert _types(published) == [
        NewsType.FUND_ASSEMBLY_CALLED,
        NewsType.FUND_ASSEMBLY_KEPT,
    ]


def test_bots_and_the_market_maker_abstain(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)

    result = setup.book._assemblies.score(fund)

    assert result.in_favor == Decimal(500)
    assert result.against == Decimal(400)
    # Bot (100) e formador abstêm
    assert result.non_voting >= Decimal(100)
    assert result.abstention == _total(setup) - Decimal(900)


def test_a_buyback_leaves_the_scoreboard_by_shrinking_the_total(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    before = setup.book._assemblies.score(fund)
    setup.engine.cash[setup.fund_client] += Decimal(100000)

    setup.book.open_buyback(TICKER, Decimal(20), Decimal(100))
    setup.book.on_open(TODAY)

    assert setup.book._assemblies.score(fund).total <= before.total


# =========================
# Emissão, troca e fundação
# =========================


def test_the_fund_does_not_issue_quotas_while_an_assembly_is_open(memory: MemoryFunds):
    setup = _assemblable(memory)

    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)
    with pytest.raises(ConflictError, match="assembleia"):
        setup.book.announce_issuance(TICKER, Decimal(10))

    setup.book.answer_assembly_invite(TICKER, BETO, True)
    with pytest.raises(ConflictError, match="assembleia"):
        setup.book.announce_issuance(TICKER, Decimal(10))


def test_the_swap_cancels_the_open_buyback_and_the_fund_orders(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    setup.engine.cash[setup.fund_client] += Decimal(100000)
    setup.book.open_buyback(TICKER, Decimal(10), Decimal(1))
    order = fund.buyback_order
    assert fund.buyback is not None
    assert order is not None
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)

    _close_all_sessions(setup)

    assert fund.terms.manager_user_id == ANA.id
    assert fund.buyback is None
    assert fund.buyback_order is None
    assert order.status is OrderStatus.CANCELED


def test_the_next_fee_goes_to_the_new_manager(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)
    _close_all_sessions(setup)
    ana_cash, old_cash = setup.engine.cash[ANA.client_id], setup.engine.cash[MANAGER]

    setup.book._pay(fund, Decimal(50), performance=False)

    assert setup.engine.cash[ANA.client_id] - ana_cash == Decimal(50)
    assert setup.engine.cash[MANAGER] == old_cash


def test_the_removed_manager_cannot_found_another_fund_for_six_months(
    memory: MemoryFunds,
):
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)
    _close_all_sessions(setup)

    assert setup.book.founding_blocked_until(MANAGER_USER) == date(2020, 7, 10)
    assert setup.book.founding_blocked_until(ANA.id) is None
    setup.engine.current_date = date(2020, 7, 10)
    assert setup.book.founding_blocked_until(MANAGER_USER) is None


def test_the_next_assembly_waits_three_months_from_the_end_of_the_last(
    memory: MemoryFunds,
):
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, None)
    _close_all_sessions(setup)
    setup.engine.current_date = date(2020, 1, 13)
    _give(setup, CAIO, 250)

    with pytest.raises(ConflictError, match="10/04/2020"):
        setup.book.convene_assembly(TICKER, CAIO, None)

    setup.engine.current_date = date(2020, 4, 10)
    setup.book.convene_assembly(TICKER, CAIO, None)


def test_the_scoreboard_is_reloaded_with_the_fund(memory: MemoryFunds):
    """O convite e a votação sobrevivem a parar e retomar a partida."""
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, BETO, True)
    assembly = setup.book.get(TICKER).assembly

    reloaded = type(setup.book)(
        1,
        setup.engine,
        lambda user_id: MANAGER,
        participants=lambda: [GESTOR, ANA, BETO],
    )

    fund = reloaded.get(TICKER)
    assert fund.assembly == assembly
    assert fund.assembly_votes == {ANA.id: True, BETO.id: True}
