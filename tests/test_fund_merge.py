# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811
from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.fund import FundComanagerDTO, FundDistributionDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    EquityEventType,
    FundAssemblyAgenda,
    FundAssemblyStatus,
    FundComanagerStatus,
    NewsType,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.core.life_budget import cents
from backend.features.funds.fund_assembly import block_message
from backend.features.funds.fund_book import Fund
from backend.features.funds.fund_merge import (
    circular_navs,
    conversion_remainder,
    converted_quotas,
    exchange_ratio,
    exit_price,
    settle_exits,
)
from backend.features.notifications.news import Headline
from tests.test_fund_assembly import (
    ANA,
    BETO,
    CAIO,
    GESTOR,
    ROBOT,
    _advance,
    _assemblable,
    _close_all_sessions,
)
from tests.test_fund_book import (
    BUYER,
    MANAGER_USER,
    TICKER,
    TODAY,
    MemoryFunds,
    Setup,
    isolated,
    memory,
)

MERGE = FundAssemblyAgenda.MERGE
SWAP = FundAssemblyAgenda.REPLACE_MANAGER
MOTHER = TICKER
DAUGHTER = "BORE11"
# O caixa estacionado de cada gestora: o balanço do teste o soma ao patrimônio em ações
PARKED: dict[UUID, Decimal] = {}


def _position(setup: Setup, user: UserDTO, ticker: str) -> Decimal:
    position = setup.engine.broker.get_positions(user.client_id).get(ticker)
    return position.size if position is not None else Decimal(0)


def _give_daughter(setup: Setup, user: UserDTO, quotas: int) -> None:
    """Põe `quotas` cotas da incorporada na carteira do jogador, pagas ao PL dela."""
    nav = setup.book._nav(setup.book.get(DAUGHTER))
    assert nav is not None
    setup.engine.cash[user.client_id] += nav * quotas
    setup.engine.broker.buy_from_fund(user.client_id, DAUGHTER, Decimal(quotas), nav)


def _illiquid(setup: Setup, ticker: str, cash_left: int) -> None:
    """Move o caixa da gestora para uma carteira que o balanço soma ao patrimônio: o PL por cota não muda, só o caixa."""
    client = setup.book.get(ticker).account.client_id
    parked = setup.engine.cash[client] - cash_left
    setup.engine.cash[client] = Decimal(cash_left)
    PARKED[client] = PARKED.get(client, Decimal(0)) + parked


def _two_funds(
    memory: MemoryFunds,
    published: list[Headline] | None = None,
    daughter_cash: int = 50000,
) -> Setup:
    """Aura (PL R$ 100) e Boreal (PL R$ 50), as duas do gestor e listadas; os mesmos jogadores têm cotas das duas."""
    setup = _assemblable(memory, published)
    PARKED.clear()
    original = setup.engine.balance_sheet

    def balance_sheet(client_id: UUID):
        # O balanço real soma ao patrimônio as ações da carteira, ao preço de mercado
        held = sum(
            (
                setup.engine.get_current_price(position) * position.size
                for position in setup.engine.broker.get_positions(client_id).values()
            ),
            Decimal(0),
        )
        return original(client_id)._replace(
            total_equity=PARKED.get(client_id, Decimal(0)) + held
        )

    setup.engine.balance_sheet = balance_sheet
    book = setup.book
    book.found(
        ticker=DAUGHTER,
        name="Boreal",
        founder_user_id=MANAGER_USER,
        manager_user_id=MANAGER_USER,
        management_fee=Decimal("0.02"),
        performance_fee=Decimal("0.20"),
    )
    daughter = book.get(DAUGHTER)
    daughter.account.quotas = Decimal(1000)
    setup.engine.cash[daughter.account.client_id] = Decimal(daughter_cash)
    book.open_offer(DAUGHTER, Decimal(200))
    book.close_offer(DAUGHTER)
    _give_daughter(setup, GESTOR, 400)
    _give_daughter(setup, ANA, 300)
    _give_daughter(setup, BETO, 200)
    _give_daughter(setup, CAIO, 100)
    return setup


def _propose(setup: Setup) -> tuple[Fund, Fund]:
    mother = setup.book.get(MOTHER)
    daughter = setup.book.get(DAUGHTER)
    setup.book.propose_merge(mother.terms.id, daughter.terms.id, GESTOR)
    return mother, daughter


def _vote(setup: Setup, ticker: str, user: UserDTO, in_favor: bool) -> None:
    setup.book.cast_assembly_vote(ticker, MERGE, user, in_favor)


# =========================
# Regra pura
# =========================


def test_the_exchange_ratio_is_the_nav_of_the_incorporated_over_the_other():
    """Com a incorporada a R$ 50 e a incorporadora a R$ 100, 2 cotas de uma valem 1 da outra."""
    ratio = exchange_ratio(Decimal(50), Decimal(100))

    assert ratio == Decimal("0.5")
    assert converted_quotas(Decimal(2), ratio) == 1


def test_whole_quotas_are_converted_and_the_fraction_comes_in_cash():
    ratio = exchange_ratio(Decimal(50), Decimal(100))

    converted = converted_quotas(Decimal(101), ratio)

    assert converted == 50
    # A cota que sobra vale R$ 50: o dinheiro paga o que não fecha uma cota inteira
    assert (
        conversion_remainder(Decimal(101), Decimal(50), converted, Decimal(100)) == 50
    )


def test_the_nav_per_quota_without_crossed_quotas_is_assets_over_quotas():
    mother, daughter = circular_navs(
        Decimal(1000), Decimal(500), Decimal(10), Decimal(10), Decimal(0), Decimal(0)
    ) or (None, None)

    assert (mother, daughter) == (Decimal(100), Decimal(50))


def test_the_crossed_quotas_count_at_the_nav_of_the_other():
    """A incorporadora, com R$ 1.000 e 2 cotas da incorporada (R$ 50 cada), vale (1.000 + 2 x 50) / 10 = R$ 110 por cota."""
    navs = circular_navs(
        Decimal(1000), Decimal(500), Decimal(10), Decimal(10), Decimal(2), Decimal(0)
    )

    assert navs == (Decimal(110), Decimal(50))


def test_the_crossed_quotas_of_both_sides_balance_the_total_equity():
    """Com uma cota cruzada de cada lado, o patrimônio das duas (R$ 1.500) é o das cotas que ficam, cada uma ao PL por cota dela."""
    navs = circular_navs(
        Decimal(1000), Decimal(500), Decimal(10), Decimal(10), Decimal(2), Decimal(1)
    )

    assert navs is not None
    mother_nav, daughter_nav = navs
    staying = mother_nav * (10 - 1) + daughter_nav * (10 - 2)
    assert abs(staying - Decimal(1500)) < Decimal("0.000001")


def test_two_funds_that_only_hold_each_other_have_no_nav():
    assert (
        circular_navs(
            Decimal(0), Decimal(0), Decimal(10), Decimal(10), Decimal(10), Decimal(10)
        )
        is None
    )


def test_the_exit_price_is_the_nav_of_the_day_in_cents():
    assert exit_price(Decimal("55.2249")) == Decimal("55.22")


@pytest.mark.parametrize(
    ("total", "daughter_cash", "mother_cash", "expected"),
    [
        (1000, 5000, 5000, (1000, 0, 0)),
        (1000, 400, 5000, (400, 600, 0)),
        (1000, 0, 300, (0, 300, 700)),
        (1000, -50, 5000, (0, 1000, 0)),
    ],
)
def test_the_daughter_cash_pays_first_and_the_mother_completes(
    total: int, daughter_cash: int, mother_cash: int, expected: tuple[int, int, int]
):
    cash = settle_exits(Decimal(total), Decimal(daughter_cash), Decimal(mother_cash))

    assert (cash.from_daughter, cash.from_mother, cash.shortfall) == tuple(
        Decimal(v) for v in expected
    )


# =========================
# Proposta
# =========================


def test_the_principal_proposes_and_both_assemblies_open_together(
    memory: MemoryFunds,
):
    setup = _two_funds(memory)

    mother, daughter = _propose(setup)

    assert mother.assemblies[MERGE].ends_on == daughter.assemblies[MERGE].ends_on
    assert mother.assemblies[MERGE].partner_fund_id == daughter.terms.id
    assert daughter.assemblies[MERGE].partner_fund_id == mother.terms.id
    assert not mother.assemblies[MERGE].absorbed
    assert daughter.assemblies[MERGE].absorbed
    # Quem propõe vota a favor nas duas
    assert mother.assembly_votes[MERGE] == {MANAGER_USER: True}
    assert daughter.assembly_votes[MERGE] == {MANAGER_USER: True}


def test_a_shareholder_does_not_propose(memory: MemoryFunds):
    setup = _two_funds(memory)
    mother = setup.book.get(MOTHER)
    daughter = setup.book.get(DAUGHTER)

    with pytest.raises(ForbiddenError):
        setup.book.propose_merge(mother.terms.id, daughter.terms.id, ANA)
    assert MERGE not in mother.assemblies


def test_a_fund_cannot_merge_with_itself(memory: MemoryFunds):
    setup = _two_funds(memory)
    mother = setup.book.get(MOTHER)

    with pytest.raises(UnprocessableEntityError):
        setup.book.propose_merge(mother.terms.id, mother.terms.id, GESTOR)


def test_only_one_merge_vote_at_a_time(memory: MemoryFunds):
    setup = _two_funds(memory)
    mother, daughter = _propose(setup)

    block, next_allowed = setup.book.merge_block(mother, GESTOR)

    assert block == "pending"
    assert next_allowed == mother.assemblies[MERGE].ends_on
    with pytest.raises(ConflictError):
        setup.book.propose_merge(mother.terms.id, daughter.terms.id, GESTOR)


def test_an_open_issuance_blocks_the_merge(memory: MemoryFunds):
    setup = _two_funds(memory)
    mother = setup.book.get(MOTHER)
    mother.account.offer_remaining = Decimal(10)

    block, _ = setup.book.merge_block(mother, GESTOR)

    assert block == "busy"


def test_without_another_listed_fund_there_is_no_partner(memory: MemoryFunds):
    setup = _assemblable(memory)

    block, _ = setup.book.merge_block(setup.book.get(MOTHER), GESTOR)

    assert block == "no_partner"


def test_the_grace_of_the_hostile_takeover_mode_blocks_the_proposal(
    memory: MemoryFunds,
):
    setup = _two_funds(memory)
    setup.book._assemblies.grace_ends = date(2020, 3, 1)
    mother = setup.book.get(MOTHER)

    block, next_allowed = setup.book.merge_block(mother, GESTOR)

    assert block == "grace"
    assert next_allowed == date(2020, 3, 1)
    with pytest.raises(ConflictError, match="carência"):
        setup.book.propose_merge(
            mother.terms.id, setup.book.get(DAUGHTER).terms.id, GESTOR
        )


@pytest.mark.parametrize("frozen_ticker", [MOTHER, DAUGHTER])
def test_a_frozen_fund_blocks_the_merge_of_both(
    memory: MemoryFunds, frozen_ticker: str
):
    setup = _two_funds(memory)
    frozen = setup.book.get(frozen_ticker)
    free = setup.book.get(DAUGHTER if frozen_ticker == MOTHER else MOTHER)
    until = date(2020, 12, 31)
    # O gestor da gestora congelada governa o país; a outra segue livre
    setup.book.frozen_until = lambda fund: until if fund is frozen else None

    assert setup.book.merge_block(frozen, GESTOR) == ("frozen", until)
    # A livre não acha parceira: a congelada não entra na fusão
    assert setup.book.merge_block(free, GESTOR) == ("no_partner", None)
    with pytest.raises(ConflictError, match="congelada"):
        setup.book.propose_merge(
            setup.book.get(MOTHER).terms.id,
            setup.book.get(DAUGHTER).terms.id,
            GESTOR,
        )


@pytest.mark.parametrize("swap_ticker", [MOTHER, DAUGHTER])
def test_a_manager_swap_in_either_fund_blocks_the_proposal(
    memory: MemoryFunds, swap_ticker: str
):
    setup = _two_funds(memory)
    # O convite pendente já conta como troca em andamento
    setup.book.convene_assembly(swap_ticker, ANA, BETO.nickname)
    other = DAUGHTER if swap_ticker == MOTHER else MOTHER

    for ticker in (MOTHER, DAUGHTER):
        block, next_allowed = setup.book.merge_block(setup.book.get(ticker), GESTOR)
        if ticker == swap_ticker:
            assert block == "swap_open"
            assert next_allowed == setup.book.get(swap_ticker).assemblies[SWAP].ends_on
        else:
            assert block == "no_partner"
    with pytest.raises(ConflictError, match="troca de gestor"):
        setup.book.propose_merge(
            setup.book.get(MOTHER).terms.id,
            setup.book.get(DAUGHTER).terms.id,
            GESTOR,
        )
    assert MERGE not in setup.book.get(other).assemblies


@pytest.mark.parametrize("ticker", [MOTHER, DAUGHTER])
def test_an_open_merge_holds_the_manager_swap_of_both_funds(
    memory: MemoryFunds, ticker: str
):
    setup = _two_funds(memory)
    mother, _ = _propose(setup)

    fund = setup.book.get(ticker)
    block, next_allowed = setup.book._assemblies.block_for(fund, ANA, TODAY, SWAP)

    assert block == "merge_open"
    assert next_allowed == mother.assemblies[MERGE].ends_on
    with pytest.raises(ConflictError, match="fusão em votação"):
        setup.book.convene_assembly(ticker, ANA, None)
    assert "fusão em votação" in block_message(block, next_allowed)


def test_the_block_texts_of_the_merge_name_the_reason():
    assert "troca de gestor" in block_message("swap_open", date(2020, 3, 1))
    assert "fusão" in block_message("merge_open", date(2020, 3, 1))
    assert "congelada" in block_message("frozen", date(2020, 3, 1))


def test_funds_holding_each_others_quotas_still_have_the_partner(
    memory: MemoryFunds,
):
    setup = _two_funds(memory)
    mother = setup.book.get(MOTHER)
    daughter = setup.book.get(DAUGHTER)
    setup.engine.broker.receive_position(
        mother.account.client_id, DAUGHTER, Decimal(10), Decimal(50)
    )

    assert setup.book.merge_partners(mother, GESTOR) == [daughter]
    assert setup.book.merge_partners(daughter, GESTOR) == [mother]


def _cross_hold(setup: Setup, held_by_mother: int, held_by_daughter: int) -> None:
    """A incorporadora passa a ter `held_by_mother` cotas da incorporada e a incorporada, `held_by_daughter` da incorporadora; as cotas saem da carteira de um cotista, e o total de cada gestora segue o mesmo."""
    mother = setup.book.get(MOTHER)
    daughter = setup.book.get(DAUGHTER)
    broker = setup.engine.broker
    if held_by_mother:
        broker.transfer_position(
            ANA.client_id, mother.account.client_id, DAUGHTER, Decimal(held_by_mother)
        )
    if held_by_daughter:
        broker.transfer_position(
            BETO.client_id,
            daughter.account.client_id,
            MOTHER,
            Decimal(held_by_daughter),
        )


def test_the_open_merge_holds_the_issuance_of_both_funds(memory: MemoryFunds):
    setup = _two_funds(memory)
    _propose(setup)

    for ticker in (MOTHER, DAUGHTER):
        with pytest.raises(ConflictError):
            setup.book.announce_issuance(ticker, Decimal(10))


# =========================
# Votação e fechamento
# =========================


def test_the_merge_passes_when_both_assemblies_approve(memory: MemoryFunds):
    published: list[Headline] = []
    setup = _two_funds(memory, published)
    mother, daughter = _propose(setup)
    quotas_before = mother.account.quotas
    ana_mother = _position(setup, ANA, MOTHER)
    cash_before = (
        setup.engine.cash[mother.account.client_id]
        + setup.engine.cash[daughter.account.client_id]
    )

    _close_all_sessions(setup)

    # A incorporada some do livro e a incorporadora segue com o ticker
    assert setup.book.is_merged(DAUGHTER)
    with pytest.raises(KeyError):
        setup.book.get(DAUGHTER)
    assert setup.book.get(MOTHER) is mother
    assert mother.assembly_history[-1].status is FundAssemblyStatus.APPROVED
    assert daughter.assembly_history[-1].status is FundAssemblyStatus.APPROVED
    # Ana tinha 300 cotas da Boreal a R$ 50: 150 da Aura a R$ 100
    assert _position(setup, ANA, MOTHER) == ana_mother + 150
    assert _position(setup, ANA, DAUGHTER) == 0
    # As cotas da Boreal viram cotas da Aura pela razão de 0,5, formador incluído
    assert mother.account.quotas > quotas_before
    # O caixa da incorporada passou inteiro à incorporadora
    assert setup.engine.cash[daughter.account.client_id] == 0
    assert setup.engine.cash[mother.account.client_id] == cash_before
    assert NewsType.FUND_MERGED in [h.news_type for h in published]


def test_the_daughter_leaves_the_market_and_the_row_keeps_the_record(
    memory: MemoryFunds,
):
    setup = _two_funds(memory)
    mother, daughter = _propose(setup)
    daughter_client = daughter.account.client_id

    _close_all_sessions(setup)

    saved = memory.funds[daughter.terms.id]
    assert saved.merged_into_fund_id == mother.terms.id
    assert saved.merged_on == date(2020, 1, 10)
    assert DAUGHTER not in setup.engine.broker.maker_accounts
    assert DAUGHTER not in setup.engine.fund_references
    assert DAUGHTER not in setup.engine.ranking_prices
    assert daughter_client not in setup.book.client_ids
    assert daughter.account.quotas == 0


def test_the_cost_of_the_quotas_goes_with_the_conversion(memory: MemoryFunds):
    """Ana pagou R$ 50 por cota da Boreal: as 150 cotas novas da Aura levam o custo total das 300 que entregou."""
    setup = _two_funds(memory)
    _propose(setup)

    _close_all_sessions(setup)

    position = setup.engine.broker.get_positions(ANA.client_id)[MOTHER]
    # 300 da Aura a R$ 100 mais 300 da Boreal a R$ 50 (R$ 15.000 de custo) agora em 150 cotas
    assert position.size == 450
    assert position.total_cost == Decimal(300 * 100 + 300 * 50)


def test_the_fraction_that_does_not_fill_a_quota_comes_in_cash(memory: MemoryFunds):
    setup = _two_funds(memory)
    _give_daughter(setup, ANA, 1)
    _propose(setup)
    cash = setup.engine.cash[ANA.client_id]

    _close_all_sessions(setup)

    # 301 cotas a R$ 50 = 150 cotas inteiras a R$ 100 e R$ 50 em dinheiro
    assert _position(setup, ANA, MOTHER) == 300 + 150
    assert setup.engine.cash[ANA.client_id] == cash + 50


def test_a_rejection_in_one_assembly_keeps_both_funds(memory: MemoryFunds):
    """Na Boreal Ana (300) vota contra e o gestor (que passa a ter 100) perde: as duas seguem separadas."""
    published: list[Headline] = []
    setup = _two_funds(memory, published)
    mother, daughter = _propose(setup)
    setup.engine.broker.sell_to_fund(
        GESTOR.client_id, DAUGHTER, Decimal(300), Decimal(50)
    )
    _vote(setup, DAUGHTER, ANA, False)
    ana_daughter = _position(setup, ANA, DAUGHTER)

    _close_all_sessions(setup)

    assert not setup.book.is_merged(DAUGHTER)
    assert setup.book.get(DAUGHTER) is daughter
    assert mother.assembly_history[-1].status is FundAssemblyStatus.REJECTED
    assert daughter.assembly_history[-1].status is FundAssemblyStatus.REJECTED
    assert _position(setup, ANA, DAUGHTER) == ana_daughter
    # A rejeição pelo voto não traz motivo de caixa
    assert daughter.assembly_history[-1].merge_shortfall is None
    assert NewsType.FUND_MERGED not in [h.news_type for h in published]


def test_without_votes_the_merge_does_not_pass(memory: MemoryFunds):
    """O gestor da proposta não tem cota da Boreal: a assembleia de lá fecha sem voto e não aprova."""
    setup = _two_funds(memory)
    setup.engine.broker.sell_to_fund(
        GESTOR.client_id, DAUGHTER, Decimal(400), Decimal(50)
    )
    mother, _daughter = _propose(setup)

    _close_all_sessions(setup)

    assert not setup.book.is_merged(DAUGHTER)
    assert mother.assembly_history[-1].status is FundAssemblyStatus.REJECTED


def test_the_ones_who_vote_against_in_the_daughter_leave_by_the_nav(
    memory: MemoryFunds,
):
    """Ana (100 cotas contra, R$ 50 cada) recebe R$ 5.000 do caixa da Boreal, que cobre sozinho."""
    setup = _two_funds(memory)
    mother, daughter = _propose(setup)
    setup.engine.broker.sell_to_fund(ANA.client_id, DAUGHTER, Decimal(200), Decimal(50))
    _vote(setup, DAUGHTER, ANA, False)
    _vote(setup, DAUGHTER, BETO, True)
    cash = setup.engine.cash[ANA.client_id]
    mother_cash = setup.engine.cash[mother.account.client_id]
    daughter_cash = setup.engine.cash[daughter.account.client_id]
    ana_mother = _position(setup, ANA, MOTHER)

    _close_all_sessions(setup)

    assert setup.book.is_merged(DAUGHTER)
    assert setup.engine.cash[ANA.client_id] == cash + 100 * 50
    assert _position(setup, ANA, DAUGHTER) == 0
    # Quem sai não recebe cotas da incorporadora
    assert _position(setup, ANA, MOTHER) == ana_mother
    # O que sobrou do caixa da Boreal passou à Aura
    assert (
        setup.engine.cash[mother.account.client_id]
        == mother_cash + daughter_cash - 100 * 50
    )


def test_the_mother_completes_the_exit_when_the_daughter_cash_falls_short(
    memory: MemoryFunds,
):
    """Ana (300 contra) leva R$ 15.000; a Boreal só tem R$ 10.000 em caixa e a Aura completa os R$ 5.000."""
    setup = _two_funds(memory)
    _illiquid(setup, DAUGHTER, 10000)
    mother, daughter = _propose(setup)
    _vote(setup, DAUGHTER, ANA, False)
    _vote(setup, DAUGHTER, BETO, True)
    _vote(setup, DAUGHTER, CAIO, True)
    cash = setup.engine.cash[ANA.client_id]
    mother_cash = setup.engine.cash[mother.account.client_id]

    _close_all_sessions(setup)

    assert setup.book.is_merged(DAUGHTER)
    assert setup.engine.cash[ANA.client_id] == cash + 300 * 50
    # O caixa da Boreal ficou todo na saída; a Aura pagou os R$ 5.000 que faltavam
    assert setup.engine.cash[daughter.account.client_id] == 0
    assert setup.engine.cash[mother.account.client_id] == mother_cash - 5000


def test_the_merge_is_rejected_when_the_two_cash_do_not_cover_the_exit(
    memory: MemoryFunds,
):
    setup = _two_funds(memory)
    _illiquid(setup, DAUGHTER, 10000)
    _illiquid(setup, MOTHER, 2000)
    mother, daughter = _propose(setup)
    _vote(setup, DAUGHTER, ANA, False)
    _vote(setup, DAUGHTER, BETO, True)
    _vote(setup, DAUGHTER, CAIO, True)
    cash = setup.engine.cash[ANA.client_id]

    # O placar mostra quanto falta enquanto a votação está aberta
    panel = setup.book.assembly_panel(daughter, GESTOR, {}, {})
    merge = panel.current[0].merge
    assert merge is not None
    assert merge.shortfall == 3000

    _close_all_sessions(setup)

    assert not setup.book.is_merged(DAUGHTER)
    assert daughter.assembly_history[-1].status is FundAssemblyStatus.REJECTED
    assert mother.assembly_history[-1].status is FundAssemblyStatus.REJECTED
    assert setup.engine.cash[ANA.client_id] == cash
    assert _position(setup, ANA, DAUGHTER) == 300
    # O histórico guarda o motivo: a rejeição foi no fechamento, por falta de caixa
    for fund in (mother, daughter):
        assert fund.assembly_history[-1].merge_shortfall == 3000
        assert memory.assemblies_saved[fund.terms.id][-1].merge_shortfall == 3000
    history = setup.book.assembly_panel(daughter, GESTOR, {}, {}).history
    assert history[0].merge_shortfall == 3000


def _stay_value(setup: Setup, user: UserDTO, nav_of: dict[str, Decimal]) -> Decimal:
    """O patrimônio do jogador nas duas gestoras: cotas de cada uma ao PL por cota dela, mais o caixa."""
    held = sum(
        (_position(setup, user, ticker) * nav for ticker, nav in nav_of.items()),
        Decimal(0),
    )
    return held + setup.engine.cash[user.client_id]


@pytest.mark.parametrize(
    ("held_by_mother", "held_by_daughter"), [(100, 0), (0, 20), (100, 20)]
)
def test_the_crossed_quotas_are_cancelled_and_who_stays_neither_gains_nor_loses(
    memory: MemoryFunds, held_by_mother: int, held_by_daughter: int
):
    setup = _two_funds(memory)
    mother = setup.book.get(MOTHER)
    daughter = setup.book.get(DAUGHTER)
    _cross_hold(setup, held_by_mother, held_by_daughter)
    _propose(setup)
    valuation = setup.book._merge_valuation(mother, daughter)
    assert valuation.mother_nav is not None
    assert valuation.daughter_nav is not None
    assert valuation.cancelled_daughter_quotas == held_by_mother
    assert valuation.cancelled_mother_quotas == held_by_daughter
    navs = {MOTHER: valuation.mother_nav, DAUGHTER: valuation.daughter_nav}
    before = {
        user: _stay_value(setup, user, navs) for user in (GESTOR, ANA, BETO, CAIO)
    }

    _close_all_sessions(setup)

    assert setup.book.is_merged(DAUGHTER)
    # As cotas cruzadas somem dos dois lados: nenhuma carteira de gestora guarda cota de gestora
    broker = setup.engine.broker
    assert _position(setup, GESTOR, DAUGHTER) == 0
    assert DAUGHTER not in broker.get_positions(mother.account.client_id)
    assert MOTHER not in broker.get_positions(daughter.account.client_id)
    # O PL por cota depois da fusão é o de antes; a única folga é a fração de cota do formador de mercado, que não vem em dinheiro
    nav_after = setup.book._nav(mother)
    assert nav_after is not None
    assert abs(nav_after - valuation.mother_nav) < Decimal("0.1")
    after = {
        user: _stay_value(setup, user, {MOTHER: nav_after})
        for user in (GESTOR, ANA, BETO, CAIO)
    }
    for user in (GESTOR, ANA, BETO, CAIO):
        assert abs(after[user] - before[user]) < before[user] * Decimal("0.0005")


def test_the_crossed_quotas_are_burned_with_a_merge_event(
    memory: MemoryFunds, captured_events: list
):
    setup = _two_funds(memory)
    _cross_hold(setup, 100, 20)
    _propose(setup)
    captured_events.clear()

    _close_all_sessions(setup)

    kinds = [
        (e.event_type, e.ticker)
        for e in captured_events
        if isinstance(e, EquityEventDTO)
    ]
    # Cada lado queima a posição cruzada; o resto da carteira e a conversão levam o rótulo da fusão
    assert (EquityEventType.MERGE_OUT, DAUGHTER) in kinds
    assert (EquityEventType.MERGE_OUT, MOTHER) in kinds
    assert (EquityEventType.MERGE_IN, MOTHER) in kinds
    assert not any(
        kind in (EquityEventType.TRANSFER_IN, EquityEventType.TRANSFER_OUT)
        for kind, _ in kinds
    )


def test_the_automatic_of_the_daughter_ends_with_the_merge(memory: MemoryFunds):
    setup = _two_funds(memory)
    stopped: list[str] = []
    setup.book._stop_automatic = lambda fund, reason: stopped.append(fund.ticker)
    _propose(setup)

    _close_all_sessions(setup)

    assert stopped == [DAUGHTER]


def test_the_pending_comanager_invites_of_the_daughter_go_with_it(
    memory: MemoryFunds,
):
    setup = _two_funds(memory)
    daughter = setup.book.get(DAUGHTER)
    invite = FundComanagerDTO(
        user_id=ANA.id,
        status=FundComanagerStatus.INVITED,
        share=Decimal(0),
        pending_share=Decimal("0.2"),
        pending_from=None,
        invited_on=TODAY,
        since=None,
    )
    daughter.comanagers.append(invite)
    repository.fund_comanager.save(daughter.terms.id, invite)
    assert [c.status for c in daughter.comanagers] == [FundComanagerStatus.INVITED]
    _propose(setup)

    _close_all_sessions(setup)

    assert daughter.comanagers == []
    assert repository.fund_comanager.of_fund(daughter.terms.id) == []


def _pend_distribution(fund: Fund, per_quota: int) -> None:
    """Põe na gestora um rendimento apurado na data-com e ainda não pago."""
    pending = FundDistributionDTO(
        data_com=TODAY,
        realized_profit=Decimal(0),
        rate=Decimal(1),
        quotas=fund.account.outside_quotas,
        per_quota=Decimal(per_quota),
        paid_per_quota=None,
        paid=None,
        paid_on=None,
    )
    fund.distributions = [*fund.distributions, pending]


def test_the_pending_distributions_are_paid_before_the_exit_and_the_ratio(
    memory: MemoryFunds,
):
    """A incorporada com R$ 10 por cota de rendimento a pagar: quem sai recebe o rendimento e sai pelo PL já sem ele."""
    setup = _two_funds(memory)
    mother, daughter = _propose(setup)
    _pend_distribution(daughter, 10)
    _pend_distribution(mother, 5)
    _vote(setup, DAUGHTER, ANA, False)
    engine = setup.engine
    broker = engine.broker
    d_client = daughter.account.client_id
    holders = sum((q for _, q in setup.book._holders(daughter)), Decimal(0))
    daughter_nav = (engine.cash[d_client] - 10 * holders) / daughter.account.quotas
    mother_nav = setup.book._nav(mother)
    assert mother_nav is not None
    mother_holders = sum((q for _, q in setup.book._holders(mother)), Decimal(0))
    ana_cash = engine.cash[ANA.client_id]
    beto_mother = _position(setup, BETO, MOTHER)
    beto_cash = engine.cash[BETO.client_id]
    mother_nav_after_payout = (
        engine.cash[mother.account.client_id] - 5 * mother_holders
    ) / mother.account.quotas
    assert mother_nav_after_payout < mother_nav

    _close_all_sessions(setup)

    assert setup.book.is_merged(DAUGHTER)
    # Ana recebeu R$ 3.000 de rendimento (300 cotas x R$ 10) e vendeu as 300 ao PL por cota sem o rendimento
    assert engine.cash[ANA.client_id] - ana_cash == pytest.approx(
        Decimal(3000) + 300 * cents(daughter_nav) + 300 * 5, abs=Decimal("0.01")
    )
    # A razão usa o PL por cota de depois do rendimento das duas: 200 cotas do Beto viram as cotas inteiras dessa razão
    ratio = daughter_nav / mother_nav_after_payout
    converted = _position(setup, BETO, MOTHER) - beto_mother
    assert converted == (200 * ratio).to_integral_value(rounding="ROUND_FLOOR")
    # O rendimento da incorporadora (R$ 5 por cota) foi pago só a quem era cotista dela; Beto recebe pelas 200 cotas da Boreal só a sobra da conversão e o da própria posição
    assert mother.distributions[-1].paid_on == TODAY
    assert daughter.distributions[-1].paid_on == TODAY
    assert engine.cash[BETO.client_id] - beto_cash < 200 * 10 + 200 * 5 + 120
    assert broker.get_positions(d_client) == {}


def test_replacing_the_manager_cancels_the_merge_of_both(memory: MemoryFunds):
    setup = _two_funds(memory)
    mother, daughter = _propose(setup)

    setup.book._replace_manager(mother, ANA.id)

    assert MERGE not in mother.assemblies
    assert MERGE not in daughter.assemblies
