"""Regras de jogo, datas e contrafactuais da expansão política."""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.core import repository
from backend.core.dto.events.equity import EquityEventDTO
from backend.core.dto.events.fixed_income import FixedIncomeEventDTO
from backend.core.dto.fixed_income_asset import FixedIncomeAssetDTO
from backend.core.dto.government import (
    CompanyProfileDTO,
    GovernmentActionDTO,
    GovernmentRulesDTO,
    GovernmentStateDTO,
    PartyDTO,
    PolicyDTO,
    ProductExposureDTO,
    SelicDecisionDTO,
    TermDTO,
)
from backend.core.enum import (
    AssetClass,
    EquityEventType,
    FixedIncomeEventType,
    FixedIncomeType,
    IndicatorSeries,
    RateIndexType,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.indicators import annual_index_rate, index_daily_rate
from backend.core.repository.series_version import using_simulation
from backend.core.runtime.user_manager import UserManager
from backend.core.utils import next_business_day
from backend.features.fixed_income.accrual import income_tax_rate, project
from backend.features.fixed_income.entities.fixed_income_position import (
    FixedIncomePosition,
)
from backend.features.fixed_income.fixed_broker import load_fixed_assets
from backend.features.government.economy import (
    campaign_gain,
    company_effect,
    macro_effect,
    state_on,
)
from backend.features.government.politics import (
    action,
    advance_day,
    ensure_ai,
    polls,
    propose,
    resolve_election,
)
from backend.features.variable_income.income_tax import assess
from backend.routes.simulation import CreateSimulationRequest
from tests.fakes import simulation_settings


def government(on=date(2003, 10, 7), **rules):
    return GovernmentStateDTO(
        rules=GovernmentRulesDTO(enabled=True, **rules),
        initialized_on=date(2003, 3, 31),
        processed_on=on,
        treasury=Decimal(1_000_000_000),
    )


def command(state, actor, **values):
    return action(
        state,
        actor,
        GovernmentActionDTO(**values),
        Decimal(100_000),
        {1, 2, 3, 4},
        0.15,
        0.03,
    )


def term(state, vice=None):
    state.term = TermDTO(
        party_id=1, president=1, vice=vice, start=date(2005, 1, 1), end=date(2009, 1, 1)
    )


def approved(kind, value, effective=date(2005, 4, 1), target="", id=1):
    return PolicyDTO(
        id=id,
        kind=kind,
        value=Decimal(str(value)),
        target=target,
        proposed_on=effective - timedelta(days=120),
        status="approved",
        effective_on=effective,
        position=4,
        author=1,
        party_id=1,
    )


def test_participation_and_invites_are_opt_in_and_cash_is_not_spent_on_affiliation():
    state = government()
    ensure_ai(state)
    assert (
        command(state, 1, action="found", name="Horizonte", acronym="HOR", amount="500")
        == {}
    )
    assert command(state, 2, action="join", party_id=1) == {}
    command(state, 1, action="nominate", member_id=2, vice_id=1)
    party = next(p for p in state.parties if p.id == 1)
    assert not party.candidate_accepted and not party.vice_accepted
    command(state, 2, action="decline_candidate")
    assert party.candidate is None and 2 in party.members
    command(state, 1, action="nominate", member_id=1, vice_id=2)
    command(state, 2, action="accept_vice")
    assert party.candidate_accepted and party.vice_accepted
    assert 3 not in party.members
    with pytest.raises(ConflictError):
        command(state, 3, action="propose", value="0.2")
    command(state, 2, action="leave")
    assert party.vice is None and "2" not in party.contributions


def test_campaign_spends_only_available_cash_and_has_diminishing_returns():
    state = government()
    command(state, 1, action="found", name="Horizonte", acronym="HOR", amount="500")
    command(state, 1, action="nominate", member_id=1)
    debit = advance_day(state, date(2003, 11, 1), 7, {1: Decimal("125.25")}, 0.03, 0)
    assert debit == {1: Decimal("125.25")}
    assert state.parties[0].spent == Decimal("125.25")
    assert campaign_gain(Decimal(16000), Decimal(8000)) < 2 * campaign_gain(
        Decimal(8000), Decimal(8000)
    )
    assert sum(polls(state, 2004, 7)[0].values()) == pytest.approx(100)


def test_ai_preserves_incumbent_program_when_humans_fill_election():
    state = government()
    ensure_ai(state)
    state.term = TermDTO(
        party_id=-1, president=-1, start=date(2005, 1, 1), end=date(2009, 1, 1)
    )
    incumbent = state.parties[0]
    for i in range(1, 4):
        state.parties.append(
            PartyDTO(
                id=i,
                name=str(i),
                acronym=f"P{i}",
                color=f"chart-{i}",
                founder=i,
                members=[i],
                candidate=i,
                candidate_accepted=True,
            )
        )
    ensure_ai(state)
    assert incumbent in state.parties
    assert not incumbent.campaign_active
    assert len(polls(state, 2008, 7)[0]) == 3


@pytest.mark.parametrize(
    "index,interest",
    [
        (RateIndexType.CDI, "1.05"),
        (RateIndexType.SELIC, "0.02"),
        (RateIndexType.IPCA, "0.04"),
    ],
)
def test_fixed_income_projection_live_accrual_and_rebuild_use_the_same_government(
    index, interest, monkeypatch, indicators
):
    buy, maturity = date(2005, 1, 3), date(2005, 2, 4)
    state = government(buy, manual_selic=True)
    state.selic_decisions = [SelicDecisionDTO(on=buy, rate=0.12, baseline=0.15)]
    state.policies = [approved("LCI_TAX", 0.1, effective=buy)]
    monkeypatch.setattr(repository.government, "_enabled", {11})
    monkeypatch.setattr(repository.government, "_states", {11: [state]})
    indicators(IndicatorSeries.CDI, {buy: Decimal("0.03")})
    indicators(IndicatorSeries.SELIC, {buy: Decimal("0.03")})
    indicators(IndicatorSeries.IPCA, {date(2005, 1, 1): Decimal("0.5")})
    asset = FixedIncomeAssetDTO(
        name="LCI Teste",
        issuer="Banco Teste",
        investment_type=FixedIncomeType.LCI,
        rate_index=index,
        interest_rate=Decimal(interest),
        maturity_date=maturity,
    )
    event = FixedIncomeEventDTO(
        simulation_id=11,
        user_id=1,
        event_date=buy,
        asset_id=1,
        event_type=FixedIncomeEventType.BUY,
        amount=Decimal(1000),
    )
    monkeypatch.setattr(
        repository.fixed_income, "get_events", lambda *_: [(asset, event)]
    )
    monkeypatch.setattr(UserManager, "get_user_id", lambda _: 1)
    with using_simulation(11):
        projection = project(asset, Decimal(1000), buy)
        live = FixedIncomePosition(
            asset=asset, total_applied=Decimal(1000), first_applied_date=buy
        )
        day = buy
        while day < maturity:
            day = next_business_day(day)
            live.accrue(day)
        rebuilt = load_fixed_assets(11, asset.asset_uuid, maturity)[asset.asset_uuid]
        assert live.current_value == rebuilt.current_value == projection.gross_amount
        assert live.net_redemption_value() == projection.net_amount
        assert projection.income_tax_rate == Decimal("0.1")


def test_announced_exemption_change_does_not_apply_before_its_effective_date(
    monkeypatch,
):
    state = government(date(2005, 4, 10))
    state.policies = [approved("STOCK_EXEMPTION", 0, effective=date(2005, 4, 20))]
    monkeypatch.setattr(repository.government, "_enabled", {11})
    monkeypatch.setattr(repository.government, "_states", {11: [state]})
    events = [
        EquityEventDTO(
            simulation_id=11,
            user_id=1,
            event_date=day,
            ticker="X3",
            event_type=kind,
            quantity=100,
            price=Decimal(price),
        )
        for day, kind, price in [
            (date(2005, 4, 11), EquityEventType.BUY, "10"),
            (date(2005, 4, 15), EquityEventType.SELL, "20"),
        ]
    ]
    assert assess(events, {"X3": AssetClass.STOCK}, date(2005, 4, 19), 11)[0].tax == 0
    assert assess(events, {"X3": AssetClass.STOCK}, date(2005, 4, 20), 11)[
        0
    ].tax == Decimal("150.00")


def test_election_and_inauguration_are_reproducible_and_preserve_accepted_ticket():
    state = government()
    command(state, 1, action="found", name="Horizonte", acronym="HOR")
    command(state, 2, action="join", party_id=1)
    command(state, 1, action="nominate", member_id=1, vice_id=2)
    command(state, 2, action="accept_vice")
    state.parties[0].support = 1e20
    clone = state.model_copy(deep=True)
    for s in (state, clone):
        advance_day(s, date(2004, 10, 7), 42, {}, 0.03, 0)
        assert s.pending_president == 1 and s.term is None
        command(s, 2, action="leave")
        advance_day(s, date(2005, 1, 1), 42, {}, 0.03, 0)
        assert s.term is not None
        assert s.term.president == 1 and s.term.vice == 2
        assert s.term.end == date(2009, 1, 1)
    assert state.model_dump() == clone.model_dump()


def test_runoff_without_remaining_candidates_becomes_neutral_without_crashing():
    state = government(date(2004, 10, 28))
    state.finalists = [1, 2]
    resolve_election(state, 2004, 2, 42)
    assert state.pending_president == -999
    advance_day(state, date(2005, 1, 1), 42, {}, 0.03, 0)
    assert state.term is not None
    assert state.term.neutral


def test_losing_or_unaffiliated_players_can_donate_in_runoff_only():
    state = government(date(2004, 10, 10))
    ensure_ai(state)
    state.finalists = [-1, -2]
    assert command(state, 4, action="donate", party_id=-1, amount="100") == {
        4: Decimal(100)
    }
    state.processed_on = date(2004, 11, 1)
    with pytest.raises(ConflictError):
        command(state, 4, action="donate", party_id=-1, amount="100")


def test_congress_reserves_budget_and_executes_after_ninety_calendar_days(monkeypatch):
    state = government(date(2005, 1, 15))
    term(state)
    propose(
        state,
        1,
        GovernmentActionDTO(
            action="propose", kind="PUBLIC_SPENDING", value=Decimal(100_000_000)
        ),
    )
    assert state.policies[0].status == "queued" and state.reserved_spending == 0
    monkeypatch.setattr("backend.features.government.politics.draw", lambda *_: 0)
    advance_day(state, date(2005, 1, 31), 7, {}, 0.03, 0)
    assert state.policies[0].effective_on == date(2005, 5, 1)
    assert state.reserved_spending == 100_000_000 and state.treasury == 1_000_000_000
    advance_day(state, date(2005, 5, 1), 7, {}, 0.03, 0)
    assert state.reserved_spending == 0 and state.treasury == 900_000_000
    assert macro_effect(state, date(2005, 5, 30)).inflation == 0
    assert macro_effect(state, date(2005, 5, 31)).inflation == 0.01


@pytest.mark.parametrize("vice,neutral", [(2, False), (None, True)])
def test_three_low_approval_months_impeach_and_keep_approved_measures(vice, neutral):
    state = government(date(2005, 1, 15))
    term(state, vice)
    state.policies = [approved("COMMON_TAX", 0.2)]
    propose(
        state,
        1,
        GovernmentActionDTO(action="propose", kind="FII_TAX", value=Decimal("0.25")),
    )
    # A fila é adicionada no terceiro mês, para testar sua retirada no impeachment.
    queued = state.policies.pop()
    for day in [date(2005, 1, 31), date(2005, 2, 28)]:
        advance_day(state, day, 7, {}, 0.20, 0)
        assert state.term is not None
        assert state.term.president == 1
    state.policies.append(queued)
    advance_day(state, date(2005, 3, 31), 7, {}, 0.20, 0)
    assert state.term is not None
    assert state.term.president == (vice or -999) and state.term.neutral == neutral
    assert state.policies[0].status == "approved" and queued.status == "withdrawn"
    if neutral:
        for day in [date(2005, 4, 30), date(2005, 5, 31), date(2005, 6, 30)]:
            advance_day(state, day, 7, {}, 0.20, 0)
        assert state.term.low_months == 0
        assert sum("Impeachment" in entry["text"] for entry in state.log) == 1


def test_selic_is_presidential_bounded_and_lagged():
    state = government(date(2005, 1, 1), manual_selic=True)
    term(state)
    with pytest.raises(ConflictError):
        command(state, 2, action="selic", value="0.15")
    with pytest.raises(ConflictError):
        command(state, 1, action="selic", value="0.10")
    command(state, 1, action="selic", value="0.145")
    with pytest.raises(ConflictError):
        command(state, 1, action="selic", value="0.145")
    assert macro_effect(state, date(2005, 3, 31)).inflation == 0
    assert macro_effect(state, date(2005, 4, 1)).inflation == pytest.approx(0.00125)
    assert macro_effect(state, date(2005, 1, 1)).selic == pytest.approx(-0.005)


def test_spending_has_approved_delay_half_life_and_autonomous_monetary_response():
    state = government()
    state.policies = [approved("PUBLIC_SPENDING", 100_000_000)]
    start = date(2005, 5, 1)
    assert macro_effect(state, start).inflation == pytest.approx(0.01)
    assert macro_effect(state, start + timedelta(days=365)).inflation == pytest.approx(
        0.005
    )
    assert macro_effect(state, start).selic == pytest.approx(0.015)


def test_autonomous_selic_responds_to_the_bounded_inflation_visible_in_the_game():
    state = government(spending_inflation=0.05)
    state.policies = [
        approved("PUBLIC_SPENDING", 100_000_000, id=i) for i in range(1, 51)
    ]
    effect = macro_effect(state, date(2005, 5, 1))
    assert effect.inflation == 0.5
    assert effect.selic == 1.5 * effect.inflation


def test_product_tariff_benefits_producer_and_hurts_importer_without_daily_compounding():
    state = government(
        companies=[
            CompanyProfileDTO(
                ticker="PROD3",
                exposures=[
                    ProductExposureDTO(
                        product="STEEL", revenue_share=0.65, imported_cost_share=0.08
                    )
                ],
            ),
            CompanyProfileDTO(
                ticker="USER3",
                exposures=[
                    ProductExposureDTO(
                        product="STEEL", revenue_share=0, imported_cost_share=0.35
                    )
                ],
            ),
        ]
    )
    state.policies = [approved("PRODUCT_TARIFF", 0.1, target="STEEL")]
    assert company_effect(state, "PROD3", date(2005, 3, 31))[0] == 1
    assert company_effect(state, "PROD3", date(2005, 4, 1))[0] > 1
    assert company_effect(state, "USER3", date(2005, 4, 1))[0] < 1
    assert company_effect(state, "USER3", date(2005, 4, 1)) == company_effect(
        state, "USER3", date(2005, 4, 2)
    )
    assert company_effect(state, "UNKNOWN3", date(2005, 4, 1))[0] == 1


def test_historical_policy_does_not_leak_into_another_match_or_prior_dates(
    monkeypatch, indicators
):
    state = government(manual_selic=True)
    state.processed_on = date(2005, 4, 1)
    state.selic_decisions = [
        SelicDecisionDTO(on=date(2005, 4, 1), rate=0.10, baseline=0.15)
    ]
    state.policies = [approved("LCI_TAX", 0.1), approved("FIXED_TAX_SHIFT", 0.05, id=2)]
    monkeypatch.setattr(repository.government, "_enabled", {11})
    monkeypatch.setattr(repository.government, "_states", {11: [state]})
    indicators(IndicatorSeries.CDI, {date(2005, 4, 1): Decimal("0.05")})
    with using_simulation(11):
        assert annual_index_rate(IndicatorSeries.CDI, date(2005, 4, 1)) == Decimal(
            "0.1"
        )
        rate = index_daily_rate(IndicatorSeries.CDI, date(2005, 4, 1))
        assert rate is not None
        assert (1 + rate) ** 252 - 1 == pytest.approx(Decimal("0.1"))
        assert income_tax_rate(FixedIncomeType.LCI, 100, date(2005, 4, 1)) == Decimal(
            "0.1"
        )
        assert income_tax_rate(FixedIncomeType.CDB, 100, date(2005, 4, 1)) == Decimal(
            "0.275"
        )
    with using_simulation(12):
        assert annual_index_rate(IndicatorSeries.CDI, date(2005, 4, 1)) != Decimal(
            "0.1"
        )
        assert income_tax_rate(FixedIncomeType.LCI, 100, date(2005, 4, 1)) == 0
    assert state_on(11, date(2005, 3, 31)) is None


def test_tax_rates_follow_sale_date_and_exemption_respects_policy(monkeypatch):

    state = government()
    state.policies = [approved("COMMON_TAX", 0.3), approved("STOCK_EXEMPTION", 0, id=2)]
    monkeypatch.setattr(repository.government, "_enabled", {11})
    monkeypatch.setattr(repository.government, "_states", {11: [state]})
    events = [
        EquityEventDTO(
            simulation_id=11,
            user_id=1,
            event_date=d,
            ticker="X3",
            event_type=k,
            quantity=100,
            price=Decimal(p),
        )
        for d, k, p in [
            (date(2005, 3, 1), EquityEventType.BUY, "10"),
            (date(2005, 3, 10), EquityEventType.SELL, "20"),
            (date(2005, 4, 1), EquityEventType.BUY, "10"),
            (date(2005, 4, 10), EquityEventType.SELL, "20"),
        ]
    ]
    months = assess(events, {"X3": AssetClass.STOCK}, date(2005, 4, 30), 11)
    assert months[0].tax == 0 and months[1].tax == Decimal("300.00")
    assert assess(events, {"X3": AssetClass.STOCK}, date(2005, 4, 30), 12)[-1].tax == 0


def test_rules_reject_duplicate_company_exposures():
    with pytest.raises(ValidationError):
        GovernmentRulesDTO(
            companies=[
                CompanyProfileDTO(
                    ticker="X3",
                    exposures=[
                        ProductExposureDTO(
                            product="STEEL", revenue_share=0.1, imported_cost_share=0.1
                        )
                    ]
                    * 2,
                )
            ]
        )


def test_government_needs_five_years_and_party_victory_has_one_unambiguous_ranking():
    body = simulation_settings().model_dump()
    body.update(
        start_date=date(2000, 2, 29),
        end_date=date(2005, 2, 28),
        government={"enabled": True},
    )
    assert CreateSimulationRequest.model_validate(body).government.enabled
    with pytest.raises(ValidationError, match="pelo menos 5 anos"):
        CreateSimulationRequest.model_validate({**body, "end_date": date(2005, 2, 27)})
    with pytest.raises(ValidationError, match="jogadores individuais"):
        CreateSimulationRequest.model_validate(
            {
                **body,
                "government": {"enabled": True, "ranking": "parties"},
                "player_grouping": "TEAMS",
            }
        )


def test_ai_selic_obeys_the_same_meeting_interval_and_limit():
    state = government(date(2005, 1, 1), manual_selic=True)
    ensure_ai(state)
    state.term = TermDTO(
        party_id=-1, president=-1, start=date(2005, 1, 1), end=date(2009, 1, 1)
    )
    advance_day(state, date(2005, 1, 1), 7, {}, 0.10, 0, 0.15)
    assert state.selic_decisions[-1].rate == pytest.approx(0.1575)
    advance_day(state, date(2005, 2, 14), 7, {}, 0.10, 0, 0.15)
    assert len(state.selic_decisions) == 1
    advance_day(state, date(2005, 2, 15), 7, {}, 0.10, 0, 0.15)
    assert len(state.selic_decisions) == 2


def test_re_election_limit_applies_to_the_person_and_ai_replaces_its_candidate():
    state = government()
    ensure_ai(state)
    state.terms_won = {"1": 2, "-1": 2}
    command(state, 1, action="found", name="Horizonte", acronym="HOR")
    with pytest.raises(ConflictError, match="dois mandatos"):
        command(state, 1, action="nominate", member_id=1)
    ensure_ai(state)
    assert state.parties[0].candidate != -1
    assert len(polls(state, 2008, 7)[0]) == 3
