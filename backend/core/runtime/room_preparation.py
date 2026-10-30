"""
A preparação de cada jogador no lobby, só em memória, no molde das equipes: fundar um
partido (com a identidade do Meu partido), entrar no de outro jogador, escolher a chapa e
convidar o vice. Sobrevive à desconexão (quem recarrega a página volta ao que preparou);
só entra na partida quem está na sala quando ela começa.
"""

from dataclasses import replace
from threading import Lock
from typing import ClassVar

from backend.core.dto.preparation import (
    PartyIdentityDTO,
    PlayerPreparationDTO,
    PreparationsDTO,
    ReservedPartyDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import PreparationKind
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.features.government import house
from backend.features.government.computer_parties import COMPUTER_PARTIES
from backend.features.government.preparation import PartyIdentity, Prepared


class RoomPreparation:
    # user_id -> o que o jogador preparou; quem não preparou nada não tem entrada
    _entries: ClassVar[dict[int, Prepared]] = {}
    _lock = Lock()

    @classmethod
    def locked_reason(cls) -> str | None:
        """Por que a preparação não aceita mudança; nulo quando o lobby está aberto a ela."""
        if SimulationManager.has_active_simulation():
            return "A partida já começou: a preparação ficou travada."
        if SettingsManager.get_selected_simulation_id() is not None:
            return "Partida salva selecionada: a preparação vale só para partida nova."
        if not SettingsManager.get().government_enabled:
            return "A expansão Governo & Política está desligada nesta partida."
        return None

    @classmethod
    def choose(
        cls,
        me: UserDTO,
        kind: PreparationKind,
        humans: list[UserDTO],
        *,
        identity: PartyIdentityDTO | None,
        founder: str | None,
        candidate: str | None,
        vice: str | None,
    ) -> None:
        """Troca a preparação de `me`; as ligações que ficam sem sentido caem sozinhas."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        by_name = {u.nickname: u for u in humans}
        with cls._lock:
            if kind is PreparationKind.NONE:
                cls._entries.pop(me.id, None)
            elif kind is PreparationKind.JOIN:
                leader = by_name.get(founder or "")
                entry = cls._entries.get(leader.id) if leader else None
                if leader is None or entry is None or entry.found is None:
                    raise NotFoundError("Esse jogador não preparou um partido.")
                if leader.id == me.id:
                    raise ConflictError("Você não entra no próprio partido: funde-o.")
                cls._entries[me.id] = Prepared(me.id, join_id=leader.id)
            else:
                if identity is None:
                    raise ConflictError("Salve o Meu partido antes de fundá-lo.")
                cls._entries[me.id] = cls._ticket(
                    me, identity, by_name, candidate, vice
                )
            cls._prune({u.id for u in humans})

    @classmethod
    def _ticket(
        cls,
        me: UserDTO,
        identity: PartyIdentityDTO,
        by_name: dict[str, UserDTO],
        candidate: str | None,
        vice: str | None,
    ) -> Prepared:
        previous = cls._entries.get(me.id)
        candidate_user = by_name.get(candidate) if candidate else me
        if candidate_user is None:
            raise NotFoundError("O candidato não está na sala.")
        member = cls._entries.get(candidate_user.id)
        if candidate_user.id != me.id and (member is None or member.join_id != me.id):
            raise UnprocessableEntityError(
                "O candidato é o fundador ou alguém que entrou no partido."
            )
        vice_user = by_name.get(vice) if vice else None
        if vice and vice_user is None:
            raise NotFoundError("O vice não está na sala.")
        if vice_user is not None:
            cls._ensure_vice_free(me, vice_user, candidate_user)
        keeps = (
            vice_user is not None
            and previous is not None
            and previous.vice_id == vice_user.id
            and previous.vice_accepted
        )
        return Prepared(
            me.id,
            found=PartyIdentity(
                identity.name, identity.abbr, identity.color, tuple(identity.flags)
            ),
            candidate_id=candidate_user.id,
            vice_id=vice_user.id if vice_user else None,
            vice_accepted=keeps,
        )

    @classmethod
    def _ensure_vice_free(cls, me: UserDTO, vice: UserDTO, candidate: UserDTO) -> None:
        """O vice é outra pessoa que não é vice nem candidata de outra chapa."""
        if vice.id == candidate.id:
            raise ConflictError("Candidato e vice precisam ser pessoas diferentes.")
        for owner_id, entry in cls._entries.items():
            if owner_id == me.id or entry.found is None:
                continue
            if entry.vice_id == vice.id:
                raise ConflictError(
                    f"{vice.nickname} já foi convidado por outra chapa."
                )
            if (entry.candidate_id or owner_id) == vice.id:
                raise ConflictError(f"{vice.nickname} é candidato de outra chapa.")

    @classmethod
    def answer_vice(cls, me: UserDTO, accept: bool) -> None:
        """O convidado aceita ou recusa a vaga de vice que um jogador preparou."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        with cls._lock:
            owner_id = next(
                (
                    uid
                    for uid, e in cls._entries.items()
                    if e.vice_id == me.id and not e.vice_accepted
                ),
                None,
            )
            if owner_id is None:
                raise NotFoundError("Você não tem convite de vice para responder.")
            entry = cls._entries[owner_id]
            cls._entries[owner_id] = (
                replace(entry, vice_accepted=True)
                if accept
                else replace(entry, vice_id=None, vice_accepted=False)
            )

    @classmethod
    def drop(cls, user_id: int) -> None:
        """O jogador saiu da sala de vez: some a preparação dele e o que dependia dela."""
        with cls._lock:
            cls._entries.pop(user_id, None)
            for uid, entry in list(cls._entries.items()):
                if entry.vice_id == user_id:
                    cls._entries[uid] = replace(
                        entry, vice_id=None, vice_accepted=False
                    )
            cls._prune(None)

    @classmethod
    def clear(cls) -> None:
        """A partida começou: a próxima sala começa sem preparação."""
        with cls._lock:
            cls._entries.clear()

    @classmethod
    def _prune(cls, present: set[int] | None) -> None:
        """Solta filiação sem fundador, candidato fora da chapa e vice que saiu da sala."""
        changed = True
        while changed:
            changed = False
            for uid, entry in list(cls._entries.items()):
                fixed = cls._fixed(entry, present)
                if fixed is None:
                    del cls._entries[uid]
                    changed = True
                elif fixed != entry:
                    cls._entries[uid] = fixed
                    changed = True

    @classmethod
    def _fixed(cls, entry: Prepared, present: set[int] | None) -> Prepared | None:
        if entry.join_id is not None:
            leader = cls._entries.get(entry.join_id)
            alive = leader is not None and leader.found is not None
            return entry if alive else None
        candidate = entry.candidate_id
        if candidate is not None and candidate != entry.user_id:
            member = cls._entries.get(candidate)
            if member is None or member.join_id != entry.user_id:
                candidate = None
        vice, accepted = entry.vice_id, entry.vice_accepted
        gone = present is not None and vice is not None and vice not in present
        if vice is not None and (gone or vice == (candidate or entry.user_id)):
            vice, accepted = None, False
        return replace(
            entry, candidate_id=candidate, vice_id=vice, vice_accepted=accepted
        )

    @classmethod
    def snapshot(cls, humans: list[UserDTO]) -> PreparationsDTO:
        """A preparação de quem está na sala, com os conflitos e o motivo da trava."""
        present = {u.id: u for u in humans}
        with cls._lock:
            entries = [e for uid, e in cls._entries.items() if uid in present]

        def name(user_id: int | None) -> str | None:
            return present[user_id].nickname if user_id in present else None

        players = [
            PlayerPreparationDTO(
                nickname=present[e.user_id].nickname,
                kind=PreparationKind.FOUND if e.found else PreparationKind.JOIN,
                party=None
                if e.found is None
                else PartyIdentityDTO(
                    name=e.found.name,
                    abbr=e.found.abbr,
                    color=e.found.color,
                    flags=list(e.found.flags),
                ),
                founder=name(e.join_id),
                candidate=name(e.candidate_id or (e.user_id if e.found else None)),
                vice=name(e.vice_id),
                vice_accepted=e.vice_accepted,
            )
            for e in entries
        ]
        return PreparationsDTO(
            players=players,
            reserved=[
                ReservedPartyDTO(name=p.name, abbr=p.abbr) for p in COMPUTER_PARTIES
            ],
            conflicts=_conflicts(entries, present),
            locked_reason=cls.locked_reason(),
        )

    @classmethod
    def ensure_ready(cls, humans: list[UserDTO]) -> None:
        """Conferido ao iniciar: nenhum partido preparado repete sigla, nome ou cor de outro."""
        if cls.locked_reason() is not None:
            return
        conflicts = cls.snapshot(humans).conflicts
        if conflicts:
            raise ConflictError(
                "Há partidos em conflito na preparação: " + " ".join(conflicts)
            )

    @classmethod
    def prepared(cls, humans: list[UserDTO]) -> list[Prepared]:
        """O que a partida nova leva da sala: só quem está nela, já sem ligação solta."""
        if cls.locked_reason() is not None:
            return []
        present = {u.id for u in humans}
        with cls._lock:
            return [e for uid, e in cls._entries.items() if uid in present]


def _conflicts(entries: list[Prepared], present: dict[int, UserDTO]) -> list[str]:
    """Sigla, nome e cor repetidos entre os partidos preparados e com os do computador."""
    founding = [(present[e.user_id].nickname, e.found) for e in entries if e.found]
    messages: list[str] = []
    for index, (nickname, identity) in enumerate(founding):
        if identity.abbr in house.COMPUTER_KEYS:
            messages.append(
                f"{nickname}: a sigla {identity.abbr} é de um partido do computador."
            )
        if any(identity.name.casefold() == p.name.casefold() for p in COMPUTER_PARTIES):
            messages.append(
                f"{nickname}: o nome {identity.name} é de um partido do computador."
            )
        for other_name, other in founding[index + 1 :]:
            pair = f"{nickname} e {other_name}"
            if identity.abbr == other.abbr:
                messages.append(f"{pair} escolheram a mesma sigla, {identity.abbr}.")
            if identity.name.casefold() == other.name.casefold():
                messages.append(f"{pair} escolheram o mesmo nome, {identity.name}.")
            if identity.color.lower() == other.color.lower():
                messages.append(f"{pair} escolheram a mesma cor.")
    return messages
