"""
Dono do estado político da partida: recebe as ações dos jogadores, roda o calendário
da eleição a cada pregão e grava cada fato como evento. O estado nasce do replay dos
eventos e só muda por `_emit`, que grava o evento e o aplica.
"""

import logging
from collections.abc import Callable
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from backend.core import repository
from backend.core.dto.events.government import GovernmentEventDTO
from backend.core.dto.government import (
    PARTY_ABBR_PATTERN,
    MeasureHoldingDTO,
    MeasurePreviewDTO,
)
from backend.core.dto.simulation import SimulationDTO
from backend.core.dto.user import UserDTO
from backend.core.enum import (
    CashflowEventType,
    GovernmentEventType,
    GovernmentNoticeKind,
    MeasureKind,
    MeasureStatus,
)
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.utils import required
from backend.features.government import approval as approval_rules
from backend.features.government import congress, election
from backend.features.government import measures as rules
from backend.features.government.calendar import ElectionCycle, election_cycle
from backend.features.government.measures import PolicyTimeline
from backend.features.government.state import (
    VIGENCE_DAYS,
    GovernmentState,
    Measure,
    Party,
    apply,
    replay,
)
from backend.features.realtime import notify
from backend.features.realtime.schemas import GovernmentUpdateEventDTO
from backend.features.simulation.simulation_engine import SimulationEngine
from backend.features.tax_policy import TaxPolicy

logger = logging.getLogger(__name__)

# Alíquota e pontos somados a um setor vão até 100% e 20 pontos
RATE_LIMIT = Decimal(1)
SECTOR_EXTRA_LIMIT = Decimal("0.2")


class GovernmentBook:
    def __init__(
        self,
        settings: SimulationDTO,
        engine: SimulationEngine,
        on_office: Callable[[UserDTO, date], None],
        random_seed: int,
    ):
        """`on_office` roda na posse de cada presidente jogador: a carteira dele congela."""
        self._settings = settings
        self._engine = engine
        self._on_office = on_office
        self._seed = random_seed
        self._first_election = required(settings.first_election)
        self._factor = settings.computer_difficulty.budget_factor
        self.state: GovernmentState = replay(
            repository.government.get_events(settings.id)
        )
        self._previous_day: date | None = None
        self._people: dict[int, UserDTO] = {}
        self._timeline = PolicyTimeline(self.state.measures.values())
        # O engine lê os impostos de cada dia do governo
        engine.use_tax_policy(self.policy)

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
        """A aprovação de hoje; só existe sob um presidente jogador."""
        term = self.state.term
        if term is None or term.president_id is None:
            return None
        return approval_rules.assess(
            term,
            self.state.measures.values(),
            approval_rules.market_on(today),
            today,
        )

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

    def cycle(self, index: int | None = None) -> ElectionCycle:
        """A eleição em curso (ou a de índice `index`)."""
        return election_cycle(
            self._first_election,
            self.state.cycle if index is None else index,
            self._settings.start_date,
        )

    def on_tick(self, users: list[UserDTO], today: date, month_changed: bool) -> bool:
        """
        Roda o calendário do dia: posse, contribuição do mês, fechamento do mês do governo
        e apuração. Devolve se o dia trouxe um resultado de turno ou um impeachment, que
        pausam a partida para todos.
        """
        people = {user.id: user for user in users}
        self._people = people
        previous, self._previous_day = self._previous_day, today
        pending = self.state.pending_term
        if pending is not None and today >= pending.start:
            self._start_term(today, people)

        cycle = self.cycle()
        self._announce_phase_change(cycle, previous, today)
        self._announce_in_force(previous, today)
        if (
            month_changed
            and self.state.runoff is None
            and cycle.campaign_start <= today < cycle.first_round
        ):
            self._collect(people, today)

        if self._close_month(today):
            return True

        if self.state.runoff is not None:
            if today >= cycle.runoff:
                self._hold_runoff(cycle, today)
                return True
        elif today >= cycle.first_round:
            self._hold_first_round(cycle, today)
            return True
        return False

    def _announce_phase_change(
        self, cycle: ElectionCycle, previous: date | None, today: date
    ) -> None:
        """A página renova no dia em que a campanha abre e no dia em que as chapas fecham."""
        if previous is None:
            return
        boundaries = (cycle.campaign_start, cycle.ticket_deadline + timedelta(days=1))
        if any(previous < boundary <= today for boundary in boundaries):
            self._notice(GovernmentNoticeKind.UPDATED)

    # Ações dos jogadores

    def found_party(
        self,
        user: UserDTO,
        today: date,
        *,
        name: str,
        abbr: str,
        color: str,
        promise: int,
        contribution: Decimal,
    ) -> None:
        self._ensure_person(user)
        self._ensure_campaign_open(today)
        self._ensure_without_party(user)
        if not PARTY_ABBR_PATTERN.match(abbr):
            raise UnprocessableEntityError("A sigla tem de 2 a 5 letras.")
        parties = self.state.parties.values()
        if any(p.abbr == abbr for p in parties):
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
            promise=promise,
            founder_id=user.id,
            contribution=str(contribution),
        )
        self._ensure_computers(today)
        self._notice(GovernmentNoticeKind.PARTY_FOUNDED, user, party_abbr=abbr)

    def join_party(
        self, user: UserDTO, today: date, party_id: int, contribution: Decimal
    ) -> None:
        self._ensure_person(user)
        self._ensure_campaign_open(today)
        self._ensure_without_party(user)
        party = self._party(party_id)
        if party.is_computer:
            raise ConflictError("O partido do computador não aceita filiados.")
        self._emit(
            GovernmentEventType.PARTY_JOINED,
            today,
            party_id=party.id,
            user_id=user.id,
            contribution=str(contribution),
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
        self, user: UserDTO, today: date, contribution: Decimal
    ) -> None:
        self._ensure_membership_open()
        party = self._my_party(user)
        self._emit(
            GovernmentEventType.CONTRIBUTION_SET,
            today,
            user_id=user.id,
            contribution=str(contribution),
        )
        self._notice(GovernmentNoticeKind.UPDATED, user, party_abbr=party.abbr)

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
        vice_user = members.get(vice) if vice else None
        if vice and vice_user is None:
            raise NotFoundError("O vice precisa ser filiado ao partido.")
        if vice_user is not None and vice_user.id == candidate_user.id:
            raise ConflictError("Candidato e vice precisam ser pessoas diferentes.")
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
        self._notice(
            GovernmentNoticeKind.VICE_ANSWERED,
            user,
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

    def preview(
        self,
        user: UserDTO,
        today: date,
        kind: MeasureKind,
        value: Decimal | None,
        sector: str | None,
        segment: str | None,
    ) -> MeasurePreviewDTO:
        """O que a medida faria, sem propô-la: régua, pontos na aprovação, voto e vigência."""
        self._ensure_president(user)
        draft = self._draft(user, today, kind, value, sector, segment)
        term = required(self.state.term)
        approved = approval_rules.term_measures(self.state.measures.values(), term)
        current = required(self.approval(today))
        vote = congress.next_vote_date(today)
        tickers = self.tickers(draft)
        return MeasurePreviewDTO(
            title=rules.title(draft),
            ruler_band=rules.ruler_band(draft),
            mark_before=current.mark,
            mark_after=approval_rules.mark_of([*approved, draft]) or Decimal(0),
            promise=term.promise,
            impact=rules.approval_impact(draft),
            chance=current.value,
            vote_date=vote,
            effective=vote + timedelta(days=VIGENCE_DAYS),
            assets=len(tickers) if draft.kind.is_sector else None,
            holdings=self._holdings(tickers) if draft.kind.is_sector else [],
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
            limit = None if kind is MeasureKind.STOCK_EXEMPTION else RATE_LIMIT
            if value is None or value < 0 or (limit is not None and value > limit):
                raise UnprocessableEntityError("Informe um valor válido para a medida.")
            before = rules.general_value(self._timeline.latest, kind)
            if value == before:
                raise ConflictError(
                    "Esse já é o valor em vigor: a medida não muda nada."
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
        No último dia útil do mês mede-se a aprovação, o Congresso vota a fila com chance
        igual a ela e, depois de 3 meses abaixo do piso, o presidente sofre impeachment.
        Devolve se houve impeachment, que pausa a partida.
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
        current = required(self.approval(today))
        streak = (
            self.state.low_streak + 1 if current.value < approval_rules.FLOOR else 0
        )
        self._emit(
            GovernmentEventType.APPROVAL_MEASURED,
            today,
            value=current.value,
            low_streak=streak,
            month=month.isoformat(),
        )
        if streak >= approval_rules.IMPEACHMENT_MONTHS:
            self._impeach(today)
            return True
        if streak == approval_rules.IMPEACHMENT_MONTHS - 1:
            self._notice(
                GovernmentNoticeKind.IMPEACHMENT_WARNING,
                self.president(),
                months_below_floor=streak,
                approval=current.value,
            )
        self._vote(today, current.value)
        self._notice(GovernmentNoticeKind.UPDATED, approval=current.value)
        return False

    def _vote(self, today: date, chance: int) -> None:
        for measure in self._queue():
            approved = congress.passes(self._seed, today, measure.id, chance)
            self._emit(
                GovernmentEventType.MEASURE_VOTED,
                today,
                measure_id=measure.id,
                approved=approved,
                chance=str(chance),
            )
            if approved:
                self._timeline = PolicyTimeline(self.state.measures.values())
            self._notice(
                GovernmentNoticeKind.MEASURE_VOTED,
                self._people.get(measure.proposer_id),
                accepted=approved,
                measure_title=rules.title(measure),
                chance=chance,
                effective=measure.effective,
                tickers=self.tickers(measure),
            )

    def _impeach(self, today: date) -> None:
        """Assume o vice que ainda é filiado; sem ele, o computador governa sem propor medidas."""
        term = required(self.state.term)
        out = self.president()
        successor = self._successor()
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

    def _successor(self) -> UserDTO | None:
        term = required(self.state.term)
        party = self.state.parties.get(term.party_id) if term.party_id else None
        if term.vice_id is None or party is None or term.vice_id not in party.members:
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

        spent: dict[str, str] = {}
        for party in self.state.player_parties():
            total = Decimal(0)
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
            spent[str(party.id)] = str(total)
        computer_amount = election.computer_spend(self.state, self._factor)
        for party in self.state.computer_parties():
            spent[str(party.id)] = str(computer_amount)
        self._emit(
            GovernmentEventType.CAMPAIGN_SPENT,
            today,
            month=month.isoformat(),
            spent=spent,
        )
        self._notice(GovernmentNoticeKind.UPDATED)

    def _hold_first_round(self, cycle: ElectionCycle, today: date) -> None:
        self._ensure_computers(today)
        running = self._running()
        points = {p.id: p.points for p in running}
        shares = election.valid_shares(points)
        winner = election.first_round_winner(shares)
        finalists = [winner] if winner is not None else election.top_two(points)
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
        )

    def _hold_runoff(self, cycle: ElectionCycle, today: date) -> None:
        running = self._running()
        finalists = [f for f in (self.state.runoff or []) if f in self.state.parties]
        points = {p.id: p.points for p in running}
        result = election.runoff(self.state, points, finalists)
        self._emit_round(
            cycle,
            today,
            round_number=2,
            running=running,
            points={pid: result.votes.get(pid, points[pid]) for pid in points},
            shares=result.shares,
            finalists=finalists,
            winner=result.winner_id,
            transfers=result.transfers,
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
        )
        winner_party = self.state.parties.get(winner) if winner is not None else None
        self._notice(
            GovernmentNoticeKind.ELECTION_RESULT,
            round_number=round_number,
            winner_abbr=winner_party.abbr if winner_party else None,
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
            promise=pending.promise,
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

    def _running(self) -> list[Party]:
        return [p for p in self.state.parties.values() if election.runs(self.state, p)]

    def _ensure_computers(self, today: date) -> None:
        """O computador completa as vagas até 3 partidos, nas faixas mais longe dos jogadores."""
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
            name, abbr, candidate = spec
            self._emit(
                GovernmentEventType.COMPUTER_PARTY_ADDED,
                today,
                party_id=self.state.next_party_id,
                name=name,
                abbr=abbr,
                candidate_name=candidate,
                promise=election.pick_promise(list(self.state.parties.values())),
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
        chance: int | None = None,
        effective: date | None = None,
        tickers: list[str] | None = None,
        months_below_floor: int | None = None,
        approval: int | None = None,
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
                chance=chance,
                effective=effective,
                tickers=tickers,
                months_below_floor=months_below_floor,
                approval=approval,
            ).to_json(),
        )
