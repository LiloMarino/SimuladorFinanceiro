from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from backend.core import repository
from backend.core.dates import add_months
from backend.core.dto.fund import (
    FundAssemblyAutoVoteDTO,
    FundAssemblyBlock,
    FundAssemblyDTO,
    FundAssemblyFeeDTO,
    FundAssemblyMergeDTO,
    FundAssemblyOptionDTO,
    FundAssemblyPanelDTO,
    FundAssemblyResultDTO,
    FundAssemblyStance,
    FundAssemblyStatusDTO,
    FundAssemblyTallyDTO,
    FundAssemblyVoteDTO,
    FundAssemblyVoterDTO,
    FundMergeSideDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import FundAssemblyAgenda, FundAssemblyStatus
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    ForbiddenError,
    UnprocessableEntityError,
)
from backend.core.utils import next_month_turn, ratio
from backend.features.funds.fund_comanagers import operators_of
from backend.features.market_maker.sessions import window_end, window_session
from backend.features.simulation.simulation_engine import SimulationEngine

if TYPE_CHECKING:
    from backend.features.funds.fund_book import Fund

# Pregões da votação, contando o da abertura, e pregões que o aliado tem para aceitar o convite
ASSEMBLY_SESSIONS = 5
INVITE_SESSIONS = 5

# A fração das cotas em circulação que dá o direito de convocar: 0,10 é 10%
CONVENE_SHARE = Decimal("0.10")

# Meses entre uma assembleia e a seguinte na mesma gestora, contados do fim da anterior
INTERVAL_MONTHS = 3

# Meses em que o gestor afastado não funda outra gestora
FOUNDING_BAN_MONTHS = 6

SWAP = FundAssemblyAgenda.REPLACE_MANAGER
FEE = FundAssemblyAgenda.FEE_INCREASE
MERGE = FundAssemblyAgenda.MERGE

# O desfecho de cada pauta quando a votação fecha: (vence, não vence)
OUTCOMES: dict[FundAssemblyAgenda, tuple[FundAssemblyStatus, FundAssemblyStatus]] = {
    SWAP: (FundAssemblyStatus.REPLACED, FundAssemblyStatus.KEPT),
    FEE: (FundAssemblyStatus.APPROVED, FundAssemblyStatus.REJECTED),
    MERGE: (FundAssemblyStatus.APPROVED, FundAssemblyStatus.REJECTED),
}

# Os estados das votações concluídas pelo voto: o convite recusado, vencido ou cancelado não conta
CONCLUDED = tuple(status for outcome in OUTCOMES.values() for status in outcome)
ACTIVE = (FundAssemblyStatus.INVITED, FundAssemblyStatus.VOTING)


@dataclass(frozen=True)
class AutoVote:
    """Os votos que ninguém dá: bots cotistas e formador de mercado no aumento de taxa.

    `in_favor` é o voto dos dois: a favor quando a gestora bateu o CDI na janela de desempenho.
    """

    bots: Decimal
    market: Decimal
    in_favor: bool

    @property
    def quotas(self) -> Decimal:
        return self.bots + self.market

    @property
    def stance(self) -> FundAssemblyStance:
        return "favor" if self.in_favor else "against"


@dataclass(frozen=True)
class Tally:
    """O placar em cotas: a favor da pauta, contra e abstenção."""

    in_favor: Decimal
    against: Decimal
    abstention: Decimal
    # A parte da abstenção que nunca vota: bots e formador de mercado nas pautas de troca e fusão
    # (e, na pauta de taxa, o gestor e os co-gestores)
    non_voting: Decimal

    @property
    def total(self) -> Decimal:
        return self.in_favor + self.against + self.abstention

    @property
    def wins(self) -> bool:
        """A pauta vence com mais cotas a favor que contra; o empate, e a votação sem voto, não."""
        return self.in_favor > self.against

    @property
    def missing_to_win(self) -> Decimal:
        """As cotas a favor que faltam para a pauta vencer; zero quando ela já vence."""
        return Decimal(0) if self.wins else self.against - self.in_favor + 1


def tally(
    *,
    total: Decimal,
    manager_user_id: int,
    holdings: Mapping[int, Decimal],
    votes: Mapping[int, bool],
) -> Tally:
    """Apura a votação sobre as cotas que cada jogador tem agora.

    O gestor não vota: as cotas dele contam contra. Quem tem cota e votou pesa o que tem;
    quem não votou, os bots e o formador de mercado (o que sobra de `total`) abstêm.
    """
    in_favor = Decimal(0)
    against = holdings.get(manager_user_id, Decimal(0))
    for user_id, quotas in holdings.items():
        if user_id == manager_user_id or quotas <= 0:
            continue
        vote = votes.get(user_id)
        if vote is True:
            in_favor += quotas
        elif vote is False:
            against += quotas
    non_voting = max(Decimal(0), total - sum(holdings.values(), Decimal(0)))
    return Tally(
        in_favor=in_favor,
        against=against,
        abstention=total - in_favor - against,
        non_voting=non_voting,
    )


def fee_tally(
    *,
    total: Decimal,
    holdings: Mapping[int, Decimal],
    votes: Mapping[int, bool],
    excluded: Collection[int],
    automatic: Decimal = Decimal(0),
    automatic_in_favor: bool = False,
) -> Tally:
    """Apura o aumento de taxa: vota quem tem cota e não opera a gestora.

    O gestor e os co-gestores (`excluded`) não pesam nem a favor nem contra. As cotas dos bots
    e do formador de mercado (`automatic`) pesam inteiras para o lado de `automatic_in_favor`.
    """
    eligible = {
        user_id: quotas
        for user_id, quotas in holdings.items()
        if user_id not in excluded and quotas > 0
    }
    in_favor = sum((q for u, q in eligible.items() if votes.get(u) is True), Decimal(0))
    against = sum((q for u, q in eligible.items() if votes.get(u) is False), Decimal(0))
    if automatic_in_favor:
        in_favor += automatic
    else:
        against += automatic
    return Tally(
        in_favor=in_favor,
        against=against,
        abstention=total - in_favor - against,
        non_voting=total - sum(eligible.values(), Decimal(0)) - automatic,
    )


def raises_fee(fund: "Fund", management_fee: Decimal, performance_fee: Decimal) -> bool:
    """Se alguma taxa pedida passa da que está em vigor: só a alta passa pela votação."""
    terms = fund.terms
    return (
        management_fee > terms.management_fee or performance_fee > terms.performance_fee
    )


def stance_of(
    user_id: int, manager_user_id: int | None, votes: Mapping[int, bool]
) -> FundAssemblyStance:
    """Para onde vão as cotas de um jogador: o gestor sempre contra, quem não votou abstém.

    Sem `manager_user_id` (a pauta em que o gestor vota como qualquer cotista) vale só o voto.
    """
    if user_id == manager_user_id:
        return "against"
    vote = votes.get(user_id)
    if vote is None:
        return "abstain"
    return "favor" if vote else "against"


def convene_block(
    *,
    quotas: Decimal,
    total: Decimal,
    is_manager: bool,
    listed: bool,
    active: bool,
    last_end: date | None,
    today: date,
    grace_ends: date | None = None,
    merge_ends: date | None = None,
) -> tuple[FundAssemblyBlock | None, date | None]:
    """Por que alguém não pode convocar a troca de gestor agora, e quando o intervalo, a carência ou a fusão em votação libera; nulo quando pode."""
    if grace_ends is not None and today < grace_ends:
        return "grace", grace_ends
    if not listed:
        return "unlisted", None
    if is_manager:
        return "manager", None
    if active:
        return "pending", None
    if quotas < total * CONVENE_SHARE:
        return "share", None
    if last_end is not None:
        next_allowed = add_months(last_end, INTERVAL_MONTHS)
        if today < next_allowed:
            return "interval", next_allowed
    if merge_ends is not None:
        return "merge_open", merge_ends
    return None, None


def fee_block(
    *, is_manager: bool, listed: bool, active: bool
) -> FundAssemblyBlock | None:
    """Por que alguém não pode propor o aumento de taxa agora; nulo quando pode.

    Só o gestor principal propõe, sem exigir cotas e sem intervalo entre propostas.
    """
    if not listed:
        return "unlisted"
    if not is_manager:
        return "manager_only"
    if active:
        return "pending"
    return None


def merge_block(
    *,
    is_manager: bool,
    listed: bool,
    active: bool,
    today: date,
    grace_ends: date | None = None,
    merge_ends: date | None = None,
    swap_ends: date | None = None,
) -> tuple[FundAssemblyBlock | None, date | None]:
    """Por que alguém não pode propor a fusão desta gestora agora, e até quando; nulo quando pode.

    Só o gestor principal propõe, sem exigir cotas e sem intervalo entre propostas. A carência do
    modo aquisição hostil vale como na troca de gestor, e a troca de gestor em votação ou com
    convite pendente (`swap_ends`) segura a fusão até o resultado dela.
    """
    if grace_ends is not None and today < grace_ends:
        return "grace", grace_ends
    block = fee_block(is_manager=is_manager, listed=listed, active=active)
    if block == "pending":
        return block, merge_ends
    if block is not None:
        return block, None
    if swap_ends is not None:
        return "swap_open", swap_ends
    return None, None


class FundAssemblies:
    """As assembleias de cotistas, uma votação por pauta: convite, votação e apuração.

    O estado vivo de cada gestora mora em `Fund` (a assembleia ativa e os votos de cada pauta e as
    concluídas pelo voto); esta classe valida, grava e apura. Quem aplica o desfecho no fechamento
    é o `FundBook`.
    """

    def __init__(
        self,
        simulation_id: int,
        engine: SimulationEngine,
        participants: Callable[[], list[UserDTO]],
        beat_cdi: Callable[["Fund", date], bool],
        grace_ends: date | None = None,
    ) -> None:
        self._simulation_id = simulation_id
        self._engine = engine
        self._participants = participants
        # A decisão de desempenho que bots e formador de mercado votam no aumento de taxa
        self._beat_cdi = beat_cdi
        # No modo aquisição hostil a assembleia só abre a partir deste dia; nulo, sem carência
        self.grace_ends = grace_ends

    # =========================
    # Estado gravado
    # =========================

    def load(
        self, fund_id: int
    ) -> tuple[
        dict[FundAssemblyAgenda, FundAssemblyDTO],
        dict[FundAssemblyAgenda, dict[int, bool]],
        list[FundAssemblyDTO],
    ]:
        """As assembleias ativas por pauta com os votos delas e as concluídas pela votação, da mais antiga à mais nova."""
        rows = repository.fund.assemblies(fund_id)
        active = {a.agenda: a for a in rows if a.status in ACTIVE}
        votes = {
            agenda: {
                v.user_id: v.in_favor for v in repository.fund.assembly_votes(a.id)
            }
            for agenda, a in active.items()
        }
        return active, votes, [a for a in rows if a.status in CONCLUDED]

    def founding_blocked_until(self, user_id: int, today: date) -> date | None:
        """Até quando o gestor afastado não funda outra gestora; nulo sem bloqueio."""
        removed_on = repository.fund.last_removal(self._simulation_id, user_id)
        if removed_on is None:
            return None
        until = add_months(removed_on, FOUNDING_BAN_MONTHS)
        return until if today < until else None

    # =========================
    # Cotas
    # =========================

    def holdings(self, fund: "Fund") -> dict[int, Decimal]:
        """As cotas dos jogadores (sem bots) na carteira pessoal, por id de usuário."""
        return self._held_by(fund, bots=False)

    def _held_by(self, fund: "Fund", *, bots: bool) -> dict[int, Decimal]:
        """As cotas na carteira pessoal dos participantes que são bots (`bots`) ou jogadores."""
        held: dict[int, Decimal] = {}
        for user in self._participants():
            if user.is_bot is not bots:
                continue
            position = self._engine.broker.get_positions(user.client_id).get(
                fund.ticker
            )
            if position is not None and position.size > 0:
                held[user.id] = position.size
        return held

    def auto_vote(self, fund: "Fund") -> AutoVote:
        """O voto dos bots cotistas e do formador de mercado no aumento de taxa, pelas cotas e pelo desempenho de agora.

        O voto é calculado a cada consulta: acompanha o desempenho até o fechamento.
        """
        operators = operators_of(fund)
        bots = sum(
            (
                quotas
                for user_id, quotas in self._held_by(fund, bots=True).items()
                if user_id not in operators
            ),
            Decimal(0),
        )
        market = fund.account.maker_quotas
        return AutoVote(
            bots=bots,
            market=market,
            in_favor=bots + market > 0
            and self._beat_cdi(fund, self._engine.current_date),
        )

    def score(
        self,
        fund: "Fund",
        agenda: FundAssemblyAgenda,
        holdings: Mapping[int, Decimal] | None = None,
    ) -> Tally:
        """O placar de agora da votação da pauta; as cotas e, no aumento de taxa, o desempenho são os de agora."""
        held = self.holdings(fund) if holdings is None else holdings
        votes = fund.assembly_votes.get(agenda, {})
        if agenda is FEE:
            auto = self.auto_vote(fund)
            return fee_tally(
                total=fund.account.quotas,
                holdings=held,
                votes=votes,
                excluded=operators_of(fund),
                automatic=auto.quotas,
                automatic_in_favor=auto.in_favor,
            )
        if agenda is MERGE:
            # Na fusão o gestor e os co-gestores votam como qualquer cotista
            return fee_tally(
                total=fund.account.quotas, holdings=held, votes=votes, excluded=()
            )
        return tally(
            total=fund.account.quotas,
            manager_user_id=fund.terms.manager_user_id,
            holdings=held,
            votes=votes,
        )

    def can_vote(
        self,
        fund: "Fund",
        agenda: FundAssemblyAgenda,
        user: UserDTO,
        holdings: Mapping[int, Decimal],
    ) -> bool:
        """Se `user` tem voto na pauta: cotista jogador; na troca de gestor e no aumento de taxa, quem opera a gestora não vota."""
        if user.is_bot or holdings.get(user.id, Decimal(0)) <= 0:
            return False
        if agenda is MERGE:
            return True
        if agenda is FEE:
            return user.id not in operators_of(fund)
        return user.id != fund.terms.manager_user_id

    def open_votes_for(self, fund: "Fund", user: UserDTO) -> list[FundAssemblyDTO]:
        """As votações abertas em que `user` pode votar e ainda não votou."""
        holdings = self.holdings(fund)
        return [
            assembly
            for agenda, assembly in fund.assemblies.items()
            if assembly.status is FundAssemblyStatus.VOTING
            and self.can_vote(fund, agenda, user, holdings)
            and user.id not in fund.assembly_votes.get(agenda, {})
        ]

    # =========================
    # Convocar
    # =========================

    def block_for(
        self,
        fund: "Fund",
        user: UserDTO,
        today: date,
        agenda: FundAssemblyAgenda = SWAP,
        holdings: Mapping[int, Decimal] | None = None,
    ) -> tuple[FundAssemblyBlock | None, date | None]:
        """Por que `user` não põe a pauta em votação agora; o intervalo entre convocações é só da troca de gestor."""
        is_manager = user.id == fund.terms.manager_user_id
        active = agenda in fund.assemblies
        if agenda is FEE:
            return fee_block(
                is_manager=is_manager, listed=fund.listed, active=active
            ), None
        if agenda is MERGE:
            open_merge = fund.assemblies.get(MERGE)
            open_swap = fund.assemblies.get(SWAP)
            return merge_block(
                is_manager=is_manager,
                listed=fund.listed,
                active=active,
                today=today,
                grace_ends=self.grace_ends,
                merge_ends=open_merge.ends_on if open_merge else None,
                swap_ends=open_swap.ends_on if open_swap else None,
            )
        held = self.holdings(fund) if holdings is None else holdings
        last = next(
            (a for a in reversed(fund.assembly_history) if a.agenda is SWAP), None
        )
        return convene_block(
            quotas=held.get(user.id, Decimal(0)),
            total=fund.account.quotas,
            is_manager=is_manager,
            listed=fund.listed,
            active=active,
            last_end=last.closed_on if last else None,
            today=today,
            grace_ends=self.grace_ends,
            merge_ends=(
                open_merge.ends_on
                if (open_merge := fund.assemblies.get(MERGE)) is not None
                else None
            ),
        )

    def convene(
        self,
        fund: "Fund",
        convener: UserDTO,
        candidate_nickname: str | None,
        today: date,
    ) -> FundAssemblyDTO:
        """Convoca a assembleia: com o próprio convocador indicado a votação abre já; com um
        aliado, o convite espera a resposta dele."""
        block, next_allowed = self.block_for(fund, convener, today, SWAP)
        if block is not None:
            raise ConflictError(block_message(block, next_allowed))
        nickname = (
            convener.nickname if candidate_nickname is None else candidate_nickname
        )
        candidate = next(
            (
                u
                for u in self._participants()
                if u.nickname == nickname and not u.is_bot
            ),
            None,
        )
        if candidate is None:
            raise UnprocessableEntityError("O indicado precisa ser um jogador da sala")
        if candidate.id == fund.terms.manager_user_id:
            raise UnprocessableEntityError("O indicado já é o gestor")

        assembly = FundAssemblyDTO(
            id=0,
            agenda=SWAP,
            convener_user_id=convener.id,
            candidate_user_id=candidate.id,
            previous_manager_user_id=fund.terms.manager_user_id,
            status=FundAssemblyStatus.INVITED,
            called_on=today,
            started_on=None,
            ends_on=window_end(today, INVITE_SESSIONS),
            closed_on=None,
            in_favor_quotas=None,
            against_quotas=None,
            abstention_quotas=None,
        )
        assembly = repository.fund.create_assembly(fund.terms.id, assembly)
        fund.assemblies[SWAP] = assembly
        fund.assembly_votes[SWAP] = {}
        if candidate.id == convener.id:
            return self._open_voting(fund, assembly, today)
        return assembly

    def propose_fee(
        self,
        fund: "Fund",
        proposer: UserDTO,
        management_fee: Decimal,
        performance_fee: Decimal,
        today: date,
    ) -> FundAssemblyDTO:
        """O gestor principal leva um aumento de taxa à votação, que abre hoje sem voto algum."""
        block, _ = self.block_for(fund, proposer, today, FEE)
        if block == "manager_only":
            raise ForbiddenError(block_message(block, None))
        if block is not None:
            raise ConflictError(block_message(block, None))
        if not raises_fee(fund, management_fee, performance_fee):
            raise UnprocessableEntityError(
                "A proposta não sobe nenhuma taxa: baixar vale sem votação"
            )
        terms = fund.terms
        assembly = FundAssemblyDTO(
            id=0,
            agenda=FEE,
            convener_user_id=proposer.id,
            candidate_user_id=None,
            previous_manager_user_id=terms.manager_user_id,
            status=FundAssemblyStatus.VOTING,
            called_on=today,
            started_on=today,
            ends_on=window_end(today, ASSEMBLY_SESSIONS),
            closed_on=None,
            in_favor_quotas=None,
            against_quotas=None,
            abstention_quotas=None,
            previous_management_fee=terms.management_fee,
            previous_performance_fee=terms.performance_fee,
            proposed_management_fee=management_fee,
            proposed_performance_fee=performance_fee,
        )
        assembly = repository.fund.create_assembly(terms.id, assembly)
        fund.assemblies[FEE] = assembly
        fund.assembly_votes[FEE] = {}
        return assembly

    def propose_merge(
        self, mother: "Fund", daughter: "Fund", proposer: UserDTO, today: date
    ) -> None:
        """O gestor principal das duas leva a fusão às assembleias, que abrem hoje juntas e fecham no mesmo pregão.

        Quem propõe vota a favor nas duas; as linhas guardam a gestora parceira e qual delas é a incorporada.
        """
        for fund in (mother, daughter):
            block, next_allowed = self.block_for(fund, proposer, today, MERGE)
            if block == "manager_only":
                raise ForbiddenError("Só o gestor propõe a fusão.")
            if block is not None:
                raise ConflictError(block_message(block, next_allowed))
        ends_on = window_end(today, ASSEMBLY_SESSIONS)
        for fund, partner, absorbed in (
            (mother, daughter, False),
            (daughter, mother, True),
        ):
            assembly = FundAssemblyDTO(
                id=0,
                agenda=MERGE,
                convener_user_id=proposer.id,
                candidate_user_id=None,
                previous_manager_user_id=fund.terms.manager_user_id,
                status=FundAssemblyStatus.VOTING,
                called_on=today,
                started_on=today,
                ends_on=ends_on,
                closed_on=None,
                in_favor_quotas=None,
                against_quotas=None,
                abstention_quotas=None,
                partner_fund_id=partner.terms.id,
                absorbed=absorbed,
            )
            created = repository.fund.create_assembly(fund.terms.id, assembly)
            fund.assemblies[MERGE] = created
            fund.assembly_votes[MERGE] = {}
            self._record_vote(fund, created, proposer.id, True, today)

    def merge_ready(self, fund: "Fund", today: date) -> bool:
        """Se a votação da fusão da gestora chegou ao último pregão."""
        assembly = fund.assemblies.get(MERGE)
        return (
            assembly is not None
            and assembly.status is FundAssemblyStatus.VOTING
            and today >= assembly.ends_on
        )

    def close_merge(
        self,
        fund: "Fund",
        today: date,
        approved: bool,
        shortfall: Decimal = Decimal(0),
    ) -> FundAssemblyDTO | None:
        """Grava o fim da votação da fusão com o placar de agora; aprovada só quando as duas assembleias aprovam e o caixa cobre a saída.

        `shortfall` é o que faltou nos caixas quando as duas votações ganharam e a fusão caiu por isso: a assembleia guarda o motivo.
        """
        assembly = fund.assemblies.get(MERGE)
        if assembly is None:
            return None
        result = self.score(fund, MERGE)
        counted = assembly.model_copy(
            update={
                "in_favor_quotas": result.in_favor,
                "against_quotas": result.against,
                "abstention_quotas": result.abstention,
                "merge_shortfall": shortfall if shortfall > 0 else None,
            }
        )
        wins, loses = OUTCOMES[MERGE]
        return self._conclude(fund, counted, wins if approved else loses, today)

    def answer(self, fund: "Fund", user: UserDTO, accept: bool, today: date) -> None:
        """O aliado indicado responde ao convite: aceitar abre a votação, recusar encerra."""
        assembly = fund.assemblies.get(SWAP)
        if (
            assembly is None
            or assembly.status is not FundAssemblyStatus.INVITED
            or assembly.candidate_user_id != user.id
        ):
            raise ForbiddenError("Não há convite desta gestora esperando você")
        if accept:
            self._open_voting(fund, assembly, today)
        else:
            self._conclude(fund, assembly, FundAssemblyStatus.DECLINED, today)

    def cancel(self, fund: "Fund", user: UserDTO, today: date) -> None:
        """Quem convocou cancela o convite que o aliado ainda não respondeu."""
        assembly = fund.assemblies.get(SWAP)
        if assembly is None or assembly.status is not FundAssemblyStatus.INVITED:
            raise ConflictError("Não há convite esperando resposta")
        if assembly.convener_user_id != user.id:
            raise ForbiddenError("Só quem convocou cancela o convite")
        self._conclude(fund, assembly, FundAssemblyStatus.CANCELLED, today)

    def expire_invite(self, fund: "Fund", today: date) -> bool:
        """O convite que passou do último pregão sem resposta cai como recusa."""
        assembly = fund.assemblies.get(SWAP)
        if (
            assembly is None
            or assembly.status is not FundAssemblyStatus.INVITED
            or today < assembly.ends_on
        ):
            return False
        self._conclude(fund, assembly, FundAssemblyStatus.EXPIRED, today)
        return True

    def _open_voting(
        self, fund: "Fund", assembly: FundAssemblyDTO, today: date
    ) -> FundAssemblyDTO:
        """A votação abre hoje por 5 pregões, com quem convocou a favor."""
        voting = assembly.model_copy(
            update={
                "status": FundAssemblyStatus.VOTING,
                "started_on": today,
                "ends_on": window_end(today, ASSEMBLY_SESSIONS),
            }
        )
        repository.fund.save_assembly(voting)
        fund.assemblies[assembly.agenda] = voting
        self._record_vote(fund, voting, assembly.convener_user_id, True, today)
        return voting

    def _conclude(
        self,
        fund: "Fund",
        assembly: FundAssemblyDTO,
        status: FundAssemblyStatus,
        today: date,
    ) -> FundAssemblyDTO:
        """Grava o fim da assembleia; as concluídas pela votação entram no histórico, de onde sai o intervalo até a próxima troca."""
        closed = assembly.model_copy(update={"status": status, "closed_on": today})
        repository.fund.save_assembly(closed)
        fund.assemblies.pop(assembly.agenda, None)
        fund.assembly_votes.pop(assembly.agenda, None)
        if status in CONCLUDED:
            fund.assembly_history.append(closed)
        return closed

    def cancel_open(
        self, fund: "Fund", agenda: FundAssemblyAgenda, today: date
    ) -> None:
        """Encerra sem resultado a assembleia aberta da pauta, quando o motivo dela deixa de existir."""
        assembly = fund.assemblies.get(agenda)
        if assembly is not None:
            self._conclude(fund, assembly, FundAssemblyStatus.CANCELLED, today)

    # =========================
    # Votar e apurar
    # =========================

    def vote(
        self,
        fund: "Fund",
        agenda: FundAssemblyAgenda,
        user: UserDTO,
        in_favor: bool,
        today: date,
    ) -> None:
        """O cotista vota na pauta; mudar o voto vale até o fim da votação."""
        assembly = fund.assemblies.get(agenda)
        if assembly is None or assembly.status is not FundAssemblyStatus.VOTING:
            raise ConflictError("Não há votação aberta desta pauta nesta gestora")
        if agenda is not MERGE and user.id in operators_of(fund):
            raise ForbiddenError(
                "O gestor não vota: as cotas dele contam contra"
                if agenda is SWAP
                else "O gestor e os co-gestores não votam o aumento de taxa"
            )
        if not self.can_vote(fund, agenda, user, self.holdings(fund)):
            raise ForbiddenError("Só vota quem tem cotas da gestora")
        self._record_vote(fund, assembly, user.id, in_favor, today)

    def _record_vote(
        self,
        fund: "Fund",
        assembly: FundAssemblyDTO,
        user_id: int,
        in_favor: bool,
        today: date,
    ) -> None:
        repository.fund.save_assembly_vote(
            assembly.id,
            FundAssemblyVoteDTO(user_id=user_id, in_favor=in_favor, voted_on=today),
        )
        votes = fund.assembly_votes.setdefault(assembly.agenda, {})
        votes[user_id] = in_favor

    def close_voting(
        self, fund: "Fund", agenda: FundAssemblyAgenda, today: date
    ) -> tuple[FundAssemblyDTO, Tally] | None:
        """Fecha a votação da pauta que chegou ao último pregão, pelas cotas de agora; nulo antes disso.

        A fusão fecha pelas duas assembleias juntas (`close_merge`).
        """
        assembly = fund.assemblies.get(agenda)
        if (
            agenda is MERGE
            or assembly is None
            or assembly.status is not FundAssemblyStatus.VOTING
            or today < assembly.ends_on
        ):
            return None
        result = self.score(fund, agenda)
        wins, loses = OUTCOMES[agenda]
        status = wins if result.wins else loses
        counted = assembly.model_copy(
            update={
                "in_favor_quotas": result.in_favor,
                "against_quotas": result.against,
                "abstention_quotas": result.abstention,
            }
        )
        return self._conclude(fund, counted, status, today), result

    # =========================
    # Painel
    # =========================

    def panel(
        self,
        fund: "Fund",
        viewer: UserDTO,
        today: date,
        nicknames: Mapping[int, str],
        colors: Mapping[int, str],
        merge_view: Callable[["Fund", FundAssemblyDTO], FundAssemblyMergeDTO | None],
        partners: Mapping[int, tuple[str, str]],
        merge_partners: list[FundMergeSideDTO],
    ) -> FundAssemblyPanelDTO:
        """A seção Assembleia como `viewer` a vê.

        `merge_view` monta a fusão de cada votação (ela mora nas duas gestoras) e `partners` dá o
        ticker e o nome de cada gestora por id.
        """
        holdings = self.holdings(fund)
        total = fund.account.quotas
        options = []
        for agenda in FundAssemblyAgenda:
            block, next_allowed = self.block_for(fund, viewer, today, agenda, holdings)
            options.append(
                FundAssemblyOptionDTO(
                    agenda=agenda,
                    can_convene=block is None,
                    block=block,
                    next_allowed_on=next_allowed,
                )
            )
        return FundAssemblyPanelDTO(
            current=[
                self._status(
                    fund,
                    assembly,
                    viewer,
                    today,
                    holdings,
                    nicknames,
                    colors,
                    merge_view(fund, assembly),
                )
                for assembly in sorted(
                    fund.assemblies.values(), key=lambda a: a.called_on
                )
            ],
            history=[
                result
                for assembly in reversed(fund.assembly_history)
                if (result := _result(assembly, nicknames, partners)) is not None
            ],
            options=options,
            merge_partners=merge_partners,
            convene_quotas=total * CONVENE_SHARE,
            my_quotas=holdings.get(viewer.id, Decimal(0)),
            blocked_founding_until=self.founding_blocked_until(viewer.id, today),
        )

    def _status(
        self,
        fund: "Fund",
        assembly: FundAssemblyDTO,
        viewer: UserDTO,
        today: date,
        holdings: Mapping[int, Decimal],
        nicknames: Mapping[int, str],
        colors: Mapping[int, str],
        merge: FundAssemblyMergeDTO | None,
    ) -> FundAssemblyStatusDTO:
        agenda = assembly.agenda
        voting = assembly.status is FundAssemblyStatus.VOTING
        manager_id = fund.terms.manager_user_id
        operators = operators_of(fund)
        votes = fund.assembly_votes.get(agenda, {})
        total = fund.account.quotas
        current = self.score(fund, agenda, holdings) if voting else None
        auto = self.auto_vote(fund) if voting and agenda is FEE else None
        voters = (
            sorted(
                (
                    FundAssemblyVoterDTO(
                        user_id=user_id,
                        nickname=nicknames.get(user_id, "?"),
                        color=colors.get(user_id),
                        quotas=quotas,
                        share=ratio(quotas, total),
                        stance=stance_of(
                            user_id, None if agenda is MERGE else manager_id, votes
                        ),
                        is_manager=user_id == manager_id,
                    )
                    for user_id, quotas in holdings.items()
                    if agenda in (SWAP, MERGE) or user_id not in operators
                ),
                key=lambda voter: voter.quotas,
                reverse=True,
            )
            if voting
            else []
        )
        start = (
            assembly.started_on
            if voting and assembly.started_on
            else assembly.called_on
        )
        return FundAssemblyStatusDTO(
            id=assembly.id,
            agenda=agenda,
            status=assembly.status,
            convener_user_id=assembly.convener_user_id,
            convener_nickname=nicknames.get(assembly.convener_user_id, "?"),
            candidate_user_id=assembly.candidate_user_id,
            candidate_nickname=_nickname(assembly.candidate_user_id, nicknames),
            fee=_fee_dto(assembly),
            merge=merge,
            called_on=assembly.called_on,
            started_on=assembly.started_on,
            ends_on=assembly.ends_on,
            session=window_session(
                start, today, ASSEMBLY_SESSIONS if voting else INVITE_SESSIONS
            ),
            sessions=ASSEMBLY_SESSIONS if voting else INVITE_SESSIONS,
            tally=_tally_dto(current) if current else None,
            voters=voters,
            non_voting=current.non_voting if current else Decimal(0),
            bots=_auto_dto(auto.bots, auto, total) if auto else None,
            market=_auto_dto(auto.market, auto, total) if auto else None,
            my_vote=votes.get(viewer.id),
            can_vote=voting and self.can_vote(fund, agenda, viewer, holdings),
        )


def _nickname(user_id: int | None, nicknames: Mapping[int, str]) -> str | None:
    return None if user_id is None else nicknames.get(user_id, "?")


def _fee_dto(assembly: FundAssemblyDTO) -> FundAssemblyFeeDTO | None:
    """As taxas da pauta de aumento; nulo nas outras pautas."""
    if (
        assembly.previous_management_fee is None
        or assembly.previous_performance_fee is None
        or assembly.proposed_management_fee is None
        or assembly.proposed_performance_fee is None
    ):
        return None
    return FundAssemblyFeeDTO(
        management_from=assembly.previous_management_fee,
        management_to=assembly.proposed_management_fee,
        performance_from=assembly.previous_performance_fee,
        performance_to=assembly.proposed_performance_fee,
    )


def _auto_dto(
    quotas: Decimal, auto: AutoVote, total: Decimal
) -> FundAssemblyAutoVoteDTO:
    return FundAssemblyAutoVoteDTO(
        quotas=quotas, share=ratio(quotas, total), stance=auto.stance
    )


def _tally_dto(result: Tally) -> FundAssemblyTallyDTO:
    return FundAssemblyTallyDTO(
        in_favor=result.in_favor,
        against=result.against,
        abstention=result.abstention,
        total=result.total,
        missing_to_win=result.missing_to_win,
    )


def _result(
    assembly: FundAssemblyDTO,
    nicknames: Mapping[int, str],
    partners: Mapping[int, tuple[str, str]],
) -> FundAssemblyResultDTO | None:
    """O resultado gravado de uma votação concluída."""
    if (
        assembly.started_on is None
        or assembly.closed_on is None
        or assembly.in_favor_quotas is None
        or assembly.against_quotas is None
        or assembly.abstention_quotas is None
    ):
        return None
    approved = assembly.status is FundAssemblyStatus.APPROVED
    partner = (
        partners.get(assembly.partner_fund_id)
        if assembly.partner_fund_id is not None
        else None
    )
    return FundAssemblyResultDTO(
        id=assembly.id,
        agenda=assembly.agenda,
        status=assembly.status,
        convener_nickname=nicknames.get(assembly.convener_user_id, "?"),
        candidate_nickname=_nickname(assembly.candidate_user_id, nicknames),
        previous_manager_nickname=nicknames.get(assembly.previous_manager_user_id, "?"),
        started_on=assembly.started_on,
        closed_on=assembly.closed_on,
        tally=_tally_dto(
            Tally(
                in_favor=assembly.in_favor_quotas,
                against=assembly.against_quotas,
                abstention=assembly.abstention_quotas,
                non_voting=Decimal(0),
            )
        ),
        fee=_fee_dto(assembly),
        effective_on=next_month_turn(assembly.closed_on)
        if approved and assembly.agenda is FEE
        else None,
        partner_ticker=partner[0] if partner else None,
        partner_name=partner[1] if partner else None,
        absorbed=assembly.absorbed,
        merge_shortfall=assembly.merge_shortfall,
    )


def block_message(block: FundAssemblyBlock, next_allowed: date | None) -> str:
    match block:
        case "unlisted":
            return "A gestora ainda não abriu o capital."
        case "manager":
            return "O gestor não convoca assembleia contra si mesmo."
        case "manager_only":
            return "Só o gestor propõe aumento de taxa."
        case "pending" if next_allowed is not None:
            return f"Já há uma fusão em votação até {next_allowed:%d/%m}."
        case "pending":
            return "A gestora já tem uma votação aberta desta pauta."
        case "swap_open":
            return "A gestora tem uma troca de gestor em andamento: a fusão espera o resultado dela."
        case "merge_open" if next_allowed is not None:
            return f"A gestora tem uma fusão em votação até {next_allowed:%d/%m}: a troca de gestor espera o resultado dela."
        case "merge_open":
            return "A gestora tem uma fusão em votação: a troca de gestor espera o resultado dela."
        case "frozen" if next_allowed is not None:
            return f"O gestor governa o país e a gestora fica congelada até {next_allowed:%d/%m/%Y}."
        case "frozen":
            return "O gestor governa o país e a gestora fica congelada."
        case "no_partner":
            return "A fusão exige outra gestora que o mesmo gestor gere."
        case "busy":
            return "A gestora tem emissão, recompra ou oferta em aberto."
        case "share":
            return f"Convocar exige {CONVENE_SHARE:.0%} das cotas da gestora."
        case "grace" if next_allowed is not None:
            return (
                f"A assembleia só abre depois da carência, em {next_allowed:%d/%m/%Y}."
            )
        case "interval" if next_allowed is not None:
            return (
                f"A gestora aceita nova assembleia a partir de {next_allowed:%d/%m/%Y}."
            )
        case _:
            return "A gestora não aceita assembleia agora."
