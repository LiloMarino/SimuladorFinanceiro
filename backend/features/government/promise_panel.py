"""As promessas de campanha traduzidas para o que o jogador vê: diálogo, cartão do Governo e balanço."""

from datetime import date, timedelta
from decimal import Decimal

from backend.core.dto.government import PromisesPanelDTO, SectorOptionDTO
from backend.core.dto.promises import (
    BalanceDTO,
    BalanceItemDTO,
    PromiseDTO,
    PromiseEffectDTO,
    PromiseOptionDTO,
    PromisePreviewDTO,
    PromiseProgressDTO,
    PromiseRecordDTO,
    PromiseRowDTO,
    PromisesPreviewDTO,
    PromiseTotalRowDTO,
    PromiseValueDTO,
    TermPromisesDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import VoterGroup
from backend.features.government import congress, promises, second_round, voters
from backend.features.government import measures as rules
from backend.features.government.government_book import (
    GovernmentBook,
)
from backend.features.government.promises import GroupEffects, Promise
from backend.features.government.state import (
    VIGENCE_DAYS,
    Balance,
    Party,
    PromiseRecord,
)

ZERO = Decimal(0)
ONE = Decimal(1)


def promise_dto(promise: Promise) -> PromiseDTO:
    return PromiseDTO(
        kind=promise.kind,
        title=rules.promise_title(promise),
        target=promise.target,
        baseline=promise.baseline,
        sector=promise.sector,
        segment=promise.segment,
        announced=promise.announced,
    )


def record_dto(record: PromiseRecord) -> PromiseRecordDTO:
    return PromiseRecordDTO(
        election_year=record.year,
        elected=record.elected,
        promises=[promise_dto(p) for p in record.promises],
    )


def _effects_dto(effects: GroupEffects) -> list[PromiseEffectDTO]:
    return [
        PromiseEffectDTO(
            group=group, loyalty=effect.loyalty, rejection=effect.rejection
        )
        for group, effect in effects.items()
    ]


# Diálogo


def build_promises_panel(
    book: GovernmentBook,
    viewer: UserDTO,
    today: date,
    sectors: list[SectorOptionDTO],
) -> PromisesPanelDTO:
    party = book.founded_party(viewer)
    reason = book.promises_open_reason(today, party)
    return PromisesPanelDTO(
        party_id=party.id,
        party_abbr=party.abbr,
        is_founder=True,
        open=reason is None,
        closed_reason=reason,
        ticket_deadline=book.cycle().ticket_deadline,
        max_promises=(
            second_round.MAX_PROMISES
            if book.state.runoff is not None
            else promises.MAX_PROMISES
        ),
        add_only=book.state.runoff is not None,
        promises=[promise_dto(p) for p in party.promises],
        options=[
            PromiseOptionDTO(
                kind=kind,
                baseline=baseline,
                step=voters.EFFECT_STEPS[kind],
                limit=promises.limit_of(kind),
            )
            for kind in promises.GENERAL_KINDS
            if (baseline := book.promise_baseline(kind, today)) is not None
        ],
        sectors=sectors,
    )


def build_preview(
    book: GovernmentBook, viewer: UserDTO, today: date, drafts: list[Promise]
) -> PromisesPreviewDTO:
    """Cada promessa da lista como rende hoje e o que voltar atrás nas já anunciadas custaria."""
    party = book.founded_party(viewer)
    kept = {p.key: p for p in drafts}
    retreat: dict[VoterGroup, Decimal] = dict.fromkeys(VoterGroup, ZERO)
    for old in party.promises:
        for group, cost in promises.retreat(old, kept.get(old.key)).items():
            retreat[group] += cost
    return PromisesPreviewDTO(
        items=[
            PromisePreviewDTO(
                promise=promise_dto(p),
                values=[
                    PromiseValueDTO(value=value, effect=effect)
                    for value, effect in promises.effects(p).items()
                    if effect != 0
                ],
                rows=_rows(party, p),
            )
            for p in drafts
        ],
        totals=[
            PromiseTotalRowDTO(
                group=group,
                support=promises.campaign_yield(drafts, group, party.rejection[group]),
                retreat=retreat[group],
            )
            for group in VoterGroup
        ],
    )


def _rows(party: Party, promise: Promise) -> list[PromiseRowDTO]:
    kept = promises.settle(promise, ONE)
    broken = promises.settle(promise, ZERO)
    rows = []
    for group in VoterGroup:
        rejection = party.rejection[group]
        rows.append(
            PromiseRowDTO(
                group=group,
                wanted=promises.reaction(group, promise) > 0,
                support=promises.yield_of(promise, group, rejection),
                support_full=promises.GAIN * promises.reaction(group, promise),
                rejection=rejection,
                loyalty=kept[group].loyalty,
                repair=-kept[group].rejection,
                breach=broken[group].rejection,
            )
        )
    return rows


# Cartão do Governo


def build_term_promises(
    book: GovernmentBook, viewer: UserDTO, today: date
) -> TermPromisesDTO | None:
    state = book.state
    term = state.term
    if term is None or term.party_id is None or not term.promises:
        return None
    party = state.parties.get(term.party_id)
    if party is None:
        return None
    end = book.term_end()
    mine = viewer.id in party.members
    return TermPromisesDTO(
        party_id=party.id,
        party_abbr=party.abbr,
        items=[_progress(book, p, today) for p in term.promises],
        weighed=term.weighed,
        last_vote=_last_vote(end) if end is not None else None,
        projection=(
            _effects_dto(book.promise_effects(term.promises, today)) if mine else []
        ),
    )


def _progress(
    book: GovernmentBook, promise: Promise, today: date
) -> PromiseProgressDTO:
    done = book.promise_progress(promise, today)
    return PromiseProgressDTO(
        promise=promise_dto(promise),
        state=promises.state_of(done),
        done=done,
        current=book.promise_value(promise, today),
    )


def _last_vote(end: date) -> date:
    """O último voto do Congresso cuja medida ainda passa a valer até o fim do mandato."""
    cutoff = end - timedelta(days=VIGENCE_DAYS)
    vote = congress.last_business_day(cutoff.year, cutoff.month)
    if vote > cutoff:
        year, month = (
            (cutoff.year - 1, 12)
            if cutoff.month == 1
            else (cutoff.year, cutoff.month - 1)
        )
        vote = congress.last_business_day(year, month)
    return vote


# Balanço


def build_balances(book: GovernmentBook, viewer: UserDTO) -> list[BalanceDTO]:
    """Os balanços dos governos que acabaram, do mais recente ao mais antigo."""
    state = book.state
    return [
        _balance(balance, state.parties.get(balance.party_id), viewer)
        for balance in reversed(state.balances)
    ]


def _balance(balance: Balance, party: Party | None, viewer: UserDTO) -> BalanceDTO:
    # Os números por grupo são do partido: só os filiados veem
    mine = party is not None and viewer.id in party.members
    return BalanceDTO(
        date=balance.day,
        term_start=balance.term_start,
        party_id=balance.party_id,
        party_abbr=party.abbr if party else "?",
        party_color=party.color if party else None,
        impeached=balance.impeached,
        items=[
            BalanceItemDTO(
                promise=promise_dto(item.promise),
                state=promises.state_of(item.done),
                done=item.done,
                effects=_effects_dto(item.effects) if mine else [],
            )
            for item in balance.items
        ],
        totals=_effects_dto(balance.total) if mine else [],
    )
