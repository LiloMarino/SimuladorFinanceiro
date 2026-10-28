"""
O estado político da partida é o replay dos eventos: quem fundou, filiou, contribuiu,
quanto cada partido já tem de apoio, o resultado de cada turno, o governo em vigor, a
fila do Congresso e a aprovação. `apply` é o único lugar que muda o estado, na partida
rodando e na retomada.
"""

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from backend.core.dto.events.government import GovernmentEventDTO
from backend.core.enum import (
    CampaignActionKind,
    DiceBand,
    MeasureKind,
    MeasureStatus,
    VoterGroup,
    VoterValue,
)
from backend.core.enum import GovernmentEventType as Event
from backend.core.utils import required
from backend.features.government import campaign, promises, voters
from backend.features.government.computer_parties import COMPUTER_FLAGS
from backend.features.government.promises import GroupEffects, Promise

# A medida aprovada vale depois da noventena
VIGENCE_DAYS = 90
# Satisfação de um grupo sem posse registrada
NEUTRAL_SATISFACTION = Decimal(50)


@dataclass(frozen=True)
class ProfileMove:
    """Uma medida aprovada que moveu o perfil do partido do governo."""

    day: date
    measure_id: int
    changes: dict[VoterValue, Decimal]


def _zero_by_group() -> dict[VoterGroup, Decimal]:
    return dict.fromkeys(VoterGroup, Decimal(0))


@dataclass
class Party:
    id: int
    name: str
    abbr: str
    # Cor escolhida pelo fundador (hex); o partido do computador não tem
    color: str | None
    # As 3 bandeiras; nulas no partido fundado antes delas, até o fundador escolher
    flags: tuple[VoterValue, ...] | None
    founder_id: int | None
    is_computer: bool
    founded: date
    # Nome do candidato do partido do computador
    candidate_name: str | None = None
    # Filiados na ordem de entrada e a contribuição mensal de cada um
    members: dict[int, Decimal] = field(default_factory=dict)
    candidate_id: int | None = None
    vice_id: int | None = None
    vice_accepted: bool = False
    # O perfil de hoje, de 0 a 100 em cada valor, e o que o moveu
    radar: dict[VoterValue, Decimal] = field(default_factory=dict)
    moves: list[ProfileMove] = field(default_factory=list)
    # Apoio da campanha em curso em cada grupo (verba, doações e ações); volta a zero a
    # cada eleição e cai pela metade a cada 3 meses, até o dia em `campaign_day`
    campaign: dict[VoterGroup, Decimal] = field(default_factory=_zero_by_group)
    campaign_day: date | None = None
    # Rejeição que as ações já repararam em cada grupo nesta campanha
    repaired: dict[VoterGroup, Decimal] = field(default_factory=_zero_by_group)
    # Rejeição em cada grupo: atravessa as eleições e só cai por reparação
    rejection: dict[VoterGroup, Decimal] = field(default_factory=_zero_by_group)
    # Apoio que os meses de governo deixaram em cada grupo; cai pela metade em 3 meses
    term_support: dict[VoterGroup, Decimal] = field(default_factory=_zero_by_group)
    # Afinidade que as promessas cumpridas somaram em cada grupo: não cai com o tempo
    loyalty: dict[VoterGroup, Decimal] = field(default_factory=_zero_by_group)
    # As promessas da campanha em curso e as das eleições passadas
    promises: list[Promise] = field(default_factory=list)
    past_promises: list["PromiseRecord"] = field(default_factory=list)
    spent: Decimal = Decimal(0)

    def __post_init__(self) -> None:
        if not self.radar:
            self.radar = voters.initial_radar(self.flags)

    @property
    def budget(self) -> Decimal:
        """Verba por mês: a soma das contribuições."""
        return sum(self.members.values(), Decimal(0))

    def standing(self, group: VoterGroup) -> voters.Standing:
        rejection = self.rejection[group]
        return voters.standing(
            group,
            self.radar,
            self.campaign[group]
            + self.term_support[group]
            + self.loyalty[group]
            + promises.campaign_yield(self.promises, group, rejection),
            rejection,
        )

    def standings(self) -> dict[VoterGroup, voters.Standing]:
        return {g: self.standing(g) for g in VoterGroup}

    def add_campaign(self, amount: Decimal) -> None:
        """A verba vira apoio igual em todos os grupos."""
        points = voters.campaign_points(amount)
        for group in VoterGroup:
            self.campaign[group] += points

    def decay_to(self, day: date) -> None:
        """O apoio da campanha perde a parte que o tempo leva entre `campaign_day` e `day`."""
        if self.campaign_day is not None and day > self.campaign_day:
            keep = campaign.decay_factor((day - self.campaign_day).days)
            for group in VoterGroup:
                self.campaign[group] *= keep
        if self.campaign_day is None or day > self.campaign_day:
            self.campaign_day = day

    def reset_campaign(self) -> None:
        self.campaign = _zero_by_group()
        self.campaign_day = None
        self.repaired = _zero_by_group()
        self.spent = Decimal(0)


@dataclass(frozen=True)
class PromiseRecord:
    """As promessas de um partido numa eleição que passou, como ficaram na apuração."""

    cycle: int
    year: int
    promises: tuple[Promise, ...]
    elected: bool


@dataclass(frozen=True)
class BalanceItem:
    """Uma promessa no balanço: quanto do caminho foi andado e o que deixou em cada grupo."""

    promise: Promise
    done: Decimal
    effects: GroupEffects


@dataclass(frozen=True)
class Balance:
    """O balanço das promessas de um governo, no fim do mandato ou no impeachment sem vice."""

    day: date
    party_id: int
    term_start: date
    items: tuple[BalanceItem, ...]
    # Impeachment sem vice: o mandato acabou antes do fim
    impeached: bool

    @property
    def total(self) -> GroupEffects:
        return promises.total(item.effects for item in self.items)


@dataclass(frozen=True)
class Poll:
    """A pesquisa do mês: o que cada grupo achava de cada partido no dia."""

    day: date
    standings: dict[int, dict[VoterGroup, voters.Standing]]


@dataclass(frozen=True)
class Donation:
    day: date
    user_id: int
    party_id: int
    amount: Decimal


@dataclass(frozen=True)
class BaseCharge:
    """A verba de base de um partido num mês: o que os filiados pagaram e o apoio que rendeu."""

    day: date
    party_id: int
    amount: Decimal
    points: Decimal


@dataclass(frozen=True)
class CampaignRecord:
    """Uma ação avulsa de campanha como saiu: o dado e o efeito, guardados no dia."""

    id: int
    day: date
    kind: CampaignActionKind
    party_id: int
    # Quem disparou; nulo no partido do computador
    user_id: int | None
    group: VoterGroup | None
    rival_id: int | None
    price: Decimal
    rolls: tuple[int, ...]
    roll: int
    band: DiceBand
    # Retorno decrescente do dia: 1, 0,5, 0,25...
    rate: Decimal
    # Mudança do apoio de quem a ação atinge, em cada grupo atingido (negativa no ataque)
    support: Decimal
    # Mudança da rejeição do partido que agiu no grupo (negativa repara, positiva é a culatra)
    rejection: Decimal

    @property
    def target_id(self) -> int:
        """O partido cujo apoio a ação mexe: o rival no ataque, o próprio nos demais."""
        if self.kind is CampaignActionKind.ATTACK and self.rival_id is not None:
            return self.rival_id
        return self.party_id


@dataclass(frozen=True)
class Ticket:
    """A chapa e os dados do partido na apuração, guardados como estavam."""

    candidate_id: int | None
    vice_id: int | None
    abbr: str
    name: str
    color: str | None
    is_computer: bool
    candidate_name: str | None
    # As promessas que a chapa levou à urna
    promises: tuple[Promise, ...] = ()


@dataclass(frozen=True)
class RoundResult:
    """O que um turno apurou, guardado como saiu (os partidos mudam depois)."""

    day: date
    cycle: int
    round: int
    # Pontos de cada partido na apuração; no 2º turno, já com a transferência
    points: dict[int, Decimal]
    shares: dict[int, Decimal]
    finalists: list[int]
    winner_id: int | None
    # Quem concorreu e a chapa de cada um
    tickets: dict[int, Ticket]
    # No 2º turno: para qual finalista foram os eleitores de cada partido que saiu
    transfers: dict[int, int]
    donations: dict[int, Decimal]


@dataclass(frozen=True)
class Term:
    """O governo em vigor; sem partido é o governo do computador."""

    party_id: int | None
    president_id: int | None
    vice_id: int | None
    start: date
    # Mandatos seguidos do mesmo presidente: o 2º é o último
    consecutive: int
    # O vice assumiu depois de um impeachment, ou o computador ficou no lugar
    succession: bool = False
    # A satisfação de cada grupo na posse; vazia vale o ponto neutro
    satisfaction: dict[VoterGroup, Decimal] = field(default_factory=dict)
    # As promessas da chapa, cobradas no fim do mandato
    promises: tuple[Promise, ...] = ()
    # Com as chapas fechadas, metade do balanço já pesou no voto; `applied` é o que pesou
    weighed: bool = False
    applied: GroupEffects = field(default_factory=dict)
    settled: bool = False


@dataclass
class Measure:
    """Uma proposta do presidente ao Congresso e o que aconteceu com ela."""

    id: int
    kind: MeasureKind
    # A alíquota (0.20), o teto em reais ou os pontos somados, conforme o tipo
    value: Decimal | None
    # O que a medida muda, como estava no dia da proposta
    before: Decimal | None
    sector: str | None
    segment: str | None
    proposer_id: int
    # Início do governo que propôs: a marca e o efeito na aprovação contam por governo
    term_start: date
    proposed: date
    status: MeasureStatus = MeasureStatus.QUEUED
    decided: date | None = None
    # A chance que a medida tinha no voto
    chance: Decimal | None = None
    effective: date | None = None


@dataclass(frozen=True)
class ApprovalPoint:
    """A satisfação de cada grupo no fechamento de um mês do governo."""

    day: date
    satisfaction: dict[VoterGroup, Decimal]


@dataclass(frozen=True)
class Impeachment:
    day: date
    president_id: int | None
    party_id: int | None
    # O vice que assumiu; nulo quando o computador ficou no lugar
    successor_id: int | None


@dataclass
class GovernmentState:
    parties: dict[int, Party] = field(default_factory=dict)
    next_party_id: int = 1
    # Eleições já concluídas: o índice do ciclo em curso
    cycle: int = 0
    last_collection: date | None = None
    polls: list[Poll] = field(default_factory=list)
    donations: list[Donation] = field(default_factory=list)
    results: list[RoundResult] = field(default_factory=list)
    # Finalistas enquanto o 2º turno não acontece
    runoff: list[int] | None = None
    # A verba de base e as ações avulsas da campanha em curso
    charges: list[BaseCharge] = field(default_factory=list)
    actions: list[CampaignRecord] = field(default_factory=list)
    next_action_id: int = 1
    # O eleito que espera a posse
    pending_term: Term | None = None
    term: Term | None = None
    measures: dict[int, Measure] = field(default_factory=dict)
    next_measure_id: int = 1
    # A satisfação medida no fechamento de cada mês do governo em curso
    approvals: list[ApprovalPoint] = field(default_factory=list)
    # Meses seguidos abaixo do piso, depois da carência; o impeachment vem no limite
    low_streak: int = 0
    last_measured: date | None = None
    impeachments: list[Impeachment] = field(default_factory=list)
    # O balanço das promessas de cada governo que acabou
    balances: list[Balance] = field(default_factory=list)

    @property
    def satisfaction(self) -> dict[VoterGroup, Decimal]:
        """A satisfação de cada grupo hoje: a do último fechamento, ou a da posse."""
        if self.approvals:
            return self.approvals[-1].satisfaction
        start = self.term.satisfaction if self.term else {}
        return {g: start.get(g, NEUTRAL_SATISFACTION) for g in VoterGroup}

    def advance(self, day: date) -> None:
        """Leva o apoio de campanha de todos os partidos até `day`, aplicando a queda do tempo."""
        for party in self.parties.values():
            party.decay_to(day)

    def uses(
        self,
        party_id: int,
        kind: CampaignActionKind,
        group: VoterGroup | None,
        day: date,
    ) -> int:
        """Quantas vezes o partido fez a mesma ação no mesmo grupo no mês de `day`."""
        return sum(
            1
            for a in self.actions
            if (a.party_id, a.kind, a.group) == (party_id, kind, group)
            and (a.day.year, a.day.month) == (day.year, day.month)
        )

    def party_of(self, user_id: int) -> Party | None:
        return next(
            (p for p in self.parties.values() if user_id in p.members),
            None,
        )

    def player_parties(self) -> list[Party]:
        return [p for p in self.parties.values() if not p.is_computer]

    def computer_parties(self) -> list[Party]:
        return [p for p in self.parties.values() if p.is_computer]


def replay(events: Iterable[GovernmentEventDTO]) -> GovernmentState:
    state = GovernmentState()
    for event in events:
        apply(state, event)
    return state


def apply(state: GovernmentState, event: GovernmentEventDTO) -> None:
    p = event.payload
    day = event.event_date
    state.advance(day)
    match event.event_type:
        case Event.PARTY_FOUNDED:
            party_id = _int(p, "party_id")
            founder = _int(p, "founder_id")
            state.parties[party_id] = Party(
                id=party_id,
                name=_str(p, "name"),
                abbr=_str(p, "abbr"),
                color=_str(p, "color"),
                flags=_flags(p),
                founder_id=founder,
                is_computer=False,
                founded=day,
                members={founder: _money(p, "contribution")},
            )
            state.next_party_id = max(state.next_party_id, party_id + 1)
        case Event.COMPUTER_PARTY_ADDED:
            party_id = _int(p, "party_id")
            state.parties[party_id] = Party(
                id=party_id,
                name=_str(p, "name"),
                abbr=_str(p, "abbr"),
                color=None,
                flags=_flags(p) or COMPUTER_FLAGS.get(_str(p, "abbr")),
                founder_id=None,
                is_computer=True,
                founded=day,
                candidate_name=_str(p, "candidate_name"),
            )
            state.next_party_id = max(state.next_party_id, party_id + 1)
        case Event.PARTY_VALUES_SET:
            _set_flags(state.parties[_int(p, "party_id")], required(_flags(p)))
        case Event.COMPUTER_PARTY_REMOVED:
            state.parties.pop(_int(p, "party_id"), None)
        case Event.PARTY_JOINED:
            state.parties[_int(p, "party_id")].members[_int(p, "user_id")] = _money(
                p, "contribution"
            )
        case Event.PARTY_LEFT | Event.MEMBER_EXPELLED:
            _remove_member(state, _int(p, "user_id"))
        case Event.CONTRIBUTION_SET:
            user_id = _int(p, "user_id")
            party = state.party_of(user_id)
            if party is not None:
                party.members[user_id] = _money(p, "contribution")
        case Event.TICKET_SET:
            party = state.parties[_int(p, "party_id")]
            party.candidate_id = _int(p, "candidate_id")
            party.vice_id = _opt_int(p, "vice_id")
            party.vice_accepted = bool(p.get("vice_accepted", False))
        case Event.VICE_ANSWERED:
            party = state.parties[_int(p, "party_id")]
            if p["accepted"]:
                party.vice_accepted = True
            else:
                party.vice_id = None
                party.vice_accepted = False
        case Event.CAMPAIGN_SPENT:
            for party_id, amount in _money_map(p, "spent").items():
                party = state.parties.get(party_id)
                if party is not None:
                    party.spent += amount
                    party.add_campaign(amount)
                    state.charges.append(
                        BaseCharge(
                            day, party_id, amount, voters.campaign_points(amount)
                        )
                    )
            state.last_collection = date.fromisoformat(_str(p, "month"))
            state.polls.append(
                Poll(
                    day,
                    {pid: party.standings() for pid, party in state.parties.items()},
                )
            )
        case Event.DONATION_MADE:
            party_id = _int(p, "party_id")
            amount = _money(p, "amount")
            party = state.parties[party_id]
            party.spent += amount
            party.add_campaign(amount)
            state.donations.append(Donation(day, _int(p, "user_id"), party_id, amount))
        case Event.CAMPAIGN_ACTION:
            _apply_action(state, event)
        case Event.ELECTION_ROUND:
            _apply_round(state, event)
        case Event.TERM_STARTED:
            pending = state.pending_term
            state.term = Term(
                party_id=_opt_int(p, "party_id"),
                president_id=_opt_int(p, "president_id"),
                vice_id=_opt_int(p, "vice_id"),
                start=day,
                consecutive=_int(p, "consecutive"),
                satisfaction=dict(pending.satisfaction) if pending else {},
                promises=pending.promises if pending else (),
            )
            state.pending_term = None
            _reset_government(state)
        case Event.MEASURE_PROPOSED:
            measure_id = _int(p, "measure_id")
            state.measures[measure_id] = Measure(
                id=measure_id,
                kind=MeasureKind(_str(p, "kind")),
                value=_opt_money(p, "value"),
                before=_opt_money(p, "before"),
                sector=_opt_str(p, "sector"),
                segment=_opt_str(p, "segment"),
                proposer_id=_int(p, "proposer_id"),
                term_start=required(state.term).start,
                proposed=day,
            )
            state.next_measure_id = max(state.next_measure_id, measure_id + 1)
        case Event.MEASURE_WITHDRAWN:
            state.measures[_int(p, "measure_id")].status = MeasureStatus.WITHDRAWN
        case Event.MEASURE_VOTED:
            measure = state.measures[_int(p, "measure_id")]
            measure.decided = day
            measure.chance = _money(p, "chance")
            if p["approved"]:
                measure.status = MeasureStatus.APPROVED
                measure.effective = day + timedelta(days=VIGENCE_DAYS)
                _move_profile(state, measure, day)
            else:
                measure.status = MeasureStatus.REJECTED
        case Event.APPROVAL_MEASURED:
            satisfaction = _satisfaction(p, "satisfaction")
            state.approvals.append(ApprovalPoint(day, satisfaction))
            state.low_streak = _int(p, "low_streak")
            state.last_measured = date.fromisoformat(_str(p, "month"))
            _remember_month(state, satisfaction)
        case Event.IMPEACHED:
            _apply_impeachment(state, event)
        case Event.PROMISES_SET:
            _apply_promises_set(state, event)
        case Event.PROMISES_WEIGHED:
            _apply_promises_weighed(state, event)
        case Event.PROMISES_SETTLED:
            _apply_promises_settled(state, event)


def _reset_government(state: GovernmentState) -> None:
    """Um governo novo começa sem a fila do anterior e sem o histórico de aprovação."""
    for measure in state.measures.values():
        if measure.status is MeasureStatus.QUEUED:
            measure.status = MeasureStatus.DROPPED
    state.approvals = []
    state.low_streak = 0


def _apply_impeachment(state: GovernmentState, event: GovernmentEventDTO) -> None:
    term = required(state.term)
    successor = _opt_int(event.payload, "successor_id")
    state.impeachments.append(
        Impeachment(
            day=event.event_date,
            president_id=term.president_id,
            party_id=term.party_id,
            successor_id=successor,
        )
    )
    state.term = Term(
        party_id=term.party_id if successor is not None else None,
        president_id=successor,
        vice_id=None,
        start=event.event_date,
        consecutive=1,
        succession=True,
        satisfaction=state.satisfaction,
        # O vice herda as promessas da chapa e é cobrado no fim do mandato
        promises=term.promises if successor is not None else (),
        weighed=term.weighed,
        applied=term.applied,
    )
    _reset_government(state)


def _remove_member(state: GovernmentState, user_id: int) -> None:
    party = state.party_of(user_id)
    if party is None:
        return
    del party.members[user_id]
    if not party.members:
        del state.parties[party.id]
        return
    # A fundação passa ao filiado mais antigo que ficou
    if party.founder_id == user_id:
        party.founder_id = next(iter(party.members))
    if party.candidate_id == user_id:
        party.candidate_id = None
    if party.vice_id == user_id:
        party.vice_id = None
        party.vice_accepted = False


def _apply_round(state: GovernmentState, event: GovernmentEventDTO) -> None:
    p = event.payload
    tickets = {
        int(pid): Ticket(
            candidate_id=_opt_int(t, "candidate_id"),
            vice_id=_opt_int(t, "vice_id"),
            abbr=_str(t, "abbr"),
            name=_str(t, "name"),
            color=_opt_str(t, "color"),
            is_computer=bool(t["is_computer"]),
            candidate_name=_opt_str(t, "candidate_name"),
            promises=tuple(
                promises.from_payload(item)  # type: ignore[arg-type]
                for item in _opt_list(t, "promises")
            ),
        )
        for pid, t in _dict(p, "tickets").items()
    }
    winner = _opt_int(p, "winner_id")
    result = RoundResult(
        day=event.event_date,
        cycle=_int(p, "cycle"),
        round=_int(p, "round"),
        points=_money_map(p, "points"),
        shares=_money_map(p, "shares"),
        finalists=[int(x) for x in _list(p, "finalists")],  # type: ignore[call-overload]
        winner_id=winner,
        tickets=tickets,
        transfers={int(a): int(b) for a, b in _dict(p, "transfers").items()},  # type: ignore[call-overload]
        donations=_money_map(p, "donations"),
    )
    state.results.append(result)
    # Sem finalistas ninguém concorreu: o governo continua do computador
    if winner is None and result.finalists:
        state.runoff = result.finalists
        return

    ticket = tickets.get(winner) if winner is not None else None
    previous = state.term
    president = ticket.candidate_id if ticket else None
    same_president = (
        previous is not None
        and president is not None
        and previous.president_id == president
    )
    winner_party = state.parties.get(winner) if winner is not None else None
    state.pending_term = Term(
        party_id=winner,
        president_id=president,
        vice_id=ticket.vice_id if ticket else None,
        start=date(event.event_date.year + 1, 1, 1),
        consecutive=(previous.consecutive + 1 if previous and same_president else 1),
        satisfaction=_satisfaction(p, "winner_satisfaction"),
        promises=tuple(winner_party.promises) if winner_party else (),
    )
    # As promessas de quem perdeu ficam no histórico do partido, sem efeito
    for party in state.parties.values():
        if party.promises:
            party.past_promises.append(
                PromiseRecord(
                    cycle=result.cycle,
                    year=event.event_date.year,
                    promises=tuple(party.promises),
                    elected=party.id == winner,
                )
            )
            party.promises = []
    # A campanha seguinte recomeça do zero: os partidos ficam, o apoio não
    state.runoff = None
    state.cycle += 1
    state.polls = []
    state.donations = []
    state.charges = []
    state.actions = []
    for party in state.parties.values():
        party.reset_campaign()


def _apply_action(state: GovernmentState, event: GovernmentEventDTO) -> None:
    """A ação rola no dia: o dado e o preço vêm do evento, o efeito sai das regras e do estado."""
    p = event.payload
    party = state.parties.get(_int(p, "party_id"))
    if party is None:
        return
    kind = CampaignActionKind(_str(p, "action"))
    group = VoterGroup(_str(p, "group")) if p.get("group") else None
    rolls = tuple(int(x) for x in _list(p, "rolls"))  # type: ignore[call-overload]
    day = event.event_date
    result = campaign.outcome(
        kind,
        rolls,
        state.uses(party.id, kind, group, day),
        campaign.EVENT_REPAIR_LIMIT - party.repaired[group] if group else Decimal(0),
        party.rejection[group] if group else Decimal(0),
    )
    record = CampaignRecord(
        id=state.next_action_id,
        day=day,
        kind=kind,
        party_id=party.id,
        user_id=_opt_int(p, "user_id"),
        group=group,
        rival_id=_opt_int(p, "rival_id"),
        price=_money(p, "price"),
        rolls=rolls,
        roll=result.roll,
        band=result.band,
        rate=result.rate,
        support=result.support,
        rejection=result.rejection,
    )
    state.next_action_id += 1
    state.actions.append(record)
    party.spent += record.price
    target = state.parties.get(record.target_id)
    if target is not None and result.support != 0:
        for affected in [group] if group else list(VoterGroup):
            target.campaign[affected] += result.support
    if group is not None and result.rejection != 0:
        party.rejection[group] = voters.clamp(party.rejection[group] + result.rejection)
        if result.rejection < 0:
            party.repaired[group] += -result.rejection


def _apply_promises_set(state: GovernmentState, event: GovernmentEventDTO) -> None:
    """
    A chapa fica com a lista nova. Quem já tinha anunciado e volta atrás (retira, troca
    ou baixa o alvo) paga a rejeição de voltar atrás nos grupos que queriam a medida.
    """
    p = event.payload
    party = state.parties.get(_int(p, "party_id"))
    if party is None:
        return
    stored: list[dict[str, Any]] = _list(p, "promises")  # type: ignore[assignment]
    new = [promises.from_payload(item) for item in stored]
    by_key = {item.key: item for item in new}
    for old in party.promises:
        cost = promises.retreat(old, by_key.get(old.key))
        for group, amount in cost.items():
            party.rejection[group] = voters.add_rejection(
                party.rejection[group], amount
            )
    party.promises = new


def _apply_promises_weighed(state: GovernmentState, event: GovernmentEventDTO) -> None:
    """Metade do balanço em vigor passa a pesar no voto do partido que governa e concorre."""
    p = event.payload
    term = state.term
    party = state.parties.get(_int(p, "party_id"))
    if term is None or party is None:
        return
    weighed = promises.effects_from_payload(_dict(p, "effects"))
    _credit(party, weighed)
    state.term = replace(term, weighed=True, applied=weighed)


def _apply_promises_settled(state: GovernmentState, event: GovernmentEventDTO) -> None:
    """O balanço do mandato fecha o que falta do que já pesou no voto."""
    p = event.payload
    term = state.term
    party_id = _int(p, "party_id")
    if term is None:
        return
    stored: list[dict[str, Any]] = _list(p, "items")  # type: ignore[assignment]
    items = tuple(
        BalanceItem(
            promise=promises.from_payload(item["promise"]),
            done=Decimal(str(item["done"])),
            effects=promises.effects_from_payload(item["effects"]),
        )
        for item in stored
    )
    balance = Balance(
        day=event.event_date,
        party_id=party_id,
        term_start=term.start,
        items=items,
        impeached=bool(p.get("impeached", False)),
    )
    state.balances.append(balance)
    party = state.parties.get(party_id)
    if party is not None and not party.is_computer:
        _credit(party, promises.remaining(balance.total, term.applied))
    state.term = replace(term, settled=True, applied={})


def _credit(party: Party, effects: GroupEffects) -> None:
    """Afinidade que não cai e rejeição que só o balanço mexe."""
    for group, effect in effects.items():
        party.loyalty[group] += effect.loyalty
        party.rejection[group] = voters.clamp(party.rejection[group] + effect.rejection)


def _set_flags(party: Party, flags: tuple[VoterValue, ...]) -> None:
    """O partido sem bandeiras sai do neutro: cada bandeira sobe ao nível de bandeira."""
    party.flags = flags
    for value in flags:
        party.radar[value] = voters.clamp(
            party.radar[value] + voters.RADAR_FLAG - voters.RADAR_NEUTRAL
        )


def _remember_month(
    state: GovernmentState, satisfaction: dict[VoterGroup, Decimal]
) -> None:
    """O mês fechado mexe no apoio e na rejeição dos partidos do presidente e do vice."""
    term = state.term
    if term is None:
        return
    governing = {
        party.id: party
        for party in (
            state.parties.get(term.party_id) if term.party_id is not None else None,
            state.party_of(term.vice_id) if term.vice_id is not None else None,
        )
        if party is not None and not party.is_computer
    }
    for party in governing.values():
        for group, value in satisfaction.items():
            party.term_support[group], party.rejection[group] = voters.remember_month(
                party.term_support[group],
                party.rejection[group],
                voters.month_verdict(value),
            )


def _move_profile(state: GovernmentState, measure: Measure, day: date) -> None:
    """A medida aprovada move o perfil do partido que governa; o do computador não muda."""
    term = state.term
    party = state.parties.get(term.party_id) if term and term.party_id else None
    if party is None or party.is_computer:
        return
    changes = voters.radar_moves(measure.kind, measure.value, measure.before)
    if not changes:
        return
    for value, points in changes.items():
        party.radar[value] = voters.clamp(party.radar[value] + points)
    party.moves.append(ProfileMove(day, measure.id, changes))


def _int(p: dict[str, object], key: str) -> int:
    return int(p[key])  # type: ignore[call-overload]


def _opt_int(p: dict[str, object], key: str) -> int | None:
    value = p.get(key)
    return None if value is None else int(value)  # type: ignore[call-overload]


def _str(p: dict[str, object], key: str) -> str:
    return str(p[key])


def _opt_money(p: dict[str, object], key: str) -> Decimal | None:
    value = p.get(key)
    return None if value is None else Decimal(str(value))


def _opt_str(p: dict[str, object], key: str) -> str | None:
    value = p.get(key)
    return None if value is None else str(value)


def _flags(p: dict[str, object]) -> tuple[VoterValue, ...] | None:
    flags = p.get("flags")
    if flags is None:
        return None
    return tuple(VoterValue(str(v)) for v in flags)  # type: ignore[attr-defined]


def _money(p: dict[str, object], key: str) -> Decimal:
    return Decimal(str(p[key]))


def _dict(p: dict[str, object], key: str) -> dict[str, dict[str, object]]:
    return p[key]  # type: ignore[return-value]


def _list(p: dict[str, object], key: str) -> list[object]:
    return p[key]  # type: ignore[return-value]


def _opt_list(p: dict[str, object], key: str) -> list[object]:
    """A lista guardada no evento; ausente nos eventos antigos, vazia."""
    return p.get(key) or []  # type: ignore[return-value]


def _satisfaction(p: dict[str, object], key: str) -> dict[VoterGroup, Decimal]:
    """A satisfação por grupo guardada no evento; ausente, todos os grupos no ponto neutro."""
    stored = p.get(key) or {}
    return {
        g: Decimal(str(stored.get(g.value, NEUTRAL_SATISFACTION)))  # type: ignore[attr-defined]
        for g in VoterGroup
    }


def _money_map(p: dict[str, object], key: str) -> dict[int, Decimal]:
    return {int(k): Decimal(str(v)) for k, v in p[key].items()}  # type: ignore[attr-defined]
