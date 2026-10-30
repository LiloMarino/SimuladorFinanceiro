"""O cartão das ações de campanha e o histórico do partido: o estado político traduzido para o que o filiado vê."""

from datetime import date
from decimal import Decimal

from backend.core.dto.campaign import (
    CampaignActionDTO,
    CampaignEntryDTO,
    CampaignGroupDTO,
    CampaignHistoryDTO,
    CampaignPanelDTO,
    CampaignRivalDTO,
    CampaignRollDTO,
    CampaignTargetDTO,
    DiceBandDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CampaignActionKind,
    CampaignEntryKind,
    DiceBand,
    VoterGroup,
)
from backend.core.exceptions.http_exceptions import ConflictError
from backend.features.government import campaign
from backend.features.government.government_book import CampaignResult, GovernmentBook
from backend.features.government.state import BaseCharge, CampaignRecord, Party

ZERO = Decimal(0)
RECENT = 4


def build_campaign(
    book: GovernmentBook, users: list[UserDTO], viewer: UserDTO, today: date
) -> CampaignPanelDTO:
    state = book.state
    state.advance(today)
    party = _my_party(book, viewer)
    cycle = book.cycle()
    reason = book.campaign_closed_reason(today, party)
    cash = book.cash_of(viewer)
    entries = _entries(book, users, party, today)
    mine = [a for a in state.actions if a.party_id == party.id]
    charges = [c for c in state.charges if c.party_id == party.id and c.amount > 0]
    last = charges[-1] if charges else None
    return CampaignPanelDTO(
        party_id=party.id,
        party_abbr=party.abbr,
        today=today,
        open=reason is None,
        closed_reason=reason,
        campaign_start=cycle.campaign_start,
        first_round=cycle.first_round,
        share_at_vote=(
            campaign.decay_factor((cycle.first_round - today).days)
            if today < cycle.first_round
            else Decimal(1)
        ),
        actions=[
            _action(book, users, party, kind, today, cash)
            for kind in CampaignActionKind
        ],
        rivals=[
            CampaignRivalDTO(party_id=p.id, abbr=p.abbr, name=p.name, color=p.color)
            for p in book.running_parties()
            if p.id != party.id
        ],
        groups=[
            CampaignGroupDTO(
                group=g,
                campaign=party.campaign[g],
                undecided=(
                    state.race.groups[g].undecided if state.race is not None else None
                ),
            )
            for g in VoterGroup
        ],
        recent=[e for e in entries if e.kind is not CampaignEntryKind.BASE_BUDGET][
            :RECENT
        ],
        actions_spent=sum((a.price for a in mine), ZERO),
        actions_count=len(mine),
        base_spent=sum((c.amount for c in charges), ZERO),
        base_charges=len(charges),
        last_charge_date=last.day if last else None,
        last_charge_amount=last.amount if last else None,
        last_charge_points=last.points if last else None,
    )


def build_history(
    book: GovernmentBook, users: list[UserDTO], viewer: UserDTO, today: date
) -> CampaignHistoryDTO:
    book.state.advance(today)
    party = _my_party(book, viewer)
    return CampaignHistoryDTO(entries=_entries(book, users, party, today))


def build_roll(
    book: GovernmentBook,
    users: list[UserDTO],
    viewer: UserDTO,
    today: date,
    result: CampaignResult,
) -> CampaignRollDTO:
    """O resultado de uma ação recém-rolada, com o apoio e a rejeição de antes e de depois."""
    state = book.state
    party = _my_party(book, viewer)
    record = result.record
    entry = _record_entry(record, party, _people(users), state.parties, today)
    group = record.group
    target = state.parties.get(record.target_id)
    return CampaignRollDTO(
        entry=entry,
        target_abbr=target.abbr if target and group else None,
        support_before=result.support_before,
        support_after=book.support_of(target, group) if target and group else None,
        rejection_before=result.rejection_before,
        rejection_after=party.rejection[group] if group else None,
    )


def _my_party(book: GovernmentBook, viewer: UserDTO) -> Party:
    party = book.state.party_of(viewer.id)
    if party is None:
        raise ConflictError("Você não está em nenhum partido.")
    return party


def _people(users: list[UserDTO]) -> dict[int, UserDTO]:
    return {user.id: user for user in users}


def _action(
    book: GovernmentBook,
    users: list[UserDTO],
    party: Party,
    kind: CampaignActionKind,
    today: date,
    cash: Decimal,
) -> CampaignActionDTO:
    price = book.action_price(kind, today)
    people = _people(users)
    targets = []
    for group in campaign.eligible_groups(kind):
        month = book.state.month_actions(party.id, kind, group, today)
        uses = len(month)
        first = month[0] if month else None
        first_user = (
            people.get(first.user_id)
            if first is not None and first.user_id is not None
            else None
        )
        repair_left = (
            campaign.EVENT_REPAIR_LIMIT - party.repaired[group]
            if group is not None and kind is CampaignActionKind.EVENT
            else ZERO
        )
        rejection = party.rejection[group] if group is not None else None
        bands = campaign.table(kind, uses, repair_left, rejection or ZERO)
        targets.append(
            CampaignTargetDTO(
                group=group,
                uses_this_month=uses,
                rate=campaign.repeat_rate(uses),
                first_by=first_user.nickname if first_user else None,
                first_day=first.day if first else None,
                repair_left=repair_left,
                repair_limit=(
                    campaign.EVENT_REPAIR_LIMIT
                    if kind is CampaignActionKind.EVENT
                    else ZERO
                ),
                support=book.support_of(party, group) if group is not None else None,
                rejection=rejection,
                bands=[
                    DiceBandDTO(
                        band=b.band,
                        first_roll=b.first_roll,
                        last_roll=b.last_roll,
                        chance=b.chance,
                        support=b.support,
                        rejection=b.rejection,
                    )
                    for b in bands
                ],
                average=campaign.average(bands),
            )
        )
    return CampaignActionDTO(
        action=kind,
        price=price,
        missing=max(ZERO, price - cash),
        advantage=kind is CampaignActionKind.TV,
        targets=targets,
    )


def _entries(
    book: GovernmentBook, users: list[UserDTO], party: Party, today: date
) -> list[CampaignEntryDTO]:
    """O que o partido fez e sofreu na campanha, do mais recente ao mais antigo."""
    state = book.state
    people = _people(users)
    entries = [
        _record_entry(a, party, people, state.parties, today)
        for a in state.actions
        if a.party_id == party.id
        or (a.kind is CampaignActionKind.ATTACK and a.rival_id == party.id)
    ]
    entries += [
        _charge_entry(index, charge, party, today)
        for index, charge in enumerate(state.charges)
        if charge.party_id == party.id and charge.amount > 0
    ]
    return sorted(entries, key=lambda e: (e.date, e.id), reverse=True)


def _share(day: date, today: date) -> Decimal:
    return campaign.decay_factor((today - day).days)


def _record_entry(
    record: CampaignRecord,
    mine: Party,
    people: dict[int, UserDTO],
    parties: dict[int, Party],
    today: date,
) -> CampaignEntryDTO:
    received = record.party_id != mine.id
    actor = parties.get(record.party_id)
    rival = parties.get(record.rival_id) if record.rival_id is not None else None
    share = _share(record.day, today)
    user = people.get(record.user_id) if record.user_id is not None else None
    return CampaignEntryDTO(
        id=record.id,
        date=record.day,
        kind=(
            CampaignEntryKind.ATTACK_RECEIVED
            if received
            else CampaignEntryKind(record.kind.value)
        ),
        nickname=None if received else (user.nickname if user else None),
        party_abbr=actor.abbr if actor else "?",
        party_color=actor.color if actor else None,
        group=record.group,
        rival_abbr=rival.abbr if rival else None,
        # O dado é de quem rolou: o atacado vê o efeito, sem o número
        rolls=[] if received else list(record.rolls),
        roll=None if received else record.roll,
        band=None if received else record.band,
        support=record.support,
        rejection=ZERO if received else record.rejection,
        worth_now=record.support * share,
        worth_share=share,
        price=None if received else record.price,
        newsworthy=(
            record.kind is CampaignActionKind.ATTACK
            or record.band in (DiceBand.VIRAL, DiceBand.DISASTER)
        ),
    )


def _charge_entry(
    index: int, charge: BaseCharge, party: Party, today: date
) -> CampaignEntryDTO:
    share = _share(charge.day, today)
    return CampaignEntryDTO(
        # Ids negativos separam a verba das ações, que contam de 1
        id=-(index + 1),
        date=charge.day,
        kind=CampaignEntryKind.BASE_BUDGET,
        nickname=None,
        party_abbr=party.abbr,
        party_color=party.color,
        group=None,
        rival_abbr=None,
        rolls=[],
        roll=None,
        band=None,
        support=charge.points,
        rejection=ZERO,
        worth_now=charge.points * share,
        worth_share=share,
        price=charge.amount,
        newsworthy=False,
    )
