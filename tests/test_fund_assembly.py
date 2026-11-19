# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from backend.core.dto.fund import FundComanagerDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    FundAssemblyAgenda,
    FundAssemblyStatus,
    FundComanagerStatus,
    NewsType,
    OrderStatus,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.features.funds.fund_assembly import (
    Tally,
    convene_block,
    fee_tally,
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

SWAP = FundAssemblyAgenda.REPLACE_MANAGER
FEE = FundAssemblyAgenda.FEE_INCREASE
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
    assert not result.wins
    assert result.missing_to_win == Decimal(101)


def test_a_tie_keeps_the_manager():
    result = tally(
        total=Decimal(1000),
        manager_user_id=1,
        holdings={1: Decimal(300), 2: Decimal(300)},
        votes={2: True},
    )

    assert result.in_favor == result.against == Decimal(300)
    assert not result.wins
    assert result.missing_to_win == Decimal(1)


def test_one_more_quota_in_favor_replaces():
    result = tally(
        total=Decimal(1000),
        manager_user_id=1,
        holdings={1: Decimal(300), 2: Decimal(301)},
        votes={2: True},
    )

    assert result.wins
    assert result.missing_to_win == 0


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

    assembly = setup.book.get(TICKER).assemblies.get(SWAP)
    assert assembly is not None
    assert assembly.status is FundAssemblyStatus.VOTING
    assert (assembly.candidate_user_id, assembly.started_on) == (ANA.id, TODAY)
    assert assembly.ends_on == LAST_SESSION
    # Quem convocou entra a favor
    assert setup.book.get(TICKER).assembly_votes[SWAP] == {ANA.id: True}
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
    assert SWAP in setup.book.get(TICKER).assemblies


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

    with pytest.raises(ConflictError, match="votação aberta desta pauta"):
        setup.book.convene_assembly(TICKER, BETO, None)


# =========================
# Convite ao aliado
# =========================


def test_the_ally_accepts_and_the_vote_opens(memory: MemoryFunds):
    published: list[Headline] = []
    setup = _assemblable(memory, published)
    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)
    fund = setup.book.get(TICKER)
    assert fund.assemblies.get(SWAP) is not None
    assert fund.assemblies[SWAP].status is FundAssemblyStatus.INVITED
    assert [f.terms.id for f, _, _ in setup.book.invites_for(BETO)] == [fund.terms.id]
    assert _types(published) == []

    setup.book.answer_assembly_invite(TICKER, BETO, True)

    assert fund.assemblies.get(SWAP) is not None
    assert fund.assemblies[SWAP].status is FundAssemblyStatus.VOTING
    assert fund.assemblies[SWAP].candidate_user_id == BETO.id
    assert fund.assembly_votes[SWAP] == {ANA.id: True}
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

    assert SWAP not in fund.assemblies
    assert fund.assembly_history == []
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
        setup.book.cast_assembly_vote(TICKER, SWAP, GESTOR, True)
    with pytest.raises(ForbiddenError, match="tem cotas"):
        setup.book.cast_assembly_vote(TICKER, SWAP, stranger, True)
    with pytest.raises(ForbiddenError, match="tem cotas"):
        setup.book.cast_assembly_vote(TICKER, SWAP, ROBOT, True)

    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, False)
    assert setup.book.get(TICKER).assembly_votes[SWAP][BETO.id] is False


def test_voting_needs_an_open_vote(memory: MemoryFunds):
    setup = _assemblable(memory)

    with pytest.raises(ConflictError, match="votação aberta"):
        setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)

    setup.book.convene_assembly(TICKER, ANA, BETO.nickname)
    with pytest.raises(ConflictError, match="votação aberta"):
        setup.book.cast_assembly_vote(TICKER, SWAP, CAIO, True)


def test_the_replacement_wins_by_the_quotas_at_the_close_of_the_last_session(
    memory: MemoryFunds,
):
    """Ana (300) convoca contra o gestor (400); Beto (200) vota a favor: 500 a 400 troca."""
    published: list[Headline] = []
    setup = _assemblable(memory, published)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)

    _close_all_sessions(setup)

    assert fund.terms.manager_user_id == ANA.id
    # O novo gestor conta o "desde" do dia em que a votação fechou
    assert fund.terms.manager_since == LAST_SESSION
    assert SWAP not in fund.assemblies
    assert fund.assembly_history[-1].status is FundAssemblyStatus.REPLACED
    assert (
        fund.assembly_history[-1].in_favor_quotas,
        fund.assembly_history[-1].against_quotas,
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
    assert SWAP in fund.assemblies

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
    assert fund.assembly_history[-1].status is FundAssemblyStatus.KEPT
    assert _types(published) == [
        NewsType.FUND_ASSEMBLY_CALLED,
        NewsType.FUND_ASSEMBLY_KEPT,
    ]


def test_bots_and_the_market_maker_abstain(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)

    result = setup.book._assemblies.score(fund, SWAP)

    assert result.in_favor == Decimal(500)
    assert result.against == Decimal(400)
    # Bot (100) e formador abstêm
    assert result.non_voting >= Decimal(100)
    assert result.abstention == _total(setup) - Decimal(900)


def test_a_buyback_leaves_the_scoreboard_by_shrinking_the_total(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    before = setup.book._assemblies.score(fund, SWAP)
    setup.engine.cash[setup.fund_client] += Decimal(100000)

    setup.book.open_buyback(TICKER, Decimal(20), Decimal(100))
    setup.book.on_open(TODAY)

    assert setup.book._assemblies.score(fund, SWAP).total <= before.total


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
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)

    _close_all_sessions(setup)

    assert fund.terms.manager_user_id == ANA.id
    assert fund.buyback is None
    assert fund.buyback_order is None
    assert order.status is OrderStatus.CANCELED


def test_the_next_fee_goes_to_the_new_manager(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)
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
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)
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
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)
    assembly = setup.book.get(TICKER).assemblies.get(SWAP)

    reloaded = type(setup.book)(
        1,
        setup.engine,
        lambda user_id: MANAGER,
        participants=lambda: [GESTOR, ANA, BETO],
    )

    fund = reloaded.get(TICKER)
    assert fund.assemblies.get(SWAP) == assembly
    assert fund.assembly_votes[SWAP] == {ANA.id: True, BETO.id: True}


# =========================
# Aumento de taxa
# =========================

RAISED = (Decimal("0.03"), Decimal("0.20"))


def _propose_fee(setup: Setup, proposer: UserDTO = GESTOR) -> None:
    setup.book.propose_fee_increase(TICKER, proposer, *RAISED)


def _comanage(setup: Setup, user: UserDTO) -> None:
    """Põe `user` como co-gestor ativo da gestora."""
    fund = setup.book.get(TICKER)
    fund.comanagers.append(
        FundComanagerDTO(
            user_id=user.id,
            status=FundComanagerStatus.ACTIVE,
            share=Decimal("0.3"),
            pending_share=None,
            pending_from=None,
            invited_on=TODAY,
            since=TODAY,
        )
    )


def test_fee_tally_leaves_the_operators_out_of_the_count():
    """O gestor (300) e o co-gestor (200) não pesam; só os 100 de quem vota contam."""
    result = fee_tally(
        total=Decimal(1000),
        holdings={1: Decimal(300), 2: Decimal(200), 3: Decimal(100), 4: Decimal(50)},
        votes={1: False, 2: False, 3: True},
        excluded={1, 2},
    )

    assert (result.in_favor, result.against) == (Decimal(100), Decimal(0))
    assert result.abstention == Decimal(900)
    # Bots, formador de mercado, gestor e co-gestor ficam fora de quem pode votar
    assert result.non_voting == Decimal(850)
    assert result.wins


def test_a_fee_vote_without_any_vote_does_not_pass():
    result = fee_tally(
        total=Decimal(1000),
        holdings={1: Decimal(300)},
        votes={},
        excluded=set(),
    )

    assert not result.wins
    assert result.missing_to_win == Decimal(1)


def test_only_the_principal_manager_proposes_a_fee_increase(memory: MemoryFunds):
    setup = _assemblable(memory)
    _comanage(setup, BETO)

    for who in (ANA, BETO):
        with pytest.raises(ForbiddenError, match="Só o gestor propõe"):
            _propose_fee(setup, who)

    # O gestor propõe sem precisar de 10% das cotas e a votação abre na hora
    _propose_fee(setup)
    assembly = setup.book.get(TICKER).assemblies[FEE]
    assert assembly.status is FundAssemblyStatus.VOTING
    assert assembly.ends_on == LAST_SESSION
    assert (assembly.previous_management_fee, assembly.proposed_management_fee) == (
        Decimal("0.02"),
        Decimal("0.03"),
    )
    # Ninguém vota por ele
    assert setup.book.get(TICKER).assembly_votes[FEE] == {}


def test_a_proposal_must_raise_a_fee(memory: MemoryFunds):
    setup = _assemblable(memory)

    with pytest.raises(UnprocessableEntityError, match="baixar vale sem votação"):
        setup.book.propose_fee_increase(
            TICKER, GESTOR, Decimal("0.01"), Decimal("0.20")
        )


def test_raising_a_fee_of_a_listed_fund_needs_the_vote_and_lowering_stays_free(
    memory: MemoryFunds,
):
    setup = _assemblable(memory)

    with pytest.raises(ConflictError, match="vai à assembleia"):
        setup.book.set_fees(TICKER, *RAISED)

    setup.book.set_fees(TICKER, Decimal("0.01"), Decimal("0.10"))
    terms = setup.book.get(TICKER).terms
    assert terms.pending_management_fee == Decimal("0.01")
    assert terms.pending_from == date(2020, 2, 3)


def test_manager_and_comanagers_do_not_vote_the_fee(memory: MemoryFunds):
    setup = _assemblable(memory)
    _comanage(setup, BETO)
    _propose_fee(setup)

    for who in (GESTOR, BETO):
        with pytest.raises(ForbiddenError, match="não votam"):
            setup.book.cast_assembly_vote(TICKER, FEE, who, True)
    with pytest.raises(ForbiddenError, match="tem cotas"):
        setup.book.cast_assembly_vote(TICKER, FEE, ROBOT, True)

    setup.book.cast_assembly_vote(TICKER, FEE, ANA, True)
    result = setup.book._assemblies.score(setup.book.get(TICKER), FEE)
    # Só Ana (300) pesa; as 400 do gestor e as 200 do co-gestor não contam contra
    assert (result.in_favor, result.against) == (Decimal(300), Decimal(0))


def test_an_approved_fee_takes_effect_in_the_month_after_the_result(
    memory: MemoryFunds,
):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    _propose_fee(setup)
    setup.book.cast_assembly_vote(TICKER, FEE, ANA, True)
    setup.book.cast_assembly_vote(TICKER, FEE, BETO, False)

    _close_all_sessions(setup)

    assert fund.assembly_history[-1].status is FundAssemblyStatus.APPROVED
    assert FEE not in fund.assemblies
    # Segue em vigor a taxa velha até a virada do mês
    assert fund.terms.management_fee == Decimal("0.02")
    assert fund.terms.pending_management_fee == Decimal("0.03")
    assert fund.terms.pending_from == date(2020, 2, 3)

    setup.book.on_month(date(2020, 2, 3))
    assert fund.terms.management_fee == Decimal("0.03")


def test_a_fee_vote_without_votes_is_rejected(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    _propose_fee(setup)

    _close_all_sessions(setup)

    assert fund.assembly_history[-1].status is FundAssemblyStatus.REJECTED
    assert fund.terms.pending_management_fee is None
    assert fund.terms.management_fee == Decimal("0.02")


def test_a_rejected_fee_can_be_proposed_again_right_away(memory: MemoryFunds):
    setup = _assemblable(memory)
    _propose_fee(setup)
    setup.book.cast_assembly_vote(TICKER, FEE, ANA, False)
    _close_all_sessions(setup)

    _propose_fee(setup)

    assert FEE in setup.book.get(TICKER).assemblies


def test_one_open_vote_per_agenda(memory: MemoryFunds):
    setup = _assemblable(memory)
    _propose_fee(setup)

    with pytest.raises(ConflictError, match="votação aberta desta pauta"):
        _propose_fee(setup)

    # A troca de gestor corre ao mesmo tempo, mas também só uma por vez
    setup.book.convene_assembly(TICKER, ANA, None)
    assert set(setup.book.get(TICKER).assemblies) == {SWAP, FEE}
    with pytest.raises(ConflictError, match="votação aberta desta pauta"):
        setup.book.convene_assembly(TICKER, BETO, None)


def test_the_interval_between_convocations_is_only_for_the_manager_swap(
    memory: MemoryFunds,
):
    setup = _assemblable(memory)
    setup.book.convene_assembly(TICKER, ANA, None)
    _close_all_sessions(setup)
    setup.engine.current_date = date(2020, 1, 13)

    # A troca espera os 3 meses, mas o aumento de taxa abre na hora
    _give(setup, CAIO, 250)
    with pytest.raises(ConflictError, match="10/04/2020"):
        setup.book.convene_assembly(TICKER, CAIO, None)
    fund = setup.book.get(TICKER)
    assert fund.terms.manager_user_id == MANAGER_USER
    _propose_fee(setup)
    assert FEE in fund.assemblies


def test_a_fee_vote_does_not_count_for_the_swap_interval(memory: MemoryFunds):
    setup = _assemblable(memory)
    _propose_fee(setup)
    _close_all_sessions(setup)

    setup.book.convene_assembly(TICKER, ANA, None)

    assert SWAP in setup.book.get(TICKER).assemblies


def test_the_fund_issues_quotas_while_only_a_fee_vote_is_open(memory: MemoryFunds):
    setup = _assemblable(memory)
    _propose_fee(setup)

    # Só a troca de gestor aberta trava a emissão
    setup.book.announce_issuance(TICKER, Decimal(10))

    assert setup.book.get(TICKER).issuance is not None


def test_replacing_the_manager_cancels_the_fee_proposal_he_made(memory: MemoryFunds):
    setup = _assemblable(memory)
    fund = setup.book.get(TICKER)
    _propose_fee(setup)
    setup.book.convene_assembly(TICKER, ANA, None)
    setup.book.cast_assembly_vote(TICKER, SWAP, BETO, True)

    _close_all_sessions(setup)

    assert fund.terms.manager_user_id == ANA.id
    assert FEE not in fund.assemblies
    assert [a.status for a in memory.assemblies(fund.terms.id)] == [
        FundAssemblyStatus.CANCELLED,
        FundAssemblyStatus.REPLACED,
    ]
    assert fund.terms.pending_management_fee is None


def test_an_open_vote_is_pending_for_who_can_vote_and_has_not_voted(
    memory: MemoryFunds,
):
    setup = _assemblable(memory)
    _comanage(setup, CAIO)
    _propose_fee(setup)

    waiting = {
        u.id for u in (GESTOR, ANA, BETO, CAIO, ROBOT) if setup.book.open_votes_for(u)
    }

    # Ana e Beto votam; o gestor, o co-gestor e o bot não
    assert waiting == {ANA.id, BETO.id}
    [(fund, assembly)] = setup.book.open_votes_for(ANA)
    assert (fund.ticker, assembly.agenda) == (TICKER, FEE)

    setup.book.cast_assembly_vote(TICKER, FEE, ANA, True)
    assert setup.book.open_votes_for(ANA) == []

    # Com a troca aberta, Ana (que votou só na taxa) volta a ter uma pendência
    setup.book.convene_assembly(TICKER, BETO, None)
    [(_, swap)] = setup.book.open_votes_for(ANA)
    assert swap.agenda is SWAP
    # Quem convocou já está a favor
    assert setup.book.open_votes_for(BETO) == [
        (setup.book.get(TICKER), setup.book.get(TICKER).assemblies[FEE])
    ]
