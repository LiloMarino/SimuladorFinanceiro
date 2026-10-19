import logging
from collections import Counter
from threading import Lock
from typing import ClassVar
from uuid import UUID

from backend.core import repository
from backend.core.dto.user import UserDTO
from backend.core.enum import PlayerGrouping
from backend.core.exceptions import NoActiveSimulationError
from backend.core.exceptions.http_exceptions import (
    ConflictError,
    LockedError,
    NotFoundError,
    UnprocessableEntityError,
)
from backend.core.player_colors import MAX_PLAYERS, PLAYER_COLORS, first_free_color
from backend.core.runtime.settings_manager import SettingsManager
from backend.core.runtime.simulation_manager import SimulationManager
from backend.core.teams import MIN_TEAMS, TEAM_COUNT, is_valid_team
from backend.core.utils.lazy_dict import LazyDict

logger = logging.getLogger(__name__)

ROOM_FULL = (
    f"A sala está cheia: {MAX_PLAYERS} de {MAX_PLAYERS} jogadores. "
    "Peça pro host liberar uma vaga ou crie sua própria sala."
)
ROOM_RESERVED = (
    "As {n} vagas que restam são de quem jogou a partida selecionada e está offline. "
    "Peça pro host escolher outra partida ou espere essas pessoas voltarem."
)


class UserManager:
    """
    Gerenciador singleton de usuários e presença de players.

    Responsável por:
    - Controlar players ativos (autenticados e conectados) na simulação
    - Manter cache lazy de usuários por client_id para acesso rápido
    - Gerenciar lifecycle de conexão (register, unregister, auth, logout)
    - Emitir eventos de entrada/saída de players
    - Sincronizar estado com a simulação ativa
    - Dar a cada player da sala uma cor exclusiva da paleta
    - Guardar a equipe de cada player quando a sala joga em equipes
    """

    # 🔹 Apenas players autenticados (presença)
    _active_players: ClassVar[dict[UUID, UserDTO]] = {}

    # 🔹 Cor de cada player da sala (user_id -> chave da paleta); a sala não repete cor
    _colors: ClassVar[dict[int, str]] = {}

    # 🔹 Cores guardadas da partida salva selecionada, inclusive de quem está ausente:
    # quem participou fica travado nelas e ninguém mais toma essas cores
    _saved_colors: ClassVar[dict[int, str]] = {}

    # 🔹 Equipe de cada player da sala (user_id -> 1..10); só existe no modo em equipes e
    # sobrevive à desconexão, para quem recarrega a página voltar para a mesma equipe
    _teams: ClassVar[dict[int, int]] = {}

    # 🔹 Equipes guardadas da partida salva selecionada: quem já jogou fica travado nelas
    _saved_teams: ClassVar[dict[int, int]] = {}

    # 🔹 Cache lazy client_id -> UserDTO (independente de presença)
    _client_user_cache: LazyDict[UUID, UserDTO | None] = LazyDict(
        loader=repository.user.get_by_client_id
    )

    _lock = Lock()

    # =========================
    # Conexão
    # =========================

    @classmethod
    def register(cls, client_id: UUID):
        logger.info(f"User connected: {client_id}")

    @classmethod
    def unregister(cls, client_id: UUID):
        logger.info(f"User disconnected: {client_id}")

        with cls._lock:
            player = cls._active_players.pop(client_id, None)
            color = cls._colors.pop(player.id, None) if player else None

        if player and color:
            cls._emit_player_exit(player, color)

    # =========================
    # Autenticação
    # =========================

    @classmethod
    def player_auth(cls, client_id: UUID) -> UserDTO | None:
        user = cls.get_user(client_id)
        if user is None:
            return None

        with cls._lock:
            if client_id in cls._active_players:
                return user

        # Com partida em andamento a cor é a da partida
        match_colors = cls._match_colors()

        # Quem não joga a partida entra autenticado, sem vaga na sala: a cor ele escolhe em join_match
        if match_colors is not None and user.id not in match_colors:
            if len(match_colors) >= MAX_PLAYERS:
                raise LockedError(cls._match_full())
            return user

        with cls._lock:
            if client_id in cls._active_players:
                return user

            if len(cls._active_players) >= MAX_PLAYERS:
                raise LockedError(ROOM_FULL)

            if match_colors is not None:
                color = match_colors[user.id]
            elif user.id in cls._saved_colors:
                color = cls._saved_colors[user.id]
            else:
                color = cls._free_color()

            cls._active_players[client_id] = user
            cls._colors[user.id] = color

        cls._emit_player_join(user, color)
        return user

    @classmethod
    def player_logout(cls, client_id: UUID):
        with cls._lock:
            # Remove presença ativa (se existir)
            user = cls._active_players.pop(client_id, None)
            color = cls._colors.pop(user.id, None) if user else None

        # Limpa caches da simulação (se houver simulação ativa)
        try:
            sim = SimulationManager.get_active_simulation()
            sim.clear_user_cache(client_id)
        except NoActiveSimulationError:
            pass

        # Emite evento de saída se o usuário estava ativo
        if user and color:
            cls._emit_player_exit(user, color)

        # Limpa cache lazy (força sessão a virar "guest")
        cls._client_user_cache.pop(client_id, None)

        logger.info(f"User logged out: client_id={client_id}")

    @classmethod
    def is_pending_join(cls, user: UserDTO) -> bool:
        """Há partida em andamento e `user` não joga nela: precisa escolher uma cor em join_match."""
        match_colors = cls._match_colors()
        return match_colors is not None and user.id not in match_colors

    @classmethod
    def join_match(cls, client_id: UUID, color: str, team: int | None = None) -> None:
        """
        Entra na partida em andamento com `color` (e `team`, em partida em equipes).
        A cor vale para quem pediu primeiro: o teto da partida e a cor livre são
        conferidos e gravados sob o mesmo lock, então dois chegando juntos não passam
        da última vaga nem repetem cor.
        """
        if color not in PLAYER_COLORS:
            raise UnprocessableEntityError("Essa cor não existe na paleta.")

        user = cls.get_user(client_id)
        if user is None:
            raise NotFoundError("Usuário não encontrado.")
        if not SimulationManager.has_active_simulation():
            raise ConflictError("Não há partida em andamento.")

        sim = SimulationManager.get_active_simulation()
        simulation_id = SimulationManager.get_active_simulation_id()

        in_teams = sim.settings.player_grouping is PlayerGrouping.TEAMS
        if in_teams and (team is None or not is_valid_team(team)):
            raise UnprocessableEntityError("Escolha uma equipe para entrar.")

        with cls._lock:
            colors = repository.simulation_player.colors(simulation_id)
            if user.id in colors:
                raise ConflictError("Você já faz parte da partida.")
            if len(colors) >= MAX_PLAYERS:
                raise LockedError(cls._match_full())

            owner_id = next((uid for uid, c in colors.items() if c == color), None)
            if owner_id is not None:
                owner = next(
                    p.nickname
                    for p in repository.simulation_player.participants(simulation_id)
                    if p.id == owner_id
                )
                raise ConflictError(f"{owner} pegou essa cor antes.")

            repository.simulation_player.save(
                simulation_id,
                {user.id: color},
                {user.id: team} if in_teams and team is not None else None,
            )
            cls._active_players[client_id] = user
            cls._colors[user.id] = color

        # Depósito e snapshot do dia: o motor tem o próprio lock, fora do nosso
        sim.add_player(user)
        cls._emit_player_join(user, color)

    # =========================
    # Queries
    # =========================

    @classmethod
    def get_user(cls, client_id: UUID) -> UserDTO | None:
        user = cls._client_user_cache[client_id]
        if user is None:
            cls._client_user_cache.pop(client_id, None)
            return None
        return user

    @classmethod
    def get_user_id(cls, client_id: UUID) -> int:
        user = cls.get_user(client_id)
        if user is None:
            raise NotFoundError(f"Usuário não encontrado para client_id={client_id}")
        return user.id

    @classmethod
    def list_active_players(cls) -> list[UserDTO]:
        with cls._lock:
            return list(cls._active_players.values())

    # =========================
    # Cores
    # =========================

    @classmethod
    def get_color(cls, user_id: int) -> str | None:
        """Cor na sala; quem saiu no meio da partida mantém a da partida."""
        with cls._lock:
            color = cls._colors.get(user_id)
        if color is None:
            color = (cls._match_colors() or {}).get(user_id)
        return color

    @classmethod
    def room_colors(cls) -> dict[int, str]:
        """Cor de cada player da sala, por user_id."""
        with cls._lock:
            return dict(cls._colors)

    @classmethod
    def set_color(cls, client_id: UUID, color: str) -> None:
        """A cor é de quem pediu primeiro: se já tem dono, quem pediu fica com a que tinha."""
        if color not in PLAYER_COLORS:
            raise UnprocessableEntityError("Essa cor não existe na paleta.")

        if SimulationManager.has_active_simulation():
            raise ConflictError("A partida já começou: as cores ficam travadas.")

        with cls._lock:
            player = cls._active_players.get(client_id)
            if player is None:
                raise NotFoundError("Você não está na sala.")

            if player.id in cls._saved_colors:
                raise ConflictError("Sua cor é a da partida selecionada.")

            if cls._colors.get(player.id) == color:
                return

            owner = next(
                (
                    p.nickname
                    for p in cls._active_players.values()
                    if cls._colors.get(p.id) == color
                ),
                None,
            )
            if owner is not None:
                raise ConflictError(f"{owner} pegou essa cor antes.")

            if color in cls._saved_colors.values():
                raise ConflictError("Essa cor é de um jogador da partida selecionada.")

            cls._colors[player.id] = color

        cls._emit_player_color(player, color, cls.get_team(player.id))

    @classmethod
    def apply_saved_colors(
        cls, colors: dict[int, str], teams: dict[int, int] | None = None
    ) -> None:
        """
        Ao selecionar uma partida salva: quem já jogou volta com a cor (e a equipe)
        guardada e fica travado; quem nunca jogou mantém a sua, se sobrou, ou ganha
        uma livre.
        """
        with cls._lock:
            overflow = cls._overflow(colors)
            if overflow:
                free = MAX_PLAYERS - len(colors)
                raise ConflictError(
                    f"A partida tem {len(colors)} jogadores e só cabem mais {free}. "
                    f"Quem nunca jogou nela e está na sala: {', '.join(overflow)}."
                )
            newcomers = [p for p in cls._active_players.values() if p.id not in colors]

            before = dict(cls._colors)
            cls._saved_colors = dict(colors)
            cls._saved_teams = dict(teams or {})
            for player in cls._active_players.values():
                if player.id in colors:
                    cls._colors[player.id] = colors[player.id]
                if player.id in cls._saved_teams:
                    cls._teams[player.id] = cls._saved_teams[player.id]

            # Cores guardadas valem para quem jogou; as dos ausentes ficam reservadas
            taken = set(colors.values())
            for player in newcomers:
                mine = cls._colors[player.id]
                if mine in taken:
                    mine = first_free_color(taken | set(cls._colors.values()))
                    cls._colors[player.id] = mine
                taken.add(mine)

            changed = [
                (p, cls._colors[p.id])
                for p in cls._active_players.values()
                if before.get(p.id) != cls._colors[p.id]
            ]
            # A partida salva em equipes manda: fora dela ninguém tem equipe
            in_teams = bool(teams)
            effective = {
                p.id: cls._teams.get(p.id) if in_teams else None
                for p in cls._active_players.values()
            }
            players = list(cls._active_players.values())

        for player, color in changed:
            cls._emit_player_color(player, color, effective[player.id])
        for player in players:
            cls._emit_player_team(player, effective[player.id])

    @classmethod
    def room_overflow(cls, colors: dict[int, str]) -> list[str]:
        """Apelidos de quem está na sala e nunca jogou a partida `colors`, quando ela não os comporta."""
        with cls._lock:
            return cls._overflow(colors)

    @classmethod
    def release_saved_colors(cls) -> None:
        """Sem partida selecionada as cores e as equipes da sala voltam a ser livres para trocar."""
        with cls._lock:
            cls._saved_colors = {}
            cls._saved_teams = {}

    # =========================
    # Equipes
    # =========================

    @classmethod
    def grouping(cls) -> PlayerGrouping:
        """Como a sala joga: a partida em andamento manda; sem ela vale a selecionada ou a nova."""
        if SimulationManager.has_active_simulation():
            return SimulationManager.get_active_simulation().settings.player_grouping
        return SettingsManager.effective_grouping()

    @classmethod
    def get_team(cls, user_id: int) -> int | None:
        """Equipe na sala; na partida em andamento vale a gravada nela. `None` fora do modo em equipes."""
        if cls.grouping() is not PlayerGrouping.TEAMS:
            return None
        match_teams = cls._match_teams()
        if match_teams is not None:
            return match_teams.get(user_id)
        with cls._lock:
            return cls._teams.get(user_id)

    @classmethod
    def room_teams(cls) -> dict[int, int]:
        """Equipe de cada player presente na sala, por user_id; vazio fora do modo em equipes."""
        if cls.grouping() is not PlayerGrouping.TEAMS:
            return {}
        return cls.chosen_teams()

    @classmethod
    def chosen_teams(cls) -> dict[int, int]:
        """Equipes que a sala escolheu, valham ou não para o agrupamento vigente (o host decide ao iniciar)."""
        with cls._lock:
            return {
                p.id: cls._teams[p.id]
                for p in cls._active_players.values()
                if p.id in cls._teams
            }

    @classmethod
    def set_team(cls, client_id: UUID, team: int) -> None:
        """Cada um escolhe a própria equipe; equipe não tem dono nem limite de membros."""
        if not is_valid_team(team):
            raise UnprocessableEntityError("Essa equipe não existe.")
        cls._ensure_teams_editable()

        with cls._lock:
            player = cls._active_players.get(client_id)
            if player is None:
                raise NotFoundError("Você não está na sala.")

            if player.id in cls._saved_teams:
                raise ConflictError("Sua equipe é a da partida selecionada.")

            if cls._teams.get(player.id) == team:
                return

            cls._teams[player.id] = team

        cls._emit_player_team(player, team)

    @classmethod
    def distribute_teams(cls) -> None:
        """
        Põe cada player sem equipe na equipe com menos gente. Sem equipes formadas, abre
        as duas primeiras; com uma só, abre mais uma para a partida poder começar.
        """
        cls._ensure_teams_editable()

        placed: list[tuple[UserDTO, int]] = []
        with cls._lock:
            missing = [
                p for p in cls._active_players.values() if p.id not in cls._teams
            ]
            counts = Counter(
                cls._teams[p.id]
                for p in cls._active_players.values()
                if p.id in cls._teams
            )
            pool = sorted(counts)
            for team in range(1, TEAM_COUNT + 1):
                if len(pool) >= MIN_TEAMS:
                    break
                if team not in counts:
                    pool.append(team)

            for player in missing:
                team = min(pool, key=lambda t: (counts[t], t))
                cls._teams[player.id] = team
                counts[team] += 1
                placed.append((player, team))

        for player, team in placed:
            cls._emit_player_team(player, team)

    @classmethod
    def reset_teams(cls) -> None:
        """Mudar o agrupamento da sala desfaz as equipes: nada foi jogado ainda."""
        with cls._lock:
            affected = [p for p in cls._active_players.values() if p.id in cls._teams]
            cls._teams.clear()

        for player in affected:
            cls._emit_player_team(player, None)

    @classmethod
    def release_room_teams(cls) -> None:
        """A partida começou: as equipes passam a morar nela e a próxima sala começa sem equipe."""
        with cls._lock:
            cls._teams.clear()

    @classmethod
    def ensure_teams_ready(cls, saved_teams: dict[int, int]) -> None:
        """
        Conferido ao iniciar em equipes: todo mundo na sala tem equipe (quem já jogou a
        partida salva traz a dela) e a partida tem pelo menos duas.
        """
        with cls._lock:
            teams = {
                p.nickname: saved_teams.get(p.id, cls._teams.get(p.id))
                for p in cls._active_players.values()
            }
        missing = [name for name, team in teams.items() if team is None]
        if missing:
            raise ConflictError(
                f"Para iniciar, todo mundo precisa estar numa equipe. Sem equipe: {', '.join(missing)}."
            )
        distinct = {team for team in teams.values() if team is not None}
        distinct |= set(saved_teams.values())
        if len(distinct) < MIN_TEAMS:
            raise ConflictError(
                "Em equipes, a partida precisa de pelo menos duas. "
                "Alguém troca de equipe, ou o host volta para todos contra todos."
            )

    @classmethod
    def _ensure_teams_editable(cls) -> None:
        if cls.grouping() is not PlayerGrouping.TEAMS:
            raise ConflictError("A sala joga todos contra todos: não há equipes.")
        if SimulationManager.has_active_simulation():
            raise ConflictError("A partida já começou: as equipes ficam travadas.")

    @classmethod
    def _match_teams(cls) -> dict[int, int] | None:
        """Equipes dos participantes da partida em andamento; `None` sem partida."""
        if not SimulationManager.has_active_simulation():
            return None
        return repository.simulation_player.teams(
            SimulationManager.get_active_simulation_id()
        )

    @classmethod
    def _match_colors(cls) -> dict[int, str] | None:
        """Cores dos participantes da partida em andamento; `None` sem partida."""
        if not SimulationManager.has_active_simulation():
            return None
        return repository.simulation_player.colors(
            SimulationManager.get_active_simulation_id()
        )

    @classmethod
    def _overflow(cls, colors: dict[int, str]) -> list[str]:
        """O chamador segura o `_lock`: ausentes da partida ocupam vaga, então novatos passam do teto."""
        newcomers = [
            p.nickname for p in cls._active_players.values() if p.id not in colors
        ]
        return newcomers if len(colors) + len(newcomers) > MAX_PLAYERS else []

    @classmethod
    def _match_full(cls) -> str:
        """Partida sem vaga: participante offline também ocupa a sua."""
        return f"A partida já tem {MAX_PLAYERS} jogadores e está lotada."

    @classmethod
    def _free_color(cls) -> str:
        taken = set(cls._colors.values()) | set(cls._saved_colors.values())
        try:
            return first_free_color(taken)
        except ValueError:
            absent = sum(
                1 for user_id in cls._saved_colors if user_id not in cls._colors
            )
            if absent:
                raise LockedError(ROOM_RESERVED.format(n=absent)) from None
            raise LockedError(ROOM_FULL) from None

    # =========================
    # Eventos
    # =========================

    @classmethod
    def _emit_player_join(cls, user: UserDTO, color: str):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        logger.info(f"Player joined: {user.nickname}")
        notify(
            "player_join",
            PlayerPresenceEventDTO(
                nickname=user.nickname, color=color, team=cls.get_team(user.id)
            ).to_json(),
        )

    @classmethod
    def _emit_player_exit(cls, user: UserDTO, color: str):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        logger.info(f"Player exited: {user.nickname}")
        notify(
            "player_exit",
            PlayerPresenceEventDTO(nickname=user.nickname, color=color).to_json(),
        )

    @classmethod
    def _emit_player_color(cls, user: UserDTO, color: str, team: int | None):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        notify(
            "player_color",
            PlayerPresenceEventDTO(
                nickname=user.nickname, color=color, team=team
            ).to_json(),
        )

    @classmethod
    def _emit_player_team(cls, user: UserDTO, team: int | None):
        from backend.features.realtime import notify  # noqa: PLC0415
        from backend.features.realtime.schemas import (  # noqa: PLC0415
            PlayerPresenceEventDTO,
        )

        color = cls.get_color(user.id)
        if color is None:
            return
        notify(
            "player_team",
            PlayerPresenceEventDTO(
                nickname=user.nickname, color=color, team=team
            ).to_json(),
        )
