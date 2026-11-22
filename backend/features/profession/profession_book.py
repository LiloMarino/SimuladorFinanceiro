from datetime import date

from backend.core import repository
from backend.core.dto.profession import (
    MechanicState,
    ProfessionPeriodDTO,
    initial_state,
)
from backend.core.enum import Profession


class ProfessionBook:
    """
    O estado da mecânica e os períodos de profissão dos jogadores de uma partida. Lê o
    banco inteiro na primeira consulta e grava cada mudança no mesmo instante, para que
    o que a memória diz seja o que o banco guarda; quem entra na partida pede `forget`.
    """

    def __init__(self, simulation_id: int):
        self._simulation_id = simulation_id
        self._states: dict[int, MechanicState] | None = None
        self._periods: dict[int, list[ProfessionPeriodDTO]] | None = None

    def forget(self) -> None:
        """Descarta o que a memória guarda: a próxima consulta lê o banco de novo."""
        self._states = None
        self._periods = None

    def state_of(self, user_id: int, profession: Profession) -> MechanicState:
        """O estado do jogador; quem ainda não tem linha começa no estado inicial da profissão."""
        if self._states is None:
            self._states = repository.profession.states(self._simulation_id)
        state = self._states.get(user_id)
        return initial_state(profession) if state is None else state

    def save_state(self, user_id: int, state: MechanicState) -> None:
        repository.profession.save_state(self._simulation_id, user_id, state)
        if self._states is not None:
            self._states = {**self._states, user_id: state}

    def periods_of(self, user_id: int) -> list[ProfessionPeriodDTO]:
        """Os períodos de profissão do jogador, do mais antigo ao mais novo; vazio quando a partida não os guarda dele."""
        if self._periods is None:
            self._periods = repository.profession.periods(self._simulation_id)
        return self._periods.get(user_id, [])

    def switch(self, user_id: int, profession: Profession, day: date) -> None:
        """Grava a troca: a profissão do jogador, o período que abre em `day` e o estado inicial da nova."""
        state = initial_state(profession)
        repository.profession.switch(
            self._simulation_id, user_id, profession, day, state
        )
        self.forget()
