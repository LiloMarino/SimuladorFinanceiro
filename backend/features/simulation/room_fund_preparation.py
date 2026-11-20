"""
A preparação da gestora de cada jogador no lobby, só em memória, no molde do partido:
quem escolhe fundar leva a identidade da Minha gestora (nome e sigla) e a gestora nasce vazia
no 1º dia da partida. A escolha sobrevive à desconexão; só funda quem está na sala quando a
partida começa, e só com a expansão Gestoras ligada nas regras.

Quem funda convida até três co-gestores entre os jogadores da sala, cada um com a parte das
taxas; o convite é privado de quem convidou e de quem foi convidado. Os que aceitaram entram
ativos na gestora no 1º dia; o convite sem resposta e o recusado não entram na partida.

Na aquisição hostil em equipes a equipe é a gestora: cada humano está em exatamente um grupo,
o do fundador ou o da gestora cujo convite aceitou, e a equipe leva o número do fundador na
ordem de usuário.
"""

from collections import Counter
from decimal import Decimal
from threading import Lock
from typing import ClassVar

from backend.core import repository
from backend.core.dto.preparation import (
    FundComanagerInviteDTO,
    FundComanagerPreparationDTO,
    FundIdentityDTO,
    FundPreparationDTO,
    MyPreparationDTO,
    PreparationsDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import FundPreparationComanagerStatus, FundPreparationKind
from backend.core.exceptions.http_exceptions import ConflictError, NotFoundError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.teams import TEAM_COUNT
from backend.features.funds.fund_comanagers import MAX_COMANAGERS, ensure_shares_fit

MIN_TAKEOVER_PLAYERS = 2

Status = FundPreparationComanagerStatus


class RoomFundPreparation:
    # user_id -> a identidade da gestora que o jogador funda; quem fica sem gestora não tem entrada
    _entries: ClassVar[dict[int, FundIdentityDTO]] = {}
    # founder_id -> guest_id -> (parte das taxas, estado do convite); a vaga conta o convite sem resposta e o aceito
    _comanagers: ClassVar[
        dict[int, dict[int, tuple[Decimal, FundPreparationComanagerStatus]]]
    ] = {}
    _lock = Lock()

    @classmethod
    def locked_reason(cls) -> str | None:
        """Por que a escolha da gestora não aceita mudança; nulo quando o lobby está aberto a ela."""
        if SimulationManager.has_active_simulation():
            return "A partida já começou: a preparação ficou travada."
        if SettingsManager.get_selected_simulation_id() is not None:
            return "Partida salva selecionada: a preparação vale só para partida nova."
        return None

    @classmethod
    def choose(
        cls,
        me: UserDTO,
        kind: FundPreparationKind,
        identity: FundIdentityDTO | None,
    ) -> None:
        """Troca a escolha de `me`: fundar a Minha gestora ou ficar sem."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        with cls._lock:
            if kind is FundPreparationKind.NONE:
                cls._entries.pop(me.id, None)
                cls._comanagers.pop(me.id, None)
                return
            if identity is None:
                raise ConflictError("Salve a Minha gestora antes de fundá-la.")
            if (
                SettingsManager.get().is_takeover_teams
                and me.id not in cls._entries
                and cls._accepted_in(me.id) is not None
            ):
                raise ConflictError(
                    "Você já é co-gestor de uma gestora: quem está num grupo não funda outra."
                )
            cls._entries[me.id] = identity

    @classmethod
    def restore(cls, me: UserDTO, identity: FundIdentityDTO) -> bool:
        """Quem fundou na última sala volta fundando; diz se recriou."""
        if cls.locked_reason() is not None:
            return False
        with cls._lock:
            if me.id in cls._entries:
                return False
            cls._entries[me.id] = identity
        return True

    @classmethod
    def drop(cls, user_id: int) -> None:
        """O jogador saiu da sala de vez: some a escolha dele."""
        with cls._lock:
            cls._entries.pop(user_id, None)
            cls._comanagers.pop(user_id, None)
            for guests in cls._comanagers.values():
                guests.pop(user_id, None)

    @classmethod
    def clear(cls) -> None:
        """A partida começou: a próxima sala começa sem preparação."""
        with cls._lock:
            cls._entries.clear()
            cls._comanagers.clear()

    @classmethod
    def invite_comanager(
        cls, me: UserDTO, humans: list[UserDTO], nickname: str, share: Decimal
    ) -> None:
        """O fundador convida um jogador da sala a co-gestor; o convite novo ocupa o lugar do recusado."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        guest = next((u for u in humans if u.nickname == nickname), None)
        if guest is None:
            raise NotFoundError("O jogador não está na sala.")
        with cls._lock:
            if me.id not in cls._entries:
                raise ConflictError("Só quem funda uma gestora convida co-gestores.")
            if guest.id == me.id:
                raise ConflictError("Você já é o gestor.")
            invites = cls._comanagers.setdefault(me.id, {})
            current = invites.get(guest.id)
            if current is not None and current[1] is not Status.DECLINED:
                raise ConflictError(
                    "Esse jogador já é co-gestor ou tem convite pendente."
                )
            others = [
                other_share
                for uid, (other_share, state) in invites.items()
                if uid != guest.id and state is not Status.DECLINED
            ]
            if len(others) >= MAX_COMANAGERS:
                raise ConflictError(
                    f"A gestora já tem {MAX_COMANAGERS} co-gestores. Remova um para convidar outro."
                )
            ensure_shares_fit(others, share)
            invites[guest.id] = (share, Status.INVITED)

    @classmethod
    def withdraw_comanager(
        cls, me: UserDTO, humans: list[UserDTO], nickname: str
    ) -> None:
        """O fundador retira o convite sem resposta, tira o co-gestor que aceitou ou limpa a marca de recusa."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        guest = next((u for u in humans if u.nickname == nickname), None)
        with cls._lock:
            invites = cls._comanagers.get(me.id, {})
            if guest is None or guest.id not in invites:
                raise NotFoundError("Esse jogador não tem convite de co-gestão seu.")
            del invites[guest.id]

    @classmethod
    def answer_comanager(
        cls, me: UserDTO, humans: list[UserDTO], owner: str, accept: bool
    ) -> None:
        """O convidado aceita ou recusa o convite de uma gestora; aceitar uma não recusa as outras."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        owner_user = next((u for u in humans if u.nickname == owner), None)
        with cls._lock:
            invite = (
                cls._comanagers.get(owner_user.id, {}).get(me.id)
                if owner_user is not None and owner_user.id in cls._entries
                else None
            )
            if owner_user is None or invite is None or invite[1] is not Status.INVITED:
                raise NotFoundError(
                    "Você não tem esse convite de co-gestão para responder."
                )
            if accept and SettingsManager.get().is_takeover_teams:
                if me.id in cls._entries:
                    raise ConflictError(
                        "Você funda uma gestora: quem está num grupo não aceita outro convite."
                    )
                if cls._accepted_in(me.id) is not None:
                    raise ConflictError(
                        "Você já é co-gestor de uma gestora: quem está num grupo não aceita outro convite."
                    )
            cls._comanagers[owner_user.id][me.id] = (
                invite[0],
                Status.ACCEPTED if accept else Status.DECLINED,
            )

    @classmethod
    def _accepted_in(cls, user_id: int) -> int | None:
        """O fundador de cuja gestora `user_id` é co-gestor aceito; nulo sem grupo. Chamado com o lock tomado."""
        return next(
            (
                founder_id
                for founder_id, guests in cls._comanagers.items()
                if founder_id in cls._entries
                and (invite := guests.get(user_id)) is not None
                and invite[1] is Status.ACCEPTED
            ),
            None,
        )

    @classmethod
    def teams(cls, humans: list[UserDTO]) -> dict[int, int]:
        """Na aquisição hostil em equipes, a equipe de cada humano: o fundador e os co-gestores aceitos dele dividem o número da gestora."""
        comanagers = cls.accepted_comanagers(humans)
        teams: dict[int, int] = {}
        for index, (founder, _) in enumerate(cls.prepared(humans), start=1):
            teams[founder.id] = index
            for guest, _ in comanagers.get(founder.id, []):
                teams.setdefault(guest.id, index)
        return teams

    @classmethod
    def accepted_comanagers(
        cls, humans: list[UserDTO]
    ) -> dict[int, list[tuple[UserDTO, Decimal]]]:
        """Por fundador, os co-gestores que aceitaram e estão na sala: o que a gestora leva para o 1º dia."""
        present = {u.id: u for u in humans}
        with cls._lock:
            return {
                founder_id: [
                    (present[uid], share)
                    for uid, (share, state) in guests.items()
                    if state is Status.ACCEPTED and uid in present
                ]
                for founder_id, guests in cls._comanagers.items()
                if founder_id in cls._entries and founder_id in present
            }

    @classmethod
    def with_mine(
        cls, mine: MyPreparationDTO, me: UserDTO, humans: list[UserDTO]
    ) -> MyPreparationDTO:
        """A preparação privada acrescida dos convites de co-gestão que `me` recebeu e dos que enviou."""
        present = {u.id: u for u in humans}
        with cls._lock:
            sent = dict(cls._comanagers.get(me.id, {})) if me.id in cls._entries else {}
            received = [
                (present[founder_id], cls._entries[founder_id], invite)
                for founder_id, guests in cls._comanagers.items()
                if founder_id in cls._entries
                and founder_id in present
                and (invite := guests.get(me.id)) is not None
                and invite[1] is not Status.DECLINED
            ]
        return mine.model_copy(
            update={
                "fund_comanager_invites": [
                    FundComanagerInviteDTO(
                        owner=owner.nickname,
                        fund_name=identity.name,
                        share=share,
                        accepted=state is Status.ACCEPTED,
                    )
                    for owner, identity, (share, state) in received
                ],
                "fund_comanagers": [
                    FundComanagerPreparationDTO(
                        nickname=present[uid].nickname, share=share, status=state
                    )
                    for uid, (share, state) in sent.items()
                    if uid in present
                ],
            }
        )

    @classmethod
    def prepared(cls, humans: list[UserDTO]) -> list[tuple[UserDTO, FundIdentityDTO]]:
        """Quem funda e com qual identidade: só quem está na sala, em ordem de usuário."""
        with cls._lock:
            entries = dict(cls._entries)
        return [
            (u, entries[u.id]) for u in sorted(humans, key=_by_id) if u.id in entries
        ]

    @classmethod
    def conflicts(
        cls, humans: list[UserDTO], *, takeover: bool = False, teams: bool = False
    ) -> list[str]:
        """Nome ou sigla repetidos entre quem funda, sigla cujas quatro letras já são de um ativo e, no modo aquisição hostil, quem ficou sem gestora (em equipes, quem ficou sem grupo ou em dois)."""
        founding = cls.prepared(humans)
        messages: list[str] = []
        if takeover and teams:
            messages.extend(
                _takeover_team_conflicts(
                    humans, founding, cls.accepted_comanagers(humans)
                )
            )
        elif takeover:
            messages.extend(_takeover_conflicts(humans, founding))
        for index, (user, identity) in enumerate(founding):
            if repository.fund.letters_taken_by_asset(identity.ticker):
                messages.append(
                    f"{user.nickname}: as letras {identity.ticker[:4]} da sigla "
                    f"{identity.ticker} já são de um ativo."
                )
            for other_user, other in founding[index + 1 :]:
                pair = f"{user.nickname} e {other_user.nickname}"
                if identity.ticker == other.ticker:
                    messages.append(
                        f"{pair} escolheram a mesma sigla de gestora, {identity.ticker}."
                    )
                if identity.name.casefold() == other.name.casefold():
                    messages.append(
                        f"{pair} escolheram o mesmo nome de gestora, {identity.name}."
                    )
        return messages

    @classmethod
    def apply(cls, snapshot: PreparationsDTO, humans: list[UserDTO]) -> PreparationsDTO:
        """A preparação do partido acrescida das gestoras e dos conflitos delas; com a expansão desligada, a escolha é ignorada."""
        reason = cls.locked_reason()
        if not SettingsManager.get().funds_enabled:
            return snapshot.model_copy(update={"fund_locked_reason": reason})
        return snapshot.model_copy(
            update={
                "funds": [
                    FundPreparationDTO(
                        nickname=user.nickname,
                        name=identity.name,
                        ticker=identity.ticker,
                    )
                    for user, identity in cls.prepared(humans)
                ],
                "fund_conflicts": cls.conflicts(
                    humans,
                    takeover=SettingsManager.get().is_fund_takeover,
                    teams=SettingsManager.get().is_takeover_teams,
                ),
                "fund_locked_reason": reason,
            }
        )

    @classmethod
    def ensure_ready(
        cls,
        humans: list[UserDTO],
        *,
        enabled: bool,
        takeover: bool = False,
        teams: bool = False,
    ) -> None:
        """Conferido ao iniciar com a expansão ligada: nenhuma gestora preparada repete nome ou sigla, nem usa letras de um ativo; no modo aquisição hostil, todo jogador funda a dele e, em equipes, cada um está num grupo só."""
        if not enabled:
            return
        conflicts = cls.conflicts(humans, takeover=takeover, teams=teams)
        if conflicts:
            raise ConflictError(
                "Há gestoras em conflito na preparação: " + " ".join(conflicts)
            )


def _takeover_conflicts(
    humans: list[UserDTO], founding: list[tuple[UserDTO, FundIdentityDTO]]
) -> list[str]:
    """No modo aquisição hostil toda gestora é de um jogador e há ao menos dois deles."""
    messages: list[str] = []
    if len(humans) < MIN_TAKEOVER_PLAYERS:
        messages.append("O modo aquisição hostil precisa de ao menos dois jogadores.")
    founders = {user.id for user, _ in founding}
    messages.extend(
        f"{user.nickname}: no modo aquisição hostil todo jogador funda a própria gestora."
        for user in sorted(humans, key=_by_id)
        if user.id not in founders
    )
    return messages


def _takeover_team_conflicts(
    humans: list[UserDTO],
    founding: list[tuple[UserDTO, FundIdentityDTO]],
    comanagers: dict[int, list[tuple[UserDTO, Decimal]]],
) -> list[str]:
    """Em equipes a equipe é a gestora: ao menos duas, no teto das cores, e cada humano em exatamente um grupo."""
    messages: list[str] = []
    if len(founding) < MIN_TAKEOVER_PLAYERS:
        messages.append("O modo aquisição hostil precisa de ao menos duas gestoras.")
    if len(founding) > TEAM_COUNT:
        messages.append(
            f"Em equipes a partida comporta no máximo {TEAM_COUNT} gestoras."
        )
    groups: Counter[int] = Counter(user.id for user, _ in founding)
    for guests in comanagers.values():
        groups.update(guest.id for guest, _ in guests)
    for user in sorted(humans, key=_by_id):
        count = groups[user.id]
        if count == 0:
            messages.append(
                f"{user.nickname}: em equipes todo jogador funda uma gestora ou é co-gestor de uma."
            )
        elif count > 1:
            messages.append(
                f"{user.nickname}: está em mais de um grupo e precisa ficar em um só."
            )
    return messages


def _by_id(user: UserDTO) -> int:
    return user.id
