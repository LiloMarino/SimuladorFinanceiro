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
    DealBreaker,
    DealStatus,
    DiceBand,
    MeasureKind,
    MeasureStatus,
    VoterGroup,
    VoterValue,
)
from backend.core.enum import GovernmentEventType as Event
from backend.core.utils import required
from backend.features.government import (
    campaign,
    house,
    promises,
    second_round,
    voters,
)
from backend.features.government import (
    deals as deal_rules,
)
from backend.features.government.computer_parties import COMPUTER_FLAGS
from backend.features.government.deals import Deal
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
    # Quanto de cada contribuição vai para a campanha do Congresso; o resto é da presidência
    congress: dict[int, Decimal] = field(default_factory=dict)
    candidate_id: int | None = None
    vice_id: int | None = None
    vice_accepted: bool = False
    # O perfil de hoje, de 0 a 100 em cada valor, e o que o moveu
    radar: dict[VoterValue, Decimal] = field(default_factory=dict)
    moves: list[ProfileMove] = field(default_factory=list)
    # Apoio da campanha em curso em cada grupo (verba, doações e ações); volta a zero a
    # cada eleição e cai pela metade a cada 3 meses, até o dia em `campaign_day`
    campaign: dict[VoterGroup, Decimal] = field(default_factory=_zero_by_group)
    # O mesmo para a campanha do Congresso: volta a zero na eleição da casa
    house_campaign: dict[VoterGroup, Decimal] = field(default_factory=_zero_by_group)
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
    # Os valores em que o líder trocou a orientação padrão da bancada
    guidance: dict[VoterValue, bool] = field(default_factory=dict)

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

    def add_house_campaign(self, amount: Decimal) -> None:
        """A verba do Congresso vira apoio à bancada, igual em todos os grupos."""
        points = voters.campaign_points(amount)
        for group in VoterGroup:
            self.house_campaign[group] += points

    @property
    def rules(self) -> dict[VoterValue, bool]:
        """A orientação padrão da bancada: Sim nas bandeiras do partido, salvo o que o líder trocou."""
        return {**house.flag_rules(self.flags), **self.guidance}

    def decay_to(self, day: date) -> None:
        """O apoio da campanha perde a parte que o tempo leva entre `campaign_day` e `day`."""
        if self.campaign_day is not None and day > self.campaign_day:
            keep = campaign.decay_factor((day - self.campaign_day).days)
            for group in VoterGroup:
                self.campaign[group] *= keep
                self.house_campaign[group] *= keep
        if self.campaign_day is None or day > self.campaign_day:
            self.campaign_day = day

    def reset_house_campaign(self) -> None:
        self.house_campaign = _zero_by_group()

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
class RunoffPoll:
    """A pesquisa semanal entre os turnos: o voto exato de cada grupo no dia."""

    day: date
    vote: voters.Vote


@dataclass(frozen=True)
class RunoffContribution:
    """A contribuição única de 2º turno de um filiado do finalista (nulo no computador)."""

    day: date
    user_id: int | None
    party_id: int
    amount: Decimal


@dataclass(frozen=True)
class Declaration:
    """O apoio declarado pelo partido eliminado; `endorsed_id` nulo é neutralidade."""

    day: date
    party_id: int
    user_id: int | None
    endorsed_id: int | None


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
    # No 2º turno: o voto de cada grupo entre os finalistas e quem não votou, em pontos do eleitorado
    groups: dict[VoterGroup, voters.GroupVote] = field(default_factory=dict)
    not_voted: Decimal = Decimal(0)


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
    # Nulo quando quem propôs é o partido do computador que governa
    proposer_id: int | None
    # Início do governo que propôs: a marca e o efeito na aprovação contam por governo
    term_start: date
    proposed: date
    # O partido que governava no dia da proposta
    party_id: int | None = None
    status: MeasureStatus = MeasureStatus.QUEUED
    decided: date | None = None
    # Como a casa votou: nula na medida da fila ou votada antes da casa existir
    tally: house.Tally | None = None
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


@dataclass(frozen=True)
class ElectedHouse:
    """A casa que uma eleição formou e o dia em que ela toma posse."""

    day: date
    takes_office: date
    cycle: int
    house: house.House


@dataclass(frozen=True)
class ImpeachmentRequest:
    """O pedido aberto: a casa vota no dia marcado."""

    opened: date
    vote_day: date


@dataclass(frozen=True)
class ImpeachmentVote:
    day: date
    opened: date
    president_id: int | None
    tally: house.Tally
    approved: bool


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
    # A disputa do 2º turno por grupo, o dia do 1º turno, as pesquisas semanais, as
    # contribuições únicas e os apoios declarados pelos partidos eliminados
    race: second_round.Race | None = None
    race_started: date | None = None
    race_polls: list[RunoffPoll] = field(default_factory=list)
    race_contributions: list[RunoffContribution] = field(default_factory=list)
    declarations: list[Declaration] = field(default_factory=list)
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
    # As casas eleitas, em ordem; antes da 1ª eleição vale a casa inicial do computador
    houses: list[ElectedHouse] = field(default_factory=list)
    # A orientação de cada bancada em cada votação aberta: "measure:7" ou "impeachment"
    orientations: dict[str, dict[int, bool]] = field(default_factory=dict)
    request: ImpeachmentRequest | None = None
    impeachment_votes: list[ImpeachmentVote] = field(default_factory=list)
    # Os acordos de apoio por emenda, da proposta ao fim
    deals: dict[int, Deal] = field(default_factory=dict)
    next_deal_id: int = 1
    # O balanço das promessas de cada governo que acabou
    balances: list[Balance] = field(default_factory=list)

    @property
    def satisfaction(self) -> dict[VoterGroup, Decimal]:
        """A satisfação de cada grupo hoje: a do último fechamento, ou a da posse."""
        if self.approvals:
            return self.approvals[-1].satisfaction
        start = self.term.satisfaction if self.term else {}
        return {g: start.get(g, NEUTRAL_SATISFACTION) for g in VoterGroup}

    def house_on(self, day: date) -> house.House:
        """A casa em exercício no dia: a última cuja posse já chegou, ou a inicial do computador."""
        seated = [e for e in self.houses if e.takes_office <= day]
        return seated[-1].house if seated else house.initial_house()

    def deals_in_force(self, day: date) -> list[Deal]:
        """Os acordos que valem no dia, na ordem em que foram propostos."""
        return [d for d in self.deals.values() if d.in_force(day)]

    def deal_of(self, bloc_key: int, day: date) -> Deal | None:
        """O acordo em vigor da bancada no dia."""
        return next(
            (d for d in self.deals_in_force(day) if d.bloc_key == bloc_key), None
        )

    def pending_deal_of(self, bloc_key: int) -> Deal | None:
        return next(
            (
                d
                for d in self.deals.values()
                if d.bloc_key == bloc_key and d.status is DealStatus.PENDING
            ),
            None,
        )

    def amendments_on(self, day: date) -> Decimal:
        """
        O que os acordos pagam no fechamento do mês que acaba em `day`, em fração do PIB por
        ano. Conta o que vigorava na véspera: o fechamento nunca depende de um fato do
        próprio dia, que na partida rodando pode vir depois dele.
        """
        return deal_rules.amendments(self.deals.values(), day - timedelta(days=1))

    def last_refusal(self, bloc_key: int) -> date | None:
        """O dia da última recusa da bancada, para a espera até a próxima proposta."""
        days = [
            d.answered
            for d in self.deals.values()
            if d.bloc_key == bloc_key
            and d.status is DealStatus.DECLINED
            and d.answered is not None
        ]
        return max(days, default=None)

    def elected_house(self) -> ElectedHouse | None:
        """A última casa eleita, tenha ou não tomado posse."""
        return self.houses[-1] if self.houses else None

    def advance(self, day: date) -> None:
        """Leva o apoio de campanha de todos os partidos até `day`, aplicando a queda do tempo."""
        for party in self.parties.values():
            party.decay_to(day)

    def month_actions(
        self,
        party_id: int,
        kind: CampaignActionKind,
        group: VoterGroup | None,
        day: date,
    ) -> list[CampaignRecord]:
        """
        As vezes que o partido fez a mesma ação no mesmo grupo no mês de `day`, da mais antiga
        à mais nova; a contagem recomeça no dia seguinte ao 1º turno.
        """
        since = date(day.year, day.month, 1)
        if self.race_started is not None:
            since = max(since, self.race_started + timedelta(days=1))
        return [
            a
            for a in self.actions
            if (a.party_id, a.kind, a.group) == (party_id, kind, group)
            and (a.day.year, a.day.month) == (day.year, day.month)
            and a.day >= since
        ]

    def uses(
        self,
        party_id: int,
        kind: CampaignActionKind,
        group: VoterGroup | None,
        day: date,
    ) -> int:
        """Quantas vezes o partido fez a mesma ação no mesmo grupo no mês de `day`."""
        return len(self.month_actions(party_id, kind, group, day))

    def runoff_total(self, party_id: int) -> Decimal:
        """Quanto o partido já contribuiu no 2º turno."""
        return sum(
            (c.amount for c in self.race_contributions if c.party_id == party_id),
            Decimal(0),
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
                congress=_congress(p, founder),
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
            party = state.parties[_int(p, "party_id")]
            user_id = _int(p, "user_id")
            party.members[user_id] = _money(p, "contribution")
            party.congress = {**party.congress, **_congress(p, user_id)}
        case Event.PARTY_LEFT | Event.MEMBER_EXPELLED:
            _remove_member(state, _int(p, "user_id"))
        case Event.CONTRIBUTION_SET:
            user_id = _int(p, "user_id")
            party = state.party_of(user_id)
            if party is not None:
                party.members[user_id] = _money(p, "contribution")
                party.congress = {**party.congress, **_congress(p, user_id)}
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
            for party_id, amount in _money_map(p, "house").items():
                party = state.parties.get(party_id)
                if party is not None:
                    party.spent += amount
                    party.add_house_campaign(amount)
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
            if state.race is not None:
                state.race.gain(party_id, voters.campaign_points(amount))
            else:
                party.add_campaign(amount)
            state.donations.append(Donation(day, _int(p, "user_id"), party_id, amount))
        case Event.CAMPAIGN_ACTION:
            _apply_action(state, event)
        case Event.RUNOFF_POLL:
            if state.race is not None:
                state.race_polls.append(RunoffPoll(day, state.race.vote()))
        case Event.RUNOFF_ENDORSED:
            _apply_endorsement(state, event)
        case Event.RUNOFF_CONTRIBUTION:
            _apply_runoff_contribution(state, event)
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
            _reset_government(state, day)
        case Event.MEASURE_PROPOSED:
            measure_id = _int(p, "measure_id")
            state.measures[measure_id] = Measure(
                id=measure_id,
                kind=MeasureKind(_str(p, "kind")),
                value=_opt_money(p, "value"),
                before=_opt_money(p, "before"),
                sector=_opt_str(p, "sector"),
                segment=_opt_str(p, "segment"),
                proposer_id=_opt_int(p, "proposer_id"),
                term_start=required(state.term).start,
                proposed=day,
                party_id=required(state.term).party_id,
            )
            state.next_measure_id = max(state.next_measure_id, measure_id + 1)
        case Event.MEASURE_WITHDRAWN:
            state.measures[_int(p, "measure_id")].status = MeasureStatus.WITHDRAWN
        case Event.MEASURE_VOTED:
            measure = state.measures[_int(p, "measure_id")]
            measure.decided = day
            measure.tally = _tally(p)
            if p["approved"]:
                measure.status = MeasureStatus.APPROVED
                measure.effective = day + timedelta(days=VIGENCE_DAYS)
                _move_profile(state, measure, day)
            else:
                measure.status = MeasureStatus.REJECTED
            _move_bloc_profiles(state, measure, day)
        case Event.APPROVAL_MEASURED:
            satisfaction = _satisfaction(p, "satisfaction")
            state.approvals.append(ApprovalPoint(day, satisfaction))
            state.low_streak = _int(p, "low_streak")
            state.last_measured = date.fromisoformat(_str(p, "month"))
            _remember_month(state, satisfaction, day)
        case Event.IMPEACHED:
            _apply_impeachment(state, event)
        case Event.HOUSE_ELECTED:
            _apply_house(state, event)
        case Event.BLOC_GUIDED:
            state.orientations.setdefault(_str(p, "ref"), {})[_int(p, "party_id")] = (
                bool(p["yes"])
            )
        case Event.GUIDANCE_RULE_SET:
            state.parties[_int(p, "party_id")].guidance[
                VoterValue(_str(p, "value"))
            ] = bool(p["yes"])
        case Event.IMPEACHMENT_REQUESTED:
            state.request = ImpeachmentRequest(
                day, date.fromisoformat(_str(p, "vote_day"))
            )
        case Event.IMPEACHMENT_VOTED:
            _apply_impeachment_vote(state, event)
        case Event.DEAL_PROPOSED:
            _apply_deal_proposed(state, event)
        case Event.DEAL_ANSWERED:
            _apply_deal_answered(state, event)
        case Event.DEAL_WITHDRAWN:
            state.deals[_int(p, "deal_id")].status = DealStatus.WITHDRAWN
        case Event.DEAL_BROKEN:
            _apply_deal_broken(state, event)
        case Event.PROMISES_SET:
            _apply_promises_set(state, event)
        case Event.PROMISES_WEIGHED:
            _apply_promises_weighed(state, event)
        case Event.PROMISES_SETTLED:
            _apply_promises_settled(state, event)


def _reset_government(state: GovernmentState, day: date) -> None:
    """Um governo novo começa sem a fila do anterior e sem o histórico de aprovação."""
    for measure in state.measures.values():
        if measure.status is MeasureStatus.QUEUED:
            measure.status = MeasureStatus.DROPPED
    state.approvals = []
    state.low_streak = 0
    state.request = None
    state.orientations.pop("impeachment", None)
    _cut_deals(state, day)


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
    # Sem vice, governa o partido do computador com mais cadeiras; nulo, o governo neutro
    state.term = Term(
        party_id=(
            term.party_id
            if successor is not None
            else _opt_int(event.payload, "party_id")
        ),
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
    _reset_government(state, event.event_date)


def _cut_deals(state: GovernmentState, day: date) -> None:
    """Um governo novo herda uma base vazia: os acordos acabam sem quebra e as propostas caem."""
    for deal in state.deals.values():
        if deal.status is DealStatus.ACTIVE:
            deal.status = DealStatus.CUT
            if deal.end is not None:
                deal.end = min(deal.end, day - timedelta(days=1))
        elif deal.status is DealStatus.PENDING:
            deal.status = DealStatus.WITHDRAWN


def _apply_deal_proposed(state: GovernmentState, event: GovernmentEventDTO) -> None:
    p = event.payload
    deal_id = _int(p, "deal_id")
    answer_by = _opt_str(p, "answer_by")
    state.deals[deal_id] = Deal(
        id=deal_id,
        bloc_key=_int(p, "bloc_key"),
        party_id=_opt_int(p, "party_id"),
        abbr=_str(p, "abbr"),
        seats=_int(p, "seats"),
        ratio=_money(p, "ratio"),
        proposed=event.event_date,
        proposer_id=_int(p, "proposer_id"),
        answer_by=date.fromisoformat(answer_by) if answer_by else None,
    )
    state.next_deal_id = max(state.next_deal_id, deal_id + 1)


def _apply_deal_answered(state: GovernmentState, event: GovernmentEventDTO) -> None:
    """A resposta aceita abre o acordo (e encerra o anterior da mesma bancada, que a renovação substitui); a recusada guarda o dia."""
    p = event.payload
    day = event.event_date
    deal = state.deals[_int(p, "deal_id")]
    deal.answered = day
    if not p["accepted"]:
        deal.status = DealStatus.DECLINED
        return
    for old in state.deals.values():
        if old.bloc_key == deal.bloc_key and old.status is DealStatus.ACTIVE:
            old.status = DealStatus.CUT
            old.end = day - timedelta(days=1)
    deal.status = DealStatus.ACTIVE
    deal.start = day
    deal.end = date.fromisoformat(_str(p, "end"))


def _apply_deal_broken(state: GovernmentState, event: GovernmentEventDTO) -> None:
    """
    O acordo acaba na hora. Quando o governo para de pagar, os grupos do aliado somam
    rejeição ao partido do presidente; quando o aliado rompe, os grupos do governo somam
    rejeição ao aliado.
    """
    p = event.payload
    day = event.event_date
    deal = state.deals[_int(p, "deal_id")]
    deal.status = DealStatus.BROKEN
    deal.end = day
    deal.broken_by = DealBreaker(_str(p, "by"))
    current = state.house_on(day)
    term = state.term
    governing = current.of_party(term.party_id) if term and term.party_id else None
    ally = current.bloc(deal.bloc_key)
    default_mix = dict(voters.WEIGHTS)
    if deal.broken_by is DealBreaker.GOVERNMENT:
        victim = state.parties.get(term.party_id) if term and term.party_id else None
        mix = ally.mix if ally is not None else default_mix
    else:
        victim = state.parties.get(deal.party_id) if deal.party_id else None
        mix = governing.mix if governing is not None else default_mix
    if victim is None:
        return
    for group, amount in deal_rules.break_rejection(mix).items():
        victim.rejection[group] = voters.add_rejection(victim.rejection[group], amount)


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
    party.congress.pop(user_id, None)
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
        groups=_group_votes(p),
        not_voted=Decimal(str(p.get("not_voted", 0))),
    )
    state.results.append(result)
    # Sem finalistas ninguém concorreu: o governo continua do computador
    if winner is None and result.finalists:
        state.runoff = result.finalists
        if len(result.finalists) == 2:
            _start_race(state, result, tickets)
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
    state.race = None
    state.race_started = None
    state.race_polls = []
    state.race_contributions = []
    state.declarations = []
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
    affected_groups = [group] if group else list(VoterGroup)
    if state.race is not None:
        # Entre os turnos o efeito mexe no voto do grupo, e o ataque que sai pela culatra
        # tira votos de quem atacou
        if result.support != 0:
            state.race.gain(record.target_id, result.support, affected_groups)
    elif target is not None and result.support != 0:
        for affected in affected_groups:
            target.campaign[affected] += result.support
    if group is not None and result.rejection != 0:
        party.rejection[group] = voters.clamp(party.rejection[group] + result.rejection)
        if result.rejection < 0:
            party.repaired[group] += -result.rejection


def _party_net(party: Party, group: VoterGroup) -> Decimal:
    """A afinidade do grupo com o partido (com a que as promessas cumpridas somaram) menos a rejeição."""
    return (
        voters.affinity(group, party.radar)
        + party.loyalty[group]
        - party.rejection[group]
    )


def _start_race(
    state: GovernmentState, result: RoundResult, tickets: dict[int, Ticket]
) -> None:
    """O 1º turno sem vencedor abre o 2º: a transferência dos eliminados é calculada ali."""
    running = [state.parties[pid] for pid in tickets if pid in state.parties]
    state.race = second_round.start(
        {p.id: p.standings() for p in running},
        {p.id: {g: _party_net(p, g) for g in VoterGroup} for p in running},
        (result.finalists[0], result.finalists[1]),
    )
    state.race_started = result.day
    state.race_polls = []
    state.race_contributions = []
    state.declarations = []


def _apply_endorsement(state: GovernmentState, event: GovernmentEventDTO) -> None:
    """O eliminado declara apoio (ou neutralidade) uma vez; os indecisos dele seguem pela confiança."""
    p = event.payload
    race = state.race
    party = state.parties.get(_int(p, "party_id"))
    if race is None or party is None or party.id in race.endorsements:
        return
    endorsed = _opt_int(p, "endorsed_id")
    trust = {
        g: second_round.trust(
            voters.affinity(g, party.radar) + party.loyalty[g], party.rejection[g]
        )
        for g in VoterGroup
    }
    race.endorse(party.id, endorsed, trust)
    state.declarations.append(
        Declaration(event.event_date, party.id, _opt_int(p, "user_id"), endorsed)
    )


def _apply_runoff_contribution(
    state: GovernmentState, event: GovernmentEventDTO
) -> None:
    """A contribuição única rende a diferença da raiz do total do partido, em todos os grupos."""
    p = event.payload
    race = state.race
    party = state.parties.get(_int(p, "party_id"))
    if race is None or party is None:
        return
    amount = _money(p, "amount")
    before = state.runoff_total(party.id)
    state.race_contributions.append(
        RunoffContribution(event.event_date, _opt_int(p, "user_id"), party.id, amount)
    )
    party.spent += amount
    race.gain(party.id, second_round.contribution_points(before + amount, before))


def _group_votes(p: dict[str, object]) -> dict[VoterGroup, voters.GroupVote]:
    """O voto por grupo guardado no 2º turno; ausente nos eventos antigos, vazio."""
    stored = p.get("groups") or {}
    return {
        VoterGroup(group): voters.GroupVote(
            shares=_money_map(value, "shares"),
            undecided=Decimal(str(value["undecided"])),
        )
        for group, value in stored.items()  # type: ignore[attr-defined]
    }


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
    previous = party.promises
    party.promises = new
    # Entre os turnos a promessa acrescentada rende na hora, no voto de cada grupo
    if state.race is not None and party.id in state.race.finalists:
        for group in VoterGroup:
            gained = promises.campaign_yield(
                new, group, party.rejection[group]
            ) - promises.campaign_yield(previous, group, party.rejection[group])
            if gained != 0:
                state.race.gain(party.id, gained, [group])


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


def _support_allies(state: GovernmentState, governing: set[int], day: date) -> None:
    """Cada mês de acordo soma apoio ao partido aliado nos grupos dele; o apoio cai pela metade em 3 meses, como o do mandato."""
    current = state.house_on(day)
    for deal in state.deals_in_force(day):
        party = state.parties.get(deal.party_id) if deal.party_id else None
        bloc = current.bloc(deal.bloc_key)
        if party is None or bloc is None or party.id in governing:
            continue
        for group, points in deal_rules.month_support(bloc.mix).items():
            party.term_support[group] = (
                party.term_support[group] * voters.SUPPORT_MONTHLY_KEEP + points
            )


def _remember_month(
    state: GovernmentState, satisfaction: dict[VoterGroup, Decimal], day: date
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
    _support_allies(state, set(governing), day)


def _apply_house(state: GovernmentState, event: GovernmentEventDTO) -> None:
    """A casa eleita no 1º turno; a campanha do Congresso acaba com a eleição."""
    p = event.payload
    blocs = tuple(
        house.Bloc(
            key=_int(b, "key"),
            party_id=_opt_int(b, "party_id"),
            abbr=_str(b, "abbr"),
            name=_str(b, "name"),
            color=_opt_str(b, "color"),
            is_computer=bool(b["is_computer"]),
            votes=_money(b, "votes"),
            seats=_int(b, "seats"),
            mix={VoterGroup(g): Decimal(str(v)) for g, v in _dict_of(b, "mix").items()},
        )
        for b in _dict_list(p, "blocs")
    )
    state.houses.append(
        ElectedHouse(
            day=event.event_date,
            takes_office=date.fromisoformat(_str(p, "takes_office")),
            cycle=_int(p, "cycle"),
            house=house.House(
                blocs,
                below=tuple(int(k) for k in _list(p, "below")),  # type: ignore[call-overload]
                last=_money(p, "last"),
                upcoming=_money(p, "upcoming"),
            ),
        )
    )
    for party in state.parties.values():
        party.reset_house_campaign()


def _apply_impeachment_vote(state: GovernmentState, event: GovernmentEventDTO) -> None:
    p = event.payload
    request = state.request
    approved = bool(p["approved"])
    state.impeachment_votes.append(
        ImpeachmentVote(
            day=event.event_date,
            opened=request.opened if request else event.event_date,
            president_id=state.term.president_id if state.term else None,
            tally=_tally(p) or house.Tally(0, 0, {}),
            approved=approved,
        )
    )
    state.request = None
    state.orientations.pop("impeachment", None)
    # Sem os votos para derrubar, a contagem de meses abaixo do piso recomeça do zero
    if not approved:
        state.low_streak = 0


def _move_bloc_profiles(state: GovernmentState, measure: Measure, day: date) -> None:
    """A bancada que o líder orientou a votar Sim move o perfil do partido, como aprovar a medida."""
    if measure.tally is None:
        return
    governing = state.term.party_id if state.term else None
    for key, vote in measure.tally.blocs.items():
        party = state.parties.get(key) if key > 0 else None
        if party is None or party.is_computer or key == governing:
            continue
        if vote.orientation:
            _move_party_profile(party, measure, day)


def _move_profile(state: GovernmentState, measure: Measure, day: date) -> None:
    """A medida aprovada move o perfil do partido que governa; o do computador não muda."""
    term = state.term
    party = state.parties.get(term.party_id) if term and term.party_id else None
    if party is None or party.is_computer:
        return
    _move_party_profile(party, measure, day)


def _move_party_profile(party: Party, measure: Measure, day: date) -> None:
    if measure.kind.is_spending:
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


def _congress(p: dict[str, object], user_id: int) -> dict[int, Decimal]:
    """A parte da contribuição que vai ao Congresso; ausente no evento, zero."""
    return {user_id: Decimal(str(p.get("congress") or 0))}


def _tally(p: dict[str, object]) -> house.Tally | None:
    """A votação guardada no evento; ausente nos eventos de antes da casa existir."""
    blocs = p.get("blocs")
    if blocs is None:
        return None
    return house.Tally(
        yes=_int(p, "yes"),
        no=_int(p, "no"),
        blocs={
            int(key): house.BlocVote(
                seats=_int(b, "seats"),
                orientation=bool(b["orientation"]),
                yes=_int(b, "yes"),
                no=_int(b, "no"),
                defected=_int(b, "defected"),
                cause=VoterGroup(str(b["cause"])) if b.get("cause") else None,
            )
            for key, b in _dict(p, "blocs").items()
        },
    )


def _dict_of(p: dict[str, object], key: str) -> dict[str, object]:
    return p[key]  # type: ignore[return-value]


def _dict_list(p: dict[str, object], key: str) -> list[dict[str, object]]:
    return p[key]  # type: ignore[return-value]


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
    # Partidas gravadas antes da campanha do Congresso não têm o mapa `house`
    return {int(k): Decimal(str(v)) for k, v in dict(p.get(key) or {}).items()}  # type: ignore[call-overload]
