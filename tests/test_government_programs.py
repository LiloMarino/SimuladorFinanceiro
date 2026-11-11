"""Programas de governo com nome: proposta, título, manchete, extinção, rebatismo e retomada."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core.dto.government import PROGRAM_NAME_MAX_LENGTH, ProposeMeasureRequest
from backend.core.enum import MeasureKind, NewsType, VoterGroup
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.features.government import approval as approval_rules
from backend.features.government import (
    congress,
    governance,
    state,
    voters,
)
from backend.features.government import measures as rules
from backend.features.government.government_book import GovernmentBook
from backend.features.government.state import Measure
from tests.test_government_book import (
    ALICE,
    SEED,
    TERM_START,
    USERS,
    book,
    congress_says,
    engine,
    govern,
    headlines,
    hold_vote_day,
    market,
    notices,
    office,
    party_of,
    settings,
    stored,
)

AUX = MeasureKind.WELFARE_SPENDING
WORKS = MeasureKind.PUBLIC_WORKS
SERVANTS = MeasureKind.SERVANT_RAISE
FAMILY = "Bolsa Família"
BRAZIL = "Auxílio Brasil"


@pytest.fixture(autouse=True)
def no_frozen_portfolio(monkeypatch: pytest.MonkeyPatch) -> None:
    """O motor de teste não monta carteira; o painel aqui é só dos gastos."""
    monkeypatch.setattr(governance, "_portfolio", lambda *_: None)


def pass_measure(
    book: GovernmentBook,
    monkeypatch,
    day: date,
    kind: MeasureKind,
    value: str,
    name: str | None = None,
) -> date:
    """Propõe a medida no dia, a casa a aprova no próximo voto e devolve o dia em que ela vale."""
    book.propose(ALICE, day, kind, Decimal(value), None, None, name)
    congress_says(monkeypatch, True)
    voted = congress.next_vote_date(day)
    hold_vote_day(book, voted)
    effective = max(m.effective for m in book.state.measures.values() if m.effective)
    return effective


def launch_family(book: GovernmentBook, monkeypatch) -> date:
    """O auxílio de 2% do PIB batizado de Bolsa Família, aprovado e em vigor; devolve o dia em que passa a valer."""
    effective = pass_measure(book, monkeypatch, TERM_START, AUX, "0.02", FAMILY)
    book.on_tick(USERS, effective + timedelta(days=1), False)
    return effective


def in_force(headlines) -> list[str]:
    """As manchetes de medida que passa a valer sem mudar o nome do programa."""
    return [
        h.text
        for _, h in headlines
        if h.news_type is NewsType.MEASURE_VOTED
        and h.text.startswith(("Passa a valer", "Já vale", "Entra em vigor"))
    ]


def programs(headlines) -> list[str]:
    """As manchetes do programa que nasce, é rebatizado ou acaba."""
    return [h.text for _, h in headlines if h.news_type is NewsType.NAMED_PROGRAM]


# Proposta


def test_the_request_limits_the_name_and_trims_it():
    ProposeMeasureRequest(kind=AUX, value=Decimal("0.02"), name="a" * 30)
    with pytest.raises(ValidationError):
        ProposeMeasureRequest(
            kind=AUX,
            value=Decimal("0.02"),
            name="a" * (PROGRAM_NAME_MAX_LENGTH + 1),
        )

    request = ProposeMeasureRequest(kind=AUX, value=Decimal("0.02"), name="  Bolsa  ")

    assert request.name == "Bolsa"


def test_only_the_welfare_and_the_works_take_a_name(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        book.propose(ALICE, TERM_START, SERVANTS, Decimal("0.03"), None, None, "Prêmio")
    book.propose(ALICE, TERM_START, WORKS, Decimal("0.012"), None, None, "PAC")

    assert book.state.measures[1].name == "PAC"


def test_a_blank_name_is_a_measure_without_name(book: GovernmentBook, engine, market):
    govern(book, engine)

    book.propose(ALICE, TERM_START, AUX, Decimal("0.02"), None, None, "")

    assert book.state.measures[1].name is None
    assert rules.title(book.state.measures[1]) == "Auxílio: 2% do PIB"


def test_the_title_of_a_named_measure_opens_with_the_program(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    book.propose(ALICE, TERM_START, AUX, Decimal("0.02"), None, None, FAMILY)

    assert rules.title(book.state.measures[1]) == f"{FAMILY}: 2% do PIB"


# Lançamento


def test_the_approved_name_is_the_program_in_force_from_the_effective_day(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)

    effective = launch_family(book, monkeypatch)

    timeline = book.spending_timeline()
    assert timeline.name_on(AUX, effective - timedelta(days=1)) is None
    assert timeline.name_on(AUX, effective) == FAMILY
    assert timeline.latest_name(AUX) == FAMILY
    assert timeline.latest_name(WORKS) is None


def test_a_rejected_name_never_becomes_the_program(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    book.propose(ALICE, TERM_START, AUX, Decimal("0.02"), None, None, FAMILY)
    congress_says(monkeypatch, False)

    hold_vote_day(book, congress.next_vote_date(TERM_START))

    assert book.spending_timeline().latest_name(AUX) is None


def test_the_launch_reaches_the_journal_when_the_program_binds(
    book: GovernmentBook, engine, market, monkeypatch, headlines
):
    govern(book, engine)

    launch_family(book, monkeypatch)

    [launched] = programs(headlines)
    assert FAMILY in launched


def test_a_measure_without_name_keeps_the_program(
    book: GovernmentBook, engine, market, monkeypatch, headlines
):
    govern(book, engine)
    launched = launch_family(book, monkeypatch)
    headlines.clear()

    effective = pass_measure(
        book, monkeypatch, launched + timedelta(days=10), AUX, "0.025"
    )
    book.on_tick(USERS, effective + timedelta(days=1), False)

    assert book.spending_timeline().latest_name(AUX) == FAMILY
    assert programs(headlines) == []
    [text] = in_force(headlines)
    assert "Auxílio" in text


# Rebatismo


def test_the_same_value_with_another_name_is_a_rename(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    day = launch_family(book, monkeypatch) + timedelta(days=10)

    book.propose(ALICE, day, AUX, Decimal("0.02"), None, None, BRAZIL)

    renamed = book.state.measures[2]
    assert (renamed.name, renamed.renamed_from) == (BRAZIL, FAMILY)


def test_the_same_value_with_the_same_name_changes_nothing(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    day = launch_family(book, monkeypatch) + timedelta(days=10)

    with pytest.raises(ConflictError):
        book.propose(ALICE, day, AUX, Decimal("0.02"), None, None, FAMILY)
    with pytest.raises(ConflictError):
        book.propose(ALICE, day, AUX, Decimal("0.02"), None, None, None)


def test_the_rename_reaches_the_journal_and_keeps_the_value(
    book: GovernmentBook, engine, market, monkeypatch, headlines
):
    govern(book, engine)
    day = launch_family(book, monkeypatch) + timedelta(days=10)
    headlines.clear()
    effective = pass_measure(book, monkeypatch, day, AUX, "0.02", BRAZIL)

    book.on_tick(USERS, effective + timedelta(days=1), False)

    timeline = book.spending_timeline()
    assert timeline.name_on(AUX, effective) == BRAZIL
    assert timeline.value_on(AUX, effective) == Decimal("0.02")
    [renamed] = programs(headlines)
    assert FAMILY in renamed and BRAZIL in renamed


def test_a_rename_costs_every_group_the_same_points_once():
    base = Measure(
        id=1,
        kind=AUX,
        value=Decimal("0.02"),
        before=Decimal("0.02"),
        sector=None,
        segment=None,
        proposer_id=1,
        term_start=TERM_START,
        proposed=TERM_START,
        name=BRAZIL,
    )
    renamed = Measure(**{**base.__dict__, "renamed_from": FAMILY})

    for group in VoterGroup:
        assert approval_rules.measure_reaction(
            group, renamed
        ) - approval_rules.measure_reaction(group, base) == (
            approval_rules.RENAME_POINTS
        )
    assert approval_rules.RENAME_POINTS < 0


# Extinção


def test_taking_the_budget_to_zero_ends_the_program_and_records_its_name(
    book: GovernmentBook, engine, market, monkeypatch, headlines
):
    govern(book, engine)
    pass_measure(book, monkeypatch, TERM_START, AUX, "0.01", FAMILY)
    day = TERM_START + timedelta(days=40)
    pass_measure(book, monkeypatch, day, AUX, "0.005")
    day += timedelta(days=40)
    headlines.clear()
    effective = pass_measure(book, monkeypatch, day, AUX, "0", "Outro nome")

    book.on_tick(USERS, effective + timedelta(days=1), False)

    ended = book.state.measures[3]
    assert (ended.name, ended.value) == (FAMILY, Decimal(0))
    assert rules.title(ended) == f"Extinção do {FAMILY}"
    assert book.spending_timeline().name_on(AUX, effective) is None
    assert FAMILY in programs(headlines)[-1]


def test_ending_a_named_program_adds_rejection_to_the_groups_it_served(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    pass_measure(book, monkeypatch, TERM_START, AUX, "0.01", FAMILY)
    pass_measure(book, monkeypatch, TERM_START + timedelta(days=40), AUX, "0.005")
    # O tamanho do salto domina qualquer ajuste de rejeição dos fechamentos do mês
    monkeypatch.setattr(voters, "PROGRAM_END_REJECTION", Decimal(50))
    party = party_of(book, ALICE)
    before = dict(party.rejection)

    pass_measure(book, monkeypatch, TERM_START + timedelta(days=80), AUX, "0")

    served = voters.program_groups(AUX)
    assert served == (VoterGroup.WELFARE,)
    for group in VoterGroup:
        if group in served:
            assert party.rejection[group] >= before[group] + Decimal(40)
        else:
            assert party.rejection[group] < before[group] + Decimal(40)


def test_cutting_without_zeroing_or_ending_an_unnamed_program_adds_no_rejection(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    party = party_of(book, ALICE)
    before = dict(party.rejection)
    base = {
        "id": 1,
        "kind": AUX,
        "before": Decimal("0.005"),
        "sector": None,
        "segment": None,
        "proposer_id": 1,
        "term_start": TERM_START,
        "proposed": TERM_START,
    }

    # Zerar um programa sem nome e cortar um com nome sem zerar não somam rejeição
    state._end_program(book.state, Measure(**base, value=Decimal(0), name=None))
    state._end_program(book.state, Measure(**base, value=Decimal("0.005"), name=FAMILY))

    assert party.rejection == before


def test_ending_the_works_also_reaches_the_groups_that_receive_them():
    assert set(voters.program_groups(WORKS)) == {
        VoterGroup.ENTREPRENEURS,
        VoterGroup.FORMAL_WORKERS,
    }


# Retomada


def test_a_resumed_game_rebuilds_the_programs_and_old_events_have_none(
    book: GovernmentBook, engine, market, monkeypatch, stored
):
    govern(book, engine)
    effective = launch_family(book, monkeypatch)
    book.propose(
        ALICE, effective + timedelta(days=30), AUX, Decimal("0.02"), None, None, BRAZIL
    )

    resumed = GovernmentBook(
        settings(),
        engine,
        lambda *_: None,
        lambda *_: Decimal(0),
        lambda *_: None,
        SEED,
    )

    assert resumed.spending_timeline().latest_name(AUX) == FAMILY
    assert resumed.state.measures[1].name == FAMILY
    assert resumed.state.measures[2].renamed_from == FAMILY
    assert resumed.state.measures[2].name == BRAZIL

    # Um evento antigo, sem a chave do nome, volta como medida sem nome
    proposed = next(e for e in stored if e.payload.get("measure_id") == 1)
    proposed.payload.pop("name", None)
    proposed.payload.pop("renamed_from", None)
    legacy = GovernmentBook(
        settings(),
        engine,
        lambda *_: None,
        lambda *_: Decimal(0),
        lambda *_: None,
        SEED,
    )
    assert legacy.state.measures[1].name is None
    assert legacy.spending_timeline().latest_name(AUX) is None


def test_repropose_keeps_the_name(book: GovernmentBook, engine, market, monkeypatch):
    govern(book, engine)
    book.propose(ALICE, TERM_START, AUX, Decimal("0.02"), None, None, FAMILY)
    congress_says(monkeypatch, False)
    hold_vote_day(book, congress.next_vote_date(TERM_START))

    book.repropose(ALICE, TERM_START + timedelta(days=40), 1)

    assert book.state.measures[2].name == FAMILY
