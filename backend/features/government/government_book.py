"""
Dono do estado político da partida: recebe as ações dos jogadores, roda o calendário
da eleição a cada pregão e grava cada fato como evento. O estado nasce do replay dos
eventos e só muda por `_emit`, que grava o evento e o aplica.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from backend.core import repository
from backend.core.dto.events.government import GovernmentEventDTO
from backend.core.dto.government import (
    PARTY_ABBR_PATTERN,
    MeasureHoldingDTO,
    MeasurePreviewDTO,
    ValueMoveDTO,
)
from backend.core.dto.pending import PendingDTO
from backend.core.dto.promises import PromiseRequest
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CampaignActionKind,
    CashflowEventType,
    ComputerDifficulty,
    GovernmentEventType,
    GovernmentNoticeKind,
    GroupVerdict,
    MeasureKind,
    MeasureStatus,
    PauseReason,
    PendingType,
    VoterGroup,
    VoterValue,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.utils import next_business_day, required
from backend.features.economy.growth import MacroCourse
from backend.features.government import approval as approval_rules
from backend.features.government import budget as budget_rules
from backend.features.government import (
    budget_panel,
    campaign,
    congress,
    election,
    headlines,
    house,
    promises,
    second_round,
    spending,
    spending_panel,
    voters,
)
from backend.features.government import measures as rules
from backend.features.government.budget import BudgetCourse
from backend.features.government.calendar import ElectionCycle, election_cycle
from backend.features.government.computer_parties import (
    COMPUTER_FLAGS,
    COMPUTER_PARTIES,
)
from backend.features.government.measures import PolicyTimeline
from backend.features.government.promises import Promise
from backend.features.government.spending import SpendingTimeline
from backend.features.government.spending_effects import SpendingEconomy
from backend.features.government.state import (
    VIGENCE_DAYS,
    CampaignRecord,
    GovernmentState,
    Measure,
    Party,
    apply,
    replay,
)
from backend.features.notifications import registry
from backend.features.notifications.news import Headline
from backend.features.realtime import notify
from backend.features.realtime.schemas import GovernmentUpdateEventDTO
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.tax_policy import TaxPolicy

logger = logging.getLogger(__name__)

# A orientação do pedido de impeachment aberto; a das medidas é "measure:<id>"
IMPEACHMENT_REF = "impeachment"


def measure_ref(measure_id: int | None) -> str:
    """A chave da votação em que o líder orienta: a medida ou, sem id, o pedido de impeachment."""
    return IMPEACHMENT_REF if measure_id is None else f"measure:{measure_id}"


# Pontos somados a um setor vão até 20 pontos
SECTOR_EXTRA_LIMIT = Decimal("0.2")


@dataclass(frozen=True)
class CampaignResult:
    """A ação rolada e o apoio e a rejeição de antes, no grupo que ela atingiu."""

    record: CampaignRecord
    # Apoio de quem a ação atinge e rejeição do partido que agiu, antes de rolar; nulos na TV
    support_before: Decimal | None
    rejection_before: Decimal | None


class GovernmentBook:
    def __init__(
        self,
        settings: SimulationDTO,
        engine: SimulationEngine,
        on_office: Callable[[UserDTO, date], None],
        on_news: Callable[[date, Headline], None],
        random_seed: int,
        macro: MacroCourse | None = None,
    ):
        """
        `on_office` roda na posse de cada presidente jogador: a carteira dele congela.
        `on_news` publica no jornal da partida a manchete de cada fato político.
        `macro` é o crescimento e o desemprego do país, que o orçamento e a aprovação leem.
        """
        self._settings = settings
        self._engine = engine
        self._on_office = on_office
        self._on_news = on_news
        self._seed = random_seed
        self._first_election = required(settings.first_election)
        self._factor = settings.computer_difficulty.budget_factor
        self.state: GovernmentState = replay(
            repository.government.get_events(settings.id)
        )
        self._previous_day: date | None = None
        self._people: dict[int, UserDTO] = {}
        self._timeline = PolicyTimeline(self.state.measures.values())
        self._spending = SpendingTimeline(self.state.measures.values())
        # As séries e os preços da partida levam o efeito das medidas de gasto aprovadas
        self._economy = SpendingEconomy(settings.id, settings.start_date)
        self._economy.update(self.state.measures.values())
        repository.economic.use_adjustment(settings.id, self._economy)
        # O orçamento lê a política e o gasto de cada dia e a conta de largada da sala
        self._macro = macro or MacroCourse(settings.start_date)
        self._macro.use_spending(self._economy.growth_points)
        self._budget = BudgetCourse(
            settings.start_date,
            self.policy,
            budget_rules.initial_account(settings.start_date, settings.initial_account),
            self._macro,
            self.spending_on,
        )
        # O engine lê os impostos e o prêmio de risco de cada dia do governo
        engine.use_tax_policy(self.policy)
        engine.use_risk_premium(self._budget.premium_on)

    def budget(self) -> BudgetCourse:
        return self._budget

    def latest_policy(self) -> TaxPolicy:
        """A política depois de todas as medidas aprovadas valerem."""
        return self._timeline.latest

    def policy_before(self, measure: Measure) -> TaxPolicy:
        """A política em que a medida cai: a do dia anterior à vigência, ou a final para a que ainda não vale."""
        if measure.status is MeasureStatus.APPROVED and measure.effective is not None:
            return self.policy(measure.effective - timedelta(days=1))
        return self._timeline.latest

    def risk_premium_on(self, day: date) -> Decimal:
        return self._budget.premium_on(day)

    def economy(self) -> SpendingEconomy:
        return self._economy

    def spending_timeline(self) -> SpendingTimeline:
        return self._spending

    def spending_on(self, day: date) -> Decimal:
        """O gasto total do governo no dia, em fração do PIB por ano."""
        return self._spending.spending_on(day)

    def value_in_force(self, kind: MeasureKind, day: date) -> Decimal | None:
        """O valor que a medida geral tem no país no dia; nulo na medida de setor."""
        if kind.is_spending:
            return self._spending.value_on(kind, day)
        return rules.general_value(self.policy(day), kind)

    def latest_value(self, kind: MeasureKind) -> Decimal | None:
        """O valor da medida geral depois de todas as aprovadas valerem."""
        if kind.is_spending:
            return self._spending.latest(kind)
        return rules.general_value(self._timeline.latest, kind)

    # Impostos e carteira do presidente

    def policy(self, day: date) -> TaxPolicy:
        """A política de impostos que vale no dia: a padrão mais as medidas já em vigor."""
        return self._timeline.on(day)

    def term_end(self) -> date | None:
        """O último dia do mandato em curso: a véspera da próxima posse."""
        if self.state.term is None:
            return None
        pending = self.state.pending_term
        # Eleito o sucessor, a posse dele já está marcada; antes disso, a da próxima eleição
        inauguration = pending.start if pending else self.cycle().inauguration
        return inauguration - timedelta(days=1)

    def president(self) -> UserDTO | None:
        term = self.state.term
        if term is None or term.president_id is None:
            return None
        return self._people.get(term.president_id)

    def ensure_can_trade(self, client_id: UUID) -> None:
        """A carteira do presidente fica congelada até o fim do mandato."""
        president = self.president()
        if president is None or president.client_id != client_id:
            return
        end = required(self.term_end())
        raise ConflictError(
            "Presidente não compra nem vende enquanto governa: sua carteira volta a "
            f"operar em {rules.short_date(end + timedelta(days=1))}."
        )

    def approval(self, today: date) -> approval_rules.Approval | None:
        """A satisfação de hoje e o alvo de cada grupo; só existe sob um presidente jogador."""
        term = self.state.term
        if term is None or term.president_id is None:
            return None
        return approval_rules.assess(
            term,
            self.state.satisfaction,
            self.state.measures.values(),
            approval_rules.market_on(
                today,
                self._macro.latest(today).unemployment,
                self._budget.premium_on(today),
            ),
            today,
        )

    def pending(self, user: UserDTO, today: date) -> list[PendingDTO]:
        """Risco de impeachment (só o presidente), convite de vice e campanha aberta sem filiação."""
        items: list[PendingDTO] = []
        if risk := self._impeachment_risk(user, today):
            items.append(risk)
        items.extend(self._unguided_votes(user, today))
        if not self._ticket_open(today):
            return items
        party = next(
            (
                p
                for p in self.state.player_parties()
                if p.vice_id == user.id and not p.vice_accepted
            ),
            None,
        )
        if party is not None:
            founder = self._people.get(party.founder_id) if party.founder_id else None
            items.append(
                registry.pending(
                    PendingType.VICE_INVITE,
                    f"{founder.nickname if founder else party.name} quer você na chapa do {party.abbr}",
                )
            )
        if self.state.party_of(user.id) is None and not user.is_bot:
            items.append(
                registry.pending(
                    PendingType.CAMPAIGN_OPEN,
                    f"As chapas fecham em {self.cycle().ticket_deadline:%d/%m}",
                )
            )
        return items

    def _unguided_votes(self, user: UserDTO, today: date) -> list[PendingDTO]:
        """Uma pendência por votação aberta em que o líder ainda não orientou a bancada."""
        party = self.state.party_of(user.id)
        if party is None or party.founder_id != user.id:
            return []
        bloc = self.state.house_on(today).of_party(party.id)
        if bloc is None or bloc.seats == 0:
            return []
        items = []
        vote_day = congress.next_vote_date(today)
        for measure in self._queue():
            orientation, guided, _ = self.measure_orientations(measure, today)
            if not guided.get(bloc.key, False):
                items.append(
                    self._unguided_item(
                        rules.title(measure),
                        vote_day,
                        party,
                        orientation[bloc.key],
                        measure_ref(measure.id),
                    )
                )
        request = self.state.request
        if request is not None:
            orientation, guided, _ = self.impeachment_orientations(today)
            if not guided.get(bloc.key, False):
                items.append(
                    self._unguided_item(
                        "Pedido de impeachment",
                        request.vote_day,
                        party,
                        orientation[bloc.key],
                        IMPEACHMENT_REF,
                    )
                )
        return [item for item in items if item is not None]

    def _unguided_item(
        self, title: str, vote_day: date, party: Party, standard: bool, ref: str
    ) -> PendingDTO:
        return registry.pending(
            PendingType.UNGUIDED_VOTE,
            f"{title} · a casa vota em {vote_day:%d/%m}. Sem você, o {party.abbr} "
            f"vota pelo padrão: {'Sim' if standard else 'Não'}.",
            ref=ref,
        )

    def _ticket_open(self, today: date) -> bool:
        """A campanha está aberta e as chapas ainda não fecharam."""
        cycle = self.cycle()
        return (
            self.state.runoff is None
            and self.state.pending_term is None
            and cycle.campaign_start <= today <= cycle.ticket_deadline
        )

    def _impeachment_risk(self, user: UserDTO, today: date) -> PendingDTO | None:
        term = self.state.term
        if term is None or term.president_id != user.id:
            return None
        current = required(self.approval(today))
        if approval_rules.in_grace(term, today.replace(day=1)):
            return None
        streak = self.state.low_streak
        if (
            streak == 0
            and current.value >= approval_rules.FLOOR + approval_rules.RISK_MARGIN
        ):
            return None
        floor = approval_rules.FLOOR
        months = approval_rules.IMPEACHMENT_MONTHS
        detail = (
            f"Aprovação em {current.value}% e {streak} de {months} fechamentos abaixo de {floor}%"
            if streak
            else f"Aprovação em {current.value}%; {months} fechamentos abaixo de {floor}% abrem o pedido de impeachment"
        )
        return registry.pending(PendingType.IMPEACHMENT_RISK, detail)

    def tickers(self, measure: Measure) -> list[str]:
        """Os ativos que a medida de setor atinge."""
        if not measure.kind.is_sector:
            return []
        return sorted(
            ticker
            for ticker, located in self._engine.classification.items()
            if located.sector == measure.sector
            and measure.segment in (None, located.segment)
        )

    # Calendário

    @property
    def seed(self) -> int:
        """A semente da partida: sorteia o voto do Congresso e o erro das pesquisas."""
        return self._seed

    def cycle(self, index: int | None = None) -> ElectionCycle:
        """A eleição em curso (ou a de índice `index`)."""
        return election_cycle(
            self._first_election,
            self.state.cycle if index is None else index,
            self._settings.start_date,
        )

    def on_tick(
        self, users: list[UserDTO], today: date, month_changed: bool
    ) -> PauseReason | None:
        """
        Roda o calendário do dia: posse, contribuição do mês, fechamento do mês do governo
        e apuração. Devolve o motivo da pausa quando o dia trouxe a abertura da campanha,
        um resultado de turno ou um impeachment, que pausam a partida para todos.
        """
        people = {user.id: user for user in users}
        self._people = people
        # O apoio de campanha chega ao dia de hoje com a queda do tempo aplicada
        self.state.advance(today)
        previous, self._previous_day = self._previous_day, today
        self._settle_term_end(today)
        pending = self.state.pending_term
        if pending is not None and today >= pending.start:
            self._start_term(today, people)

        cycle = self.cycle()
        self._weigh_promises(cycle, today)
        campaign_opened = self._announce_calendar(cycle, previous, today)
        self._announce_in_force(previous, today)
        if (
            month_changed
            and self.state.runoff is None
            and cycle.campaign_start <= today < cycle.first_round
        ):
            self._collect(people, today)

        if self._close_month(today):
            return PauseReason.IMPEACHMENT

        if self.state.runoff is not None:
            if today >= cycle.runoff:
                self._hold_runoff(cycle, today)
                return PauseReason.RUNOFF_RESULT
            self._run_between_rounds(cycle, today)
        elif today >= cycle.first_round:
            self._hold_first_round(cycle, today)
            return PauseReason.FIRST_ROUND_RESULT
        return PauseReason.CAMPAIGN_OPENED if campaign_opened else None

    def _announce_calendar(
        self, cycle: ElectionCycle, previous: date | None, today: date
    ) -> bool:
        """
        Avisa a sala dos marcos do calendário: a abertura da campanha (que pausa a partida),
        os lembretes das chapas e da véspera do 1º turno e a página que renova quando as
        chapas fecham. Devolve se a campanha abriu hoje.
        """
        if previous is None:
            # Numa partida nova o primeiro dia simulado é o primeiro dia útil da data inicial,
            # e a campanha que já abre nele também é anunciada; numa retomada não há o que anunciar
            first_day = next_business_day(self._settings.start_date - timedelta(days=1))
            if today != first_day:
                return False
            previous = self._settings.start_date - timedelta(days=1)

        if previous < cycle.campaign_start <= today:
            self._notice(
                GovernmentNoticeKind.CAMPAIGN_OPENED,
                ticket_deadline=cycle.ticket_deadline,
                first_round=cycle.first_round,
            )
            self._on_news(
                today,
                headlines.campaign_opened(cycle.first_round, cycle.ticket_deadline),
            )
            return True
        if previous < cycle.ticket_deadline + timedelta(days=1) <= today:
            self._notice(GovernmentNoticeKind.UPDATED)
            self._on_news(
                today,
                headlines.tickets_closed(
                    self._tickets(), (cycle.first_round - today).days
                ),
            )
        if previous < cycle.ticket_reminder <= today:
            self._on_news(today, headlines.tickets_closing(cycle.ticket_deadline))
            self._notice(
                GovernmentNoticeKind.TICKETS_CLOSING,
                ticket_deadline=cycle.ticket_deadline,
                first_round=cycle.first_round,
            )
        if previous < cycle.eve <= today:
            self._on_news(today, headlines.election_eve(cycle.first_round))
            self._notice(
                GovernmentNoticeKind.ELECTION_EVE,
                ticket_deadline=cycle.ticket_deadline,
                first_round=cycle.first_round,
            )
        return False

    # Ações dos jogadores

    def found_party(
        self,
        user: UserDTO,
        today: date,
        *,
        name: str,
        abbr: str,
        color: str,
        flags: list[VoterValue],
        contribution: Decimal,
        congress: Decimal = Decimal(0),
    ) -> None:
        self._ensure_person(user)
        self._ensure_campaign_open(today)
        self._ensure_without_party(user)
        self._ensure_valid_flags(flags)
        self._ensure_split(contribution, congress)
        if not PARTY_ABBR_PATTERN.match(abbr):
            raise UnprocessableEntityError("A sigla tem de 2 a 8 letras.")
        parties = self.state.parties.values()
        if abbr in house.COMPUTER_KEYS or any(p.abbr == abbr for p in parties):
            raise ConflictError(f"Já existe um partido com a sigla {abbr}.")
        if any(p.name.casefold() == name.casefold() for p in parties):
            raise ConflictError("Já existe um partido com esse nome.")
        if any(p.color and p.color.lower() == color.lower() for p in parties):
            raise ConflictError("Essa cor já é de outro partido.")
        self._emit(
            GovernmentEventType.PARTY_FOUNDED,
            today,
            party_id=self.state.next_party_id,
            name=name,
            abbr=abbr,
            color=color.lower(),
            flags=[v.value for v in flags],
            founder_id=user.id,
            contribution=str(contribution),
            congress=str(congress),
        )
        self._ensure_computers(today)
        self._notice(GovernmentNoticeKind.PARTY_FOUNDED, user, party_abbr=abbr)
        self._on_news(today, headlines.party_founded(user.nickname, abbr, name))

    def set_flags(self, user: UserDTO, today: date, flags: list[VoterValue]) -> None:
        """O fundador do partido sem bandeiras escolhe as 3; depois elas não mudam mais."""
        party = self._founded_party(user)
        if party.flags is not None:
            raise ConflictError("As bandeiras do partido já foram escolhidas.")
        self._ensure_valid_flags(flags)
        self._emit(
            GovernmentEventType.PARTY_VALUES_SET,
            today,
            party_id=party.id,
            flags=[v.value for v in flags],
        )
        self._notice(GovernmentNoticeKind.UPDATED, user, party_abbr=party.abbr)

    def _ensure_valid_flags(self, flags: list[VoterValue]) -> None:
        if not voters.is_valid_flags(flags):
            raise UnprocessableEntityError(
                "Escolha 3 bandeiras diferentes; Mercado livre e Justiça social não "
                "andam juntas."
            )

    def join_party(
        self,
        user: UserDTO,
        today: date,
        party_id: int,
        contribution: Decimal,
        congress: Decimal = Decimal(0),
    ) -> None:
        self._ensure_person(user)
        self._ensure_campaign_open(today)
        self._ensure_without_party(user)
        self._ensure_split(contribution, congress)
        party = self._party(party_id)
        if party.is_computer:
            raise ConflictError("O partido do computador não aceita filiados.")
        self._emit(
            GovernmentEventType.PARTY_JOINED,
            today,
            party_id=party.id,
            user_id=user.id,
            contribution=str(contribution),
            congress=str(congress),
        )
        self._ensure_computers(today)
        self._notice(GovernmentNoticeKind.UPDATED, user, party_abbr=party.abbr)

    def leave_party(self, user: UserDTO, today: date) -> None:
        self._ensure_membership_open()
        party = self._my_party(user)
        self._emit(GovernmentEventType.PARTY_LEFT, today, user_id=user.id)
        self._ensure_computers(today)
        self._notice(GovernmentNoticeKind.UPDATED, user, party_abbr=party.abbr)

    def set_contribution(
        self,
        user: UserDTO,
        today: date,
        contribution: Decimal,
        congress: Decimal = Decimal(0),
    ) -> None:
        self._ensure_membership_open()
        self._ensure_split(contribution, congress)
        party = self._my_party(user)
        self._emit(
            GovernmentEventType.CONTRIBUTION_SET,
            today,
            user_id=user.id,
            contribution=str(contribution),
            congress=str(congress),
        )
        self._notice(GovernmentNoticeKind.UPDATED, user, party_abbr=party.abbr)

    def _ensure_split(self, contribution: Decimal, congress: Decimal) -> None:
        if not 0 <= congress <= contribution:
            raise UnprocessableEntityError(
                "A parte do Congresso fica entre zero e a contribuição inteira."
            )

    # Congresso: a orientação do líder

    def guide(
        self, user: UserDTO, today: date, measure_id: int | None, yes: bool
    ) -> None:
        """O líder orienta a bancada numa votação aberta, até a véspera; sem `measure_id`, é o pedido de impeachment."""
        party = self._leader_party(user)
        bloc = self.state.house_on(today).of_party(party.id)
        if bloc is None or bloc.seats == 0:
            raise ConflictError("O partido não tem bancada na casa.")
        if measure_id is None:
            request = self.state.request
            if request is None:
                raise ConflictError("Não há pedido de impeachment aberto.")
            vote_day = request.vote_day
        else:
            measure = self._measure(measure_id)
            if measure.status is not MeasureStatus.QUEUED:
                raise ConflictError("A medida já foi votada ou retirada.")
            vote_day = congress.next_vote_date(today)
        if today >= vote_day:
            raise ConflictError("A casa vota hoje: a orientação fechou na véspera.")
        self._emit(
            GovernmentEventType.BLOC_GUIDED,
            today,
            ref=measure_ref(measure_id),
            party_id=party.id,
            yes=yes,
            user_id=user.id,
        )
        self._notice(GovernmentNoticeKind.UPDATED, user, party_abbr=party.abbr)

    def set_guidance_rule(
        self, user: UserDTO, today: date, value: VoterValue, yes: bool
    ) -> None:
        """O líder troca a orientação padrão do partido para um valor."""
        party = self._leader_party(user)
        self._emit(
            GovernmentEventType.GUIDANCE_RULE_SET,
            today,
            party_id=party.id,
            value=value.value,
            yes=yes,
            user_id=user.id,
        )
        self._notice(GovernmentNoticeKind.UPDATED, user, party_abbr=party.abbr)

    def _leader_party(self, user: UserDTO) -> Party:
        party = self._my_party(user)
        if party.founder_id != user.id:
            raise ForbiddenError("Só o líder do partido orienta a bancada.")
        return party

    def effects_of(self, measure: Measure) -> dict[VoterValue, Decimal]:
        """O que a medida avança (+) ou recua (-) nos valores; a de gasto não mexe neles."""
        if measure.kind.is_spending:
            return {}
        return voters.measure_effects(measure.kind, measure.value, measure.before)

    def bloc_orientation(
        self,
        bloc: house.Bloc,
        ref: str,
        default: Callable[[dict[VoterValue, bool]], bool],
    ) -> tuple[bool, bool]:
        """A orientação da bancada numa votação e se o líder a deu; sem ela vale a regra padrão do partido."""
        party_id = bloc.party_id
        chosen = (
            self.state.orientations.get(ref, {}).get(party_id) if party_id else None
        )
        if chosen is not None:
            return chosen, True
        return default(self._bloc_rules(bloc)), False

    def _bloc_rules(self, bloc: house.Bloc) -> dict[VoterValue, bool]:
        """A regra de orientação da bancada: a do partido (do jogador ou do computador) ou, sem partido, Não em tudo."""
        party = self.state.parties.get(bloc.party_id) if bloc.party_id else None
        if party is not None:
            return party.rules
        flags = COMPUTER_FLAGS.get(bloc.abbr) if bloc.is_computer else None
        return house.flag_rules(flags) if flags else house.flag_rules(None)

    def measure_orientations(
        self, measure: Measure, day: date
    ) -> tuple[dict[int, bool], dict[int, bool], dict[int, Decimal]]:
        """Por bancada da casa em exercício: a orientação, se o líder a deu e o que os eleitores querem."""
        effects = self.effects_of(measure)
        by_group = house.reactions(effects)
        proposer = self.state.party_of(measure.proposer_id)
        orientations, guided, wanted = {}, {}, {}
        for bloc in self.state.house_on(day).seated:
            # A bancada do partido que propôs a medida vota Sim sem orientação
            own = proposer is not None and proposer.id == bloc.party_id
            orientations[bloc.key], guided[bloc.key] = self.bloc_orientation(
                bloc,
                measure_ref(measure.id),
                lambda rules, effects=effects, own=own: (
                    own or house.default_orientation(rules, effects)
                ),
            )
            wanted[bloc.key] = house.wants(bloc.mix, by_group)
        return orientations, guided, wanted

    def impeachment_orientations(
        self, day: date
    ) -> tuple[dict[int, bool], dict[int, bool], dict[int, Decimal]]:
        """O mesmo para o pedido de impeachment: pelos eleitores, e a bancada do presidente vota Não."""
        term = self.state.term
        by_group = house.impeachment_reactions(self.state.satisfaction)
        orientations, guided, wanted = {}, {}, {}
        for bloc in self.state.house_on(day).seated:
            mood = house.mood(bloc.mix, self.state.satisfaction)
            governing = term is not None and bloc.party_id == term.party_id
            orientations[bloc.key], guided[bloc.key] = self.bloc_orientation(
                bloc,
                IMPEACHMENT_REF,
                lambda _rules, mood=mood, governing=governing: (
                    not governing and house.impeachment_orientation(mood)
                ),
            )
            wanted[bloc.key] = house.wants(bloc.mix, by_group)
        return orientations, guided, wanted

    def expel(
        self, founder: UserDTO, today: date, nickname: str, users: list[UserDTO]
    ) -> None:
        self._ensure_membership_open()
        party = self._founded_party(founder)
        target = next((u for u in users if u.nickname == nickname), None)
        if target is None or target.id not in party.members:
            raise NotFoundError("Esse jogador não é filiado ao seu partido.")
        if target.id == founder.id:
            raise ConflictError("Você não pode se expulsar do próprio partido.")
        self._emit(
            GovernmentEventType.MEMBER_EXPELLED, today, user_id=target.id, by=founder.id
        )
        self._ensure_computers(today)
        self._notice(
            GovernmentNoticeKind.EXPELLED, founder, target=target, party_abbr=party.abbr
        )
        self._on_news(today, headlines.expelled(target.nickname, party.abbr))

    def set_ticket(
        self,
        founder: UserDTO,
        today: date,
        candidate: str,
        vice: str | None,
        users: list[UserDTO],
    ) -> None:
        self._ensure_membership_open()
        party = self._founded_party(founder)
        if today > self.cycle().ticket_deadline:
            raise ConflictError("A inscrição de chapas já fechou.")
        members = {u.nickname: u for u in users if u.id in party.members}
        candidate_user = members.get(candidate)
        if candidate_user is None:
            raise NotFoundError("O candidato precisa ser filiado ao partido.")
        if not election.is_eligible(self.state, candidate_user.id):
            raise ConflictError(
                f"{candidate} cumpriu dois mandatos seguidos e não concorre de novo."
            )
        rival = election.vice_of_other(self.state, party, candidate_user.id)
        if rival is not None:
            raise ConflictError(f"{candidate} é vice do {rival.abbr} e não concorre.")
        vice_user = (
            self._pick_vice(party, vice, candidate_user, users) if vice else None
        )
        # Quem já aceitou o convite segue aceito se a vaga continua dele
        keeps_vice = (
            vice_user is not None
            and party.vice_accepted
            and party.vice_id == vice_user.id
        )
        self._emit(
            GovernmentEventType.TICKET_SET,
            today,
            party_id=party.id,
            candidate_id=candidate_user.id,
            vice_id=vice_user.id if vice_user else None,
            vice_accepted=keeps_vice,
        )
        if vice_user is not None and not keeps_vice:
            self._notice(
                GovernmentNoticeKind.VICE_INVITED,
                founder,
                target=vice_user,
                party_abbr=party.abbr,
            )
        else:
            self._notice(GovernmentNoticeKind.UPDATED, founder, party_abbr=party.abbr)

    def _pick_vice(
        self,
        party: Party,
        nickname: str,
        candidate: UserDTO,
        users: list[UserDTO],
    ) -> UserDTO:
        """O vice é qualquer jogador da sala que a regra da chapa deixa convidar."""
        person = next((u for u in users if u.nickname == nickname), None)
        if person is None:
            raise NotFoundError("Esse jogador não está na sala.")
        if person.is_bot:
            raise ForbiddenError("Bot não é vice.")
        if person.id == candidate.id:
            raise ConflictError("Candidato e vice precisam ser pessoas diferentes.")
        blocker = election.vice_blocker(self.state, party, person.id)
        if blocker is not None:
            raise ConflictError(f"{nickname} não pode ser vice: {blocker}.")
        return person

    def answer_vice(self, user: UserDTO, today: date, accept: bool) -> None:
        party = next(
            (
                p
                for p in self.state.player_parties()
                if p.vice_id == user.id and not p.vice_accepted
            ),
            None,
        )
        if party is None:
            raise NotFoundError("Você não tem convite de vice para responder.")
        self._emit(
            GovernmentEventType.VICE_ANSWERED, today, party_id=party.id, accepted=accept
        )
        founder = self._people.get(party.founder_id) if party.founder_id else None
        self._notice(
            GovernmentNoticeKind.VICE_ANSWERED,
            user,
            target=founder,
            party_abbr=party.abbr,
            accepted=accept,
        )

    def donate(
        self, user: UserDTO, today: date, party_id: int, amount: Decimal
    ) -> None:
        finalists = self.state.runoff
        if finalists is None:
            raise ConflictError("A doação só abre entre o 1º e o 2º turno.")
        if today > self.cycle().donation_deadline:
            raise ConflictError("O prazo para doar acabou.")
        mine = self._my_party(user)
        if mine.id in finalists:
            raise ConflictError("Só quem ficou de fora doa a um finalista.")
        if party_id not in finalists:
            raise ConflictError("A doação vai para um dos finalistas.")
        if self._engine.get_cash(user.client_id) < amount:
            raise ConflictError("Caixa insuficiente para essa doação.")
        party = self._party(party_id)
        self._engine.pay_campaign(
            user.client_id, amount, CashflowEventType.CAMPAIGN_DONATION
        )
        self._emit(
            GovernmentEventType.DONATION_MADE,
            today,
            user_id=user.id,
            party_id=party_id,
            amount=str(amount),
        )
        self._notice(
            GovernmentNoticeKind.DONATION,
            user,
            party_abbr=party.abbr,
            amount=amount,
        )
        self._on_news(today, headlines.donation(user.nickname, party.abbr, amount))

    # 2º turno: declaração de apoio e contribuição única

    def endorse(self, user: UserDTO, today: date, endorsed_id: int | None) -> None:
        """
        A fundadora do partido eliminado declara apoio a um finalista, ou neutralidade
        (`endorsed_id` nulo). A declaração é uma só e não se desfaz.
        """
        self._ensure_person(user)
        party = self._founded_party(user)
        race = self._open_race(today)
        if party.id in race.finalists:
            raise ConflictError("Só quem ficou de fora declara apoio.")
        if party.id not in self._eliminated():
            raise ConflictError("Seu partido não disputou o 1º turno.")
        if party.id in race.endorsements:
            raise ConflictError("A declaração de apoio é uma só.")
        if endorsed_id is not None and endorsed_id not in race.finalists:
            raise UnprocessableEntityError("O apoio vai a um dos finalistas.")
        self._emit(
            GovernmentEventType.RUNOFF_ENDORSED,
            today,
            party_id=party.id,
            user_id=user.id,
            endorsed_id=endorsed_id,
        )
        self._notice(
            GovernmentNoticeKind.ENDORSEMENT,
            user,
            party_abbr=party.abbr,
            rival_abbr=self._party_abbr(endorsed_id),
        )
        self._on_news(
            today, headlines.endorsement(party.abbr, self._party_abbr(endorsed_id))
        )

    def contribute_runoff(self, user: UserDTO, today: date, amount: Decimal) -> None:
        """A contribuição única do filiado de um finalista, que vai para a campanha do 2º turno."""
        self._ensure_person(user)
        party = self._my_party(user)
        race = self._open_race(today)
        if party.id not in race.finalists:
            raise ConflictError("Só filiado de finalista contribui; os demais doam.")
        if any(c.user_id == user.id for c in self.state.race_contributions):
            raise ConflictError("A contribuição do 2º turno é uma só.")
        if amount <= 0:
            raise UnprocessableEntityError("Informe um valor maior que zero.")
        if self._engine.get_cash(user.client_id) < amount:
            raise ConflictError("Caixa insuficiente para essa contribuição.")
        self._engine.pay_campaign(
            user.client_id, amount, CashflowEventType.CAMPAIGN_DONATION
        )
        self._emit(
            GovernmentEventType.RUNOFF_CONTRIBUTION,
            today,
            user_id=user.id,
            party_id=party.id,
            amount=str(amount),
        )
        self._notice(
            GovernmentNoticeKind.DONATION,
            user,
            party_abbr=party.abbr,
            amount=amount,
        )

    def _open_race(self, today: date) -> second_round.Race:
        """A disputa do 2º turno, enquanto o prazo de campanha dela vale."""
        race = self.state.race
        if race is None:
            raise ConflictError("Isso só vale entre o 1º e o 2º turno.")
        if today > self.cycle().donation_deadline:
            raise ConflictError("O prazo do 2º turno acabou: a votação é amanhã.")
        return race

    def _eliminated(self) -> set[int]:
        """Os partidos que disputaram o 1º turno e não chegaram ao 2º."""
        result = self.state.results[-1] if self.state.results else None
        if result is None:
            return set()
        return set(result.tickets) - set(self.state.runoff or [])

    # Ações avulsas de campanha

    def campaign_closed_reason(
        self, today: date, party: Party | None = None
    ) -> str | None:
        """Por que as ações não estão abertas hoje (para `party`, quando dada); nulo quando valem."""
        cycle = self.cycle()
        runoff = self.state.runoff
        if runoff is not None:
            if today > cycle.donation_deadline:
                return "As ações valem até a véspera do 2º turno."
            if party is not None and party.id not in runoff:
                return "Entre os turnos só os finalistas fazem ações."
            return None
        if today < cycle.campaign_start:
            return "A campanha ainda não abriu."
        if today >= cycle.first_round:
            return "As ações valem até a véspera do 1º turno."
        return None

    def action_price(self, kind: CampaignActionKind, today: date) -> Decimal:
        """O preço da ação no dia, corrigido pelo IPCA quando a partida corrige os valores."""
        return campaign.price(
            kind,
            self._settings.start_date,
            today,
            self._settings.inflation_adjusted,
        )

    def support_of(self, party: Party, group: VoterGroup) -> Decimal:
        """O apoio do partido no grupo: a pesquisa da campanha, ou o voto dele no 2º turno."""
        race = self.state.race
        if race is not None and party.id in race.finalists:
            return race.groups[group].votes[party.id]
        return party.standing(group).support

    def cash_of(self, user: UserDTO) -> Decimal:
        return self._engine.get_cash(user.client_id)

    def running_parties(self) -> list[Party]:
        """Os partidos que concorrem hoje, do mais antigo ao mais novo."""
        return sorted(self._running(), key=lambda p: p.id)

    def campaign_action(
        self,
        user: UserDTO,
        today: date,
        kind: CampaignActionKind,
        group: VoterGroup | None,
        rival_id: int | None,
    ) -> CampaignResult:
        """
        Dispara uma ação de campanha do partido de `user`: a validação vem antes da
        cobrança, então a ação que falha não cobra nada. O dado sai da semente da partida.
        """
        self._ensure_person(user)
        party = self._my_party(user)
        reason = self.campaign_closed_reason(today, party)
        if reason is not None:
            raise ConflictError(reason)
        rival = self._check_action_target(party, kind, group, rival_id)
        price = self.action_price(kind, today)
        missing = price - self.cash_of(user)
        if missing > 0:
            raise ConflictError(
                f"Caixa insuficiente para essa ação: faltam R$ {missing:,.2f}."
            )
        self._engine.pay_campaign(
            user.client_id, price, CashflowEventType.CAMPAIGN_ACTION
        )
        target = rival or party
        support_before = self.support_of(target, group) if group else None
        rejection_before = party.rejection[group] if group else None
        record = self._emit_action(party, user.id, today, kind, group, rival, price)
        self._notice(
            GovernmentNoticeKind.CAMPAIGN_ACTION,
            user,
            party_abbr=party.abbr,
            campaign_action=kind,
            group=group,
            rival_abbr=rival.abbr if rival else None,
        )
        return CampaignResult(record, support_before, rejection_before)

    def _check_action_target(
        self,
        party: Party,
        kind: CampaignActionKind,
        group: VoterGroup | None,
        rival_id: int | None,
    ) -> Party | None:
        """Confere o grupo e o rival que a ação pede; devolve o rival do ataque."""
        if kind is CampaignActionKind.TV:
            if group is not None:
                raise UnprocessableEntityError("A TV atinge todos os grupos.")
        elif group is None:
            raise UnprocessableEntityError("Escolha o grupo da ação.")
        if kind is not CampaignActionKind.ATTACK:
            if rival_id is not None:
                raise UnprocessableEntityError("Só o ataque tem rival.")
            return None
        rival = self.state.parties.get(rival_id) if rival_id is not None else None
        if rival is None or not election.runs(self.state, rival):
            raise NotFoundError("Escolha um partido rival que esteja na eleição.")
        if rival.id == party.id:
            raise ConflictError("O ataque vai a um partido rival, e não ao seu.")
        if self.state.runoff is not None and rival.id not in self.state.runoff:
            raise ConflictError("No 2º turno o ataque vai ao outro finalista.")
        return rival

    def _emit_action(
        self,
        party: Party,
        user_id: int | None,
        today: date,
        kind: CampaignActionKind,
        group: VoterGroup | None,
        rival: Party | None,
        price: Decimal,
    ) -> CampaignRecord:
        rolls = campaign.roll_dice(self._seed, self.state.next_action_id, kind)
        self._emit(
            GovernmentEventType.CAMPAIGN_ACTION,
            today,
            user_id=user_id,
            party_id=party.id,
            action=kind.value,
            group=group.value if group else None,
            rival_id=rival.id if rival else None,
            price=str(price),
            rolls=list(rolls),
        )
        record = self.state.actions[-1]
        headline = headlines.campaign_action(
            record.id,
            kind,
            record.band,
            party.abbr,
            group,
            rival.abbr if rival else None,
        )
        if headline is not None:
            self._on_news(today, headline)
        return record

    # Promessas de campanha

    def promise_value(self, promise: Promise, day: date) -> Decimal | None:
        """O que a medida prometida vale no país no dia; nulo na medida de setor."""
        return self.value_in_force(promise.kind, day)

    def promise_exempt(self, promise: Promise, day: date) -> bool:
        rule = self.policy(day).sector_rule(promise.sector, promise.segment)
        return rule is not None and rule.exempt

    def promise_progress(self, promise: Promise, day: date) -> Decimal:
        """Quanto do caminho do "era" ao alvo o país andou no dia."""
        return promises.progress(
            promise, self.promise_value(promise, day), self.promise_exempt(promise, day)
        )

    def promise_effects(
        self, items: tuple[Promise, ...], day: date
    ) -> promises.GroupEffects:
        """O balanço das promessas no dia, somado em cada grupo."""
        return promises.total(
            promises.settle(item, self.promise_progress(item, day)) for item in items
        )

    def promise_baseline(self, kind: MeasureKind, day: date) -> Decimal | None:
        """O "era" de uma promessa nova: o que a medida muda, como está hoje."""
        return self.value_in_force(kind, day)

    def promises_open_reason(
        self, today: date, party: Party | None = None
    ) -> str | None:
        """Por que a chapa (`party`, quando dada) não mexe nas promessas hoje; nulo quando pode."""
        cycle = self.cycle()
        runoff = self.state.runoff
        if runoff is not None:
            if today > cycle.donation_deadline:
                return "As promessas fecham na véspera do 2º turno."
            if party is not None and party.id not in runoff:
                return "Entre os turnos só os finalistas prometem."
            return None
        if today < cycle.campaign_start:
            return "A campanha ainda não abriu."
        if today > cycle.ticket_deadline:
            return "As promessas travam quando as chapas fecham."
        return None

    def founded_party(self, user: UserDTO) -> Party:
        """O partido que `user` fundou (ou herdou)."""
        self._ensure_person(user)
        return self._founded_party(user)

    def draft_promises(
        self, user: UserDTO, today: date, items: list[PromiseRequest]
    ) -> list[Promise]:
        """Valida a lista de promessas da chapa como ficaria; a que já existia mantém o "era" e o anúncio."""
        party = self.founded_party(user)
        reason = self.promises_open_reason(today, party)
        if reason is not None:
            raise ConflictError(reason)
        runoff = self.state.runoff
        limit = (
            second_round.MAX_PROMISES if runoff is not None else promises.MAX_PROMISES
        )
        if len(items) > limit:
            raise UnprocessableEntityError(f"No máximo {limit} promessas por chapa.")
        existing = {p.key: p for p in party.promises}
        final: list[Promise] = []
        for item in items:
            promise = self._build_promise(item, existing.get(_key(item)), today)
            if any(p.key == promise.key for p in final):
                raise ConflictError("A mesma medida não é prometida duas vezes.")
            final.append(promise)
        if runoff is not None and any(old not in final for old in party.promises):
            raise ConflictError("No 2º turno as promessas só se acrescentam.")
        return final

    def set_promises(
        self, user: UserDTO, today: date, items: list[PromiseRequest]
    ) -> None:
        """
        A fundadora anuncia a lista de promessas da chapa (até 3; até 4 no 2º turno, só acrescentando). Uma promessa nova rende
        desde o anúncio; voltar atrás depois dele (retirar, trocar ou baixar o alvo) soma
        rejeição em quem queria a medida.
        """
        party = self.founded_party(user)
        final = self.draft_promises(user, today, items)
        if final == party.promises:
            raise ConflictError("As promessas não mudaram.")
        had_promises = bool(party.promises)
        self._emit(
            GovernmentEventType.PROMISES_SET,
            today,
            party_id=party.id,
            promises=[promises.to_payload(p) for p in final],
        )
        self._notice(GovernmentNoticeKind.PROMISES_SET, user, party_abbr=party.abbr)
        self._on_news(
            today, headlines.promises_set(party.abbr, len(final), had_promises)
        )

    def _build_promise(
        self, item: PromiseRequest, old: Promise | None, today: date
    ) -> Promise:
        """Valida o pedido e monta a promessa; a que já existia mantém o "era" e o dia do anúncio."""
        kind = item.kind
        if not promises.promisable(kind):
            raise UnprocessableEntityError("Essa medida não se promete.")
        announced = old.announced if old else today
        if kind.is_sector:
            self._ensure_located(item.sector, item.segment)
            promise = Promise(kind, None, None, item.sector, item.segment, announced)
            if old is None and self.promise_exempt(promise, today):
                raise ConflictError(
                    "Esse setor já é isento: não se promete o que já vale."
                )
            return promise
        if item.sector is not None or item.segment is not None:
            raise UnprocessableEntityError("Essa medida não é de um setor.")
        limit = promises.limit_of(kind)
        target = item.target
        if target is None or target < 0 or (limit is not None and target > limit):
            raise UnprocessableEntityError("Informe um alvo válido para a promessa.")
        baseline = old.baseline if old else self.promise_baseline(kind, today)
        if target == baseline:
            raise ConflictError(
                "Esse já é o valor em vigor: não se promete o que já vale."
            )
        return Promise(kind, target, baseline, None, None, announced)

    def _announce_computer_promises(self, today: date) -> None:
        """Cada partido do computador promete, por regra, medidas dos próprios valores."""
        if self.promises_open_reason(today) is not None:
            return
        baselines = {
            kind: value
            for kind in promises.GENERAL_KINDS
            if (value := self.promise_baseline(kind, today)) is not None
        }
        for party in sorted(self.state.computer_parties(), key=lambda p: p.id):
            if party.promises:
                continue
            picks = promises.computer_picks(party.radar, baselines, today)
            if picks:
                self._emit(
                    GovernmentEventType.PROMISES_SET,
                    today,
                    party_id=party.id,
                    promises=[promises.to_payload(p) for p in picks],
                )

    def _weigh_promises(self, cycle: ElectionCycle, today: date) -> None:
        """
        Com as chapas fechadas, o partido que governa e concorre passa a ser votado com
        metade do balanço das promessas em vigor; o balanço do fim do mandato fecha o resto.
        """
        term = self.state.term
        if (
            term is None
            or term.weighed
            or term.settled
            or not term.promises
            or term.party_id is None
            or today <= cycle.ticket_deadline
        ):
            return
        party = self.state.parties.get(term.party_id)
        if party is None or party.is_computer or not election.runs(self.state, party):
            return
        half = promises.scaled(
            self.promise_effects(term.promises, today), promises.WEIGHED_SHARE
        )
        self._emit(
            GovernmentEventType.PROMISES_WEIGHED,
            today,
            party_id=party.id,
            effects=promises.effects_to_payload(half),
        )

    def _settle_term_end(self, today: date) -> None:
        """No fim do mandato vale o que estava em vigor em 31 de dezembro."""
        end = self.term_end()
        if end is not None and today >= end:
            self._settle_promises(today, end)

    def _settle_promises(
        self, today: date, day: date, *, impeached: bool = False
    ) -> None:
        """Fecha o balanço das promessas da chapa que governa, pelo que valia em `day`."""
        term = self.state.term
        if term is None or term.settled or not term.promises or term.party_id is None:
            return
        party = self.state.parties.get(term.party_id)
        if party is None or party.is_computer:
            return
        items = []
        kept = 0
        for promise in term.promises:
            done = self.promise_progress(promise, day)
            kept += done >= 1
            items.append(
                {
                    "promise": promises.to_payload(promise),
                    "done": str(done),
                    "effects": promises.effects_to_payload(
                        promises.settle(promise, done)
                    ),
                }
            )
        self._emit(
            GovernmentEventType.PROMISES_SETTLED,
            today,
            party_id=party.id,
            impeached=impeached,
            items=items,
        )
        self._notice(GovernmentNoticeKind.PROMISES_SETTLED, party_abbr=party.abbr)
        self._on_news(
            today, headlines.promises_settled(party.abbr, kept, len(term.promises))
        )

    # Medidas do presidente

    def propose(
        self,
        user: UserDTO,
        today: date,
        kind: MeasureKind,
        value: Decimal | None,
        sector: str | None,
        segment: str | None,
    ) -> None:
        self._ensure_president(user)
        draft = self._draft(user, today, kind, value, sector, segment)
        self._ensure_not_queued(draft)
        self._emit(
            GovernmentEventType.MEASURE_PROPOSED,
            today,
            measure_id=self.state.next_measure_id,
            kind=draft.kind.value,
            value=None if draft.value is None else str(draft.value),
            before=None if draft.before is None else str(draft.before),
            sector=draft.sector,
            segment=draft.segment,
            proposer_id=user.id,
        )
        self._notice(
            GovernmentNoticeKind.MEASURE_PROPOSED,
            user,
            measure_title=rules.title(draft),
        )
        self._on_news(
            today, headlines.measure_proposed(user.nickname, rules.title(draft))
        )

    def repropose(self, user: UserDTO, today: date, measure_id: int) -> None:
        self._ensure_president(user)
        old = self._measure(measure_id)
        if old.status is not MeasureStatus.REJECTED or not self.is_current(old):
            raise ConflictError("Só uma medida rejeitada deste governo volta à fila.")
        self.propose(user, today, old.kind, old.value, old.sector, old.segment)

    def withdraw(self, user: UserDTO, today: date, measure_id: int) -> None:
        self._ensure_president(user)
        measure = self._measure(measure_id)
        if measure.status is not MeasureStatus.QUEUED:
            raise ConflictError("A medida já foi votada ou retirada.")
        self._emit(GovernmentEventType.MEASURE_WITHDRAWN, today, measure_id=measure.id)
        self._notice(
            GovernmentNoticeKind.MEASURE_WITHDRAWN,
            user,
            measure_title=rules.title(measure),
        )
        self._on_news(
            today, headlines.measure_withdrawn(user.nickname, rules.title(measure))
        )

    def preview(
        self,
        user: UserDTO,
        today: date,
        kind: MeasureKind,
        value: Decimal | None,
        sector: str | None,
        segment: str | None,
    ) -> MeasurePreviewDTO:
        """O que a medida faria, sem propô-la: perfil do partido, pontos na aprovação, voto e vigência."""
        self._ensure_president(user)
        draft = self._draft(user, today, kind, value, sector, segment)
        vote = congress.next_vote_date(today)
        tickers = self.tickers(draft)
        moves = voters.radar_moves(draft.kind, draft.value, draft.before)
        return MeasurePreviewDTO(
            title=rules.title(draft),
            profile_moves=[
                ValueMoveDTO(value=v, points=points) for v, points in moves.items()
            ],
            impact=approval_rules.measure_impact(draft),
            vote_date=vote,
            effective=vote + timedelta(days=VIGENCE_DAYS),
            assets=len(tickers) if draft.kind.is_sector else None,
            holdings=self._holdings(tickers) if draft.kind.is_sector else [],
            budget=budget_panel.measure_budget(
                self._budget,
                self._timeline.latest,
                self._spending,
                draft,
                today,
                vote + timedelta(days=VIGENCE_DAYS),
                self.term_end(),
            ),
            inflation=spending_panel.inflation_effect(draft, today),
            reactions=spending_panel.reactions(draft),
        )

    def _holdings(self, tickers: list[str]) -> list[MeasureHoldingDTO]:
        """Quanto cada jogador tem nos ativos que a medida atinge."""
        covered = set(tickers)
        holdings = []
        for person in self._people.values():
            portfolio = self._engine.get_portfolio(person.client_id)
            value = sum(
                (
                    p.current_value
                    for p in portfolio.variable_income
                    if p.ticker in covered
                ),
                Decimal(0),
            )
            if value > 0 and portfolio.assets_value > 0:
                holdings.append(
                    MeasureHoldingDTO(
                        nickname=person.nickname,
                        share=value / portfolio.assets_value,
                        value=value,
                    )
                )
        return sorted(holdings, key=lambda h: h.value, reverse=True)

    def _draft(
        self,
        user: UserDTO,
        today: date,
        kind: MeasureKind,
        value: Decimal | None,
        sector: str | None,
        segment: str | None,
    ) -> Measure:
        """Valida o pedido e monta a medida como entraria na fila."""
        term = required(self.state.term)
        before: Decimal | None = None
        if kind.is_sector:
            self._ensure_located(sector, segment)
            if kind is MeasureKind.SECTOR_EXEMPT:
                value = None
            elif value is None or not 0 < value <= SECTOR_EXTRA_LIMIT:
                raise UnprocessableEntityError(
                    "Os pontos somados ao IR do setor vão de 0,1 a 20."
                )
        else:
            if sector is not None or segment is not None:
                raise UnprocessableEntityError("Essa medida não é de um setor.")
            limit = promises.limit_of(kind)
            if value is None or value < 0 or (limit is not None and value > limit):
                raise UnprocessableEntityError("Informe um valor válido para a medida.")
            before = self.latest_value(kind)
            if value == before:
                raise ConflictError(
                    "Esse já é o valor em vigor: a medida não muda nada."
                )
            # Uma medida de gasto anda no máximo um passo de referência por vez
            if (
                kind.is_spending
                and abs(value - required(before)) > spending.STEPS[kind]
            ):
                points = f"{spending.STEPS[kind] * 100:.1f}".replace(".", ",")
                raise UnprocessableEntityError(
                    f"A medida anda no máximo {points} ponto para cima ou para baixo."
                )
        return Measure(
            id=self.state.next_measure_id,
            kind=kind,
            value=value,
            before=before,
            sector=sector,
            segment=segment,
            proposer_id=user.id,
            term_start=term.start,
            proposed=today,
        )

    def _ensure_located(self, sector: str | None, segment: str | None) -> None:
        located = self._engine.classification.values()
        if sector is None or all(c.sector != sector for c in located):
            raise NotFoundError("Setor não encontrado.")
        if segment is not None and all(
            (c.sector, c.segment) != (sector, segment) for c in located
        ):
            raise NotFoundError("Segmento não encontrado nesse setor.")

    def _ensure_not_queued(self, draft: Measure) -> None:
        for queued in self._queue():
            if (queued.kind, queued.sector, queued.segment) == (
                draft.kind,
                draft.sector,
                draft.segment,
            ):
                raise ConflictError("Já tem uma medida igual na fila.")

    def _ensure_president(self, user: UserDTO) -> None:
        president = self.president()
        if president is None or president.id != user.id:
            raise ForbiddenError("Só o presidente propõe medidas.")

    def _measure(self, measure_id: int) -> Measure:
        measure = self.state.measures.get(measure_id)
        if measure is None:
            raise NotFoundError("Medida não encontrada.")
        return measure

    def is_current(self, measure: Measure) -> bool:
        """Se a medida foi proposta pelo governo em curso."""
        term = self.state.term
        return term is not None and measure.term_start == term.start

    def _queue(self) -> list[Measure]:
        return sorted(
            (
                m
                for m in self.state.measures.values()
                if m.status is MeasureStatus.QUEUED
            ),
            key=lambda m: m.id,
        )

    # Fechamento do mês do governo: aprovação, voto do Congresso e impeachment

    def _close_month(self, today: date) -> bool:
        """
        No último dia útil do mês cada grupo anda um terço do caminho até o alvo, a casa
        vota o pedido de impeachment aberto e a fila de medidas e, depois de 6 fechamentos
        seguidos abaixo do piso (a contar do 13º mês do mandato), o pedido de impeachment
        abre para a casa votar no mês seguinte. Devolve se o presidente caiu, o que pausa
        a partida.
        """
        term = self.state.term
        month = today.replace(day=1)
        if (
            term is None
            or term.president_id is None
            or not congress.is_vote_day(today)
            or self.state.last_measured == month
        ):
            return False
        request = self.state.request
        if (
            request is not None
            and today >= request.vote_day
            and self._vote_impeachment(today)
        ):
            return True
        before = required(self.approval(today))
        satisfaction = {
            g: approval_rules.next_satisfaction(before.satisfaction[g], t.target)
            for g, t in before.targets.items()
        }
        value = approval_rules.rounded(approval_rules.overall(satisfaction))
        below = (
            not approval_rules.in_grace(term, month) and value < approval_rules.FLOOR
        )
        streak = self.state.low_streak + 1 if below else 0
        self._emit(
            GovernmentEventType.APPROVAL_MEASURED,
            today,
            value=value,
            satisfaction={g.value: str(v) for g, v in satisfaction.items()},
            low_streak=streak,
            month=month.isoformat(),
        )
        if streak >= approval_rules.IMPEACHMENT_MONTHS and self.state.request is None:
            self._request_impeachment(today)
        elif streak == approval_rules.IMPEACHMENT_MONTHS - 1:
            self._notice(
                GovernmentNoticeKind.IMPEACHMENT_WARNING,
                self.president(),
                months_below_floor=streak,
                approval=value,
            )
        self._vote(today)
        self._notice_month_closed(before.value, satisfaction, value)
        return False

    def _request_impeachment(self, today: date) -> None:
        """O 6º fechamento seguido abaixo do piso abre o pedido; a casa vota no dia de votação do mês seguinte."""
        vote_day = congress.next_vote_date(today + timedelta(days=1))
        self._emit(
            GovernmentEventType.IMPEACHMENT_REQUESTED,
            today,
            vote_day=vote_day.isoformat(),
        )
        term = required(self.state.term)
        president = self.president()
        self._notice(
            GovernmentNoticeKind.IMPEACHMENT_REQUESTED,
            president,
            party_abbr=self._party_abbr(term.party_id),
            effective=vote_day,
        )
        if president is not None:
            self._on_news(
                today,
                headlines.impeachment_requested(
                    president.nickname,
                    self._party_abbr(term.party_id),
                    vote_day,
                ),
            )

    def _vote_impeachment(self, today: date) -> bool:
        """A casa vota o pedido: com 68 votos Sim o presidente cai; sem eles a contagem recomeça do zero."""
        request = required(self.state.request)
        current = self.state.house_on(today)
        orientations, _, wanted = self.impeachment_orientations(today)
        tally = house.count(
            f"impeachment:{request.opened.isoformat()}",
            self._seed,
            current,
            orientations,
            wanted,
        )
        by_group = house.impeachment_reactions(self.state.satisfaction)
        approved = tally.yes >= house.IMPEACHMENT_VOTES
        self._emit(
            GovernmentEventType.IMPEACHMENT_VOTED,
            today,
            approved=approved,
            **self._tally_payload(tally, current, by_group),
        )
        term = required(self.state.term)
        president = self.president()
        self._notice(
            GovernmentNoticeKind.IMPEACHMENT_VOTED,
            president,
            party_abbr=self._party_abbr(term.party_id),
            accepted=approved,
            yes=tally.yes,
            no=tally.no,
            defected=tally.defected,
        )
        if approved:
            self._impeach(today, tally)
        elif president is not None:
            self._on_news(
                today,
                headlines.impeachment_rejected(
                    president.nickname,
                    self._party_abbr(term.party_id),
                    tally.yes,
                    tally.no,
                ),
            )
        return approved

    def _tally_payload(
        self,
        tally: house.Tally,
        current: house.House,
        reactions: dict[VoterGroup, Decimal],
    ) -> dict[str, object]:
        """O placar como vai no evento, com a causa de quem desobedeceu em cada bancada."""
        blocs = {}
        for key, vote in tally.blocs.items():
            bloc = current.bloc(key)
            cause = (
                house.contrary_group(bloc.mix, reactions, vote.orientation)
                if bloc is not None and vote.defected
                else None
            )
            blocs[str(key)] = {
                "seats": vote.seats,
                "orientation": vote.orientation,
                "yes": vote.yes,
                "no": vote.no,
                "defected": vote.defected,
                "cause": cause.value if cause else None,
            }
        return {
            "yes": tally.yes,
            "no": tally.no,
            "defected": tally.defected,
            "blocs": blocs,
        }

    def _notice_month_closed(
        self,
        previous: int,
        satisfaction: dict[VoterGroup, Decimal],
        value: int,
    ) -> None:
        """Conta à sala como os grupos fecharam o mês; o front mostra só aos filiados do governo."""
        term = required(self.state.term)
        verdicts = {g: voters.month_verdict(v) for g, v in satisfaction.items()}
        self._notice(
            GovernmentNoticeKind.MONTH_CLOSED,
            party_abbr=self._party_abbr(term.party_id),
            approval=value,
            previous_approval=previous,
            groups_approved=[
                g for g, v in verdicts.items() if v is GroupVerdict.APPROVES
            ],
            groups_reproved=[
                g for g, v in verdicts.items() if v is GroupVerdict.REPROVES
            ],
        )

    def _vote(self, today: date) -> None:
        """A casa vota cada medida da fila: a bancada segue a orientação, e parte dela desobedece."""
        current = self.state.house_on(today)
        for measure in self._queue():
            orientations, _, wanted = self.measure_orientations(measure, today)
            tally = house.count(
                f"{measure_ref(measure.id)}:{today.isoformat()}",
                self._seed,
                current,
                orientations,
                wanted,
            )
            approved = tally.yes >= house.MAJORITY
            self._emit(
                GovernmentEventType.MEASURE_VOTED,
                today,
                measure_id=measure.id,
                approved=approved,
                **self._tally_payload(
                    tally, current, house.reactions(self.effects_of(measure))
                ),
            )
            if approved:
                self._timeline = PolicyTimeline(self.state.measures.values())
                self._spending = SpendingTimeline(self.state.measures.values())
                self._economy.update(self.state.measures.values())
            self._notice(
                GovernmentNoticeKind.MEASURE_VOTED,
                self._people.get(measure.proposer_id),
                accepted=approved,
                measure_title=rules.title(measure),
                yes=tally.yes,
                no=tally.no,
                defected=tally.defected,
                effective=measure.effective,
                tickers=self.tickers(measure),
            )
            self._on_news(
                today,
                headlines.measure_voted(
                    rules.title(measure),
                    approved,
                    measure.effective,
                    self.tickers(measure),
                    tally.yes,
                    tally.no,
                    tally.defected,
                ),
            )

    def _impeach(self, today: date, tally: house.Tally) -> None:
        """Assume o vice que segue na partida; sem ele, o computador governa sem propor medidas."""
        term = required(self.state.term)
        out = self.president()
        successor = self._successor()
        # Sem vice o mandato acaba aqui, e o que não foi cumprido vira rejeição
        if successor is None:
            self._settle_promises(today, today, impeached=True)
        self._emit(
            GovernmentEventType.IMPEACHED,
            today,
            successor_id=successor.id if successor else None,
        )
        if successor is not None:
            self._on_office(successor, today)
        self._notice(
            GovernmentNoticeKind.IMPEACHMENT,
            out,
            target=successor,
            party_abbr=self._party_abbr(term.party_id),
        )
        if out is not None:
            self._on_news(
                today,
                headlines.impeachment(
                    out.nickname,
                    self._party_abbr(term.party_id),
                    successor.nickname if successor else None,
                    tally.yes,
                    tally.no,
                ),
            )

    def _successor(self) -> UserDTO | None:
        term = required(self.state.term)
        if term.vice_id is None:
            return None
        return self._people.get(term.vice_id)

    def _party_abbr(self, party_id: int | None) -> str | None:
        party = self.state.parties.get(party_id) if party_id is not None else None
        return party.abbr if party else None

    def _announce_in_force(self, previous: date | None, today: date) -> None:
        """Avisa a sala no dia em que cada medida aprovada passa a valer."""
        if previous is None:
            return
        for measure in self.state.measures.values():
            if (
                measure.status is MeasureStatus.APPROVED
                and measure.effective is not None
                and previous < measure.effective <= today
            ):
                self._notice(
                    GovernmentNoticeKind.MEASURE_IN_FORCE,
                    measure_title=rules.title(measure),
                    effective=measure.effective,
                    tickers=self.tickers(measure),
                )
                self._on_news(
                    today,
                    headlines.measure_in_force(
                        rules.title(measure), self.tickers(measure)
                    ),
                )

    # Calendário: contribuição, apuração e posse

    def _collect(self, people: dict[int, UserDTO], today: date) -> None:
        """
        No 1º dia útil do mês cada filiado paga a contribuição que escolheu, se o caixa
        cobre; o partido do computador gasta a verba da dificuldade.
        """
        month = today.replace(day=1)
        if self.state.last_collection == month:
            return
        self._ensure_computers(today)
        self._announce_computer_promises(today)

        spent: dict[str, str] = {}
        to_house: dict[str, str] = {}
        for party in self.state.player_parties():
            total = Decimal(0)
            house_total = Decimal(0)
            # Sem candidato à presidência, toda a contribuição vai para o Congresso
            runs = election.runs(self.state, party)
            for user_id, contribution in party.members.items():
                user = people.get(user_id)
                if (
                    user is None
                    or contribution <= 0
                    or self._engine.get_cash(user.client_id) < contribution
                ):
                    continue
                self._engine.pay_campaign(
                    user.client_id,
                    contribution,
                    CashflowEventType.CAMPAIGN_CONTRIBUTION,
                )
                total += contribution
                house_total += (
                    party.congress.get(user_id, Decimal(0)) if runs else contribution
                )
            spent[str(party.id)] = str(total - house_total)
            to_house[str(party.id)] = str(house_total)
        computer_amount = election.computer_spend(self.state, self._factor)
        for party in sorted(self.state.computer_parties(), key=lambda p: p.id):
            # Das ações sobra a verba de base, que o computador divide entre a presidência e o Congresso
            left = self._computer_campaign(party, computer_amount, today)
            computer_house = left * house.COMPUTER_HOUSE_SHARE
            spent[str(party.id)] = str(left - computer_house)
            to_house[str(party.id)] = str(computer_house)
        self._emit(
            GovernmentEventType.CAMPAIGN_SPENT,
            today,
            month=month.isoformat(),
            spent=spent,
            house=to_house,
        )
        self._notice(GovernmentNoticeKind.UPDATED)

    def _computer_campaign(self, party: Party, budget: Decimal, today: date) -> Decimal:
        """
        O computador gasta uma fatia da verba do mês em ações, por regra: TV quando a
        fatia cobre o preço; senão eventos nos grupos de maior afinidade; na dificuldade
        difícil, ataque ao líder da pesquisa. Devolve o que sobra para a verba de base.
        """
        pot = budget * campaign.COMPUTER_ACTION_SHARE
        plan: list[tuple[CampaignActionKind, VoterGroup | None, Party | None]] = []
        tv = self.action_price(CampaignActionKind.TV, today)
        event = self.action_price(CampaignActionKind.EVENT, today)
        attack = self.action_price(CampaignActionKind.ATTACK, today)
        if pot >= tv:
            plan.append((CampaignActionKind.TV, None, None))
            pot -= tv
        else:
            by_affinity = sorted(
                VoterGroup,
                key=lambda g: (-voters.affinity(g, party.radar), g.value),
            )
            for group in by_affinity:
                if pot < event:
                    break
                plan.append((CampaignActionKind.EVENT, group, None))
                pot -= event
        if (
            self._settings.computer_difficulty is ComputerDifficulty.HARD
            and pot >= attack
        ):
            target = self._attack_target(party)
            if target is not None:
                plan.append((CampaignActionKind.ATTACK, target[1], target[0]))
        left = budget
        for kind, group, rival in plan:
            price = self.action_price(kind, today)
            self._emit_action(party, None, today, kind, group, rival, price)
            left -= price
        return left

    def _attack_target(self, party: Party) -> tuple[Party, VoterGroup] | None:
        """O líder da pesquisa entre os rivais e o grupo em que ele está mais forte."""
        rivals = [p for p in self.running_parties() if p.id != party.id]
        if not rivals:
            return None
        totals = election.intention(self.state).total
        leader = max(rivals, key=lambda p: (totals.get(p.id, Decimal(0)), -p.id))
        group = max(VoterGroup, key=lambda g: (leader.standing(g).balance, g.value))
        return leader, group

    def _hold_first_round(self, cycle: ElectionCycle, today: date) -> None:
        self._ensure_computers(today)
        running = self._running()
        vote = election.intention(self.state)
        points = vote.total
        shares = election.valid_shares(points)
        winner = election.first_round_winner(shares)
        finalists = [winner] if winner is not None else election.top_two(points)
        self._elect_house(cycle, today)
        self._emit_round(
            cycle,
            today,
            round_number=1,
            running=running,
            points=points,
            shares=shares,
            finalists=finalists,
            winner=winner,
            transfers={},
            satisfaction=(
                election.start_satisfaction(vote, winner) if winner is not None else {}
            ),
        )

    def _elect_house(self, cycle: ElectionCycle, today: date) -> None:
        """
        A casa sai do mesmo modelo de grupos, pesando o histórico do partido mais do que a
        campanha: os três do computador sempre entram, e o partido de jogador entra se
        tiver filiado.
        """
        candidates, strengths = self._house_field()
        elected = house.elect(candidates, strengths)
        self._emit(
            GovernmentEventType.HOUSE_ELECTED,
            today,
            cycle=self.state.cycle,
            takes_office=cycle.inauguration.isoformat(),
            blocs=[
                {
                    "key": b.key,
                    "party_id": b.party_id,
                    "abbr": b.abbr,
                    "name": b.name,
                    "color": b.color,
                    "is_computer": b.is_computer,
                    "votes": str(b.votes),
                    "seats": b.seats,
                    "mix": {g.value: str(v) for g, v in b.mix.items()},
                }
                for b in elected.blocs
            ],
            below=list(elected.below),
            last=str(elected.last),
            upcoming=str(elected.upcoming),
        )
        self._notice(GovernmentNoticeKind.HOUSE_ELECTED)

    def house_field(
        self,
    ) -> tuple[list[house.Candidate], dict[int, dict[VoterGroup, Decimal]]]:
        """Os partidos na disputa da casa e a força de cada um em cada grupo, como estão hoje."""
        return self._house_field()

    def _house_field(
        self,
    ) -> tuple[list[house.Candidate], dict[int, dict[VoterGroup, Decimal]]]:
        candidates: list[house.Candidate] = []
        strengths: dict[int, dict[VoterGroup, Decimal]] = {}
        zero = dict.fromkeys(VoterGroup, Decimal(0))
        for spec in COMPUTER_PARTIES:
            key = house.COMPUTER_KEYS[spec.abbr]
            party = next(
                (p for p in self.state.computer_parties() if p.abbr == spec.abbr), None
            )
            candidates.append(
                house.Candidate(
                    key, spec.abbr, spec.name, None, True, party.id if party else None
                )
            )
            radar = party.radar if party else voters.initial_radar(spec.flags)
            strengths[key] = {
                g: house.strength(
                    g,
                    radar,
                    party.loyalty[g] if party else zero[g],
                    party.rejection[g] if party else zero[g],
                    party.house_campaign[g] if party else zero[g],
                )
                for g in VoterGroup
            }
        for party in sorted(self.state.player_parties(), key=lambda p: p.id):
            candidates.append(
                house.Candidate(
                    party.id, party.abbr, party.name, party.color, False, party.id
                )
            )
            strengths[party.id] = {
                g: house.strength(
                    g,
                    party.radar,
                    party.loyalty[g],
                    party.rejection[g],
                    party.house_campaign[g],
                )
                for g in VoterGroup
            }
        return candidates, strengths

    def _hold_runoff(self, cycle: ElectionCycle, today: date) -> None:
        """A votação do 2º turno: o voto de cada grupo entre os finalistas; quem seguia indeciso se abstém."""
        running = self._running()
        finalists = [f for f in (self.state.runoff or []) if f in self.state.parties]
        first_round = self.state.results[-1].points if self.state.results else {}
        race = self.state.race
        if race is None or len(finalists) != 2:
            # Um finalista só: ele leva o 2º turno sem disputa
            vote = voters.restrict(election.intention(self.state), finalists)
        else:
            vote = race.vote()
        votes = {pid: vote.total.get(pid, Decimal(0)) for pid in finalists}
        shares = election.valid_shares(votes)
        winner = second_round.winner(votes, first_round)
        points = {
            pid: votes.get(pid, first_round.get(pid, Decimal(0))) for pid in first_round
        }
        self._emit_round(
            cycle,
            today,
            round_number=2,
            running=running,
            points=points,
            shares=shares,
            finalists=finalists,
            winner=winner,
            transfers=self._transfers(race, finalists),
            satisfaction=election.start_satisfaction(vote, winner),
            groups=vote.groups,
            not_voted=vote.undecided,
        )

    def _transfers(
        self, race: second_round.Race | None, finalists: list[int]
    ) -> dict[int, int]:
        """Para qual finalista foi, no total do país, a maior parte dos eleitores de cada partido que saiu."""
        if race is None:
            return {}
        flow: dict[int, dict[int, Decimal]] = {}
        for group, disputed in race.groups.items():
            for eliminated, sent in disputed.sent.items():
                for finalist, amount in sent.items():
                    by_finalist = flow.setdefault(eliminated, {})
                    by_finalist[finalist] = by_finalist.get(finalist, Decimal(0)) + (
                        voters.WEIGHTS[group] * amount
                    )
        return {
            eliminated: max(by_finalist, key=lambda f: (by_finalist[f], -f))
            for eliminated, by_finalist in flow.items()
        }

    def _run_between_rounds(self, cycle: ElectionCycle, today: date) -> None:
        """
        O calendário entre os turnos: o computador eliminado declara apoio, o computador
        finalista contribui e faz o evento dele uma vez, e a pesquisa sai a cada semana.
        """
        race = self.state.race
        if race is None:
            return
        changed = False
        for party in self.state.computer_parties():
            if party.id in race.finalists or party.id in race.endorsements:
                continue
            if party.id not in self._eliminated():
                continue
            finalists = {f: self.state.parties[f].radar for f in race.finalists}
            endorsed = second_round.computer_endorsement(party.radar, finalists)
            self._emit(
                GovernmentEventType.RUNOFF_ENDORSED,
                today,
                party_id=party.id,
                user_id=None,
                endorsed_id=endorsed,
            )
            self._on_news(
                today, headlines.endorsement(party.abbr, self._party_abbr(endorsed))
            )
            changed = True
        for finalist in race.finalists:
            party = self.state.parties[finalist]
            if party.is_computer and not self.state.runoff_total(finalist):
                self._computer_runoff(party, today)
                changed = True
        eve = cycle.donation_deadline
        due = sum(
            1
            for d in second_round.poll_days(required(self.state.race_started), eve)
            if d <= today
        )
        while len(self.state.race_polls) < due:
            self._emit(GovernmentEventType.RUNOFF_POLL, today)
            changed = True
        if changed:
            self._notice(GovernmentNoticeKind.UPDATED)

    def _computer_runoff(self, party: Party, today: date) -> None:
        """O finalista do computador contribui com metade da verba mensal e faz um evento no grupo com mais indecisos."""
        race = required(self.state.race)
        budget = election.computer_spend(self.state, self._factor)
        amount = budget * second_round.COMPUTER_CONTRIBUTION_SHARE
        self._emit(
            GovernmentEventType.RUNOFF_CONTRIBUTION,
            today,
            user_id=None,
            party_id=party.id,
            amount=str(amount),
        )
        group = max(VoterGroup, key=lambda g: (race.groups[g].undecided, g.value))
        self._emit_action(
            party,
            None,
            today,
            CampaignActionKind.EVENT,
            group,
            None,
            self.action_price(CampaignActionKind.EVENT, today),
        )

    def _emit_round(
        self,
        cycle: ElectionCycle,
        today: date,
        *,
        round_number: int,
        running: list[Party],
        points: dict[int, Decimal],
        shares: dict[int, Decimal],
        finalists: list[int],
        winner: int | None,
        transfers: dict[int, int],
        satisfaction: dict[VoterGroup, Decimal],
        groups: dict[VoterGroup, voters.GroupVote] | None = None,
        not_voted: Decimal = Decimal(0),
    ) -> None:
        tickets: dict[str, dict[str, object]] = {}
        for party in running:
            candidate, vice = election.effective_ticket(self.state, party)
            tickets[str(party.id)] = {
                "candidate_id": candidate,
                "vice_id": vice,
                "abbr": party.abbr,
                "name": party.name,
                "color": party.color,
                "is_computer": party.is_computer,
                "candidate_name": party.candidate_name,
                "promises": [promises.to_payload(p) for p in party.promises],
            }
        donations: dict[int, Decimal] = {}
        for donation in self.state.donations:
            donations[donation.party_id] = (
                donations.get(donation.party_id, Decimal(0)) + donation.amount
            )
        self._emit(
            GovernmentEventType.ELECTION_ROUND,
            today,
            cycle=cycle.index,
            round=round_number,
            tickets=tickets,
            points={str(k): str(v) for k, v in points.items()},
            shares={str(k): str(v) for k, v in shares.items()},
            finalists=finalists,
            winner_id=winner,
            transfers={str(k): v for k, v in transfers.items()},
            donations={str(k): str(v) for k, v in donations.items()},
            winner_satisfaction={
                g.value: str(v.quantize(approval_rules.SATISFACTION_PRECISION))
                for g, v in satisfaction.items()
            },
            groups={
                g.value: {
                    "shares": {str(k): str(v) for k, v in gv.shares.items()},
                    "undecided": str(gv.undecided),
                }
                for g, gv in (groups or {}).items()
            },
            not_voted=str(not_voted),
        )
        winner_party = self.state.parties.get(winner) if winner is not None else None
        self._notice(
            GovernmentNoticeKind.ELECTION_RESULT,
            round_number=round_number,
            winner_abbr=winner_party.abbr if winner_party else None,
        )
        if winner_party is not None:
            candidate, _ = election.effective_ticket(self.state, winner_party)
            self._on_news(
                today,
                headlines.round_won(
                    round_number,
                    self._candidate_name(winner_party, candidate),
                    winner_party.abbr,
                    shares[winner_party.id],
                ),
            )
        elif len(finalists) == 2:
            self._on_news(
                today,
                headlines.runoff_called(
                    [(self.state.parties[f].abbr, shares[f]) for f in finalists],
                    cycle.runoff,
                ),
            )

    def _start_term(self, today: date, people: dict[int, UserDTO]) -> None:
        pending = required(self.state.pending_term)
        self._emit(
            GovernmentEventType.TERM_STARTED,
            today,
            party_id=pending.party_id,
            president_id=pending.president_id,
            vice_id=pending.vice_id,
            consecutive=pending.consecutive,
        )
        president = people.get(pending.president_id) if pending.president_id else None
        if president is not None:
            self._on_office(president, today)
        party = self.state.parties.get(pending.party_id) if pending.party_id else None
        # O aviso da posse leva o nome do presidente: o computador usa o nome da chapa, o jogador o apelido
        name = president.nickname if president else None
        if party is not None and party.is_computer:
            name = party.candidate_name
        self._notice(
            GovernmentNoticeKind.TERM_STARTED,
            winner_abbr=party.abbr if party else None,
            winner_name=name,
        )
        if name is not None:
            self._on_news(
                today,
                headlines.term_started(
                    name, party.abbr if party else None, self.term_end()
                ),
            )

    def _candidate_name(self, party: Party, candidate_id: int | None) -> str:
        """O nome na urna: o do computador vem da chapa, o do jogador é o apelido."""
        person = self._people.get(candidate_id) if candidate_id is not None else None
        if person is not None:
            return person.nickname
        return party.candidate_name or party.abbr

    def _tickets(self) -> list[tuple[str, str, str | None]]:
        """A chapa de cada partido que concorre: sigla, candidato e vice."""
        tickets = []
        for party in self.running_parties():
            candidate, vice = election.effective_ticket(self.state, party)
            vice_person = self._people.get(vice) if vice is not None else None
            tickets.append(
                (
                    party.abbr,
                    self._candidate_name(party, candidate),
                    vice_person.nickname if vice_person else None,
                )
            )
        return tickets

    def _running(self) -> list[Party]:
        return [p for p in self.state.parties.values() if election.runs(self.state, p)]

    def _ensure_computers(self, today: date) -> None:
        """O computador completa as vagas até 3 partidos, cada um com as bandeiras dele."""
        wanted = max(
            0, election.PARTIES_PER_ELECTION - len(self.state.player_parties())
        )
        computers = sorted(self.state.computer_parties(), key=lambda p: p.id)
        while len(computers) > wanted:
            removed = computers.pop()
            self._emit(
                GovernmentEventType.COMPUTER_PARTY_REMOVED, today, party_id=removed.id
            )
        while len(self.state.computer_parties()) < wanted:
            spec = election.next_computer_party(self.state)
            if spec is None:
                return
            self._emit(
                GovernmentEventType.COMPUTER_PARTY_ADDED,
                today,
                party_id=self.state.next_party_id,
                name=spec.name,
                abbr=spec.abbr,
                candidate_name=spec.candidate,
                flags=[v.value for v in spec.flags],
            )

    # Regras de quem pode agir

    def _ensure_person(self, user: UserDTO) -> None:
        if user.is_bot:
            raise ForbiddenError("Bot não participa de partido.")

    def _ensure_without_party(self, user: UserDTO) -> None:
        if self.state.party_of(user.id) is not None:
            raise ConflictError("Você já está em um partido. Saia dele antes.")

    def _ensure_campaign_open(self, today: date) -> None:
        cycle = self.cycle()
        if self.state.runoff is not None:
            raise ConflictError("Entre os turnos só dá para doar.")
        if not cycle.campaign_start <= today < cycle.first_round:
            raise ConflictError(
                "Partidos só abrem na campanha, um ano antes do 1º turno."
            )

    def _ensure_membership_open(self) -> None:
        if self.state.runoff is not None:
            raise ConflictError("Entre os turnos só dá para doar.")

    def _party(self, party_id: int) -> Party:
        party = self.state.parties.get(party_id)
        if party is None:
            raise NotFoundError("Partido não encontrado.")
        return party

    def _my_party(self, user: UserDTO) -> Party:
        party = self.state.party_of(user.id)
        if party is None:
            raise ConflictError("Você não está em nenhum partido.")
        return party

    def _founded_party(self, user: UserDTO) -> Party:
        party = self._my_party(user)
        if party.founder_id != user.id:
            raise ForbiddenError("Só a fundadora do partido faz isso.")
        return party

    # Eventos e avisos

    def _emit(
        self, event_type: GovernmentEventType, day: date, **payload: object
    ) -> None:
        event = GovernmentEventDTO(
            simulation_id=self._settings.id,
            event_type=event_type,
            payload=payload,
            event_date=day,
        )
        repository.government.insert(event)
        apply(self.state, event)

    def _notice(
        self,
        kind: GovernmentNoticeKind,
        actor: UserDTO | None = None,
        *,
        target: UserDTO | None = None,
        party_abbr: str | None = None,
        amount: Decimal | None = None,
        round_number: int | None = None,
        winner_abbr: str | None = None,
        winner_name: str | None = None,
        accepted: bool | None = None,
        measure_title: str | None = None,
        yes: int | None = None,
        no: int | None = None,
        defected: int | None = None,
        effective: date | None = None,
        tickers: list[str] | None = None,
        months_below_floor: int | None = None,
        approval: int | None = None,
        previous_approval: int | None = None,
        groups_approved: list[VoterGroup] | None = None,
        groups_reproved: list[VoterGroup] | None = None,
        ticket_deadline: date | None = None,
        first_round: date | None = None,
        campaign_action: CampaignActionKind | None = None,
        group: VoterGroup | None = None,
        rival_abbr: str | None = None,
    ) -> None:
        notify(
            "government_update",
            GovernmentUpdateEventDTO(
                kind=kind,
                actor=actor.nickname if actor else None,
                target=target.nickname if target else None,
                party_abbr=party_abbr,
                amount=amount,
                round=round_number,
                winner_abbr=winner_abbr,
                winner_name=winner_name,
                accepted=accepted,
                measure_title=measure_title,
                yes=yes,
                no=no,
                defected=defected,
                effective=effective,
                tickers=tickers,
                months_below_floor=months_below_floor,
                approval=approval,
                previous_approval=previous_approval,
                groups_approved=groups_approved,
                groups_reproved=groups_reproved,
                ticket_deadline=ticket_deadline,
                first_round=first_round,
                campaign_action=campaign_action,
                group=group,
                rival_abbr=rival_abbr,
            ).to_json(),
        )


def _key(item: PromiseRequest) -> tuple[MeasureKind, str | None, str | None]:
    return (item.kind, item.sector, item.segment)
