"""
A preparação da gestora de cada jogador no lobby, só em memória, no molde do partido:
quem escolhe fundar leva a identidade da Minha gestora (nome e sigla) e a gestora nasce vazia
no 1º dia da partida. A escolha sobrevive à desconexão; só funda quem está na sala quando a
partida começa, e só com a expansão Gestoras ligada nas regras.
"""

from threading import Lock
from typing import ClassVar

from backend.core import repository
from backend.core.dto.preparation import (
    FundIdentityDTO,
    FundPreparationDTO,
    PreparationsDTO,
)
from backend.core.dto.user import UserDTO
from backend.core.enum import FundPreparationKind
from backend.core.exceptions.http_exceptions import ConflictError
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager


class RoomFundPreparation:
    # user_id -> a identidade da gestora que o jogador funda; quem fica sem gestora não tem entrada
    _entries: ClassVar[dict[int, FundIdentityDTO]] = {}
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
                return
            if identity is None:
                raise ConflictError("Salve a Minha gestora antes de fundá-la.")
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

    @classmethod
    def clear(cls) -> None:
        """A partida começou: a próxima sala começa sem preparação."""
        with cls._lock:
            cls._entries.clear()

    @classmethod
    def prepared(cls, humans: list[UserDTO]) -> list[tuple[UserDTO, FundIdentityDTO]]:
        """Quem funda e com qual identidade: só quem está na sala, em ordem de usuário."""
        with cls._lock:
            entries = dict(cls._entries)
        return [
            (u, entries[u.id]) for u in sorted(humans, key=_by_id) if u.id in entries
        ]

    @classmethod
    def conflicts(cls, humans: list[UserDTO]) -> list[str]:
        """Nome ou sigla repetidos entre quem funda, e sigla cujas quatro letras já são de um ativo."""
        founding = cls.prepared(humans)
        messages: list[str] = []
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
                "conflicts": [*snapshot.conflicts, *cls.conflicts(humans)],
                "fund_locked_reason": reason,
            }
        )

    @classmethod
    def ensure_ready(cls, humans: list[UserDTO], *, enabled: bool) -> None:
        """Conferido ao iniciar com a expansão ligada: nenhuma gestora preparada repete nome ou sigla, nem usa letras de um ativo."""
        if not enabled:
            return
        conflicts = cls.conflicts(humans)
        if conflicts:
            raise ConflictError(
                "Há gestoras em conflito na preparação: " + " ".join(conflicts)
            )


def _by_id(user: UserDTO) -> int:
    return user.id
