"""Medidas de gasto no livro do governo: proposta, voto, vigência, retomada, prévia, painel, reação dos grupos e promessas."""

# As fixtures do livro vêm do módulo dos testes dele e entram como parâmetro de cada teste
# ruff: noqa: F401, F811

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from backend.core import repository
from backend.core.dto.promises import PromiseRequest
from backend.core.enum import EffectPhase, MeasureKind, MeasureStatus, VoterGroup
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    UnprocessableEntityError,
)
from backend.features.government import (
    approval as approval_rules,
)
from backend.features.government import (
    budget_panel,
    governance,
    promises,
    spending,
    spending_effects,
    voters,
)
from backend.features.government.governance import build_governance
from backend.features.government.government_book import GovernmentBook
from tests.test_government_book import (
    ALICE,
    CAMPAIGN_OPEN,
    FIRST_VOTE,
    RED,
    SEED,
    TERM_START,
    USERS,
    book,
    congress_says,
    engine,
    found,
    govern,
    headlines,
    market,
    notices,
    office,
    settings,
    stored,
)

AUX = MeasureKind.WELFARE_SPENDING
SERVANTS = MeasureKind.SERVANT_RAISE
RETIREES = MeasureKind.RETIREE_RAISE
WORKS = MeasureKind.PUBLIC_WORKS


@pytest.fixture(autouse=True)
def no_frozen_portfolio(monkeypatch: pytest.MonkeyPatch) -> None:
    """O motor de teste não monta carteira; o painel aqui é só dos gastos."""
    monkeypatch.setattr(governance, "_portfolio", lambda *_: None)


def propose(book: GovernmentBook, kind: MeasureKind, value: str) -> None:
    book.propose(ALICE, TERM_START, kind, Decimal(value), None, None)


def approve_first(book: GovernmentBook, monkeypatch) -> date:
    """Aprova a primeira medida da fila no voto de janeiro e devolve o dia em que ela vale."""
    congress_says(monkeypatch, True)
    book.on_tick(USERS, FIRST_VOTE, False)
    effective = book.state.measures[1].effective
    assert effective is not None
    return effective


# Validação


def test_the_measures_start_from_the_default_values(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    for kind in spending.KINDS:
        assert book.latest_value(kind) == spending.DEFAULTS[kind]
        assert book.value_in_force(kind, TERM_START) == spending.DEFAULTS[kind]


def test_a_spending_measure_keeps_the_value_it_replaces(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    propose(book, AUX, "0.02")

    [queued] = book.state.measures.values()
    assert (queued.value, queued.before) == (Decimal("0.02"), Decimal("0.015"))
    assert queued.status is MeasureStatus.QUEUED


@pytest.mark.parametrize(
    ("kind", "value"),
    [
        (AUX, "0.021"),
        (AUX, "0.009"),
        (WORKS, "0.0121"),
        (SERVANTS, "0.0301"),
        (RETIREES, "0.04"),
    ],
)
def test_a_measure_moves_one_reference_step_at_most(
    book: GovernmentBook, engine, market, kind, value
):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        propose(book, kind, value)


@pytest.mark.parametrize("kind", [SERVANTS, RETIREES])
def test_the_raises_never_go_below_zero(book: GovernmentBook, engine, market, kind):
    govern(book, engine)

    with pytest.raises(UnprocessableEntityError):
        propose(book, kind, "-0.01")


def test_the_ceiling_of_the_value_in_force_is_respected(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    monkeypatch.setattr(spending, "LIMITS", {**spending.LIMITS, AUX: Decimal("0.02")})
    monkeypatch.setattr(promises.spending, "LIMITS", spending.LIMITS)

    propose(book, AUX, "0.02")
    book.withdraw(ALICE, TERM_START, 1)
    with pytest.raises(UnprocessableEntityError):
        propose(book, AUX, "0.025")


def test_the_same_value_changes_nothing(book: GovernmentBook, engine, market):
    govern(book, engine)

    with pytest.raises(ConflictError):
        propose(book, AUX, "0.015")


def test_one_measure_of_each_kind_waits_in_the_queue(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    propose(book, AUX, "0.02")

    with pytest.raises(ConflictError):
        propose(book, AUX, "0.01")
    propose(book, WORKS, "0.012")

    assert len(book.state.measures) == 2


# Voto e vigência


def test_an_approved_spending_measure_binds_ninety_days_after_the_vote(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book, AUX, "0.02")

    effective = approve_first(book, monkeypatch)

    assert effective == FIRST_VOTE + timedelta(days=90)
    assert book.spending_timeline().value_on(
        AUX, effective - timedelta(days=1)
    ) == Decimal("0.015")
    assert book.spending_timeline().value_on(AUX, effective) == Decimal("0.02")
    assert book.latest_value(AUX) == Decimal("0.02")
    assert book.spending_on(effective) == spending.BASE_SPENDING + Decimal("0.005")


def test_a_rejected_spending_measure_changes_nothing(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book, AUX, "0.02")
    congress_says(monkeypatch, False)

    book.on_tick(USERS, FIRST_VOTE, False)

    assert book.state.measures[1].status is MeasureStatus.REJECTED
    assert book.latest_value(AUX) == Decimal("0.015")
    assert book.economy().effects == ()


def test_spending_never_touches_the_tax_policy(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    policy = book.latest_policy()
    propose(book, AUX, "0.02")

    effective = approve_first(book, monkeypatch)

    assert book.latest_policy() == policy
    assert book.policy(effective) == policy


def test_the_approved_measure_becomes_an_effect_that_starts_on_the_effective_day(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book, AUX, "0.02")

    effective = approve_first(book, monkeypatch)

    [effect] = book.economy().effects
    assert (effect.kind, effect.start) == (AUX, effective)
    assert effect.steps == pytest.approx(1.0)
    assert book.economy().inflation_points(effective) == 0
    assert book.economy().inflation_points(effective + timedelta(days=183)) > 0


def test_a_resumed_game_rebuilds_the_same_effects_from_the_events(
    book: GovernmentBook,
    engine,
    market,
    monkeypatch,
    stored,
    notices,
    office,
    headlines,
):
    govern(book, engine)
    propose(book, AUX, "0.02")
    propose(book, SERVANTS, "0.03")
    effective = approve_first(book, monkeypatch)
    later = effective + timedelta(days=400)

    resumed = GovernmentBook(settings(), engine, lambda *_: None, lambda *_: None, SEED)

    assert resumed.economy().effects == book.economy().effects
    assert len(resumed.economy().effects) == 2
    for day in (effective, effective + timedelta(days=100), later):
        assert resumed.economy().inflation_points(day) == pytest.approx(
            book.economy().inflation_points(day)
        )
        assert resumed.spending_on(day) == book.spending_on(day)
    assert resumed.latest_value(AUX) == Decimal("0.02")


def test_the_book_registers_the_economy_as_the_adjustment_of_the_game(
    book: GovernmentBook, engine, market
):
    assert repository.economic._adjustments[settings().id] is book.economy()


# Prévia e orçamento


def test_the_preview_of_a_raise_in_spending_reads_the_cost_and_the_inflation(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    preview = book.preview(ALICE, TERM_START, AUX, Decimal("0.02"), None, None)

    assert preview.budget.spending_change == Decimal("0.005")
    assert preview.budget.revenue_change == 0
    assert preview.budget.tax_name == ""
    assert preview.budget.spending_after == preview.budget.spending_before + Decimal(
        "0.005"
    )
    assert preview.budget.result_after == preview.budget.result_before - Decimal(
        "0.005"
    )
    assert preview.budget.debt_after > preview.budget.debt_before
    assert preview.inflation is not None
    assert preview.inflation.peak == Decimal("0.25")
    assert preview.inflation.peak_month == 6
    assert preview.inflation.ipca_after > preview.inflation.ipca_before
    assert preview.inflation.selic_after - preview.inflation.selic_before == Decimal(
        "0.00375"
    )
    assert preview.inflation.stocks < 0
    assert preview.inflation.curve[0].points == 0
    assert preview.inflation.curve[6].points == Decimal("0.25")
    assert preview.inflation.curve[24].points < preview.inflation.curve[6].points


def test_the_preview_of_a_cut_lowers_the_cost_and_the_inflation(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    preview = book.preview(ALICE, TERM_START, AUX, Decimal("0.01"), None, None)

    assert preview.budget.spending_change == Decimal("-0.005")
    assert preview.budget.result_after > preview.budget.result_before
    assert preview.budget.debt_after < preview.budget.debt_before
    assert preview.inflation is not None
    assert preview.inflation.peak == Decimal("-0.25")
    assert preview.inflation.ipca_after < preview.inflation.ipca_before
    assert preview.inflation.stocks > 0


def test_works_also_add_to_the_growth_in_the_preview(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    works = book.preview(ALICE, TERM_START, WORKS, Decimal("0.012"), None, None)
    aid = book.preview(ALICE, TERM_START, AUX, Decimal("0.02"), None, None)

    assert works.inflation is not None and aid.inflation is not None
    assert works.inflation.growth == Decimal("0.6")
    assert aid.inflation.growth == 0


def test_a_tax_measure_has_no_inflation_in_the_preview(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    preview = book.preview(
        ALICE, TERM_START, MeasureKind.STOCK_PROFIT_RATE, Decimal("0.05"), None, None
    )

    assert preview.inflation is None
    assert preview.budget.spending_change == 0
    assert preview.budget.spending_before == preview.budget.spending_after


def test_a_raise_costs_the_folha_and_only_in_the_next_january(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    preview = book.preview(ALICE, TERM_START, SERVANTS, Decimal("0.03"), None, None)

    assert preview.budget.spending_change == spending.RAISE_BASES[SERVANTS] * Decimal(
        "0.03"
    )
    assert preview.budget.debt_after > preview.budget.debt_before


def test_the_queue_result_adds_the_tax_revenue_and_subtracts_the_spending(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    propose(book, AUX, "0.02")
    propose(book, WORKS, "0.012")

    queue = budget_panel.queue_budget(
        book.budget(),
        book.latest_policy(),
        [m for m in book.state.measures.values() if m.status is MeasureStatus.QUEUED],
        TERM_START,
    )

    assert queue.total == Decimal("-0.010")
    assert queue.result_if_passes == queue.result_now + queue.total


def test_the_budget_spends_the_measures_from_the_day_they_bind(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book, AUX, "0.02")
    effective = approve_first(book, monkeypatch)

    month_before = book.budget().latest(effective - timedelta(days=40))
    after = book.budget().latest(effective + timedelta(days=70))

    assert month_before.spending == spending.BASE_SPENDING
    assert after.spending == spending.BASE_SPENDING + Decimal("0.005")


# Reação dos grupos


@pytest.mark.parametrize(
    ("kind", "reactions"),
    [
        (AUX, ["-1.25", "-0.65", "0.2", "0.25", "-0.3", "2.25"]),
        (SERVANTS, ["-0.5", "-0.5", "0", "1.5", "0.3", "0.3"]),
        (RETIREES, ["-0.5", "-0.25", "0.25", "0.2", "1.1", "0.5"]),
        (WORKS, ["0.3", "1.5", "1", "0", "-0.2", "0.2"]),
    ],
)
def test_the_reaction_of_a_step_follows_the_numbers_of_the_design(kind, reactions):
    before = spending.DEFAULTS[kind]
    value = before + spending.STEPS[kind]

    got = [voters.measure_reaction(group, kind, value, before) for group in VoterGroup]

    assert got == [Decimal(r) for r in reactions]


def test_a_cut_reverses_the_reaction_of_every_group():
    before = spending.DEFAULTS[AUX]

    up = voters.measure_reaction(
        VoterGroup.WELFARE, AUX, before + spending.STEPS[AUX], before
    )
    down = voters.measure_reaction(
        VoterGroup.WELFARE, AUX, before - spending.STEPS[AUX], before
    )

    assert down == -up


def test_every_group_has_a_spending_measure_that_pleases_it():
    pleased = {
        group
        for kind in spending.KINDS
        for group in VoterGroup
        if voters.measure_reaction(
            group,
            kind,
            spending.DEFAULTS[kind] + spending.STEPS[kind],
            spending.DEFAULTS[kind],
        )
        > 0
    }

    assert pleased == set(VoterGroup)


def test_the_preview_lists_the_reaction_of_the_six_groups(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    preview = book.preview(ALICE, TERM_START, AUX, Decimal("0.02"), None, None)

    by_group = {r.group: r.points for r in preview.reactions}
    assert set(by_group) == set(VoterGroup)
    assert by_group[VoterGroup.WELFARE] > 0 > by_group[VoterGroup.INVESTORS]
    assert by_group[VoterGroup.WELFARE] == approval_rules.MEASURE_POINTS * Decimal(
        "2.25"
    )


# Painel do governo


def test_the_tax_card_keeps_only_taxes_and_the_spending_card_has_the_four_measures(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    propose(book, AUX, "0.02")

    panel = build_governance(book, engine, USERS, ALICE, TERM_START)

    assert not any(row.kind.is_spending for row in panel.taxes)
    assert [row.kind for row in panel.spending.rows] == list(spending.KINDS)
    aid = next(row for row in panel.spending.rows if row.kind is AUX)
    assert aid.value == Decimal("0.015")
    assert aid.since is None
    assert aid.step == Decimal("0.005")
    assert aid.pending is not None and aid.pending.value == Decimal("0.02")
    assert aid.phase is None and aid.curve == []
    assert panel.spending.total == spending.BASE_SPENDING
    assert panel.spending.total_difference == 0
    assert panel.spending.rest == spending.REST_SPENDING


def test_the_queue_shows_the_inflation_and_the_result_of_each_measure(
    book: GovernmentBook, engine, market
):
    govern(book, engine)
    propose(book, AUX, "0.02")
    propose(book, WORKS, "0.002")

    panel = build_governance(book, engine, USERS, ALICE, TERM_START)

    by_kind = {m.kind: m for m in panel.queue}
    assert by_kind[AUX].inflation_effect == Decimal("0.25")
    assert by_kind[AUX].budget_effect == Decimal("-0.005")
    # Cortar obras tira inflação e melhora o resultado
    assert by_kind[WORKS].inflation_effect == Decimal("-0.15")
    assert by_kind[WORKS].budget_effect == Decimal("0.005")


def test_the_card_shows_the_effect_of_an_approved_measure_after_it_binds(
    book: GovernmentBook, engine, market, monkeypatch
):
    govern(book, engine)
    propose(book, AUX, "0.02")
    effective = approve_first(book, monkeypatch)
    day = effective + timedelta(days=100)

    panel = build_governance(book, engine, USERS, ALICE, day)

    aid = next(row for row in panel.spending.rows if row.kind is AUX)
    assert aid.value == Decimal("0.02")
    assert aid.since == effective
    assert aid.phase is EffectPhase.RISING
    assert aid.inflation > 0
    assert aid.elapsed_months == 3
    assert panel.spending.total_difference == Decimal("0.005")
    assert panel.spending.inflation == aid.inflation


# Promessas


def test_every_spending_measure_can_be_promised_from_its_value_in_force(
    book: GovernmentBook, engine, market
):
    govern(book, engine)

    for kind in spending.KINDS:
        assert promises.promisable(kind)
        assert book.promise_baseline(kind, TERM_START) == spending.DEFAULTS[kind]


def test_the_computer_promises_stay_within_the_step_and_the_limit_of_the_measure():
    baselines = {kind: spending.DEFAULTS[kind] for kind in spending.KINDS}
    radar = {value: Decimal(1) for value in promises.voters.VoterValue}

    picks = promises.computer_picks(radar, baselines, date(2020, 11, 1))

    for pick in picks:
        assert pick.target is not None and pick.baseline is not None
        assert (
            abs(pick.target - pick.baseline) == promises.voters.EFFECT_STEPS[pick.kind]
        )
        assert 0 <= pick.target <= spending.LIMITS[pick.kind]


def test_the_promise_limit_is_per_measure():
    assert promises.limit_of(MeasureKind.STOCK_EXEMPTION) is None
    assert promises.limit_of(MeasureKind.STOCK_PROFIT_RATE) == Decimal(1)
    assert promises.limit_of(AUX) == spending.LIMITS[AUX]
    assert promises.limit_of(SERVANTS) == spending.LIMITS[SERVANTS]


def test_a_promise_above_the_limit_of_the_measure_is_refused(
    book: GovernmentBook, engine, market
):
    found(book, ALICE, "AAA", RED)
    over = spending.LIMITS[AUX] + Decimal("0.01")

    with pytest.raises(UnprocessableEntityError):
        book.draft_promises(
            ALICE, CAMPAIGN_OPEN, [PromiseRequest(kind=AUX, target=over)]
        )

    [kept] = book.draft_promises(
        ALICE, CAMPAIGN_OPEN, [PromiseRequest(kind=AUX, target=Decimal("0.03"))]
    )
    assert (kept.target, kept.baseline) == (Decimal("0.03"), Decimal("0.015"))
