"""
A preparação de cada jogador no lobby, só em memória, no molde das equipes: fundar um
partido (com a identidade do Meu partido), entrar no de outro jogador, escolher a chapa,
convidar o vice e propor federação ao partido de outro fundador. Sobrevive à desconexão (quem recarrega a página volta ao que preparou);
só entra na partida quem está na sala quando ela começa. O convite de vice sem resposta é
privado: só quem convidou e quem foi convidado o enxergam.
"""

from dataclasses import replace
from threading import Lock
from typing import ClassVar

from backend.core.dto.preparation import (
    FederationInviteDTO,
    MyPreparationDTO,
    PartyIdentityDTO,
    PlayerPreparationDTO,
    PreparationFederationDTO,
    PreparationsDTO,
    ReservedPartyDTO,
    ViceInviteDTO,
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
from backend.features.government import federations, house, voters
from backend.features.government.computer_parties import COMPUTER_PARTIES
from backend.features.government.preparation import PartyIdentity, Prepared


class RoomPreparation:
    # user_id -> o que o jogador preparou; quem não preparou nada não tem entrada
    _entries: ClassVar[dict[int, Prepared]] = {}
    # user_id -> a sigla do partido que saiu da preparação levando a filiação do jogador
    _left: ClassVar[dict[int, str]] = {}
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
        """Troca a preparação de `me`; as ligações que ficam sem sentido caem sozinhas. O vice só muda em INVITE_VICE e WITHDRAW_VICE."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        by_name = {u.nickname: u for u in humans}
        with cls._lock:
            cls._left.pop(me.id, None)
            abbrs = cls._abbrs()
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
            elif kind is PreparationKind.INVITE_VICE:
                cls._invite_vice(me, by_name, vice)
            elif kind is PreparationKind.WITHDRAW_VICE:
                cls._withdraw_vice(me)
            else:
                if identity is None:
                    raise ConflictError("Salve o Meu partido antes de fundá-lo.")
                cls._entries[me.id] = cls._ticket(me, identity, by_name, candidate)
            cls._prune({u.id for u in humans}, abbrs)

    @classmethod
    def restore(
        cls, me: UserDTO, humans: list[UserDTO], identity: PartyIdentityDTO
    ) -> bool:
        """Quem fundou na última sala volta fundando, candidato e sem vice; diz se recriou."""
        if cls.locked_reason() is not None:
            return False
        by_name = {u.nickname: u for u in humans}
        with cls._lock:
            if me.id in cls._entries or me.id in cls._left:
                return False
            cls._entries[me.id] = cls._ticket(me, identity, by_name, None)
        return True

    @classmethod
    def _ticket(
        cls,
        me: UserDTO,
        identity: PartyIdentityDTO,
        by_name: dict[str, UserDTO],
        candidate: str | None,
    ) -> Prepared:
        """Salva a fundação e a chapa; o vice já convidado segue como está."""
        previous = cls._entries.get(me.id)
        candidate_user = by_name.get(candidate) if candidate else me
        if candidate_user is None:
            raise NotFoundError("O candidato não está na sala.")
        member = cls._entries.get(candidate_user.id)
        if candidate_user.id != me.id and (member is None or member.join_id != me.id):
            raise UnprocessableEntityError(
                "O candidato é o fundador ou alguém que entrou no partido."
            )
        if previous is not None and previous.vice_id == candidate_user.id:
            raise ConflictError(
                "Candidato e vice precisam ser pessoas diferentes: retire o convite do vice."
            )
        return Prepared(
            me.id,
            found=PartyIdentity(
                identity.name, identity.abbr, identity.color, tuple(identity.flags)
            ),
            candidate_id=candidate_user.id,
            vice_id=previous.vice_id if previous else None,
            vice_accepted=previous.vice_accepted if previous else False,
            vice_declined_id=previous.vice_declined_id if previous else None,
            federation_partner_id=previous.federation_partner_id if previous else None,
            federation_name=previous.federation_name if previous else None,
            federation_candidate_id=previous.federation_candidate_id
            if previous
            else None,
            federation_accepted=previous.federation_accepted if previous else False,
        )

    @classmethod
    def _invite_vice(
        cls, me: UserDTO, by_name: dict[str, UserDTO], vice: str | None
    ) -> None:
        """Convida o jogador para vice; a chapa tem uma vaga, então o convite novo ocupa o lugar do anterior."""
        entry = cls._entries.get(me.id)
        if entry is None or entry.found is None:
            raise ConflictError("Só quem funda um partido convida o vice.")
        vice_user = by_name.get(vice or "")
        if vice_user is None:
            raise NotFoundError("O vice não está na sala.")
        candidate_id = entry.candidate_id or me.id
        cls._ensure_vice_free(me, vice_user, candidate_id)
        if entry.vice_id == vice_user.id:
            raise ConflictError(
                f"{vice_user.nickname} já é o vice da chapa."
                if entry.vice_accepted
                else f"{vice_user.nickname} já foi convidado e ainda não respondeu."
            )
        cls._entries[me.id] = replace(
            entry,
            vice_id=vice_user.id,
            vice_accepted=False,
            vice_declined_id=None,
        )

    @classmethod
    def _withdraw_vice(cls, me: UserDTO) -> None:
        """Retira o convite aguardando, o vice aceito ou a marca de convite recusado."""
        entry = cls._entries.get(me.id)
        if entry is None or entry.found is None:
            raise ConflictError("Só quem funda um partido convida o vice.")
        if entry.vice_id is None and entry.vice_declined_id is None:
            raise ConflictError("A chapa não tem convite de vice para retirar.")
        cls._entries[me.id] = replace(
            entry, vice_id=None, vice_accepted=False, vice_declined_id=None
        )

    @classmethod
    def _ensure_vice_free(cls, me: UserDTO, vice: UserDTO, candidate_id: int) -> None:
        """O vice é outra pessoa que não aceitou ser vice de outra chapa nem é candidata de outra; convite pendente de outra chapa não bloqueia."""
        if vice.id == candidate_id:
            raise ConflictError("Candidato e vice precisam ser pessoas diferentes.")
        for owner_id, entry in cls._entries.items():
            if owner_id == me.id or entry.found is None:
                continue
            if entry.vice_id == vice.id and entry.vice_accepted:
                raise ConflictError(f"{vice.nickname} já é vice de outra chapa.")
            if (entry.candidate_id or owner_id) == vice.id:
                raise ConflictError(f"{vice.nickname} é candidato de outra chapa.")

    @classmethod
    def answer_vice(
        cls, me: UserDTO, humans: list[UserDTO], owner: str, accept: bool
    ) -> None:
        """O convidado aceita ou recusa o convite de uma chapa; aceitar um recusa os outros convites abertos dele."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        owner_user = next((u for u in humans if u.nickname == owner), None)
        with cls._lock:
            entry = cls._entries.get(owner_user.id) if owner_user else None
            if (
                owner_user is None
                or entry is None
                or entry.vice_id != me.id
                or entry.vice_accepted
            ):
                raise NotFoundError("Você não tem esse convite de vice para responder.")
            if not accept:
                cls._entries[owner_user.id] = replace(
                    entry, vice_id=None, vice_accepted=False, vice_declined_id=me.id
                )
                return
            cls._ensure_vice_free(owner_user, me, entry.candidate_id or owner_user.id)
            for uid, other in list(cls._entries.items()):
                if uid == owner_user.id or other.vice_id != me.id:
                    continue
                if not other.vice_accepted:
                    cls._entries[uid] = replace(
                        other, vice_id=None, vice_accepted=False, vice_declined_id=me.id
                    )
            cls._entries[owner_user.id] = replace(entry, vice_accepted=True)

    @classmethod
    def propose_federation(
        cls,
        me: UserDTO,
        humans: list[UserDTO],
        partner: str | None,
        name: str | None,
        candidate: str | None,
    ) -> None:
        """O fundador propõe federação ao fundador de outro partido; sem `partner`, desfaz a proposta ou a federação combinada."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        by_name = {u.nickname: u for u in humans}
        with cls._lock:
            entry = cls._entries.get(me.id)
            if entry is None or entry.found is None:
                raise ConflictError("Só quem funda um partido propõe federação.")
            if partner is None:
                cls._clear_federation(me.id)
                return
            other_user = by_name.get(partner)
            other = cls._entries.get(other_user.id) if other_user else None
            if other_user is None or other is None or other.found is None:
                raise NotFoundError("Esse jogador não preparou um partido.")
            if other_user.id == me.id:
                raise ConflictError("Você não se federa com o próprio partido.")
            # Cada fundador envia uma proposta por vez e pode receber várias
            if entry.federation_partner_id is not None or cls._federated(me.id):
                raise ConflictError(
                    "Seu partido já tem uma proposta enviada ou uma federação combinada."
                )
            if cls._federated(other_user.id):
                raise ConflictError("O outro partido já tem uma federação combinada.")
            candidate_user = by_name.get(candidate) if candidate else me
            if candidate_user is None or not (
                cls._in_party(candidate_user.id, me.id)
                or cls._in_party(candidate_user.id, other_user.id)
            ):
                raise UnprocessableEntityError(
                    "O candidato é do partido de um dos dois fundadores."
                )
            label = (name or "").strip() or federations.default_name(
                entry.found.abbr, other.found.abbr
            )
            cls._entries[me.id] = replace(
                entry,
                federation_partner_id=other_user.id,
                federation_name=label,
                federation_candidate_id=candidate_user.id,
                federation_accepted=False,
            )

    @classmethod
    def answer_federation(
        cls, me: UserDTO, humans: list[UserDTO], owner: str, accept: bool
    ) -> None:
        """O fundador convidado aceita ou recusa uma das propostas recebidas; aceitar derruba as outras que envolvem um dos dois."""
        reason = cls.locked_reason()
        if reason is not None:
            raise ConflictError(reason)
        owner_user = next((u for u in humans if u.nickname == owner), None)
        with cls._lock:
            entry = cls._entries.get(owner_user.id) if owner_user else None
            if (
                owner_user is None
                or entry is None
                or entry.federation_partner_id != me.id
                or entry.federation_accepted
            ):
                raise NotFoundError(
                    "Você não tem essa proposta de federação para responder."
                )
            if not accept:
                cls._reset_federation(owner_user.id)
                return
            cls._entries[owner_user.id] = replace(entry, federation_accepted=True)
            # As propostas abertas dos dois fundadores, enviadas ou recebidas, caem com a federação
            formed = {me.id, owner_user.id}
            for uid, other in list(cls._entries.items()):
                if (
                    uid != owner_user.id
                    and other.federation_partner_id is not None
                    and not other.federation_accepted
                    and (uid in formed or other.federation_partner_id in formed)
                ):
                    cls._reset_federation(uid)

    @classmethod
    def _federated(cls, user_id: int) -> bool:
        """O fundador está numa federação já combinada, como proponente ou como parceiro."""
        return any(
            e.federation_accepted and user_id in (e.user_id, e.federation_partner_id)
            for e in cls._entries.values()
        )

    @classmethod
    def _reset_federation(cls, user_id: int) -> None:
        """Zera a proposta (ou a federação combinada) que o fundador enviou."""
        entry = cls._entries.get(user_id)
        if entry is not None:
            cls._entries[user_id] = replace(
                entry,
                federation_partner_id=None,
                federation_name=None,
                federation_candidate_id=None,
                federation_accepted=False,
            )

    @classmethod
    def _clear_federation(cls, user_id: int) -> None:
        """Desfaz a proposta que o fundador enviou e a federação combinada em que ele é o parceiro."""
        cls._reset_federation(user_id)
        for uid, entry in list(cls._entries.items()):
            if entry.federation_accepted and entry.federation_partner_id == user_id:
                cls._reset_federation(uid)

    @classmethod
    def _in_party(cls, user_id: int, founder_id: int) -> bool:
        """O jogador é o fundador ou entrou no partido dele."""
        if user_id == founder_id:
            return True
        member = cls._entries.get(user_id)
        return member is not None and member.join_id == founder_id

    @classmethod
    def drop(cls, user_id: int) -> None:
        """O jogador saiu da sala de vez: some a preparação dele e o que dependia dela."""
        with cls._lock:
            abbrs = cls._abbrs()
            cls._entries.pop(user_id, None)
            cls._left.pop(user_id, None)
            for uid, entry in list(cls._entries.items()):
                if user_id in (entry.vice_id, entry.vice_declined_id):
                    cls._entries[uid] = replace(
                        entry,
                        vice_id=None if entry.vice_id == user_id else entry.vice_id,
                        vice_accepted=entry.vice_accepted and entry.vice_id != user_id,
                        vice_declined_id=None,
                    )
            cls._prune(None, abbrs)

    @classmethod
    def clear(cls) -> None:
        """A partida começou: a próxima sala começa sem preparação."""
        with cls._lock:
            cls._entries.clear()
            cls._left.clear()

    @classmethod
    def _abbrs(cls) -> dict[int, str]:
        """A sigla de cada partido preparado, pelo fundador."""
        return {uid: e.found.abbr for uid, e in cls._entries.items() if e.found}

    @classmethod
    def _prune(cls, present: set[int] | None, abbrs: dict[int, str]) -> None:
        """
        Solta filiação sem fundador, candidato fora da chapa e vice que saiu da sala.
        `abbrs` são as siglas de antes da mudança: quem perde o partido guarda a dele.
        """
        changed = True
        while changed:
            changed = False
            for uid, entry in list(cls._entries.items()):
                fixed = cls._fixed(entry, present)
                if fixed is None:
                    del cls._entries[uid]
                    if entry.join_id in abbrs:
                        cls._left[uid] = abbrs[entry.join_id]
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
        vice, accepted, declined = (
            entry.vice_id,
            entry.vice_accepted,
            entry.vice_declined_id,
        )
        gone = present is not None and vice is not None and vice not in present
        if vice is not None and (gone or vice == (candidate or entry.user_id)):
            vice, accepted = None, False
        if present is not None and declined is not None and declined not in present:
            declined = None
        fixed = replace(
            entry,
            candidate_id=candidate,
            vice_id=vice,
            vice_accepted=accepted,
            vice_declined_id=declined,
        )
        return cls._fixed_federation(fixed, present)

    @classmethod
    def _fixed_federation(cls, entry: Prepared, present: set[int] | None) -> Prepared:
        """A federação some quando o parceiro deixa de fundar ou sai da sala; o candidato fora dos dois partidos volta ao proponente."""
        partner_id = entry.federation_partner_id
        if partner_id is None:
            return entry
        partner = cls._entries.get(partner_id)
        if (
            partner is None
            or partner.found is None
            or (present is not None and partner_id not in present)
        ):
            return replace(
                entry,
                federation_partner_id=None,
                federation_name=None,
                federation_candidate_id=None,
                federation_accepted=False,
            )
        candidate = entry.federation_candidate_id
        if candidate is not None and not (
            cls._in_party(candidate, entry.user_id)
            or cls._in_party(candidate, partner_id)
        ):
            return replace(entry, federation_candidate_id=None)
        return entry

    @classmethod
    def snapshot(cls, humans: list[UserDTO]) -> PreparationsDTO:
        """A preparação de quem está na sala, com os conflitos e o motivo da trava."""
        present = {u.id: u for u in humans}
        with cls._lock:
            entries = [e for uid, e in cls._entries.items() if uid in present]

        def name(user_id: int | None) -> str | None:
            return present[user_id].nickname if user_id in present else None

        # A federação combinada, vista pelos dois fundadores
        combined: dict[int, PreparationFederationDTO] = {}
        for e in entries:
            partner_id = e.federation_partner_id
            if not e.federation_accepted or partner_id not in present:
                continue
            candidate = name(e.federation_candidate_id or e.user_id) or ""
            label = e.federation_name or ""
            combined[e.user_id] = PreparationFederationDTO(
                partner=present[partner_id].nickname, name=label, candidate=candidate
            )
            combined[partner_id] = PreparationFederationDTO(
                partner=present[e.user_id].nickname, name=label, candidate=candidate
            )

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
                vice=name(e.vice_id) if e.vice_accepted else None,
                vice_accepted=e.vice_accepted,
                federation=combined.get(e.user_id),
            )
            for e in entries
        ]
        return PreparationsDTO(
            players=players,
            reserved=[
                ReservedPartyDTO(name=p.name, abbr=p.abbr, flags=list(p.flags))
                for p in COMPUTER_PARTIES
            ],
            conflicts=_conflicts(entries, present),
            pending_invites=sum(
                1 for e in entries if e.vice_id in present and not e.vice_accepted
            ),
            radar_neutral=voters.RADAR_NEUTRAL,
            radar_flag=voters.RADAR_FLAG,
            locked_reason=cls.locked_reason(),
        )

    @classmethod
    def mine(cls, me: UserDTO, humans: list[UserDTO]) -> MyPreparationDTO:
        """Os convites de vice e as propostas de federação sem resposta de `me`, os que ele enviou e o partido que saiu."""
        present = {u.id: u for u in humans}
        with cls._lock:
            own = cls._entries.get(me.id)
            owners = [
                e
                for uid, e in cls._entries.items()
                if uid in present
                and e.found is not None
                and e.vice_id == me.id
                and not e.vice_accepted
            ]
            left = cls._left.get(me.id)
            offers = [
                e
                for uid, e in cls._entries.items()
                if uid in present
                and e.found is not None
                and e.federation_partner_id == me.id
                and not e.federation_accepted
            ]

        invites = [
            ViceInviteDTO(
                owner=present[e.user_id].nickname,
                abbr=e.found.abbr,  # type: ignore[union-attr]
                candidate=name_of(present, e.candidate_id or e.user_id) or "",
            )
            for e in owners
        ]
        invited = None
        if own is not None and own.vice_id is not None and not own.vice_accepted:
            invited = name_of(present, own.vice_id)
        vice_declined = name_of(present, own.vice_declined_id) if own else None
        federation_invites = [
            FederationInviteDTO(
                owner=present[e.user_id].nickname,
                abbr=e.found.abbr,  # type: ignore[union-attr]
                name=e.federation_name or "",
                candidate=name_of(present, e.federation_candidate_id or e.user_id)
                or "",
            )
            for e in offers
        ]
        federation_invited = None
        if (
            own is not None
            and own.federation_partner_id is not None
            and not own.federation_accepted
        ):
            partner = present.get(own.federation_partner_id)
            federation_invited = partner.nickname if partner else None
        return MyPreparationDTO(
            invites=invites,
            invited=invited,
            vice_declined=vice_declined,
            left_party=left,
            federation_invites=federation_invites,
            federation_invited=federation_invited,
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


def name_of(present: dict[int, UserDTO], user_id: int | None) -> str | None:
    """O apelido de quem está na sala; nulo para quem saiu ou não foi escolhido."""
    return present[user_id].nickname if user_id in present else None


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
