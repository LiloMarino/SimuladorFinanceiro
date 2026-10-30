"""A página Governo: impostos em vigor, aprovação, fila do Congresso e a carteira do presidente."""

from collections.abc import Callable
from datetime import date
from decimal import Decimal

from backend.core.dto.government import (
    ApprovalDTO,
    ApprovalFactorDTO,
    ApprovalPointDTO,
    ClosingDTO,
    FrozenPortfolioDTO,
    FrozenSliceDTO,
    GovernmentPanelDTO,
    GroupApprovalDTO,
    ImpeachmentDTO,
    InterestDTO,
    MeasureDTO,
    SectorMeasureDTO,
    SectorOptionDTO,
    SegmentOptionDTO,
    TaxRowDTO,
    UpcomingEffectDTO,
    VoteDTO,
)
from backend.core.dto.portfolio import PortfolioDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import GroupVerdict, MeasureKind, MeasureStatus, VoterGroup
from backend.features.government import approval as approval_rules
from backend.features.government import (
    budget_panel,
    congress,
    house_panel,
    promises,
    spending_panel,
    voters,
)
from backend.features.government import measures as rules
from backend.features.government.government_book import GovernmentBook
from backend.features.government.panel import build_term
from backend.features.government.promise_panel import build_term_promises
from backend.features.government.state import (
    NEUTRAL_SATISFACTION,
    VIGENCE_DAYS,
    Measure,
)
from backend.features.simulation.simulation_engine import SimulationEngine


def build_governance(
    book: GovernmentBook,
    engine: SimulationEngine,
    users: list[UserDTO],
    viewer: UserDTO,
    today: date,
) -> GovernmentPanelDTO:
    state = book.state
    people = {user.id: user for user in users}
    term = state.term
    president = book.president()
    is_president = president is not None and president.id == viewer.id
    current = book.approval(today)
    measures = sorted(state.measures.values(), key=lambda m: m.id)

    # As medidas que a chapa que governa prometeu: ganham a marca de promessa
    promised = {p.key for p in term.promises} if term is not None else set()

    def dto(measure: Measure) -> MeasureDTO:
        return _measure(
            measure,
            _nickname(people, measure.proposer_id) or book.proposer_name(measure),
            today,
            house_panel.vote_dto(book, viewer, today, measure),
            is_president,
            measures,
            promised,
            budget_panel.result_change(book.policy_before(measure), measure),
            spending_panel.peak_inflation(measure),
        )

    pending = [
        m
        for m in measures
        if m.status is MeasureStatus.QUEUED
        or (m.status is MeasureStatus.APPROVED and _waiting(m, today))
    ]
    rejected = [
        m
        for m in reversed(measures)
        if m.status is MeasureStatus.REJECTED
        and book.is_current(m)
        and not _retried(m, measures)
    ]
    policy = book.policy(today)
    end = book.term_end()
    impeachment = state.impeachments[-1] if state.impeachments else None
    # O voto que aprovou o impeachment mais recente
    ousting = next((v for v in reversed(state.impeachment_votes) if v.approved), None)

    return GovernmentPanelDTO(
        today=today,
        term=build_term(term, state, people),
        computer_until_inauguration=term is None,
        is_president=is_president,
        term_end=end,
        next_election=book.cycle().first_round,
        congress=house_panel.build_congress(book, viewer, today, people),
        approval=_approval(book, current, viewer, today),
        taxes=[
            TaxRowDTO(
                kind=kind,
                value=(
                    policy.fixed_income_floor
                    if kind is MeasureKind.FIXED_INCOME_TABLE
                    else rules.general_value(policy, kind) or Decimal(0)
                ),
                top_value=(
                    policy.fixed_income_top_rate
                    if kind is MeasureKind.FIXED_INCOME_TABLE
                    else None
                ),
                pending=next(
                    (dto(m) for m in reversed(pending) if m.kind is kind), None
                ),
                promised=any(key[0] is kind for key in promised),
            )
            for kind in promises.TAX_KINDS
        ],
        spending=spending_panel.spending_card(
            book.spending_timeline(),
            book.economy(),
            book.budget().latest(today).gdp,
            today,
            {m.kind: dto(m) for m in pending if m.kind.is_spending},
            {key[0] for key in promised},
        ),
        sector_measures=[
            SectorMeasureDTO(measure=dto(m), assets=len(book.tickers(m)))
            for m in reversed(measures)
            if m.kind.is_sector and m.status is MeasureStatus.APPROVED
        ],
        queue=[dto(m) for m in [*pending, *rejected]],
        queue_budget=budget_panel.queue_budget(
            book.budget(),
            book.latest_policy(),
            [m for m in pending if m.status is MeasureStatus.QUEUED],
            today,
        ),
        next_vote=congress.next_vote_date(today),
        portfolio=(
            _portfolio(engine, president, end, pending, today)
            if president is not None and end is not None
            else None
        ),
        sectors=sector_options(engine),
        last_impeachment=(
            ImpeachmentDTO(
                date=impeachment.day,
                president=_nickname(people, impeachment.president_id),
                successor=_nickname(people, impeachment.successor_id),
                months=approval_rules.IMPEACHMENT_MONTHS,
                floor=approval_rules.FLOOR,
                yes=ousting.tally.yes if ousting else 0,
                no=ousting.tally.no if ousting else 0,
            )
            if impeachment
            else None
        ),
        vigence_days=VIGENCE_DAYS,
        promises=build_term_promises(book, viewer, today),
    )


def _nickname(people: dict[int, UserDTO], user_id: int | None) -> str | None:
    user = people.get(user_id) if user_id is not None else None
    return user.nickname if user else None


def _waiting(measure: Measure, today: date) -> bool:
    return measure.effective is not None and measure.effective > today


def _retried(rejected: Measure, measures: list[Measure]) -> bool:
    """A medida rejeitada que já voltou à fila (ou passou) não pede outra tentativa."""
    return any(
        m.id > rejected.id
        and (m.kind, m.sector, m.segment)
        == (rejected.kind, rejected.sector, rejected.segment)
        and m.status in (MeasureStatus.QUEUED, MeasureStatus.APPROVED)
        for m in measures
    )


def _measure(
    measure: Measure,
    proposer: str | None,
    today: date,
    vote: VoteDTO | None,
    is_president: bool,
    measures: list[Measure],
    promised: set[tuple[MeasureKind, str | None, str | None]],
    budget_effect: Decimal,
    inflation_effect: Decimal,
) -> MeasureDTO:
    queued = measure.status is MeasureStatus.QUEUED
    waiting = measure.status is MeasureStatus.APPROVED and _waiting(measure, today)
    days_left = (
        (measure.effective - today).days if waiting and measure.effective else None
    )
    return MeasureDTO(
        id=measure.id,
        kind=measure.kind,
        title=rules.title(measure),
        sector=measure.sector,
        segment=measure.segment,
        value=measure.value,
        proposer=proposer or "?",
        proposed=measure.proposed,
        status=measure.status,
        vote_date=congress.next_vote_date(today) if queued else measure.decided,
        vote=vote,
        effective=measure.effective,
        waiting_days=VIGENCE_DAYS - days_left if days_left is not None else None,
        days_left=days_left,
        impact=approval_rules.measure_impact(measure),
        budget_effect=budget_effect,
        inflation_effect=inflation_effect,
        fulfills_promise=(
            measure.status in (MeasureStatus.QUEUED, MeasureStatus.APPROVED)
            and (measure.kind, measure.sector, measure.segment) in promised
        ),
        can_withdraw=is_president and queued,
        can_repropose=(
            is_president
            and measure.status is MeasureStatus.REJECTED
            and not _retried(measure, measures)
        ),
    )


def _approval(
    book: GovernmentBook,
    current: approval_rules.Approval | None,
    viewer: UserDTO,
    today: date,
) -> ApprovalDTO | None:
    term = book.state.term
    if current is None or term is None:
        return None
    measured = book.state.approvals
    # A linha parte da posse e segue um ponto por fechamento de mês
    start = {g: term.satisfaction.get(g, NEUTRAL_SATISFACTION) for g in VoterGroup}
    series = [(term.start, start), *((p.day, p.satisfaction) for p in measured)]
    history = [
        ApprovalPointDTO(
            date=day, value=approval_rules.rounded(approval_rules.overall(values))
        )
        for day, values in series
    ]
    before = series[-2][1] if len(series) > 1 else None
    return ApprovalDTO(
        value=current.value,
        previous=(
            approval_rules.rounded(approval_rules.overall(before))
            if before is not None
            else None
        ),
        target=current.target,
        history=history,
        groups=[
            _group_approval(group, current, series) for group in _groups_by_weight()
        ],
        upcoming=[
            UpcomingEffectDTO(
                measure_id=m.id,
                description=(
                    f"A caminho: {rules.title(m)}, aprovada em "
                    f"{rules.short_date(m.decided or today)}, pesa quando valer"
                ),
                effective=m.effective or today,
                impact=approval_rules.measure_impact(m),
            )
            for m in current.upcoming
        ],
        closes_on=congress.next_vote_date(today),
        reproves_below=int(voters.REPROVES_BELOW),
        approves_above=int(voters.APPROVES_ABOVE),
        floor=approval_rules.FLOOR,
        low_streak=book.state.low_streak,
        impeachment_months=approval_rules.IMPEACHMENT_MONTHS,
        grace_until=approval_rules.grace_end(term),
        in_grace=approval_rules.in_grace(term, today.replace(day=1)),
        closing=_closing(book, viewer),
    )


def _groups_by_weight() -> list[VoterGroup]:
    return sorted(VoterGroup, key=lambda g: voters.WEIGHTS[g], reverse=True)


def _group_approval(
    group: VoterGroup,
    current: approval_rules.Approval,
    series: list[tuple[date, dict[VoterGroup, Decimal]]],
) -> GroupApprovalDTO:
    target = current.targets[group]
    satisfaction = current.satisfaction[group]
    return GroupApprovalDTO(
        group=group,
        weight=voters.WEIGHTS[group],
        readings=list(voters.READINGS[group]),
        satisfaction=approval_rules.rounded(satisfaction),
        target=approval_rules.rounded(target.target),
        verdict=voters.month_verdict(satisfaction),
        previous=(
            approval_rules.rounded(series[-2][1][group]) if len(series) > 1 else None
        ),
        history=[
            ApprovalPointDTO(date=day, value=approval_rules.rounded(values[group]))
            for day, values in series
        ],
        factors=[
            ApprovalFactorDTO(
                kind=f.kind,
                points=f.points.quantize(Decimal("0.1")),
                description=f.description,
                measure_id=f.measure_id,
            )
            for f in target.factors
        ],
    )


def _closing(book: GovernmentBook, viewer: UserDTO) -> ClosingDTO | None:
    """O que o último fechamento fez com o partido do presidente, para os filiados dele."""
    state = book.state
    term = state.term
    party = state.parties.get(term.party_id) if term and term.party_id else None
    if party is None or viewer.id not in party.members or not state.approvals:
        return None
    last = state.approvals[-1]
    verdicts = {g: voters.month_verdict(v) for g, v in last.satisfaction.items()}

    def groups(wanted: GroupVerdict) -> list[VoterGroup]:
        return [g for g in _groups_by_weight() if verdicts[g] is wanted]

    return ClosingDTO(
        month=last.day,
        party_abbr=party.abbr,
        approved=groups(GroupVerdict.APPROVES),
        reproved=groups(GroupVerdict.REPROVES),
        neutral=groups(GroupVerdict.NEUTRAL),
    )


def _portfolio(
    engine: SimulationEngine,
    president: UserDTO,
    end: date,
    pending: list[Measure],
    today: date,
) -> FrozenPortfolioDTO:
    portfolio = engine.get_portfolio(president.client_id)
    total = (
        portfolio.cash + portfolio.variable_income_value + portfolio.fixed_income_value
    )

    def share(value: Decimal) -> Decimal:
        return value / total if total > 0 else Decimal(0)

    held = {p.ticker for p in portfolio.variable_income}
    slices = []
    for sector in portfolio.sectors:
        tickers = sorted(
            t
            for t, located in engine.classification.items()
            if t in held and located.sector == sector.sector
        )
        slices.append(
            FrozenSliceDTO(
                label=sector.sector or "Sem setor",
                tickers=tickers,
                share=share(sector.value),
            )
        )
    slices += [
        FrozenSliceDTO(label=pos.asset.name, tickers=[], share=share(pos.current_value))
        for pos in portfolio.fixed_income
    ]
    slices.append(
        FrozenSliceDTO(label="Caixa", tickers=[], share=share(portfolio.cash))
    )
    return FrozenPortfolioDTO(
        nickname=president.nickname,
        total_networth=portfolio.total_networth,
        frozen_until=end,
        slices=sorted(slices, key=lambda s: s.share, reverse=True),
        interests=_interests(portfolio, pending, share, today),
    )


def _interests(
    portfolio: PortfolioDTO,
    pending: list[Measure],
    share: Callable[[Decimal], Decimal],
    today: date,
) -> list[InterestDTO]:
    """Os setores do presidente que têm medida na fila ou esperando a vigência."""
    interests = []
    for measure in pending:
        if not measure.kind.is_sector:
            continue
        value = Decimal(0)
        for sector in portfolio.sectors:
            if sector.sector != measure.sector:
                continue
            if measure.segment is None:
                value = sector.value
            else:
                value = sum(
                    (s.value for s in sector.segments if s.segment == measure.segment),
                    Decimal(0),
                )
        if value > 0:
            interests.append(
                InterestDTO(
                    sector=rules.target_name(measure),
                    share=share(value),
                    measure_id=measure.id,
                    vote_date=(
                        congress.next_vote_date(today)
                        if measure.status is MeasureStatus.QUEUED
                        else None
                    ),
                    effective=measure.effective,
                )
            )
    return interests


def sector_options(engine: SimulationEngine) -> list[SectorOptionDTO]:
    by_sector: dict[str, dict[str, list[str]]] = {}
    for ticker, located in engine.classification.items():
        by_sector.setdefault(located.sector, {}).setdefault(located.segment, []).append(
            ticker
        )
    return [
        SectorOptionDTO(
            name=name,
            assets=sum(len(t) for t in segments.values()),
            tickers=sorted(t for tickers in segments.values() for t in tickers),
            segments=[
                SegmentOptionDTO(name=seg, assets=len(tickers))
                for seg, tickers in sorted(segments.items())
            ],
        )
        for name, segments in sorted(by_sector.items())
    ]
